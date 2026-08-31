# backend/app/services/funding_eligibility_service.py

from datetime import date
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import FundingOpportunity, User
from app.services import researcher_feature_service

def is_deadline_valid(deadline: Optional[date]) -> Tuple[bool, str, str]:
    """
    Check if funding deadline is active, closing soon, or expired.
    
    Rules:
    - deadline before today -> expired -> exclude
    - deadline today or future -> potentially eligible
    - missing deadline -> do not automatically exclude unless required; mark as unknown
    """
    if deadline is None:
        return True, "unknown", "Deadline not specified; marked as unknown."
    
    today = date.today()
    if deadline < today:
        return False, "expired", f"Funding deadline has passed ({deadline})."
    elif deadline == today:
        return True, "closing_soon", f"Funding deadline is today ({deadline})."
    else:
        return True, "open", "Deadline is active."

def is_status_active(status: Optional[str]) -> Tuple[bool, str, str]:
    """
    Check if funding status is active.
    
    Rules:
    - active / open -> eligible for further matching
    - closed -> exclude
    - draft -> exclude
    - missing status -> exclude by data policy
    """
    if not status or not status.strip():
        return False, "unknown", "Funding status is missing; excluded by data policy."
    
    clean_status = status.strip().lower()
    if clean_status in ("active", "open"):
        return True, "passed", "Funding status is active."
    elif clean_status == "closed":
        return False, "failed", "Funding status is closed."
    elif clean_status == "draft":
        return False, "failed", "Funding status is draft."
    else:
        return False, "failed", f"Funding status '{status}' is inactive."

def check_research_stage(
    researcher_features: Dict[str, Any],
    funding_stage: Optional[str]
) -> Tuple[bool, str, str]:
    """
    Compare researcher's current/relevant stage vs funding research_stage.
    
    If funding stage is clearly incompatible with the researcher, exclude it.
    If researcher stage cannot be determined or funding stage is not restricted, mark as unknown/passed.
    """
    if not funding_stage or not funding_stage.strip():
        return True, "unknown", "No research stage restrictions."
    
    clean_funding_stage = funding_stage.strip().lower()
    designation = (researcher_features.get("designation") or "").lower()
    
    # Example stage incompatibility rules:
    # If funding explicitly requires "Commercialization" or "Development" only, but researcher is a Student/Undergraduate with no patents or publications
    if "commercialization" in clean_funding_stage and ("student" in designation or "undergraduate" in designation):
        if researcher_features.get("patent_count", 0) == 0 and researcher_features.get("publication_count", 0) == 0:
            return False, "failed", f"Research stage '{funding_stage}' requires commercialization capacity not matching researcher profile."
            
    return True, "passed", f"Research stage '{funding_stage}' is compatible or unrestricted."

def check_geographic_scope(
    researcher_features: Dict[str, Any],
    geographic_scope: Optional[str]
) -> Tuple[bool, str, str]:
    """
    Compare researcher location / organization vs funding geographic_scope.
    
    Rules:
    - Global / International / Unspecified -> compatible
    - US only vs researcher in India / Non-US institution -> exclude if explicitly restricted
    """
    if not geographic_scope or not geographic_scope.strip():
        return True, "passed", "Geographic scope is unrestricted."
    
    clean_scope = geographic_scope.strip().lower()
    if any(term in clean_scope for term in ["global", "international", "worldwide", "any"]):
        return True, "passed", f"Geographic scope '{geographic_scope}' is international."
    
    organization = (researcher_features.get("organization") or "").lower()
    email = (researcher_features.get("email") or "").lower()
    
    # Infer researcher location signals
    is_india = any(k in organization for k in ["iisc", "pvpsit", "iit", "nit", "india"]) or email.endswith(".in")
    is_us = any(k in organization for k in ["stanford", "mit", "harvard", "berkeley", "usa", "united states"]) or email.endswith(".edu")
    
    # Explicit mismatch checks
    if ("united states only" in clean_scope or "us only" in clean_scope or "usa only" in clean_scope) and is_india and not is_us:
        return False, "failed", f"Explicit geographic restriction '{geographic_scope}' does not match researcher location."
        
    if ("india only" in clean_scope or "indian institutions only" in clean_scope) and is_us and not is_india:
        return False, "failed", f"Explicit geographic restriction '{geographic_scope}' does not match researcher location."

    return True, "passed", f"Geographic scope '{geographic_scope}' is compatible."

