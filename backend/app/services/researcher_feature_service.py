from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models import User, ResearchProfile, Publication, Patent

def get_researcher_profile(db: Session, user_id: int) -> Optional[ResearchProfile]:
    """Retrieve ResearchProfile for given user_id."""
    return db.query(ResearchProfile).filter(ResearchProfile.user_id == user_id).first()

def get_researcher_publications(db: Session, user_id: int) -> List[Publication]:
    """Retrieve all Publications for given user_id."""
    return db.query(Publication).filter(Publication.user_id == user_id).all()

def get_researcher_patents(db: Session, user_id: int) -> List[Patent]:
    """Retrieve all Patents for given user_id."""
    return db.query(Patent).filter(Patent.user_id == user_id).all()

def _clean_list(raw_input: Optional[str]) -> List[str]:
    """Utility to split comma/semicolon/newline separated strings into clean tokens."""
    if not raw_input:
        return []
    cleaned = []
    # Replace newlines and semicolons with commas
    standardized = raw_input.replace("\n", ",").replace(";", ",")
    for token in standardized.split(","):
        stripped = token.strip()
        if stripped and stripped not in cleaned:
            cleaned.append(stripped)
    return cleaned

def build_researcher_features(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Build a comprehensive researcher feature dictionary combining profile data,
    publication titles/journals, and patent technology domains.
    """
    profile = get_researcher_profile(db, user_id)
    publications = get_researcher_publications(db, user_id)
    patents = get_researcher_patents(db, user_id)

    # 1. Extract publication topics
    pub_topics = []
    for pub in publications:
        if pub.title:
            pub_topics.append(pub.title.strip())

    # 2. Extract patent technology domains & titles
    patent_domains = []
    for pat in patents:
        if pat.technology_domain and pat.technology_domain.strip() not in patent_domains:
            patent_domains.append(pat.technology_domain.strip())
        if pat.title and pat.title.strip() not in patent_domains:
            patent_domains.append(pat.title.strip())

    # 3. Handle research profile data
    if profile:
        domain = profile.research_domain.strip() if profile.research_domain else "Unspecified"
        tech_area = profile.technology_area.strip() if profile.technology_area else "Unspecified"
        interests = _clean_list(profile.research_interests)
        keywords = _clean_list(profile.keywords)
    else:
        # Fallback if profile row does not exist in DB: infer from publications & patents if available
        domain = "Unspecified"
        tech_area = "Unspecified"
        
        # If patent domains exist, use the most common patent domain as tech_area
        if patent_domains:
            tech_area = patent_domains[0]
            domain = patent_domains[0]
        
        # Infer interests and keywords from publication titles
        interests = []
        keywords = []
        for pub_title in pub_topics:
            words = [w.strip() for w in pub_title.split() if len(w) > 3]
            for w in words:
                if w not in keywords:
                    keywords.append(w)

    return {
        "user_id": user_id,
        "research_domain": domain,
        "technology_area": tech_area,
        "research_interests": interests,
        "keywords": keywords,
        "publication_topics": pub_topics,
        "patent_domains": patent_domains
    }
