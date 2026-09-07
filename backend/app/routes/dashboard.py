# backend/app/routes/dashboard.py

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import dashboard_service, alert_service

router = APIRouter()

@router.get("/dashboard/{user_id}")
def get_integrated_dashboard(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve single integrated research intelligence dashboard aggregation for user ID.
    Aggregates outputs from Parts 1-11 without recalculating core business logic.
    """
    try:
        return dashboard_service.get_integrated_dashboard_data(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard aggregation: {str(e)}"
        )

@router.get("/alerts/{user_id}")
def get_user_alerts(
    user_id: int,
    unread_only: bool = Query(False, description="Filter for unread alerts only"),
    priority: Optional[str] = Query(None, description="Filter by priority (high, medium, low)"),
    db: Session = Depends(get_db)
):
    """Retrieve active non-dismissed alerts for user ID."""
    return alert_service.get_user_alerts(db, user_id, unread_only=unread_only, priority=priority)

@router.post("/alerts/generate/{user_id}")
def trigger_alert_generation(user_id: int, db: Session = Depends(get_db)):
    """Trigger real event alert evaluation and generation for user ID."""
    alerts = alert_service.generate_user_alerts(db, user_id)
    return {
        "success": True,
        "user_id": user_id,
        "active_alerts_count": len(alerts),
        "alerts": alerts
    }

@router.patch("/alerts/{alert_id}/read")
def mark_alert_read(alert_id: int, user_id: int = Query(..., description="User ID for authorization"), db: Session = Depends(get_db)):
    """Mark specified alert as read for user ID."""
    res = alert_service.mark_alert_as_read(db, alert_id, user_id)
    if not res.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res.get("message"))
    return res

@router.patch("/alerts/{alert_id}/dismiss")
def dismiss_alert(alert_id: int, user_id: int = Query(..., description="User ID for authorization"), db: Session = Depends(get_db)):
    """Dismiss specified alert for user ID."""
    res = alert_service.dismiss_alert(db, alert_id, user_id)
    if not res.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res.get("message"))
    return res
