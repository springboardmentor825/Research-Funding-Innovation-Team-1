from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.researcher import ResearcherProfileSummary
from app.schemas.research_intelligence import (
    ResearcherIntelligenceResponse,
    ResearcherComparisonResponse
)
from app.services import researcher_feature_service, researcher_intelligence_service

router = APIRouter()

@router.get("/compare", response_model=ResearcherComparisonResponse)
def compare_researchers(
    user1: int = Query(..., description="First researcher User ID"),
    user2: int = Query(..., description="Second researcher User ID"),
    db: Session = Depends(get_db)
):
    """Compare two researchers side-by-side based on actual database evidence."""
    comp = researcher_intelligence_service.get_researcher_comparison(db, user1, user2)
    if not comp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"One or both specified researchers (ID {user1}, {user2}) do not exist."
        )
    return comp

@router.get("/intelligence", response_model=List[ResearcherIntelligenceResponse])
def get_all_researchers_intelligence(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve Researcher Profile Intelligence for all registered researchers."""
    users = db.query(User).limit(limit).all()
    results = []
    for u in users:
        prof = researcher_intelligence_service.get_researcher_intelligence_profile(db, u.id)
        if prof:
            results.append(prof)
    return results

@router.get("/{user_id}/intelligence", response_model=ResearcherIntelligenceResponse)
def get_researcher_intelligence(user_id: int, db: Session = Depends(get_db)):
    """Retrieve 360° Researcher Profile Intelligence for the specified user_id."""
    profile = researcher_intelligence_service.get_researcher_intelligence_profile(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Researcher with User ID {user_id} does not exist."
        )
    return profile

@router.get("/{user_id}/features", response_model=ResearcherProfileSummary)
def get_researcher_features(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve normalized researcher features, profile signals, publication topics,
    and patent domains for the specified user_id.
    """
    features = researcher_feature_service.build_researcher_features(db, user_id)
    if features is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} does not exist."
        )
    return features
