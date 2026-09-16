from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, FundingApplication, FundingOpportunity
from app.auth import get_current_user

router = APIRouter()

@router.get("/overview")
def platform_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Role-gated summary of the platform for administrators (read-only)."""
    if current_user.role != "administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required."
        )

    user_rows = (
        db.query(User.role, func.count(User.id))
        .group_by(User.role)
        .all()
    )
    user_counts = {role: count for role, count in user_rows}
    user_counts["total"] = sum(user_counts.values())

    app_rows = (
        db.query(FundingApplication.status, func.count(FundingApplication.id))
        .group_by(FundingApplication.status)
        .all()
    )
    application_counts = {st: count for st, count in app_rows}
    application_counts["total"] = sum(application_counts.values())

    open_funding = (
        db.query(func.count(FundingOpportunity.id))
        .filter(FundingOpportunity.status == "open")
        .scalar()
        or 0
    )

    recent_users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .limit(8)
        .all()
    )
    recent_users_out = [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
            "login_type": u.login_type,
            "created_at": u.created_at,
        }
        for u in recent_users
    ]

    recent_applications = (
        db.query(FundingApplication, User, FundingOpportunity)
        .join(User, FundingApplication.user_id == User.id)
        .join(FundingOpportunity, FundingApplication.funding_id == FundingOpportunity.id)
        .order_by(FundingApplication.submitted_at.desc())
        .limit(8)
        .all()
    )
    recent_applications_out = [
        {
            "id": app.id,
            "applicant_name": user.full_name,
            "applicant_email": user.email,
            "title": opp.title,
            "funder": opp.funder,
            "amount_range": opp.amount_range,
            "status": app.status,
            "submitted_at": app.submitted_at,
        }
        for app, user, opp in recent_applications
    ]

    return {
        "user_counts": user_counts,
        "application_counts": application_counts,
        "open_funding": open_funding,
        "recent_users": recent_users_out,
        "recent_applications": recent_applications_out,
    }