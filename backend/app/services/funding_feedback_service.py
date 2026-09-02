# backend/app/services/funding_feedback_service.py

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from app.models import User, FundingOpportunity, FundingRecommendation

ALLOWED_FEEDBACK_VALUES = {"viewed", "saved", "relevant", "not_relevant", "dismissed", "applied"}

def record_feedback(
    db: Session,
    user_id: int,
    funding_id: int,
    feedback: str,
    match_score: float = 0.0,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Store or update researcher interaction feedback for a funding opportunity recommendation.
    Supported feedback values: viewed, saved, relevant, not_relevant, dismissed, applied.
    """
    clean_feedback = (feedback or "").strip().lower()
    if clean_feedback not in ALLOWED_FEEDBACK_VALUES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feedback '{feedback}'. Supported values: {', '.join(sorted(ALLOWED_FEEDBACK_VALUES))}"
        )

    # 1. Verify User exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    # 2. Verify Funding Opportunity exists
    funding = db.query(FundingOpportunity).filter(FundingOpportunity.id == funding_id).first()
    if not funding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funding opportunity with ID {funding_id} not found."
        )

    # 3. Query existing recommendation record or create a new one
    rec = db.query(FundingRecommendation).filter(
        FundingRecommendation.user_id == user_id,
        FundingRecommendation.funding_id == funding_id
    ).first()

    if rec:
        rec.status = clean_feedback
        rec.feedback = clean_feedback
        if match_score > 0:
            rec.match_score = match_score
        if reason:
            rec.reason = reason
    else:
        rec = FundingRecommendation(
            user_id=user_id,
            funding_id=funding_id,
            match_score=match_score,
            reason=reason or "User direct interaction feedback",
            status=clean_feedback,
            feedback=clean_feedback
        )
        db.add(rec)

    try:
        db.commit()
        db.refresh(rec)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record feedback transaction: {str(e)}"
        )

    return {
        "success": True,
        "user_id": user_id,
        "funding_id": funding_id,
        "status": clean_feedback,
        "message": f"Feedback '{clean_feedback}' successfully recorded for funding opportunity #{funding_id}."
    }

def get_feedback_history(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve all recommendation interaction history for a user, joined with opportunity title and funder.
    """
    results = (
        db.query(FundingRecommendation, FundingOpportunity)
        .join(FundingOpportunity, FundingRecommendation.funding_id == FundingOpportunity.id)
        .filter(FundingRecommendation.user_id == user_id)
        .order_by(desc(FundingRecommendation.id))
        .all()
    )

    history = []
    for rec, opp in results:
        history.append({
            "id": rec.id,
            "user_id": rec.user_id,
            "funding_id": opp.id,
            "title": opp.title,
            "funder": opp.funder,
            "amount_range": opp.amount_range,
            "status": rec.status or "recommended",
            "feedback": rec.feedback,
            "match_score": rec.match_score,
            "reason": rec.reason,
            "created_at": rec.created_at or rec.generated_at,
            "updated_at": rec.updated_at or rec.generated_at
        })
    return history

def get_user_feedback_for_funding(db: Session, user_id: int, funding_id: int) -> Optional[str]:
    """Retrieve feedback status for a specific user and funding ID."""
    rec = db.query(FundingRecommendation).filter(
        FundingRecommendation.user_id == user_id,
        FundingRecommendation.funding_id == funding_id
    ).first()
    return rec.feedback if rec else None

def get_saved_funding(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Retrieve all funding opportunities saved by the user."""
    results = (
        db.query(FundingRecommendation, FundingOpportunity)
        .join(FundingOpportunity, FundingRecommendation.funding_id == FundingOpportunity.id)
        .filter(
            FundingRecommendation.user_id == user_id,
            FundingRecommendation.status == "saved"
        )
        .order_by(desc(FundingRecommendation.id))
        .all()
    )

    return [
        {
            "id": rec.id,
            "user_id": rec.user_id,
            "funding_id": opp.id,
            "title": opp.title,
            "funder": opp.funder,
            "amount_range": opp.amount_range,
            "status": "saved",
            "feedback": "saved",
            "match_score": rec.match_score,
            "reason": rec.reason,
            "created_at": rec.created_at or rec.generated_at,
            "updated_at": rec.updated_at or rec.generated_at
        }
        for rec, opp in results
    ]

def get_dismissed_funding(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Retrieve all funding opportunities dismissed by the user."""
    results = (
        db.query(FundingRecommendation, FundingOpportunity)
        .join(FundingOpportunity, FundingRecommendation.funding_id == FundingOpportunity.id)
        .filter(
            FundingRecommendation.user_id == user_id,
            FundingRecommendation.status.in_(["dismissed", "not_relevant"])
        )
        .order_by(desc(FundingRecommendation.id))
        .all()
    )

    return [
        {
            "id": rec.id,
            "user_id": rec.user_id,
            "funding_id": opp.id,
            "title": opp.title,
            "funder": opp.funder,
            "amount_range": opp.amount_range,
            "status": rec.status,
            "feedback": rec.feedback,
            "match_score": rec.match_score,
            "reason": rec.reason,
            "created_at": rec.created_at or rec.generated_at,
            "updated_at": rec.updated_at or rec.generated_at
        }
        for rec, opp in results
    ]

def get_applied_funding(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Retrieve all funding opportunities marked as applied by the user."""
    results = (
        db.query(FundingRecommendation, FundingOpportunity)
        .join(FundingOpportunity, FundingRecommendation.funding_id == FundingOpportunity.id)
        .filter(
            FundingRecommendation.user_id == user_id,
            FundingRecommendation.status == "applied"
        )
        .order_by(desc(FundingRecommendation.id))
        .all()
    )

    return [
        {
            "id": rec.id,
            "user_id": rec.user_id,
            "funding_id": opp.id,
            "title": opp.title,
            "funder": opp.funder,
            "amount_range": opp.amount_range,
            "status": "applied",
            "feedback": "applied",
            "match_score": rec.match_score,
            "reason": rec.reason,
            "created_at": rec.created_at or rec.generated_at,
            "updated_at": rec.updated_at or rec.generated_at
        }
        for rec, opp in results
    ]
