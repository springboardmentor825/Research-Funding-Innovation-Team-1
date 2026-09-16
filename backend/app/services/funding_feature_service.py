from typing import Dict, Any, List, Optional
from app.models import FundingOpportunity

def _parse_list(raw_val: Optional[str]) -> List[str]:
    """Extract clean, normalized tokens from comma/semicolon/slash separated text."""
    if not raw_val:
        return []
    tokens = []
    # Replace slashes, semicolons, and newlines with commas
    standardized = raw_val.replace("/", ",").replace(";", ",").replace("\n", ",")
    for part in standardized.split(","):
        cleaned = part.strip()
        if cleaned and cleaned not in tokens:
            tokens.append(cleaned)
    return tokens

def extract_funding_features(opportunity: FundingOpportunity) -> Dict[str, Any]:
    """
    Extract and normalize features from a FundingOpportunity database model.
    """
    title = (opportunity.title or "").strip()
    funder = (opportunity.funder or "").strip()
    description = (opportunity.description or "").strip()
    amount_range = (opportunity.amount_range or "").strip()
    deadline = opportunity.deadline
    funding_type = (opportunity.funding_type or "Grant").strip()
    research_stage = (opportunity.research_stage or "Unspecified").strip()
    geographic_scope = (opportunity.geographic_scope or "Global").strip()
    status = (opportunity.status or "open").strip().lower()

    domains = _parse_list(opportunity.research_domains)
    tech_areas = _parse_list(opportunity.technology_areas)
    keywords = _parse_list(opportunity.keywords)
    badges = _parse_list(opportunity.match_badges)
    eligibility_tokens = _parse_list(opportunity.eligibility)

    # If domains or keywords are empty, fallback to title tokens or match_badges
    if not domains and badges:
        domains = badges
    if not keywords and badges:
        keywords = badges

    return {
        "id": opportunity.id,
        "title": title,
        "funder": funder,
        "description": description,
        "amount_range": amount_range,
        "deadline": deadline,
        "status": status,
        "research_domains": domains,
        "technology_areas": tech_areas,
        "keywords": keywords,
        "match_badges": badges,
        "eligibility": eligibility_tokens,
        "eligibility_raw": opportunity.eligibility or "",
        "research_stage": research_stage,
        "geographic_scope": geographic_scope,
        "funding_type": funding_type,
        "semantic_fit": opportunity.semantic_fit or 0
    }
