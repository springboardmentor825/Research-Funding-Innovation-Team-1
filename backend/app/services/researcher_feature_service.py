# backend/app/services/researcher_feature_service.py

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models import User, ResearchProfile, Publication, Patent

def get_researcher_profile(db: Session, user_id: int) -> Optional[ResearchProfile]:
    """Retrieve ResearchProfile for given user_id."""
    return db.query(ResearchProfile).filter(ResearchProfile.user_id == user_id).first()

def get_researcher_publications(db: Session, user_id: int) -> List[Publication]:
    """Retrieve all Publications for given user_id, ignoring empty titles and deduplicating."""
    pubs = db.query(Publication).filter(Publication.user_id == user_id).all()
    seen_titles = set()
    unique_pubs = []
    for pub in pubs:
        title = (pub.title or "").strip()
        if title and title.lower() not in seen_titles:
            seen_titles.add(title.lower())
            unique_pubs.append(pub)
    return unique_pubs

def get_researcher_patents(db: Session, user_id: int) -> List[Patent]:
    """Retrieve all Patents for given user_id, deduplicating titles and domains."""
    pats = db.query(Patent).filter(Patent.user_id == user_id).all()
    seen_ids = set()
    unique_pats = []
    for pat in pats:
        if pat.patent_id not in seen_ids:
            seen_ids.add(pat.patent_id)
            unique_pats.append(pat)
    return unique_pats

def _normalize_tokens(raw_input: Optional[str]) -> List[str]:
    """
    Utility to split comma/semicolon/pipe/newline separated strings into clean tokens.
    Preserves multi-word concepts (e.g. 'Natural Language Processing', 'Retrieval-Augmented Generation')
    while removing duplicates case-insensitively.
    """
    if not raw_input:
        return []
    
    # Replace separators with commas
    standardized = raw_input.replace("\n", ",").replace(";", ",").replace("|", ",")
    
    seen_lower = set()
    cleaned_tokens = []
    
    for token in standardized.split(","):
        stripped = token.strip()
        if not stripped:
            continue
        
        # Check case-insensitive duplicate
        lower_val = stripped.lower()
        if lower_val not in seen_lower:
            seen_lower.add(lower_val)
            cleaned_tokens.append(stripped)
            
    return cleaned_tokens

def build_researcher_features(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Build a comprehensive researcher feature dictionary combining profile data,
    publication topics, and patent domains for the given user_id.
    
    Returns None if the user ID does not exist in the database.
    """
    # 1. Verify User Existence
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    # 2. Fetch DB Records
    profile = get_researcher_profile(db, user_id)
    publications = get_researcher_publications(db, user_id)
    patents = get_researcher_patents(db, user_id)

    # 3. Extract Publications Topics & Patent Domains
    pub_topics = [pub.title.strip() for pub in publications if pub.title and pub.title.strip()]
    
    patent_domains = []
    for pat in patents:
        if pat.technology_domain:
            dom = pat.technology_domain.strip()
            if dom and dom not in patent_domains:
                patent_domains.append(dom)
        if pat.title:
            ptitle = pat.title.strip()
            if ptitle and ptitle not in patent_domains and ptitle not in pub_topics:
                patent_domains.append(ptitle)

    # 4. Process Profile Data
    if profile:
        has_profile = True
        organization = profile.organization.strip() if profile.organization else None
        designation = profile.designation.strip() if profile.designation else None
        bio = profile.bio.strip() if profile.bio else None
        
        domains = _normalize_tokens(profile.research_domain)
        tech_areas = _normalize_tokens(profile.technology_area)
        interests = _normalize_tokens(profile.research_interests)
        keywords = _normalize_tokens(profile.keywords)
    else:
        has_profile = False
        organization = None
        designation = None
        bio = None
        domains = []
        tech_areas = []
        interests = []
        keywords = []

    # 5. Build Unified Combined Research Text representation for vector embeddings
    text_parts = []
    if domains:
        text_parts.append(f"Research domain: {', '.join(domains)}.")
    if tech_areas:
        text_parts.append(f"Technology areas: {', '.join(tech_areas)}.")
    if interests:
        text_parts.append(f"Research interests: {', '.join(interests)}.")
    if keywords:
        text_parts.append(f"Keywords: {', '.join(keywords)}.")
    if pub_topics:
        text_parts.append(f"Publications: {', '.join(pub_topics[:5])}.")
    if patent_domains:
        text_parts.append(f"Patent domains: {', '.join(patent_domains[:5])}.")
        
    combined_research_text = " ".join(text_parts).strip()

    publications_raw = [{"id": pub.publication_id, "title": pub.title.strip()} for pub in publications if pub.title and pub.title.strip()]
    patents_raw = [{"id": pat.patent_id, "title": pat.title.strip() if pat.title else "", "technology_domain": pat.technology_domain.strip() if pat.technology_domain else ""} for pat in patents]


    return {
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "organization": organization,
        "designation": designation,
        "bio": bio,
        "research_domain": domains,
        "technology_areas": tech_areas,
        "research_interests": interests,
        "keywords": keywords,
        "publication_topics": pub_topics,
        "patent_domains": patent_domains,
        "publications_raw": publications_raw,
        "patents_raw": patents_raw,
        "combined_research_text": combined_research_text,
        "publication_count": len(publications),
        "patent_count": len(patents),
        "interest_count": len(interests),
        "keyword_count": len(keywords),
        "has_profile": has_profile
    }

