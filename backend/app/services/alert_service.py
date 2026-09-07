# backend/app/services/alert_service.py

import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Alert, User, FundingOpportunity, Publication, Patent
from app.services import (
    funding_matching_service,
    funding_analytics_service,
    collaboration_service,
    patent_intelligence_service,
    researcher_intelligence_service
)

def _generate_event_signature(user_id: int, alert_type: str, entity_type: str, entity_id: int, detail_str: str = "") -> str:
    """Generate deterministic signature key for alert deduplication."""
    raw = f"{user_id}:{alert_type}:{entity_type}:{entity_id}:{detail_str}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

def generate_user_alerts(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Generate meaningful, event-driven alerts for a specific user ID based on real DB data.
    Uses strict deduplication via event_signature.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    created_alerts = []
    today = date.today()

    # --------------------------------------------------------------------------
    # 1. FUNDING ALERTS (High Matches & Deadline Urgency)
    # --------------------------------------------------------------------------
    try:
        recs_data = funding_matching_service.rank_funding_opportunities(db, user_id, top_k=15)
        recommendations = recs_data.get("recommendations", [])

        for rec in recommendations:
            opp_id = rec.get("funding_id")
            score = float(rec.get("match_score", 0))
            title = rec.get("title", "Funding Opportunity")
            deadline_str = rec.get("deadline")

            # A. High Funding Match Alert (score >= 80)
            if score >= 80.0:
                sig = _generate_event_signature(user_id, "funding", "funding_opportunity", opp_id, "high_match")
                existing = db.query(Alert).filter(Alert.event_signature == sig).first()
                if not existing:
                    alert = Alert(
                        user_id=user_id,
                        alert_type="funding",
                        title=f"Strong Funding Match: {title}",
                        message=f"New high match recommendation ({score:.1f}% fit). Focus area aligns strongly with your research profile.",
                        priority="high" if score >= 85.0 else "medium",
                        related_entity_type="funding",
                        related_entity_id=opp_id,
                        event_signature=sig
                    )
                    db.add(alert)
                    created_alerts.append(alert)

            # B. Deadline Approaching Alert (score >= 65, deadline within 30 days)
            if deadline_str and score >= 65.0:
                try:
                    if isinstance(deadline_str, str):
                        dl_date = datetime.strptime(deadline_str[:10], "%Y-%m-%d").date()
                    elif isinstance(deadline_str, (datetime, date)):
                        dl_date = deadline_str if isinstance(deadline_str, date) else deadline_str.date()
                    else:
                        dl_date = None
                except Exception:
                    dl_date = None

                if dl_date:
                    days_remaining = (dl_date - today).days
                    if 0 <= days_remaining <= 30:
                        urgency = "high" if days_remaining <= 10 else "medium"
                        sig = _generate_event_signature(user_id, "funding_deadline", "funding_opportunity", opp_id, f"dl_{days_remaining}")
                        existing = db.query(Alert).filter(Alert.event_signature == sig).first()
                        if not existing:
                            alert = Alert(
                                user_id=user_id,
                                alert_type="funding",
                                title=f"Deadline Alert: {title}",
                                message=f"Application deadline in {days_remaining} days ({dl_date.strftime('%b %d, %Y')}). Match score: {score:.1f}%.",
                                priority=urgency,
                                related_entity_type="funding",
                                related_entity_id=opp_id,
                                event_signature=sig,
                                expires_at=datetime.combine(dl_date + timedelta(days=1), datetime.min.time())
                            )
                            db.add(alert)
                            created_alerts.append(alert)
    except Exception as e:
        print(f"Warning: Failed to generate funding alerts for user {user_id}: {e}")

    # --------------------------------------------------------------------------
    # 2. COLLABORATION ALERTS (Strong Peers)
    # --------------------------------------------------------------------------
    try:
        collab_data = collaboration_service.get_collaboration_recommendations(db, user_id, limit=5)
        collaborators = collab_data.get("collaborators", [])

        for col in collaborators:
            c_id = col.get("researcher_id")
            c_name = col.get("name", "Researcher")
            c_score = float(col.get("score", 0))
            shared_techs = col.get("shared_technologies", [])

            if c_score >= 75.0:
                sig = _generate_event_signature(user_id, "collaboration", "researcher", c_id, "top_match")
                existing = db.query(Alert).filter(Alert.event_signature == sig).first()
                if not existing:
                    alert = Alert(
                        user_id=user_id,
                        alert_type="collaboration",
                        title=f"Potential Collaborator Identified: {c_name}",
                        message=f"{c_name} shares strong research alignment ({c_score:.1f}% match) in {', '.join(shared_techs[:2]) if shared_techs else 'your domain'}.",
                        priority="high" if c_score >= 85.0 else "medium",
                        related_entity_type="collaborator",
                        related_entity_id=c_id,
                        event_signature=sig
                    )
                    db.add(alert)
                    created_alerts.append(alert)
    except Exception as e:
        print(f"Warning: Failed to generate collaboration alerts for user {user_id}: {e}")

    # --------------------------------------------------------------------------
    # 3. PATENT & INNOVATION ALERTS (Emerging Technology Growth)
    # --------------------------------------------------------------------------
    try:
        pat_analytics = patent_intelligence_service.get_patent_intelligence_analytics(db)
        emerging = pat_analytics.get("emerging_technologies", [])

        for em in emerging[:3]:
            tech_name = em.get("technology", "Emerging Tech")
            count = em.get("patent_count", 0)
            sig = _generate_event_signature(user_id, "patent", "technology", 0, f"emerging_{tech_name}")
            existing = db.query(Alert).filter(Alert.event_signature == sig).first()
            if not existing:
                alert = Alert(
                    user_id=user_id,
                    alert_type="patent",
                    title=f"Emerging Technology Trend: {tech_name}",
                    message=f"Significant patent filing acceleration detected in '{tech_name}' ({count} patents in active portfolio).",
                    priority="medium",
                    related_entity_type="patent",
                    related_entity_id=0,
                    event_signature=sig
                )
                db.add(alert)
                created_alerts.append(alert)
    except Exception as e:
        print(f"Warning: Failed to generate patent alerts for user {user_id}: {e}")

    # --------------------------------------------------------------------------
    # 4. RESEARCH PROFILE ALERTS (Completeness & Activity)
    # --------------------------------------------------------------------------
    try:
        r_intel = researcher_intelligence_service.get_researcher_intelligence_profile(db, user_id)
        comp_score = r_intel.get("profile_completeness", {}).get("completeness_score", 100)

        if comp_score < 80.0:
            sig = _generate_event_signature(user_id, "research", "profile", user_id, f"incomplete_{int(comp_score)}")
            existing = db.query(Alert).filter(Alert.event_signature == sig).first()
            if not existing:
                alert = Alert(
                    user_id=user_id,
                    alert_type="research",
                    title="Profile Optimization Suggestion",
                    message=f"Your researcher profile completeness is currently {comp_score:.0f}%. Add research interests and keywords to boost recommendation accuracy.",
                    priority="low",
                    related_entity_type="profile",
                    related_entity_id=user_id,
                    event_signature=sig
                )
                db.add(alert)
                created_alerts.append(alert)
    except Exception as e:
        print(f"Warning: Failed to generate profile alerts for user {user_id}: {e}")

    try:
        db.commit()
        for a in created_alerts:
            db.refresh(a)
    except Exception as e:
        db.rollback()
        print(f"Warning: Failed to commit alerts: {e}")

    return get_user_alerts(db, user_id)

def get_user_alerts(
    db: Session,
    user_id: int,
    unread_only: bool = False,
    priority: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve active non-dismissed alerts for user ID."""
    query = db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.is_dismissed == False
    )

    if unread_only:
        query = query.filter(Alert.is_read == False)
    if priority:
        query = query.filter(Alert.priority == priority.lower())

    alerts = query.order_by(desc(Alert.created_at)).all()
    today_dt = datetime.now()

    result = []
    for a in alerts:
        # Auto-expire temporary alerts if past expires_at
        if a.expires_at and a.expires_at < today_dt:
            continue

        result.append({
            "id": a.id,
            "user_id": a.user_id,
            "alert_type": a.alert_type,
            "title": a.title,
            "message": a.message,
            "priority": a.priority,
            "related_entity_type": a.related_entity_type,
            "related_entity_id": a.related_entity_id,
            "is_read": a.is_read,
            "is_dismissed": a.is_dismissed,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M:%S") if a.created_at else None,
            "expires_at": a.expires_at.strftime("%Y-%m-%d %H:%M:%S") if a.expires_at else None
        })

    return result

def mark_alert_as_read(db: Session, alert_id: int, user_id: int) -> Dict[str, Any]:
    """Mark alert as read with user authorization check."""
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == user_id).first()
    if not alert:
        return {"success": False, "message": f"Alert #{alert_id} not found for user {user_id}."}

    alert.is_read = True
    try:
        db.commit()
        db.refresh(alert)
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

    return {"success": True, "alert_id": alert_id, "is_read": True}

def dismiss_alert(db: Session, alert_id: int, user_id: int) -> Dict[str, Any]:
    """Soft-delete/dismiss alert so it does not reappear."""
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == user_id).first()
    if not alert:
        return {"success": False, "message": f"Alert #{alert_id} not found for user {user_id}."}

    alert.is_dismissed = True
    try:
        db.commit()
        db.refresh(alert)
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

    return {"success": True, "alert_id": alert_id, "is_dismissed": True}
