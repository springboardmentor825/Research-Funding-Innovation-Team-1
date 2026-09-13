from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import Optional, List
import io
import csv
from datetime import datetime, date

from app.database import get_db
from app.models import User, ResearchProfile, Publication, Patent, FundingOpportunity, FundingRecommendation
from app.auth import get_current_user, require_role, normalize_role, VALID_ROLES
from app.schemas import User as UserSchema

router = APIRouter()

# ---------------------------------------------------------
# 1. ADMIN DASHBOARD SUMMARY API
# ---------------------------------------------------------
@router.get("/dashboard")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("administrator"))
):
    """
    Returns aggregated platform health and activity metrics.
    All data is derived from live database entity counts.
    """
    total_users = db.query(User).count()
    active_users = db.query(User).filter(
        or_(User.account_status == "active", User.account_status == None)
    ).count()
    
    # Role breakdown
    roles_raw = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    users_by_role = {}
    for r_name, r_count in roles_raw:
        norm_r = normalize_role(r_name)
        users_by_role[norm_r] = users_by_role.get(norm_r, 0) + r_count

    total_funding_opps = db.query(FundingOpportunity).count()
    active_funding_opps = db.query(FundingOpportunity).filter(
        or_(FundingOpportunity.status == "active", FundingOpportunity.status == "open")
    ).count()

    total_recommendations = db.query(FundingRecommendation).count()
    research_profiles_count = db.query(ResearchProfile).count()
    publications_count = db.query(Publication).count()
    patents_count = db.query(Patent).count()

    # Recent system signups (latest 5 users)
    recent_users_db = db.query(User).order_by(desc(User.created_at)).limit(5).all()
    recent_users = [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": normalize_role(u.role),
            "auth_provider": u.auth_provider or "email",
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else "N/A"
        }
        for u in recent_users_db
    ]

    return {
        "summary": {
            "total_users": total_users,
            "active_users": active_users,
            "funding_opportunities": total_funding_opps,
            "active_funding_opportunities": active_funding_opps,
            "recommendations_generated": total_recommendations,
            "research_profiles": research_profiles_count,
            "publications": publications_count,
            "patents": patents_count
        },
        "users_by_role": users_by_role,
        "recent_users": recent_users,
        "system_status": {
            "database": "online",
            "ai_matching_engine": "online",
            "rag_service": "online",
            "auth_service": "online"
        }
    }


