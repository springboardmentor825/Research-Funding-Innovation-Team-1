# backend/app/services/researcher_intelligence_service.py

from typing import List, Dict, Any, Optional
from collections import Counter
from sqlalchemy.orm import Session
from app.models import User, ResearchProfile, Publication, Patent, FundingRecommendation
from app.services import (
    researcher_feature_service,
    collaboration_service,
    funding_analytics_service,
    funding_matching_service
)

def _calculate_profile_completeness(features: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate transparent Profile Completeness Score (0-100) and identify missing fields."""
    missing = []
    score = 0
    
    if features.get("research_domain"):
        score += 15
    else:
        missing.append("research_domain")
        
    if features.get("technology_areas"):
        score += 15
    else:
        missing.append("technology_areas")
        
    if features.get("research_interests"):
        score += 15
    else:
        missing.append("research_interests")
        
    if features.get("keywords"):
        score += 10
    else:
        missing.append("keywords")
        
    if features.get("bio"):
        score += 10
    else:
        missing.append("bio")
        
    if features.get("publication_count", 0) > 0:
        score += 20
    else:
        missing.append("publications")
        
    if features.get("patent_count", 0) > 0:
        score += 15
    else:
        missing.append("patents")
        
    return {
        "completeness_score": min(100, score),
        "missing_fields": missing
    }

def get_researcher_intelligence_profile(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Generate Part 9 Researcher Profile Intelligence for a given user_id.
    Aggregates profile signals, publications, patents, funding intelligence (Parts 4 & 6),
    and collaboration potential (Part 7).
    """
    features = researcher_feature_service.build_researcher_features(db, user_id)
    if not features:
        return None

    # 1. Technology Evidence Breakdown
    tech_counter = Counter()
    pub_tech_counter = Counter()
    pat_tech_counter = Counter()

    for tech in features["technology_areas"]:
        tech_counter[tech] += 1
        
    for ptopic in features["publication_topics"]:
        # Find technology matches in publication titles
        for tech in features["technology_areas"]:
            if tech.lower() in ptopic.lower():
                tech_counter[tech] += 1
                pub_tech_counter[tech] += 1

    for pdom in features["patent_domains"]:
        for tech in features["technology_areas"]:
            if tech.lower() in pdom.lower():
                tech_counter[tech] += 1
                pat_tech_counter[tech] += 1

    technology_profile = []
    for tech, count in tech_counter.most_common():
        prominence = "High" if count >= 3 else ("Medium" if count == 2 else "Emerging")
        technology_profile.append({
            "technology": tech,
            "evidence_count": count,
            "publication_count": pub_tech_counter[tech],
            "patent_count": pat_tech_counter[tech],
            "prominence": prominence
        })

    # 2. Funding Intelligence Integration (Reusing Parts 4 & 6)
    funding_dashboard = funding_analytics_service.get_dashboard_summary(db, user_id)
    recs = db.query(FundingRecommendation).filter(FundingRecommendation.user_id == user_id).all()
    strong_matches = sum(1 for r in recs if r.match_score >= 80)
    avg_score = round(sum(r.match_score for r in recs) / max(len(recs), 1), 1) if recs else 0.0

    funding_intelligence = {
        "total_recommendations": len(recs),
        "strong_funding_matches": strong_matches,
        "average_match_score": avg_score,
        "active_saved_grants": funding_dashboard.get("saved_opportunities_count", 0),
        "applications_submitted": funding_dashboard.get("applied_opportunities_count", 0),
        "top_funding_domains": features["research_domain"][:3]
    }

    # 3. Collaboration Intelligence Integration (Reusing Part 7)
    collab_data = collaboration_service.get_collaboration_recommendations(db, user_id, limit=3)
    top_collaborators = collab_data.get("collaborators", []) if collab_data else []

    collaboration_intelligence = {
        "total_candidates_evaluated": collab_data.get("total_candidates_evaluated", 0) if collab_data else 0,
        "top_collaborator_count": len(top_collaborators),
        "top_collaborators": [
            {
                "researcher_id": c["researcher_id"],
                "name": c["name"],
                "score": c["score"],
                "match_category": c["match_category"],
                "shared_domains": c["shared_domains"][:2],
                "explanation": c["explanation"]
            }
            for c in top_collaborators
        ]
    }

    # 4. Research Activity Score (0-100)
    pub_score = min(40, features["publication_count"] * 10)
    pat_score = min(30, features["patent_count"] * 15)
    breadth_score = min(30, len(features["technology_areas"]) * 10)
    activity_score = min(100, pub_score + pat_score + breadth_score)

    completeness = _calculate_profile_completeness(features)

    # 5. Temporal Trends
    trends = []
    if features["publication_count"] > 0:
        trends.append({"type": "publication_activity", "trend": "active", "detail": f"{features['publication_count']} published research papers"})
    if features["patent_count"] > 0:
        trends.append({"type": "patent_innovation", "trend": "active", "detail": f"{features['patent_count']} patent intellectual property records"})

    return {
        "researcher_id": user_id,
        "name": features["full_name"],
        "email": features["email"],
        "organization": features["organization"],
        "designation": features["designation"],
        "bio": features["bio"],
        "primary_domain": features["research_domain"][0] if features["research_domain"] else "Multidisciplinary",
        "research_domains": features["research_domain"],
        "technology_profile": technology_profile,
        "research_interests": features["research_interests"],
        "keywords": features["keywords"],
        "publication_count": features["publication_count"],
        "patent_count": features["patent_count"],
        "publication_intelligence": {
            "total_publications": features["publication_count"],
            "topics": features["publication_topics"][:5]
        },
        "patent_intelligence": {
            "total_patents": features["patent_count"],
            "domains": features["patent_domains"][:5]
        },
        "funding_intelligence": funding_intelligence,
        "collaboration_intelligence": collaboration_intelligence,
        "research_activity_score": activity_score,
        "profile_completeness": completeness,
        "trends": trends
    }

def get_researcher_comparison(db: Session, user_id1: int, user_id2: int) -> Optional[Dict[str, Any]]:
    """Compare two researchers side-by-side based on actual database evidence."""
    r1 = get_researcher_intelligence_profile(db, user_id1)
    r2 = get_researcher_intelligence_profile(db, user_id2)

    if not r1 or not r2:
        return None

    # Compute shared features
    doms1 = set(d.lower() for d in r1["research_domains"])
    doms2 = set(d.lower() for d in r2["research_domains"])
    shared_domains = [d for d in r1["research_domains"] if d.lower() in doms2]

    techs1 = set(t.lower() for t in [x["technology"] for x in r1["technology_profile"]])
    techs2 = set(t.lower() for t in [x["technology"] for x in r2["technology_profile"]])
    shared_techs = [t for t in [x["technology"] for x in r1["technology_profile"]] if t.lower() in techs2]

    ints1 = set(i.lower() for i in r1["research_interests"])
    ints2 = set(i.lower() for i in r2["research_interests"])
    shared_interests = [i for i in r1["research_interests"] if i.lower() in ints2]

    # Complementary capabilities matrix
    comp1_to_2 = [t for t in [x["technology"] for x in r1["technology_profile"]] if t.lower() not in techs2]
    comp2_to_1 = [t for t in [x["technology"] for x in r2["technology_profile"]] if t.lower() not in techs1]

    return {
        "researcher1": {
            "id": r1["researcher_id"],
            "name": r1["name"],
            "organization": r1["organization"],
            "activity_score": r1["research_activity_score"]
        },
        "researcher2": {
            "id": r2["researcher_id"],
            "name": r2["name"],
            "organization": r2["organization"],
            "activity_score": r2["research_activity_score"]
        },
        "shared_domains": shared_domains,
        "shared_technologies": shared_techs,
        "shared_interests": shared_interests,
        "complementary_capabilities": [
            {"provider": r1["name"], "capabilities": comp1_to_2[:3]},
            {"provider": r2["name"], "capabilities": comp2_to_1[:3]}
        ],
        "comparison_matrix": {
            "publication_counts": {r1["name"]: r1["publication_count"], r2["name"]: r2["publication_count"]},
            "patent_counts": {r1["name"]: r1["patent_count"], r2["name"]: r2["patent_count"]},
            "activity_scores": {r1["name"]: r1["research_activity_score"], r2["name"]: r2["research_activity_score"]}
        }
    }
