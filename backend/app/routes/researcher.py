# backend/app/routes/researcher.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.researcher import ResearcherProfileSummary
from app.services import researcher_feature_service

router = APIRouter()

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