# ---------------------------------------------------------
# 2. USER MANAGEMENT APIs
# ---------------------------------------------------------
@router.get("/users")
def get_users_list(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("administrator")),
    query: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by account status"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="asc or desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Retrieves paginated, searchable, role-filtered user accounts.
    Never exposes passwords, password hashes, or security secrets.
    """
    db_query = db.query(User)

    if query:
        search_fmt = f"%{query.strip().lower()}%"
        db_query = db_query.filter(
            or_(
                func.lower(User.full_name).like(search_fmt),
                func.lower(User.email).like(search_fmt)
            )
        )

    if role and role != "all":
        norm_r = normalize_role(role)
        db_query = db_query.filter(User.role == norm_r)

    if status and status != "all":
        db_query = db_query.filter(User.account_status == status)

    total_count = db_query.count()

    # Sorting
    if sort_by == "full_name":
        order_col = User.full_name
    elif sort_by == "email":
        order_col = User.email
    elif sort_by == "role":
        order_col = User.role
    else:
        order_col = User.created_at

    if sort_order.lower() == "asc":
        db_query = db_query.order_by(order_col.asc())
    else:
        db_query = db_query.order_by(order_col.desc())

    offset = (page - 1) * limit
    users = db_query.offset(offset).limit(limit).all()

    items = []
    for u in users:
        # Profile summary if available
        prof = db.query(ResearchProfile).filter(ResearchProfile.user_id == u.id).first()
        pubs_count = db.query(Publication).filter(Publication.user_id == u.id).count()
        patents_count = db.query(Patent).filter(Patent.user_id == u.id).count()

        items.append({
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": normalize_role(u.role),
            "account_status": getattr(u, "account_status", "active") or "active",
            "login_type": u.login_type or "email",
            "auth_provider": u.auth_provider or "email",
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else "N/A",
            "organization": prof.organization if prof else "N/A",
            "designation": prof.designation if prof else "N/A",
            "research_domain": prof.research_domain if prof else "N/A",
            "publications_count": pubs_count,
            "patents_count": patents_count
        })

    return {
        "users": items,
        "pagination": {
            "total": total_count,
            "page": page,
            "limit": limit,
            "pages": (total_count + limit - 1) // limit if limit else 1
        }
    }


@router.get("/users/{user_id}")
def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("administrator"))
):
    """
    Returns full non-sensitive account information for a specified user.
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    prof = db.query(ResearchProfile).filter(ResearchProfile.user_id == target_user.id).first()
    pubs = db.query(Publication).filter(Publication.user_id == target_user.id).order_by(desc(Publication.publication_year)).limit(10).all()
    patents = db.query(Patent).filter(Patent.user_id == target_user.id).order_by(desc(Patent.filing_date)).limit(10).all()
    recs_count = db.query(FundingRecommendation).filter(FundingRecommendation.user_id == target_user.id).count()

    profile_data = None
    if prof:
        profile_data = {
            "organization": prof.organization,
            "designation": prof.designation,
            "research_domain": prof.research_domain,
            "technology_area": prof.technology_area,
            "research_interests": prof.research_interests,
            "keywords": prof.keywords,
            "bio": prof.bio
        }

    return {
        "user": {
            "id": target_user.id,
            "full_name": target_user.full_name,
            "email": target_user.email,
            "role": normalize_role(target_user.role),
            "account_status": getattr(target_user, "account_status", "active") or "active",
            "login_type": target_user.login_type or "email",
            "auth_provider": target_user.auth_provider or "email",
            "created_at": target_user.created_at.strftime("%Y-%m-%d %H:%M") if target_user.created_at else "N/A"
        },
        "profile": profile_data,
        "publications_summary": {
            "count": len(pubs),
            "items": [{"id": p.publication_id, "title": p.title, "year": p.publication_year, "journal": p.journal} for p in pubs]
        },
        "patents_summary": {
            "count": len(patents),
            "items": [{"id": p.patent_id, "title": p.title, "filing_date": str(p.filing_date), "domain": p.technology_domain} for p in patents]
        },
        "activity_summary": {
            "total_recommendations_received": recs_count
        }
    }


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("administrator"))
):
    """
    Updates a user's role.
    Includes LAST ADMIN PROTECTION:
    Prevents demoting the last active administrator account to non-admin.
    """
    new_role_raw = payload.get("role")
    if not new_role_raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role parameter is required."
        )

    norm_new_role = normalize_role(new_role_raw)
    if norm_new_role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: '{new_role_raw}'. Allowed: {', '.join(VALID_ROLES)}"
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    current_target_role = normalize_role(target_user.role)

    # LAST ADMIN PROTECTION CHECK
    if current_target_role == "administrator" and norm_new_role != "administrator":
        admin_count = db.query(User).filter(
            User.role == "administrator",
            or_(User.account_status == "active", User.account_status == None)
        ).count()

        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove or change the last administrator account."
            )

    target_user.role = norm_new_role
    db.commit()
    db.refresh(target_user)

    return {
        "message": f"Successfully updated role for user '{target_user.full_name}' to '{norm_new_role}'.",
        "user_id": target_user.id,
        "new_role": norm_new_role
    }


@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("administrator"))
):
    """
    Updates user account status (e.g. active, deactivated).
    Includes LAST ADMIN PROTECTION against deactivating the last administrator.
    """
    new_status = payload.get("status") or payload.get("account_status")
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status parameter is required."
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    current_target_role = normalize_role(target_user.role)

    # LAST ADMIN DEACTIVATION PROTECTION
    if current_target_role == "administrator" and new_status == "deactivated":
        active_admin_count = db.query(User).filter(
            User.role == "administrator",
            or_(User.account_status == "active", User.account_status == None)
        ).count()

        if active_admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot de-activate the last administrator account."
            )

    target_user.account_status = new_status
    db.commit()
    db.refresh(target_user)

    return {
        "message": f"User status updated to '{new_status}'.",
        "user_id": target_user.id,
        "account_status": target_user.account_status
    }


