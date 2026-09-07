# backend/app/services/funding_analytics_service.py

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import statistics
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import (
    FundingOpportunity,
    FundingRecommendation,
    User,
    Publication,
    Patent
)

from app.services import (
    researcher_feature_service,
    funding_matching_service,
    funding_feedback_service,
    funding_personalization_service,
    funding_eligibility_service
)

SCORE_BUCKETS = [
    {"range": "90-100", "min_score": 90, "max_score": 100},
    {"range": "80-89", "min_score": 80, "max_score": 89},
    {"range": "70-79", "min_score": 70, "max_score": 79},
    {"range": "60-69", "min_score": 60, "max_score": 69},
    {"range": "50-59", "min_score": 50, "max_score": 59},
    {"range": "40-49", "min_score": 40, "max_score": 49},
    {"range": "0-39", "min_score": 0, "max_score": 39},
]

def get_global_funding_landscape(db: Session) -> Dict[str, Any]:
    """Calculate overall funding landscape analytics directly from database records."""
    opportunities = db.query(FundingOpportunity).all()
    total_opps = len(opportunities)
    
    today = date.today()
    active_cnt = 0
    expired_cnt = 0
    closed_cnt = 0
    
    deadlines_7d = 0
    deadlines_30d = 0
    deadlines_60d = 0
    deadlines_90d = 0
    
    domain_dist: Dict[str, int] = {}
    tech_dist: Dict[str, int] = {}
    funder_dist: Dict[str, int] = {}
    type_dist: Dict[str, int] = {}
    
    amounts = []
    
    for opp in opportunities:
        # Funder
        funder_name = opp.funder or "Unknown Funder"
        funder_dist[funder_name] = funder_dist.get(funder_name, 0) + 1
        
        # Funding Type
        ftype = getattr(opp, "funding_type", None) or getattr(opp, "grant_type", None) or "Grant"
        type_dist[ftype] = type_dist.get(ftype, 0) + 1
        
        # Domains
        raw_domains = getattr(opp, "eligible_domains", None) or getattr(opp, "domain", None) or "General Research"
        if isinstance(raw_domains, str):
            domains = [d.strip() for d in raw_domains.split(",") if d.strip()]
        elif isinstance(raw_domains, list):
            domains = raw_domains
        else:
            domains = ["General Research"]
            
        for d in domains:
            domain_dist[d] = domain_dist.get(d, 0) + 1
            
        # Tech areas
        raw_tech = getattr(opp, "technology_areas", None) or getattr(opp, "keywords", None) or ""
        if isinstance(raw_tech, str):
            techs = [t.strip() for t in raw_tech.split(",") if t.strip()]
        elif isinstance(raw_tech, list):
            techs = raw_tech
        else:
            techs = []
            
        for t in techs:
            tech_dist[t] = tech_dist.get(t, 0) + 1
            
        # Amounts
        amt = getattr(opp, "funding_amount", None) or getattr(opp, "amount", None)
        if amt and isinstance(amt, (int, float)) and amt > 0:
            amounts.append(float(amt))
            
        # Deadlines
        dl = opp.deadline
        if dl:
            if isinstance(dl, str):
                try:
                    dl_date = datetime.strptime(dl[:10], "%Y-%m-%d").date()
                except Exception:
                    dl_date = None
            elif isinstance(dl, datetime):
                dl_date = dl.date()
            elif isinstance(dl, date):
                dl_date = dl
            else:
                dl_date = None
                
            if dl_date:
                days_left = (dl_date - today).days
                if days_left < 0:
                    expired_cnt += 1
                else:
                    active_cnt += 1
                    if days_left <= 7:
                        deadlines_7d += 1
                    if days_left <= 30:
                        deadlines_30d += 1
                    if days_left <= 60:
                        deadlines_60d += 1
                    if days_left <= 90:
                        deadlines_90d += 1
            else:
                active_cnt += 1
        else:
            active_cnt += 1

    avg_amt = sum(amounts) / len(amounts) if amounts else None
    med_amt = statistics.median(amounts) if amounts else None
    tot_amt = sum(amounts) if amounts else None

    return {
        "total_opportunities": total_opps,
        "active_opportunities": active_cnt,
        "expired_opportunities": expired_cnt,
        "closed_opportunities": closed_cnt,
        "upcoming_deadlines_7d": deadlines_7d,
        "upcoming_deadlines_30d": deadlines_30d,
        "upcoming_deadlines_60d": deadlines_60d,
        "upcoming_deadlines_90d": deadlines_90d,
        "domain_distribution": domain_dist,
        "technology_distribution": tech_dist,
        "funder_distribution": funder_dist,
        "funding_type_distribution": type_dist,
        "average_amount": avg_amt,
        "median_amount": med_amt,
        "total_funding_amount": tot_amt
    }

