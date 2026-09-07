# backend/app/services/dashboard_service.py

from typing import Dict, Any, List
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.models import User, FundingOpportunity, Publication, Patent, FundingRecommendation
from app.services import (
    researcher_feature_service,
    funding_matching_service,
    funding_analytics_service,
    collaboration_service,
    patent_intelligence_service,
    researcher_intelligence_service,
    alert_service
)

def get_integrated_dashboard_data(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Aggregate outputs from Parts 1-11 into a single integrated dashboard data structure.
    Does NOT recalculate or duplicate core business logic.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found.")

    # 1. Part 9: 360° Researcher Profile Intelligence
    r_intelligence = researcher_intelligence_service.get_researcher_intelligence_profile(db, user_id)

    # 2. Parts 4 & 5: Funding Recommendations & Personalization Breakdown
    recs_data = funding_matching_service.rank_funding_opportunities(db, user_id, top_k=10)
    top_recs = recs_data.get("recommendations", [])

    # 3. Part 6: Funding Analytics & Recommendation System Health
    analytics_dash = funding_analytics_service.get_dashboard_summary(db, user_id)

    # 4. Parts 7 & 10: Collaboration Recommendations & Network Summary
    collab_data = collaboration_service.get_collaboration_recommendations(db, user_id, limit=5)
    collaborators = collab_data.get("collaborators", [])

    # 5. Parts 8 & 11: Patent & Innovation Intelligence Analytics
    patent_analytics = patent_intelligence_service.get_patent_intelligence_analytics(db)

    # 6. Part 12: Generate & Retrieve Event Alerts
    alerts = alert_service.generate_user_alerts(db, user_id)
    unread_alerts_count = sum(1 for a in alerts if not a.get("is_read"))

    # 7. Calculate Authoritative KPIs directly from backend outputs
    strong_matches = sum(1 for r in top_recs if float(r.get("match_score", 0)) >= 75.0)
    upcoming_deadlines = analytics_dash.get("kpis", {}).get("upcoming_deadlines_30d", 0)
    saved_count = analytics_dash.get("kpis", {}).get("saved_opportunities", 0)
    applied_count = analytics_dash.get("kpis", {}).get("applied_opportunities", 0)

    total_active_funding = db.query(FundingOpportunity).filter(FundingOpportunity.status == "active").count()
    if total_active_funding == 0:
        total_active_funding = db.query(FundingOpportunity).count()

    user_pub_count = db.query(Publication).filter(Publication.user_id == user_id).count()
    user_pat_count = db.query(Patent).filter(Patent.user_id == user_id).count()

    emerging_techs = patent_analytics.get("emerging_technologies", [])
    network_size = collab_data.get("total_candidates_evaluated", 0)

    kpis = {
        "active_funding": total_active_funding,
        "strong_matches": strong_matches,
        "upcoming_deadlines": upcoming_deadlines,
        "potential_collaborators": len(collaborators),
        "network_size": network_size,
        "publications": user_pub_count,
        "patents": user_pat_count,
        "emerging_technologies": len(emerging_techs),
        "saved_opportunities": saved_count,
        "applications": applied_count,
        "unread_alerts": unread_alerts_count
    }

    # 8. Build Chronological Recent Research Intelligence Timeline
    recent_activity = []
    
    # A. Top Funding Matches
    for r in top_recs[:3]:
        recent_activity.append({
            "id": f"funding_{r.get('funding_id')}",
            "category": "funding",
            "title": f"Strong Funding Match: {r.get('title')}",
            "description": f"Match Score: {r.get('match_score')}%. Funder: {r.get('funder')}",
            "timestamp": "Recently Scored",
            "entity_type": "funding",
            "entity_id": r.get("funding_id")
        })

    # B. Top Collaborators
    for c in collaborators[:2]:
        recent_activity.append({
            "id": f"collab_{c.get('researcher_id')}",
            "category": "collaboration",
            "title": f"Potential Collaborator: {c.get('name')}",
            "description": f"Match Score: {c.get('score')}%. Shared Tech: {', '.join(c.get('shared_technologies', [])[:2])}",
            "timestamp": "Network Active",
            "entity_type": "collaborator",
            "entity_id": c.get("researcher_id")
        })

    # C. Innovation Trends
    if emerging_techs:
        top_e = emerging_techs[0]
        recent_activity.append({
            "id": f"innovation_{top_e.get('technology')}",
            "category": "patent",
            "title": f"Emerging Innovation Trend: {top_e.get('technology')}",
            "description": f"Filing growth acceleration (+{top_e.get('growth_rate', 0)}%). Active patents: {top_e.get('patent_count')}.",
            "timestamp": "Trending Now",
            "entity_type": "patent",
            "entity_id": 0
        })

    return {
        "user_id": user_id,
        "kpis": kpis,
        "researcher": r_intelligence,
        "funding": {
            "top_recommendations": top_recs,
            "upcoming_deadlines": analytics_dash.get("upcoming_deadlines", []),
            "domain_distribution": analytics_dash.get("domain_distribution", [])
        },
        "collaboration": {
            "top_collaborators": collaborators,
            "total_candidates": collab_data.get("total_candidates_evaluated", 0)
        },
        "network": {
            "network_size": network_size,
            "potential_collaborators_count": len(collaborators)
        },
        "patents": {
            "total_patents": patent_analytics.get("total_patents", 0),
            "active_patents": patent_analytics.get("active_patents", 0),
            "expired_patents": patent_analytics.get("expired_patents", 0),
            "recent_patents": patent_analytics.get("recent_patents", [])
        },
        "innovation": {
            "emerging_technologies": emerging_techs,
            "top_technology_domains": patent_analytics.get("technology_distribution", {})
        },
        "analytics": {
            "health_score": analytics_dash.get("health_score", {}),
            "score_distribution": analytics_dash.get("score_distribution", []),
            "feedback_summary": analytics_dash.get("feedback_summary", {})
        },
        "recent_activity": recent_activity,
        "alerts": alerts
    }