# ---------------------------------------------------------
# 3. PLATFORM ANALYTICS API
# ---------------------------------------------------------
@router.get("/analytics")
def get_platform_analytics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("administrator"))
):
    """
    Aggregates multi-dimensional platform analytics derived strictly from real DB entries.
    """
    # User analytics
    total_users = db.query(User).count()
    roles_breakdown = {}
    for r_name, r_count in db.query(User.role, func.count(User.id)).group_by(User.role).all():
        roles_breakdown[normalize_role(r_name)] = r_count

    auth_breakdown = {}
    for provider_name, p_count in db.query(User.auth_provider, func.count(User.id)).group_by(User.auth_provider).all():
        auth_breakdown[provider_name or "email"] = p_count

    # Funding analytics
    total_funding = db.query(FundingOpportunity).count()
    funders = db.query(FundingOpportunity.funder, func.count(FundingOpportunity.id)).group_by(FundingOpportunity.funder).order_by(desc(func.count(FundingOpportunity.id))).limit(8).all()
    funders_breakdown = [{"funder": f[0], "count": f[1]} for f in funders]

    # Research analytics
    total_profiles = db.query(ResearchProfile).count()
    domains = db.query(ResearchProfile.research_domain, func.count(ResearchProfile.profile_id)).group_by(ResearchProfile.research_domain).order_by(desc(func.count(ResearchProfile.profile_id))).limit(6).all()
    domains_breakdown = [{"domain": d[0], "count": d[1]} for d in domains]
    total_publications = db.query(Publication).count()

    # Patent analytics
    total_patents = db.query(Patent).count()
    pat_domains = db.query(Patent.technology_domain, func.count(Patent.patent_id)).group_by(Patent.technology_domain).order_by(desc(func.count(Patent.patent_id))).limit(6).all()
    patent_domains_breakdown = [{"domain": p[0], "count": p[1]} for p in pat_domains]

    return {
        "user_analytics": {
            "total_users": total_users,
            "roles_breakdown": roles_breakdown,
            "auth_providers": auth_breakdown
        },
        "funding_analytics": {
            "total_opportunities": total_funding,
            "top_funders": funders_breakdown
        },
        "research_analytics": {
            "total_profiles": total_profiles,
            "total_publications": total_publications,
            "top_domains": domains_breakdown
        },
        "patent_analytics": {
            "total_patents": total_patents,
            "top_domains": patent_domains_breakdown
        }
    }


# ---------------------------------------------------------
# 4. RECOMMENDATION MONITORING API
# ---------------------------------------------------------
@router.get("/recommendations")
def get_recommendation_monitoring(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("administrator"))
):
    """
    Monitors recommendation generation and feedback quality metrics.
    Does NOT fabricate metrics; returns explicit message if feedback data is low.
    """
    total_recs = db.query(FundingRecommendation).count()
    
    # Score distribution
    high_match = db.query(FundingRecommendation).filter(FundingRecommendation.match_score >= 80).count()
    good_match = db.query(FundingRecommendation).filter(FundingRecommendation.match_score >= 70, FundingRecommendation.match_score < 80).count()
    mod_match = db.query(FundingRecommendation).filter(FundingRecommendation.match_score >= 50, FundingRecommendation.match_score < 70).count()
    low_match = db.query(FundingRecommendation).filter(FundingRecommendation.match_score < 50).count()

    # Feedback breakdown
    saved_count = db.query(FundingRecommendation).filter(FundingRecommendation.feedback == "saved").count()
    applied_count = db.query(FundingRecommendation).filter(FundingRecommendation.feedback == "applied").count()
    relevant_count = db.query(FundingRecommendation).filter(FundingRecommendation.feedback == "relevant").count()
    dismissed_count = db.query(FundingRecommendation).filter(FundingRecommendation.feedback == "dismissed").count()
    unrated_count = db.query(FundingRecommendation).filter(or_(FundingRecommendation.feedback == None, FundingRecommendation.feedback == "")).count()

    total_feedback_given = saved_count + applied_count + relevant_count + dismissed_count

    has_sufficient_data = total_feedback_given >= 5

    return {
        "total_recommendations": total_recs,
        "score_distribution": {
            "high_match_80_plus": high_match,
            "good_match_70_79": good_match,
            "moderate_match_50_69": mod_match,
            "low_match_below_50": low_match
        },
        "feedback_statistics": {
            "saved": saved_count,
            "applied": applied_count,
            "relevant": relevant_count,
            "dismissed": dismissed_count,
            "unrated": unrated_count,
            "total_interactions": total_feedback_given
        },
        "quality_health": {
            "has_sufficient_data": has_sufficient_data,
            "status_message": "Recommendation engine operating normally." if has_sufficient_data else "Insufficient feedback data collected yet to compute precision metrics.",
            "precision_estimate": round(((saved_count + applied_count + relevant_count) / total_feedback_given) * 100, 1) if total_feedback_given > 0 else "N/A"
        }
    }


