from datetime import date, timedelta
from typing import Dict, Any, List

def classify_deadline(deadline_date: date) -> str:
    """
    Classify funding opportunity deadline status.
    Returns: 'expired', 'closing_soon', or 'open'.
    """
    if not deadline_date:
        return "open"
    today = date.today()
    if deadline_date < today:
        return "expired"
    elif deadline_date <= today + timedelta(days=30):
        return "closing_soon"
    else:
        return "open"

def is_eligible(researcher_features: Dict[str, Any], opportunity_features: Dict[str, Any]) -> bool:
    """
    Check basic eligibility rules.
    Missing eligibility is treated as unknown (returns True).
    Expired deadline or inactive status returns False.
    """
    # 1. Status check
    status = opportunity_features.get("status", "open").lower()
    if status in ["expired", "closed", "inactive"]:
        return False

    # 2. Deadline check
    deadline = opportunity_features.get("deadline")
    if deadline and classify_deadline(deadline) == "expired":
        return False

    # 3. Geographic / eligibility rule check (if explicitly specified and incompatible)
    geo_scope = opportunity_features.get("geographic_scope", "").lower()
    # Example: If opportunity strictly requires USA Only, but researcher profile specified a foreign org
    # Treat missing data as eligible (unknown)
    return True

def filter_eligible_funding(
    researcher_features: Dict[str, Any],
    opportunities: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Filter list of funding opportunity feature dicts, returning only eligible and unexpired ones.
    """
    eligible_opportunities = []
    for opp in opportunities:
        if is_eligible(researcher_features, opp):
            # Attach classified deadline status for downstream scoring
            deadline = opp.get("deadline")
            opp["deadline_status"] = classify_deadline(deadline) if deadline else "open"
            eligible_opportunities.append(opp)
    return eligible_opportunities
