from datetime import date, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.funding_opportunity import FundingOpportunity

def split_and_clean_field(value: Optional[str], lowercase: bool = True) -> List[str]:
    """
    Split comma/semicolon/pipe delimited strings into a clean list of unique strings.
    """
    if not value or not isinstance(value, str):
        return []
    
    # Handle multiple potential separators (comma, semicolon, pipe)
    raw_items = value.replace(";", ",").replace("|", ",").split(",")
    items = []
    seen = set()
    for item in raw_items:
        cleaned = item.strip()
        if cleaned:
            key = cleaned.lower() if lowercase else cleaned
            if key not in seen:
                seen.add(key)
                items.append(cleaned.lower() if lowercase else cleaned)
    return items

def classify_deadline(deadline_date: Optional[date], current_date: Optional[date] = None) -> str:
    """
    Classify deadline into: active, closing_soon (within 30 days), or expired.
    """
    if not deadline_date:
        return "unknown"
    if current_date is None:
        current_date = date.today()
        
    days_remaining = (deadline_date - current_date).days
    if days_remaining < 0:
        return "expired"
    elif days_remaining <= 30:
        return "closing_soon"
    else:
        return "active"

def normalize_funding_record(funding: FundingOpportunity, current_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Convert a FundingOpportunity ORM record into a normalized dictionary representation
    optimized for future recommendation scoring and matching.
    """
    if not funding:
        return {}

    deadline_status = classify_deadline(funding.deadline, current_date)
    
    return {
        "id": funding.id,
        "title": funding.title,
        "funder": funding.funder,
        "amount_range": funding.amount_range,
        "deadline": str(funding.deadline) if funding.deadline else None,
        "deadline_status": deadline_status,
        "description": funding.description or "",
        "domains": split_and_clean_field(funding.research_domains, lowercase=True),
        "technologies": split_and_clean_field(funding.technology_areas, lowercase=True),
        "keywords": split_and_clean_field(funding.keywords, lowercase=True),
        "eligibility": funding.eligibility or "",
        "research_stage": funding.research_stage or "",
        "geographic_scope": funding.geographic_scope or "",
        "funding_type": funding.funding_type or "",
        "status": funding.status or "active",
        "match_badges": split_and_clean_field(funding.match_badges, lowercase=False)
    }

def get_all_funding_opportunities(db: Session) -> List[FundingOpportunity]:
    """Retrieve all funding opportunities from database."""
    return db.query(FundingOpportunity).all()

def get_active_funding_opportunities(db: Session) -> List[FundingOpportunity]:
    """Retrieve only active funding opportunities."""
    return db.query(FundingOpportunity).filter(
        or_(
            FundingOpportunity.status == "active",
            FundingOpportunity.status == "open"
        )
    ).all()

def get_funding_by_id(db: Session, funding_id: int) -> Optional[FundingOpportunity]:
    """Retrieve a single funding opportunity by primary key ID."""
    return db.query(FundingOpportunity).filter(FundingOpportunity.id == funding_id).first()

def get_funding_by_domain(db: Session, domain: str) -> List[FundingOpportunity]:
    """Retrieve funding opportunities matching a given domain substring."""
    if not domain or not domain.strip():
        return []
    pattern = f"%{domain.strip()}%"
    return db.query(FundingOpportunity).filter(
        FundingOpportunity.research_domains.like(pattern)
    ).all()

def get_funding_by_status(db: Session, status: str) -> List[FundingOpportunity]:
    """Retrieve funding opportunities matching a specific status."""
    clean_status = status.strip().lower() if status else "active"
    if clean_status == "open":
        clean_status = "active"
    return db.query(FundingOpportunity).filter(FundingOpportunity.status == clean_status).all()

def detect_duplicate_funding(db: Session) -> List[Dict[str, Any]]:
    """
    Detect duplicate funding opportunities based on combinations of title, funder, and deadline.
    Returns list of duplicate groups.
    """
    all_opps = db.query(FundingOpportunity).all()
    groups: Dict[tuple, List[int]] = {}
    
    for opp in all_opps:
        key = (
            opp.title.strip().lower() if opp.title else "",
            opp.funder.strip().lower() if opp.funder else "",
            str(opp.deadline) if opp.deadline else ""
        )
        if key not in groups:
            groups[key] = []
        groups[key].append(opp.id)
        
    duplicates = []
    for key, ids in groups.items():
        if len(ids) > 1:
            duplicates.append({
                "title": key[0],
                "funder": key[1],
                "deadline": key[2],
                "matching_ids": ids,
                "count": len(ids)
            })
    return duplicates
