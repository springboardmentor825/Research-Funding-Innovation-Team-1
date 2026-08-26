from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.database import get_db
from app.models import FundingOpportunity, FundingRecommendation, User
from app.schemas import (
    FundingOpportunitySchema,
    FundingOpportunityCreate,
    FundingRecommendationResponse,
    FundingFeedbackRequest
)
from app.services.funding_matching_service import rank_funding_opportunities

router = APIRouter()

# ============================================================
# RECOMMENDATION ENGINE ENDPOINTS
# ============================================================

@router.get("/recommendations/{user_id}", response_model=FundingRecommendationResponse)
@router.post("/recommendations/{user_id}", response_model=FundingRecommendationResponse)
def get_user_funding_recommendations(
    user_id: int,
    top_k: int = Query(10, ge=1, le=100, description="Number of recommendations to return"),
    db: Session = Depends(get_db)
):
    """
    Generate personalized funding opportunity recommendations for a researcher.
    Evaluates profile, publications, patents, eligibility, and semantic fit.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    recommendations_data = rank_funding_opportunities(db, user_id, top_k=top_k)
    return recommendations_data


@router.post("/recommendations/feedback", status_code=status.HTTP_200_OK)
def submit_recommendation_feedback(
    feedback_in: FundingFeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    Store researcher feedback for a funding opportunity recommendation.
    Supported values: relevant, not_relevant, saved, applied, dismissed.
    """
    valid_feedback = ["relevant", "not_relevant", "saved", "applied", "dismissed"]
    if feedback_in.feedback not in valid_feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feedback value. Must be one of: {', '.join(valid_feedback)}"
        )

    # Check if recommendation record exists for this user and funding opportunity
    rec = db.query(FundingRecommendation).filter(
        FundingRecommendation.user_id == feedback_in.user_id,
        FundingRecommendation.funding_id == feedback_in.funding_id
    ).first()

    if rec:
        rec.feedback = feedback_in.feedback
        rec.status = feedback_in.feedback
    else:
        rec = FundingRecommendation(
            user_id=feedback_in.user_id,
            funding_id=feedback_in.funding_id,
            match_score=0.0,
            reason="User provided direct feedback",
            status=feedback_in.feedback,
            feedback=feedback_in.feedback
        )
        db.add(rec)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record feedback: {str(e)}"
        )

    return {
        "status": "success",
        "message": f"Feedback '{feedback_in.feedback}' recorded for funding_id {feedback_in.funding_id}."
    }

# ============================================================
# FUNDING SEARCH / FILTER ENDPOINT
# ============================================================

@router.get("/search", response_model=List[FundingOpportunitySchema])
def search_funding_opportunities(
    keyword: Optional[str] = Query(None, description="Search term in title, description, or keywords"),
    domain: Optional[str] = Query(None, description="Filter by research domain"),
    technology_area: Optional[str] = Query(None, description="Filter by technology area"),
    funder: Optional[str] = Query(None, description="Filter by funder name"),
    minimum_score: Optional[int] = Query(None, description="Filter by minimum semantic fit score"),
    deadline_before: Optional[date] = Query(None, description="Filter by deadline before given date"),
    opp_status: Optional[str] = Query(None, alias="status", description="Filter by status (open/expired/etc)"),
    db: Session = Depends(get_db)
):
    """
    Search and filter funding opportunities based on user-defined criteria.
    """
    query = db.query(FundingOpportunity)

    if keyword:
        pattern = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                FundingOpportunity.title.like(pattern),
                FundingOpportunity.description.like(pattern),
                FundingOpportunity.keywords.like(pattern),
                FundingOpportunity.match_badges.like(pattern)
            )
        )

    if domain:
        query = query.filter(FundingOpportunity.research_domains.like(f"%{domain.strip()}%"))

    if technology_area:
        query = query.filter(FundingOpportunity.technology_areas.like(f"%{technology_area.strip()}%"))

    if funder:
        query = query.filter(FundingOpportunity.funder.like(f"%{funder.strip()}%"))

    if minimum_score is not None:
        query = query.filter(FundingOpportunity.semantic_fit >= minimum_score)

    if deadline_before:
        query = query.filter(FundingOpportunity.deadline <= deadline_before)

    if opp_status:
        query = query.filter(FundingOpportunity.status == opp_status.strip().lower())
    else:
        # Default to open opportunities in search unless requested otherwise
        query = query.filter(FundingOpportunity.status == "open")

    return query.all()

# ============================================================
# STANDARD CRUD ENDPOINTS (For backward compatibility)
# ============================================================

@router.get("/", response_model=List[FundingOpportunitySchema])
def list_funding(db: Session = Depends(get_db)):
    """Retrieve all funding opportunities."""
    return db.query(FundingOpportunity).filter(FundingOpportunity.status == "open").all()

@router.post("/", response_model=FundingOpportunitySchema, status_code=status.HTTP_201_CREATED)
def create_funding(
    opportunity_in: FundingOpportunityCreate,
    db: Session = Depends(get_db)
):
    """Instantiate a new funding opportunity."""
    opp = FundingOpportunity(**opportunity_in.model_dump())
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return opp
