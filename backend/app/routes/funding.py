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
    FundingRecommendationItem,
    FundingRecommendationResponse,
    FundingFeedbackRequest
)
from app.services.funding_matching_service import rank_funding_opportunities, calculate_match_score
from app.services.researcher_feature_service import build_researcher_features
from app.services.funding_feature_service import extract_funding_features

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

@router.get("/saved/{user_id}", response_model=List[FundingRecommendationItem])
def get_user_saved_funding(user_id: int, db: Session = Depends(get_db)):
    """Retrieve all funding opportunities saved by the user."""
    recs = db.query(FundingRecommendation).filter(
        FundingRecommendation.user_id == user_id,
        FundingRecommendation.status == "saved"
    ).all()
    
    saved_items = []
    researcher_features = build_researcher_features(db, user_id)
    for rec in recs:
        opp = db.query(FundingOpportunity).filter(FundingOpportunity.id == rec.funding_id).first()
        if opp:
            opp_feat = extract_funding_features(opp)
            rec_item = calculate_match_score(researcher_features, opp_feat, user_feedback="saved")
            saved_items.append(rec_item)
    return saved_items

@router.get("/history/{user_id}")
def get_user_recommendation_history(user_id: int, db: Session = Depends(get_db)):
    """Retrieve user's recommendation activity log (viewed, saved, dismissed, applied, feedback)."""
    recs = db.query(FundingRecommendation).filter(FundingRecommendation.user_id == user_id).all()
    
    history_items = []
    for rec in recs:
        opp = db.query(FundingOpportunity).filter(FundingOpportunity.id == rec.funding_id).first()
        history_items.append({
            "funding_id": rec.funding_id,
            "title": opp.title if opp else f"Opportunity #{rec.funding_id}",
            "funder": opp.funder if opp else "N/A",
            "match_score": int(rec.match_score),
            "status": rec.status or "viewed",
            "feedback": rec.feedback or rec.status or "viewed",
            "created_at": str(rec.created_at) if hasattr(rec, "created_at") else None
        })
    return {"user_id": user_id, "activity_count": len(history_items), "history": history_items}

# ============================================================
# FUNDING SEARCH / FILTER ENDPOINT
# ============================================================

@router.get("/search", response_model=List[FundingRecommendationItem])
def search_funding_opportunities(
    keyword: Optional[str] = Query(None, description="Search term in title, description, or keywords"),
    domain: Optional[str] = Query(None, description="Filter by research domain"),
    technology_area: Optional[str] = Query(None, description="Filter by technology area"),
    funder: Optional[str] = Query(None, description="Filter by funder name"),
    minimum_score: Optional[int] = Query(None, description="Filter by minimum semantic fit score"),
    deadline_before: Optional[date] = Query(None, description="Filter by deadline before given date"),
    opp_status: Optional[str] = Query(None, alias="status", description="Filter by status (open/expired/etc)"),
    user_id: Optional[int] = Query(16, description="User ID for personalized match score calculation"),
    db: Session = Depends(get_db)
):
    """
    Search and filter funding opportunities with dynamic personalized match score calculation.
    """
    query = db.query(FundingOpportunity)

    if keyword and isinstance(keyword, str) and keyword.strip():
        pattern = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                FundingOpportunity.title.like(pattern),
                FundingOpportunity.description.like(pattern),
                FundingOpportunity.keywords.like(pattern),
                FundingOpportunity.match_badges.like(pattern)
            )
        )

    if domain and isinstance(domain, str) and domain.strip():
        query = query.filter(FundingOpportunity.research_domains.like(f"%{domain.strip()}%"))

    if technology_area and isinstance(technology_area, str) and technology_area.strip():
        query = query.filter(FundingOpportunity.technology_areas.like(f"%{technology_area.strip()}%"))

    if funder and isinstance(funder, str) and funder.strip():
        query = query.filter(FundingOpportunity.funder.like(f"%{funder.strip()}%"))

    if minimum_score is not None and isinstance(minimum_score, (int, float)):
        query = query.filter(FundingOpportunity.semantic_fit >= minimum_score)

    if deadline_before and isinstance(deadline_before, date):
        query = query.filter(FundingOpportunity.deadline <= deadline_before)

    if opp_status and isinstance(opp_status, str) and opp_status.strip():
        query = query.filter(FundingOpportunity.status == opp_status.strip().lower())
    else:
        # Default to open opportunities in search unless requested otherwise
        query = query.filter(FundingOpportunity.status == "open")

    try:
        opps = query.all()

        # Calculate personalized match scores for the user
        target_user_id = user_id or 16
        researcher_features = build_researcher_features(db, target_user_id)
        
        # Retrieve user feedback items to apply boosts/penalties
        user_recs = db.query(FundingRecommendation).filter(FundingRecommendation.user_id == target_user_id).all()
        feedback_map = {r.funding_id: (r.feedback or r.status) for r in user_recs if r.feedback or r.status}

        results = []
        for opp in opps:
            opp_feat = extract_funding_features(opp)
            fb = feedback_map.get(opp.id)
            rec_item = calculate_match_score(researcher_features, opp_feat, user_feedback=fb)
            results.append(rec_item)

        # Sort by match score descending
        results.sort(key=lambda x: x["match_score"] if isinstance(x, dict) else getattr(x, "match_score", 0), reverse=True)
        return results
    except Exception as exc:
        import traceback
        print("ERROR IN SEARCH_FUNDING_OPPORTUNITIES:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(exc))

# ============================================================
# STANDARD CRUD ENDPOINTS (For backward compatibility)
# ============================================================

@router.get("/", response_model=List[FundingRecommendationItem])
def list_funding(
    user_id: Optional[int] = Query(16, description="User ID for personalized match score calculation"),
    db: Session = Depends(get_db)
):
    """Retrieve all open funding opportunities with personalized match scores."""
    opps = db.query(FundingOpportunity).filter(FundingOpportunity.status == "open").all()
    target_user_id = user_id or 16
    researcher_features = build_researcher_features(db, target_user_id)

    user_recs = db.query(FundingRecommendation).filter(FundingRecommendation.user_id == target_user_id).all()
    feedback_map = {r.funding_id: (r.feedback or r.status) for r in user_recs if r.feedback or r.status}

    results = []
    for opp in opps:
        opp_feat = extract_funding_features(opp)
        fb = feedback_map.get(opp.id)
        rec_item = calculate_match_score(researcher_features, opp_feat, user_feedback=fb)
        results.append(rec_item)

    results.sort(key=lambda x: x["match_score"] if isinstance(x, dict) else getattr(x, "match_score", 0), reverse=True)
    return results

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