def check_basic_eligibility(
    researcher_features: Dict[str, Any],
    eligibility_text: Optional[str]
) -> Tuple[bool, str, str]:
    """
    Inspect funding eligibility text for explicit constraints.
    
    Normalizes case, spaces, and synonyms.
    Only excludes if profile contains enough structured information to prove incompatibility.
    If info cannot be reliably determined, marks as unknown and allows continuation.
    """
    if not eligibility_text or not eligibility_text.strip():
        return True, "passed", "No explicit eligibility text constraints."
    
    clean_text = eligibility_text.strip().lower()
    designation = (researcher_features.get("designation") or "").lower()
    
    # Check explicit degree / role disqualifications
    if "postdoctoral researchers only" in clean_text or "postdoc only" in clean_text:
        if "student" in designation or "undergraduate" in designation:
            return False, "failed", f"Eligibility constraint '{eligibility_text}' requires postdoctoral status."
            
    if "us citizens only" in clean_text or "us permanent residents only" in clean_text:
        email = (researcher_features.get("email") or "").lower()
        organization = (researcher_features.get("organization") or "").lower()
        if email.endswith(".in") or "iisc" in organization or "pvpsit" in organization:
            return False, "failed", f"Eligibility constraint '{eligibility_text}' restricts citizenship."

    return True, "passed", "No explicit eligibility conflict found."

def filter_eligible_funding(
    db: Session,
    user_id: int,
    funding_opportunities: Optional[List[FundingOpportunity]] = None
) -> Dict[str, Any]:
    """
    Main eligibility filtering function.
    
    Evaluates funding opportunities against:
    1. Deadline validity
    2. Status check
    3. Research stage check
    4. Geographic scope check
    5. Basic eligibility text check
    
    Separates eligibility (Part 3) from relevance (Part 4).
    Returns dict containing 'eligible' and 'excluded' opportunity lists with clear reasons.
    """
    # 1. Fetch Researcher Features
    researcher_features = researcher_feature_service.build_researcher_features(db, user_id)
    if researcher_features is None:
        return {
            "error": "user_not_found",
            "user_id": user_id,
            "message": f"User with ID {user_id} does not exist."
        }

    # 2. Fetch Funding Opportunities from DB if not provided
    if funding_opportunities is None:
        funding_opportunities = db.query(FundingOpportunity).all()

    eligible_list = []
    excluded_list = []

    for opp in funding_opportunities:
        # Perform eligibility checks
        deadline_passed, deadline_status, deadline_msg = is_deadline_valid(opp.deadline)
        status_passed, status_check, status_msg = is_status_active(opp.status)
        stage_passed, stage_check, stage_msg = check_research_stage(researcher_features, opp.research_stage)
        geo_passed, geo_check, geo_msg = check_geographic_scope(researcher_features, opp.geographic_scope)
        el_passed, el_check, el_msg = check_basic_eligibility(researcher_features, opp.eligibility)

        # Aggregate result
        is_eligible = deadline_passed and status_passed and stage_passed and geo_passed and el_passed
        
        # Formulate clear exclusion reason if not eligible
        if not is_eligible:
            reasons = []
            if not deadline_passed:
                reasons.append(deadline_msg)
            if not status_passed:
                reasons.append(status_msg)
            if not stage_passed:
                reasons.append(stage_msg)
            if not geo_passed:
                reasons.append(geo_msg)
            if not el_passed:
                reasons.append(el_msg)
            exclusion_reason = " ".join(reasons)
        else:
            exclusion_reason = "Passed all eligibility filters."

        item_result = {
            "funding_id": opp.id,
            "title": opp.title,
            "funder": opp.funder,
            "eligible": is_eligible,
            "deadline_status": deadline_status,
            "status_check": status_check,
            "research_stage_check": stage_check,
            "geographic_check": geo_check,
            "eligibility_check": el_check,
            "reason": exclusion_reason,
            "amount_range": opp.amount_range,
            "deadline": opp.deadline,
            "research_stage": opp.research_stage,
            "geographic_scope": opp.geographic_scope,
            "funding_type": opp.funding_type
        }

        if is_eligible:
            eligible_list.append(item_result)
        else:
            excluded_list.append(item_result)

    return {
        "user_id": user_id,
        "total_opportunities": len(funding_opportunities),
        "eligible_count": len(eligible_list),
        "excluded_count": len(excluded_list),
        "eligible": eligible_list,
        "excluded": excluded_list
    }
