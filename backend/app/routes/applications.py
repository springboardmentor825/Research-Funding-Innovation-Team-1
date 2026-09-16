from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FundingApplication, FundingOpportunity, FundingRecommendation, User
from app.schemas import FundingApplicationCreate, FundingApplicationOut, FundingApplicationSummary
from app.auth import get_current_user

router = APIRouter()


@router.post("", response_model=FundingApplicationOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=FundingApplicationOut, status_code=status.HTTP_201_CREATED)
def submit_application(
    application_in: FundingApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a grant application against an open funding opportunity.
    Idempotent per (user, funding): a duplicate submit returns the existing application (409),
    """
    if not application_in.research_statement or len(application_in.research_statement.strip()) < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Research statement must be at least 30 characters long."
        )

    opp = db.query(FundingOpportunity).filter(FundingOpportunity.id == application_in.funding_id).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funding opportunity {application_in.funding_id} not found."
        )

    existing = db.query(FundingApplication).filter(
        FundingApplication.user_id == current_user.id,
        FundingApplication.funding_id == application_in.funding_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You have already applied to this funding opportunity (application #{existing.id})."
        )

    app_obj = FundingApplication(
        user_id=current_user.id,
        funding_id=application_in.funding_id,
        research_statement=application_in.research_statement.strip(),
        budget_ask=application_in.budget_ask.strip() if application_in.budget_ask else None,
        status="submitted"
    )
    db.add(app_obj)
    db.flush()

    # Keep recommendation feedback in sync
    rec = db.query(FundingRecommendation).filter(
        FundingRecommendation.user_id == current_user.id,
        FundingRecommendation.funding_id == application_in.funding_id
    ).first()
    if rec:
        rec.feedback = "applied"
        rec.status = "applied"

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit application: {str(e)}"
        )
    db.refresh(app_obj)
    return app_obj


@router.get("", response_model=List[FundingApplicationSummary])
@router.get("/", response_model=List[FundingApplicationSummary])
def list_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List the current user's submitted grant applications with funding context.
    """
    rows = (
        db.query(FundingApplication, FundingOpportunity)
        .join(FundingOpportunity, FundingApplication.funding_id == FundingOpportunity.id)
        .filter(FundingApplication.user_id == current_user.id)
        .order_by(FundingApplication.submitted_at.desc())
        .all()
    )
    return [
        {
            "id": app.id,
            "funding_id": app.funding_id,
            "title": opp.title,
            "funder": opp.funder,
            "amount_range": opp.amount_range,
            "deadline": str(opp.deadline) if opp.deadline else None,
            "status": app.status,
            "budget_ask": app.budget_ask,
            "submitted_at": app.submitted_at,
        }
        for app, opp in rows
    ]


@router.get("/{application_id}", response_model=FundingApplicationSummary, include_in_schema=True)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    row = (
        db.query(FundingApplication, FundingOpportunity)
        .join(FundingOpportunity, FundingApplication.funding_id == FundingOpportunity.id)
        .filter(FundingApplication.id == application_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")
    app, opp = row
    if app.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your application.")
    return {
        "id": app.id,
        "funding_id": app.funding_id,
        "title": opp.title,
        "funder": opp.funder,
        "amount_range": opp.amount_range,
        "deadline": str(opp.deadline) if opp.deadline else None,
        "status": app.status,
        "budget_ask": app.budget_ask,
        "submitted_at": app.submitted_at,
    }


@router.post("/{application_id}/withdraw", response_model=FundingApplicationOut)
def withdraw_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app_obj = db.query(FundingApplication).filter(FundingApplication.id == application_id).first()
    if not app_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")
    if app_obj.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your application.")
    if app_obj.status == "withdrawn":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Application already withdrawn.")

    app_obj.status = "withdrawn"
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to withdraw application: {str(e)}"
        )
    db.refresh(app_obj)
    return app_obj