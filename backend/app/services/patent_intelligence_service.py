# backend/app/services/patent_intelligence_service.py

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from collections import Counter
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Patent, User, Publication
from app.services import researcher_feature_service

def _normalize_tech_name(tech: Optional[str]) -> str:
    """Normalize technology strings while preserving multi-word concepts."""
    if not tech:
        return "Uncategorized"
    cleaned = tech.strip()
    return cleaned if cleaned else "Uncategorized"

def get_patent_intelligence_analytics(db: Session) -> Dict[str, Any]:
    """
    Compute comprehensive Part 8 Patent & Innovation Intelligence analytics.
    Calculates totals, active/expired statuses, temporal trends, emerging tech indicators,
    and top inventors/institutions using actual database records.
    """
    patents = db.query(Patent).all()
    total_patents = len(patents)

    if total_patents == 0:
        return {
            "total_patents": 0,
            "active_patents": 0,
            "expired_patents": 0,
            "patents_by_year": {},
            "technology_distribution": [],
            "domain_distribution": [],
            "trends": [],
            "emerging_technologies": [],
            "top_inventors": [],
            "top_institutions": []
        }

    active_count = 0
    expired_count = 0
    years_counter = Counter()
    tech_counter = Counter()
    domain_counter = Counter()
    inventor_counter = Counter()
    institution_counter = Counter()
    
    # Yearly technology counters for trend detection
    # Recent = 2024-2026, Previous = 2021-2023
    current_year = datetime.now().year
    tech_recent_counter = Counter()
    tech_previous_counter = Counter()

    for p in patents:
        # Status calculation: patents filed within 20 years are active
        f_date = p.filing_date
        f_year = f_date.year if f_date else 2020
        
        years_counter[str(f_year)] += 1
        
        if (current_year - f_year) <= 20:
            active_count += 1
        else:
            expired_count += 1
            
        tech = _normalize_tech_name(p.technology_domain)
        tech_counter[tech] += 1
        domain_counter[tech] += 1  # technology_domain serves as primary domain
        
        if p.inventor:
            inventor_counter[p.inventor.strip()] += 1
        if p.assignee:
            institution_counter[p.assignee.strip()] += 1

        if f_year >= (current_year - 2):
            tech_recent_counter[tech] += 1
        elif f_year >= (current_year - 5):
            tech_previous_counter[tech] += 1

    # Format distributions with percentages
    tech_dist = [
        {"technology": tech, "count": count, "percentage": round((count / total_patents) * 100, 1)}
        for tech, count in tech_counter.most_common(10)
    ]
    
    domain_dist = [
        {"domain": dom, "count": count, "percentage": round((count / total_patents) * 100, 1)}
        for dom, count in domain_counter.most_common(10)
    ]

    # Calculate temporal technology trends and emerging technologies
    all_techs = set(tech_counter.keys())
    trends = []
    emerging_technologies = []

    for tech in all_techs:
        recent = tech_recent_counter[tech]
        previous = tech_previous_counter[tech]
        
        if previous > 0:
            growth = round((recent - previous) / previous, 2)
        else:
            growth = float(recent)  # Infinity/1.0 scale if previous was zero

        if recent > previous:
            trend_status = "increasing"
        elif recent < previous and previous > 0:
            trend_status = "declining"
        else:
            trend_status = "stable"

        # Explicit Threshold Rule for Emerging Technology:
        # Recent count >= 2 and growth rate > 0.20 (or new high recent activity)
        is_emerging = (recent >= 2 and growth >= 0.20) or (recent >= 3 and previous == 0)

        trend_obj = {
            "technology": tech,
            "trend": trend_status,
            "recent_count": recent,
            "previous_count": previous,
            "growth_rate": growth,
            "is_emerging": is_emerging
        }
        trends.append(trend_obj)
        if is_emerging:
            emerging_technologies.append(trend_obj)

    trends.sort(key=lambda x: (x["recent_count"], x["growth_rate"]), reverse=True)
    emerging_technologies.sort(key=lambda x: (x["recent_count"], x["growth_rate"]), reverse=True)

    # Top Inventors & Institutions
    top_inventors = []
    for inv_name, count in inventor_counter.most_common(5):
        # Find matching user_id if inventor name matches a registered User
        user_match = db.query(User).filter(User.full_name.ilike(f"%{inv_name}%")).first()
        top_inventors.append({
            "researcher_id": user_match.id if user_match else None,
            "name": inv_name,
            "patent_count": count,
            "primary_domain": "Intellectual Property & Patents"
        })

    top_institutions = [
        {"institution": inst, "patent_count": count}
        for inst, count in institution_counter.most_common(5)
    ]

    return {
        "total_patents": total_patents,
        "active_patents": active_count,
        "expired_patents": expired_count,
        "patents_by_year": dict(sorted(years_counter.items())),
        "technology_distribution": tech_dist,
        "domain_distribution": domain_dist,
        "trends": trends,
        "emerging_technologies": emerging_technologies,
        "top_inventors": top_inventors,
        "top_institutions": top_institutions
    }

def get_patent_detail_intelligence(db: Session, patent_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve detailed intelligence and innovation scores for a specific patent."""
    patent = db.query(Patent).filter(Patent.patent_id == patent_id).first()
    if not patent:
        return None

    user = db.query(User).filter(User.id == patent.user_id).first()
    
    # Find related publications of the owner user that share technology keywords
    related_pubs = []
    if user:
        pubs = db.query(Publication).filter(Publication.user_id == user.id).all()
        p_tech = (patent.technology_domain or "").lower()
        for pub in pubs:
            if p_tech and (p_tech in pub.title.lower()):
                related_pubs.append({"id": pub.publication_id, "title": pub.title, "year": pub.publication_year})

    # Calculate transparent Patent Innovation Indicator Score (0-100)
    current_year = datetime.now().year
    f_year = patent.filing_date.year if patent.filing_date else 2020
    recency_score = max(0, 100 - (current_year - f_year) * 10)  # 100 for recent filing
    assignee_score = 90 if patent.assignee else 60
    tech_clarity_score = 95 if patent.technology_domain else 70
    pub_link_score = 95 if len(related_pubs) > 0 else 70

    innovation_score = int(round(
        (recency_score * 0.35) +
        (assignee_score * 0.20) +
        (tech_clarity_score * 0.25) +
        (pub_link_score * 0.20)
    ))

    return {
        "patent_id": patent.patent_id,
        "title": patent.title,
        "inventor": patent.inventor,
        "assignee": patent.assignee,
        "technology_domain": patent.technology_domain,
        "filing_date": str(patent.filing_date),
        "status": "Active" if (current_year - f_year) <= 20 else "Expired",
        "researcher_id": user.id if user else None,
        "researcher_name": user.full_name if user else patent.inventor,
        "related_publications": related_pubs,
        "innovation_score": min(100, max(0, innovation_score)),
        "innovation_indicators": {
            "recency_score": recency_score,
            "assignee_score": assignee_score,
            "technology_clarity": tech_clarity_score,
            "publication_linkage": pub_link_score
        }
    }