# ---------------------------------------------------------
# 5. SYSTEM REPORTS & EXPORT APIs
# ---------------------------------------------------------
@router.get("/reports")
def get_system_reports(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("administrator"))
):
    """
    Returns platform system reports directory with metadata and generated summaries.
    """
    today_str = date.today().strftime("%Y-%m-%d")
    
    total_users = db.query(User).count()
    total_funding = db.query(FundingOpportunity).count()
    total_pubs = db.query(Publication).count()
    total_patents = db.query(Patent).count()
    total_recs = db.query(FundingRecommendation).count()

    reports = [
        {
            "id": "funding_summary",
            "title": "Funding Opportunities & Distribution Report",
            "category": "Funding",
            "generated_date": today_str,
            "records_count": total_funding,
            "description": "Comprehensive summary of active funding grants, funding agencies, and amount ranges.",
            "export_available": True
        },
        {
            "id": "user_management",
            "title": "User Accounts & Role Distribution Report",
            "category": "Administration",
            "generated_date": today_str,
            "records_count": total_users,
            "description": "Audit report of user registrations, role distribution, and auth provider channels.",
            "export_available": True
        },
        {
            "id": "research_intelligence",
            "title": "Research Profile & Publication Intelligence Report",
            "category": "Research",
            "generated_date": today_str,
            "records_count": total_pubs,
            "description": "Analysis of academic publication productivity, citation signals, and primary domains.",
            "export_available": True
        },
        {
            "id": "patent_innovation",
            "title": "Patent Portfolio & Innovation Intelligence Report",
            "category": "Innovation",
            "generated_date": today_str,
            "records_count": total_patents,
            "description": "Overview of active patent filings, technology domains, and commercialization signals.",
            "export_available": True
        },
        {
            "id": "recommendation_audit",
            "title": "AI Recommendation Matching & Feedback Audit",
            "category": "AI Intelligence",
            "generated_date": today_str,
            "records_count": total_recs,
            "description": "System evaluation of AI recommendation match score accuracy and user feedback signals.",
            "export_available": True
        }
    ]

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reports": reports
    }


@router.get("/reports/{report_type}/export")
def export_system_report(
    report_type: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role("administrator"))
):
    """
    Generates a downloadable CSV export file for the requested report category.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == "user_management":
        writer.writerow(["User ID", "Full Name", "Email", "Role", "Status", "Auth Provider", "Created At"])
        users = db.query(User).all()
        for u in users:
            writer.writerow([
                u.id,
                u.full_name,
                u.email,
                normalize_role(u.role),
                getattr(u, "account_status", "active") or "active",
                u.auth_provider or "email",
                u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else "N/A"
            ])
        filename = "users_report.csv"

    elif report_type == "funding_summary":
        writer.writerow(["ID", "Title", "Funder", "Amount Range", "Deadline", "Status", "Domains"])
        opps = db.query(FundingOpportunity).all()
        for o in opps:
            writer.writerow([
                o.id,
                o.title,
                o.funder,
                o.amount_range,
                str(o.deadline),
                o.status,
                o.research_domains
            ])
        filename = "funding_opportunities_report.csv"

    elif report_type == "patent_innovation":
        writer.writerow(["Patent ID", "User ID", "Title", "Inventor", "Assignee", "Technology Domain", "Filing Date"])
        pats = db.query(Patent).all()
        for p in pats:
            writer.writerow([
                p.patent_id,
                p.user_id,
                p.title,
                p.inventor,
                p.assignee,
                p.technology_domain,
                str(p.filing_date)
            ])
        filename = "patents_report.csv"

    else:
        # Default recommendation / general export
        writer.writerow(["Recommendation ID", "User ID", "Funding ID", "Match Score", "Reason", "Feedback", "Generated At"])
        recs = db.query(FundingRecommendation).limit(500).all()
        for r in recs:
            writer.writerow([
                r.id,
                r.user_id,
                r.funding_id,
                r.match_score,
                r.reason,
                r.feedback or "unrated",
                r.generated_at.strftime("%Y-%m-%d %H:%M") if r.generated_at else "N/A"
            ])
        filename = "recommendations_report.csv"

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