def get_recommendation_score_analytics(recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate score distribution, averages, and categorization from recommendation items."""
    total_recs = len(recommendations)
    if total_recs == 0:
        return {
            "total_recommendations": 0,
            "average_score": 0.0,
            "median_score": 0.0,
            "highest_score": 0.0,
            "lowest_score": 0.0,
            "excellent_match_count": 0,
            "strong_match_count": 0,
            "moderate_match_count": 0,
            "weak_match_count": 0,
            "poor_match_count": 0,
            "score_distribution": []
        }

    scores = [float(item.get("match_score", 0)) for item in recommendations]
    avg_score = round(sum(scores) / total_recs, 2)
    med_score = round(statistics.median(scores), 2)
    max_score = round(max(scores), 2)
    min_score = round(min(scores), 2)

    # Categories
    exc = sum(1 for s in scores if s >= 90)
    strg = sum(1 for s in scores if 80 <= s < 90)
    mod = sum(1 for s in scores if 70 <= s < 80)
    weak = sum(1 for s in scores if 60 <= s < 70)
    poor = sum(1 for s in scores if s < 60)

    # Buckets
    distribution = []
    for b in SCORE_BUCKETS:
        cnt = sum(1 for s in scores if b["min_score"] <= s <= b["max_score"])
        pct = round((cnt / total_recs) * 100.0, 1)
        distribution.append({
            "range": b["range"],
            "min_score": b["min_score"],
            "max_score": b["max_score"],
            "count": cnt,
            "percentage": pct
        })

    return {
        "total_recommendations": total_recs,
        "average_score": avg_score,
        "median_score": med_score,
        "highest_score": max_score,
        "lowest_score": min_score,
        "excellent_match_count": exc,
        "strong_match_count": strg,
        "moderate_match_count": mod,
        "weak_match_count": weak,
        "poor_match_count": poor,
        "score_distribution": distribution
    }

def get_deadline_analytics(db: Session, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate deadline intelligence for recommended opportunities."""
    today = date.today()
    within_7 = 0
    within_30 = 0
    within_60 = 0
    within_90 = 0
    expired = 0
    no_deadline = 0
    
    priority_recs = []
    
    for item in recommendations:
        dl = item.get("deadline")
        score = item.get("match_score", 0)
        days_remaining = None
        
        if dl:
            if isinstance(dl, str):
                try:
                    dl_date = datetime.strptime(dl[:10], "%Y-%m-%d").date()
                except Exception:
                    dl_date = None
            elif isinstance(dl, datetime):
                dl_date = dl.date()
            elif isinstance(dl, date):
                dl_date = dl
            else:
                dl_date = None

            if dl_date:
                days_remaining = (dl_date - today).days
                if days_remaining < 0:
                    expired += 1
                else:
                    if days_remaining <= 7:
                        within_7 += 1
                    if days_remaining <= 30:
                        within_30 += 1
                    if days_remaining <= 60:
                        within_60 += 1
                    if days_remaining <= 90:
                        within_90 += 1
                        
                    # Derive Priority based on score + urgency
                    if score >= 70 and days_remaining <= 30:
                        p_level = "HIGH" if days_remaining <= 14 else "MEDIUM"
                        priority_recs.append({
                            "funding_id": item.get("funding_id"),
                            "title": item.get("title"),
                            "match_score": score,
                            "days_remaining": days_remaining,
                            "deadline": str(dl_date),
                            "priority": p_level
                        })
            else:
                no_deadline += 1
        else:
            no_deadline += 1

    return {
        "within_7_days": within_7,
        "within_30_days": within_30,
        "within_60_days": within_60,
        "within_90_days": within_90,
        "expired": expired,
        "no_deadline": no_deadline,
        "priority_recommendations": sorted(priority_recs, key=lambda x: x["days_remaining"])
    }

def get_recommendation_activity_analytics(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
    """Calculate feedback activity, view rate, save rate, and application rate."""
    query = db.query(FundingRecommendation)
    if user_id is not None:
        query = query.filter(FundingRecommendation.user_id == user_id)
        
    recs = query.all()
    total_cnt = len(recs)
    
    views = 0
    saves = 0
    dismissals = 0
    relevant = 0
    not_relevant = 0
    applications = 0
    
    for r in recs:
        st = (r.status or r.feedback or "viewed").lower()
        if st in ["viewed", "saved", "relevant", "not_relevant", "dismissed", "applied"]:
            views += 1
        if st == "saved":
            saves += 1
        elif st == "dismissed":
            dismissals += 1
        elif st == "relevant":
            relevant += 1
        elif st == "not_relevant":
            not_relevant += 1
        elif st == "applied":
            applications += 1
            saves += 1 # Applied implies saved/interested

    feedback_given = saves + dismissals + relevant + not_relevant + applications
    coverage = round(feedback_given / total_cnt, 2) if total_cnt > 0 else 0.0
    
    pos_feedback = saves + relevant + applications
    neg_feedback = dismissals + not_relevant
    tot_feedback_denom = pos_feedback + neg_feedback
    
    pos_rate = round(pos_feedback / tot_feedback_denom, 2) if tot_feedback_denom > 0 else 0.0
    neg_rate = round(neg_feedback / tot_feedback_denom, 2) if tot_feedback_denom > 0 else 0.0
    
    v_rate = round(views / total_cnt, 2) if total_cnt > 0 else 0.0
    s_rate = round(saves / total_cnt, 2) if total_cnt > 0 else 0.0
    d_rate = round(dismissals / total_cnt, 2) if total_cnt > 0 else 0.0
    a_rate = round(applications / total_cnt, 2) if total_cnt > 0 else 0.0

    return {
        "total_recommendations": total_cnt,
        "views": views,
        "saves": saves,
        "dismissals": dismissals,
        "relevant_feedback": relevant,
        "not_relevant_feedback": not_relevant,
        "applications": applications,
        "feedback_coverage": coverage,
        "positive_feedback_rate": pos_rate,
        "negative_feedback_rate": neg_rate,
        "view_rate": v_rate,
        "save_rate": s_rate,
        "dismiss_rate": d_rate,
        "application_rate": a_rate
    }

def get_personalization_performance(db: Session, user_id: int) -> Dict[str, Any]:
    """Evaluate Part 5 personalization adjustments and behavioral history impact."""
    signals = funding_personalization_service.get_user_feedback_signals(db, user_id)
    history = funding_feedback_service.get_feedback_history(db, user_id)
    
    saved_cnt = sum(1 for h in history if h.get("status") == "saved")
    applied_cnt = sum(1 for h in history if h.get("status") == "applied")
    dismissed_cnt = sum(1 for h in history if h.get("status") == "dismissed")
    
    adjustments = []
    r_features = researcher_feature_service.build_researcher_features(db, user_id)
    
    recs = funding_matching_service.rank_funding_opportunities(db, user_id, top_k=20)
    for item in recs.get("recommendations", []):
        bd = item.get("match_breakdown", {})
        fb_adj = bd.get("feedback", 0.0)
        adjustments.append(fb_adj)
        
    avg_adj = round(sum(adjustments) / len(adjustments), 2) if adjustments else 0.0
    max_adj = round(max(adjustments), 2) if adjustments else 0.0
    min_adj = round(min(adjustments), 2) if adjustments else 0.0

    return {
        "average_adjustment": avg_adj,
        "max_adjustment": max_adj,
        "min_adjustment": min_adj,
        "saved_items_count": saved_cnt,
        "applied_items_count": applied_cnt,
        "dismissed_items_count": dismissed_cnt,
        "positive_signal_domains": list(signals.get("positive_domains", set())),
        "negative_signal_domains": list(signals.get("negative_domains", set()))
    }

def evaluate_top_k_precision(db: Session, user_id: int, recommendations: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Calculate Precision@5, Precision@10, Precision@20.
    Handles insufficient feedback gracefully with status: 'insufficient_feedback'.
    """
    history = funding_feedback_service.get_feedback_history(db, user_id)
    feedback_map = {h["funding_id"]: h.get("status") or h.get("feedback") for h in history}
    
    results = {}
    for k in [5, 10, 20]:
        top_slice = recommendations[:k]
        rel_cnt = 0
        not_rel_cnt = 0
        evaluated_cnt = 0
        
        for item in top_slice:
            fid = item.get("funding_id")
            fb = feedback_map.get(fid)
            if fb in ["saved", "relevant", "applied"]:
                rel_cnt += 1
                evaluated_cnt += 1
            elif fb in ["dismissed", "not_relevant"]:
                not_rel_cnt += 1
                evaluated_cnt += 1

        if evaluated_cnt < 2:
            results[str(k)] = {
                "top_k": k,
                "evaluated_items": evaluated_cnt,
                "relevant_count": rel_cnt,
                "not_relevant_count": not_rel_cnt,
                "precision": None,
                "status": "insufficient_feedback"
            }
        else:
            prec = round(rel_cnt / evaluated_cnt, 2)
            results[str(k)] = {
                "top_k": k,
                "evaluated_items": evaluated_cnt,
                "relevant_count": rel_cnt,
                "not_relevant_count": not_rel_cnt,
                "precision": prec,
                "status": "evaluated"
            }

    return results

def run_recommendation_diagnostics(db: Session, user_id: int, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run diagnostics verifying score consistency, publication/patent evidence completeness, and anomalies."""
    valid_score_cnt = 0
    invalid_score_cnt = 0
    
    ev_complete_cnt = 0
    ev_incomplete_cnt = 0
    
    diagnostics = []
    
    user_pubs_cnt = db.query(Publication).filter(Publication.user_id == user_id).count()
    user_pats_cnt = db.query(Patent).filter(Patent.user_id == user_id).count()
    
    scores = []
    for item in recommendations:
        s = float(item.get("match_score", 0))
        scores.append(s)
        bd = item.get("match_breakdown", {})
        
        # 1. Score Breakdown Consistency Check: sum(bd.values()) == final_score
        if bd:
            bd_sum = sum(float(v) for v in bd.values())
            if abs(bd_sum - s) <= 1.5 or (s == 100 and bd_sum >= 100):
                valid_score_cnt += 1
            else:
                invalid_score_cnt += 1
        else:
            valid_score_cnt += 1
            
        # 2. Evidence Consistency Check
        reasons = item.get("reasons", [])
        has_pub_claim = any("publication" in str(r).lower() for r in reasons)
        has_pat_claim = any("patent" in str(r).lower() for r in reasons)
        
        if (has_pub_claim and user_pubs_cnt == 0) or (has_pat_claim and user_pats_cnt == 0):
            ev_incomplete_cnt += 1
        else:
            ev_complete_cnt += 1

    tot_recs = len(recommendations)
    score_val_rate = round(valid_score_cnt / tot_recs, 2) if tot_recs > 0 else 1.0
    ev_val_rate = round(ev_complete_cnt / tot_recs, 2) if tot_recs > 0 else 1.0

    # Diagnostic checks
    # Check 1: Identical Scores Anomaly
    unique_scores = len(set(scores))
    if tot_recs > 3 and unique_scores == 1:
        diagnostics.append({
            "check_name": "Identical Scores Anomaly",
            "passed": False,
            "details": "All recommendations returned identical scores.",
            "affected_count": tot_recs
        })
    else:
        diagnostics.append({
            "check_name": "Identical Scores Anomaly",
            "passed": True,
            "details": f"Recommendations show healthy score variance ({unique_scores} unique scores).",
            "affected_count": 0
        })

    # Check 2: Score Components Consistency
    if invalid_score_cnt > 0:
        diagnostics.append({
            "check_name": "Mathematical Score Consistency",
            "passed": False,
            "details": f"{invalid_score_cnt} recommendations had score breakdown sum mismatch.",
            "affected_count": invalid_score_cnt
        })
    else:
        diagnostics.append({
            "check_name": "Mathematical Score Consistency",
            "passed": True,
            "details": "100% of recommendation score component breakdowns match the final score.",
            "affected_count": 0
        })

    # Check 3: Publication Evidence Consistency
    diagnostics.append({
        "check_name": "Publication & Patent Evidence Consistency",
        "passed": ev_incomplete_cnt == 0,
        "details": f"Evidence completeness: {ev_complete_cnt}/{tot_recs} recommendations verified against user publications and patents.",
        "affected_count": ev_incomplete_cnt
    })

    return {
        "valid_score_consistency_count": valid_score_cnt,
        "invalid_score_consistency_count": invalid_score_cnt,
        "score_validation_rate": score_val_rate,
        "evidence_complete_count": ev_complete_cnt,
        "evidence_incomplete_count": ev_incomplete_cnt,
        "evidence_validation_rate": ev_val_rate,
        "diagnostics_list": diagnostics
    }

def calculate_recommendation_health(
    diagnostics: Dict[str, Any],
    score_analytics: Dict[str, Any],
    activity_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate a transparent overall Recommendation Engine Health Score (0-100).
    Formulated cleanly as:
    Score Consistency (30%) + Evidence Consistency (30%) + Score Variance/Quality (20%) + Engagement/Coverage (20%)
    """
    score_val_rate = diagnostics.get("score_validation_rate", 1.0)
    ev_val_rate = diagnostics.get("evidence_validation_rate", 1.0)
    
    score_health = score_val_rate * 30.0
    evidence_health = ev_val_rate * 30.0
    
    tot_recs = score_analytics.get("total_recommendations", 0)
    avg_s = score_analytics.get("average_score", 0.0)
    quality_pts = 20.0 if (30.0 <= avg_s <= 95.0 and tot_recs > 0) else 10.0
    
    coverage = activity_metrics.get("feedback_coverage", 0.0)
    engagement_pts = min(20.0, 10.0 + (coverage * 10.0))
    
    total_health_score = round(score_health + evidence_health + quality_pts + engagement_pts)
    total_health_score = max(0, min(100, total_health_score))
    
    if total_health_score >= 85:
        status = "Excellent"
    elif total_health_score >= 70:
        status = "Good"
    elif total_health_score >= 50:
        status = "Fair"
    else:
        status = "Needs Improvement"

    strengths = []
    warnings = []
    
    if score_val_rate == 1.0:
        strengths.append("100% mathematical score component reconciliation")
    if ev_val_rate == 1.0:
        strengths.append("100% publication & patent evidence consistency")
    if 60.0 <= avg_s <= 90.0:
        strengths.append(f"Optimal average match score calibration ({avg_s}%)")
        
    if coverage < 0.2:
        warnings.append("Low user feedback coverage (< 20%). Encourage user interaction to improve personalization.")
    if diagnostics.get("evidence_incomplete_count", 0) > 0:
        warnings.append("Some recommendations contain unverified publication or patent claims.")

    return {
        "score": total_health_score,
        "status": status,
        "strengths": strengths,
        "warnings": warnings,
        "calculation_breakdown": {
            "score_consistency_pts": round(score_health, 1),
            "evidence_consistency_pts": round(evidence_health, 1),
            "quality_variance_pts": round(quality_pts, 1),
            "engagement_coverage_pts": round(engagement_pts, 1)
        }
    }

def get_researcher_analytics(db: Session, user_id: int) -> Dict[str, Any]:
    """Compile comprehensive Part 6 Researcher Analytics for a specific user ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found.")

    # 1. Feature Extraction
    r_features = researcher_feature_service.build_researcher_features(db, user_id)
    domain = r_features.get("research_domain", "General Research")
    techs = r_features.get("technology_areas", []) or [r_features.get("technology_area", "N/A")]
    interests = r_features.get("research_interests", [])
    
    # 2. Recommendations & Eligibility
    recs_data = funding_matching_service.rank_funding_opportunities(db, user_id, top_k=20)
    recommendations = recs_data.get("recommendations", [])
    
    # 3. Score & Deadline Analytics
    score_analytics = get_recommendation_score_analytics(recommendations)
    deadline_analytics = get_deadline_analytics(db, recommendations)
    activity_analytics = get_recommendation_activity_analytics(db, user_id)
    personalization_perf = get_personalization_performance(db, user_id)
    
    # 4. Top-K Evaluation & Diagnostics
    evaluation = evaluate_top_k_precision(db, user_id, recommendations)
    diagnostics = run_recommendation_diagnostics(db, user_id, recommendations)
    health_score = calculate_recommendation_health(diagnostics, score_analytics, activity_analytics)

    # 5. Domain Analysis
    domain_map: Dict[str, Dict[str, Any]] = {}
    for item in recommendations:
        raw_doms = item.get("eligible_domains") or item.get("domain") or "General Research"
        dom_list = [d.strip() for d in raw_doms.split(",")] if isinstance(raw_doms, str) else [raw_doms]
        score = float(item.get("match_score", 0))
        
        for d in dom_list:
            if d not in domain_map:
                domain_map[d] = {"count": 0, "scores": []}
            domain_map[d]["count"] += 1
            domain_map[d]["scores"].append(score)

    domain_analysis = []
    tot_rec_cnt = len(recommendations)
    for d, val in domain_map.items():
        cnt = val["count"]
        avg_s = round(sum(val["scores"]) / cnt, 1) if cnt > 0 else 0.0
        pct = round((cnt / tot_rec_cnt) * 100.0, 1) if tot_rec_cnt > 0 else 0.0
        domain_analysis.append({
            "domain": d,
            "recommendation_count": cnt,
            "average_score": avg_s,
            "percentage": pct,
            "positive_feedback_count": 0,
            "negative_feedback_count": 0
        })

    # Profile summary
    strong_pct = round((score_analytics["excellent_match_count"] + score_analytics["strong_match_count"]) / max(1, tot_rec_cnt) * 100.0, 1)
    profile = {
        "user_id": user_id,
        "full_name": user.full_name,
        "research_domain": domain,
        "technology_areas": techs,
        "research_interests": interests,
        "funding_preferences": personalization_perf["positive_signal_domains"],
        "top_funding_domains": [da["domain"] for da in sorted(domain_analysis, key=lambda x: x["recommendation_count"], reverse=True)[:3]],
        "average_match_score": score_analytics["average_score"],
        "strong_match_percentage": strong_pct,
        "application_activity": activity_analytics["applications"]
    }

    # Generate transparent insights
    insights = []
    if deadline_analytics["within_30_days"] > 0:
        insights.append(f"{deadline_analytics['within_30_days']} recommended funding opportunities have deadlines within 30 days.")
    if domain_analysis:
        top_d = sorted(domain_analysis, key=lambda x: x["recommendation_count"], reverse=True)[0]
        insights.append(f"Recommendations are highest in '{top_d['domain']}' ({top_d['percentage']}% of total).")
    if activity_analytics["feedback_coverage"] > 0:
        insights.append(f"User interaction coverage is {int(activity_analytics['feedback_coverage']*100)}% with {activity_analytics['saves']} saved grants.")
    else:
        insights.append("No interaction history recorded yet. Interact with recommendations (save, apply, dismiss) to activate personalization.")

    return {
        "user_id": user_id,
        "researcher_funding_profile": profile,
        "recommendation_summary": score_analytics,
        "score_distribution": score_analytics["score_distribution"],
        "top_recommendations": recommendations[:5],
        "domain_analysis": domain_analysis,
        "deadline_analysis": deadline_analytics,
        "activity_analysis": activity_analytics,
        "personalization_analysis": personalization_perf,
        "evaluation": evaluation,
        "diagnostics": diagnostics,
        "health_score": health_score,
        "insights": insights
    }

def get_performance_analytics(db: Session, user_id: int) -> Dict[str, Any]:
    """Retrieve performance and evaluation metrics for a researcher."""
    recs_data = funding_matching_service.rank_funding_opportunities(db, user_id, top_k=20)
    recommendations = recs_data.get("recommendations", [])
    
    score_analytics = get_recommendation_score_analytics(recommendations)
    activity_metrics = get_recommendation_activity_analytics(db, user_id)
    top_k_eval = evaluate_top_k_precision(db, user_id, recommendations)
    diagnostics = run_recommendation_diagnostics(db, user_id, recommendations)
    health_score = calculate_recommendation_health(diagnostics, score_analytics, activity_metrics)

    return {
        "user_id": user_id,
        "top_k_evaluation": top_k_eval,
        "activity_metrics": activity_metrics,
        "score_statistics": {
            "average_score": score_analytics["average_score"],
            "median_score": score_analytics["median_score"],
            "highest_score": score_analytics["highest_score"],
            "lowest_score": score_analytics["lowest_score"]
        },
        "diagnostics": diagnostics,
        "health_score": health_score
    }

def get_dashboard_summary(db: Session, user_id: int) -> Dict[str, Any]:
    """Generate clean, frontend-ready dashboard summary for user ID."""
    researcher_analytics = get_researcher_analytics(db, user_id)
    
    kpis = {
        "total_eligible": researcher_analytics["recommendation_summary"]["total_recommendations"],
        "average_match_score": researcher_analytics["recommendation_summary"]["average_score"],
        "saved_opportunities": researcher_analytics["activity_analysis"]["saves"],
        "applied_opportunities": researcher_analytics["activity_analysis"]["applications"],
        "upcoming_deadlines_30d": researcher_analytics["deadline_analysis"]["within_30_days"]
    }
    
    domain_dist = [
        {"domain": item["domain"], "count": item["recommendation_count"]}
        for item in researcher_analytics["domain_analysis"]
    ]

    return {
        "user_id": user_id,
        "kpis": kpis,
        "top_recommendations": researcher_analytics["top_recommendations"][:3],
        "upcoming_deadlines": researcher_analytics["deadline_analysis"]["priority_recommendations"][:3],
        "domain_distribution": domain_dist,
        "score_distribution": researcher_analytics["score_distribution"],
        "feedback_summary": researcher_analytics["activity_analysis"],
        "health_score": researcher_analytics["health_score"],
        "alerts": researcher_analytics["insights"]
    }
