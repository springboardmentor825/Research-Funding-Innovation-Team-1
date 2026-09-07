# backend/app/routes/collaboration.py

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.research_intelligence import CollaborationResponse
from app.services import collaboration_service

router = APIRouter()

@router.get("/{user_id}/collaborators", response_model=CollaborationResponse)
def get_collaborator_recommendations(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    domain: Optional[str] = Query(default=None, description="Optional domain filter"),
    db: Session = Depends(get_db)
):
    """
    Retrieve Part 7 Research Collaboration Recommendations for the specified researcher (user_id).
    Calculates multi-dimensional compatibility, shared vs. complementary expertise, and evidence explanations.
    """
    results = collaboration_service.get_collaboration_recommendations(
        db, user_id=user_id, limit=limit, domain_filter=domain
    )
    if results is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Researcher with User ID {user_id} does not exist."
        )
    return results
