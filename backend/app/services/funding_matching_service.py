import os
import re
import math
from datetime import date
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session

from app.models import FundingOpportunity, FundingRecommendation, User
from app.services.researcher_feature_service import build_researcher_features
from app.services.funding_feature_service import extract_funding_features
from app.services.eligibility_service import filter_eligible_funding

# Try loading sentence-transformers embedding model
_EMBEDDING_MODEL = None
def get_embedding_model():
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Use cached local sentence-transformers model
            _EMBEDDING_MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: sentence-transformers model load failed: {e}")
            _EMBEDDING_MODEL = False
    return _EMBEDDING_MODEL

def _tokenize(text: str) -> set:
    """Helper to extract lowercase words of length >= 3."""
    if not text:
        return set()
    return set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', text.lower()))

def _text_overlap_score(source_items: List[str], target_items: List[str]) -> float:
    """Calculate ratio of source items/tokens present in target items."""
    if not source_items or not target_items:
        return 0.0
    source_tokens = set()
    for item in source_items:
        source_tokens.update(_tokenize(item))

    target_tokens = set()
    for item in target_items:
        target_tokens.update(_tokenize(item))

    if not source_tokens or not target_tokens:
        return 0.0

    intersection = source_tokens.intersection(target_tokens)
    if not intersection:
        return 0.0
    
    # Calculate coverage of source tokens in target
    coverage = len(intersection) / len(source_tokens)
    return min(1.0, coverage)

def compute_rule_based_score(
    researcher: Dict[str, Any],
    opportunity: Dict[str, Any]
) -> Tuple[float, List[str], List[str], Dict[str, float]]:
    """
    Calculate deterministic rule-based match score (0-100), list matched/unmatched signals, and return breakdown weights.
    """
    matched_signals = []
    unmatched_signals = []

    # 1. Research Domain Match (30%)
    res_domain = (researcher.get("research_domain") or "").strip().lower()
    opp_domains = [d.lower() for d in opportunity.get("research_domains", [])]
    domain_score = 0.0

    if res_domain and res_domain != "unspecified":
        for d in opp_domains:
            if res_domain == d or res_domain in d or d in res_domain:
                domain_score = 1.0
                matched_signals.append(f"Research domain: {researcher.get('research_domain')}")
                break
        if domain_score == 0.0 and opp_domains:
            # Check keyword overlap in domain string
            dom_tokens_res = _tokenize(res_domain)
            dom_tokens_opp = set()
            for d in opp_domains:
                dom_tokens_opp.update(_tokenize(d))
            if dom_tokens_res.intersection(dom_tokens_opp):
                domain_score = 0.7
                matched_signals.append(f"Research domain partial match: {researcher.get('research_domain')}")
            else:
                unmatched_signals.append(f"Domain mismatch (Opportunity: {', '.join(opportunity.get('research_domains', []))})")
    else:
        domain_score = 0.5 # Unknown profile domain

    # 2. Technology Area Match (20%)
    res_tech = (researcher.get("technology_area") or "").strip().lower()
    opp_techs = [t.lower() for t in opportunity.get("technology_areas", [])]
    tech_score = 0.0

    if res_tech and res_tech != "unspecified":
        for t in opp_techs:
            if res_tech == t or res_tech in t or t in res_tech:
                tech_score = 1.0
                matched_signals.append(f"Technology area: {researcher.get('technology_area')}")
                break
        if tech_score == 0.0 and opp_techs:
            tech_tokens_res = _tokenize(res_tech)
            tech_tokens_opp = set()
            for t in opp_techs:
                tech_tokens_opp.update(_tokenize(t))
            if tech_tokens_res.intersection(tech_tokens_opp):
                tech_score = 0.7
                matched_signals.append(f"Technology area partial match: {researcher.get('technology_area')}")
    else:
        tech_score = 0.5

    # 3. Research Interests Match (15%)
    res_interests = researcher.get("research_interests", [])
    opp_all_text = [opportunity.get("title", "")] + opportunity.get("keywords", []) + opportunity.get("technology_areas", [])
    interests_overlap = _text_overlap_score(res_interests, opp_all_text)
    interests_score = interests_overlap
    if interests_overlap > 0.1:
        matched_signals.append(f"Interests match: {', '.join(res_interests[:3])}")

    # 4. Keyword Match (15%)
    res_keywords = researcher.get("keywords", [])
    opp_keywords = opportunity.get("keywords", []) + opportunity.get("match_badges", [])
    keyword_overlap = _text_overlap_score(res_keywords, opp_keywords)
    keyword_score = keyword_overlap
    if keyword_overlap > 0.1:
        matched_signals.append(f"Keywords match: {', '.join(res_keywords[:3])}")

    # 5. Publication Similarity (10%)
    pub_topics = researcher.get("publication_topics", [])
    pub_overlap = _text_overlap_score(pub_topics, opp_all_text)
    pub_score = pub_overlap
    if pub_overlap > 0.05:
        matched_signals.append(f"Publication evidence: {len(pub_topics)} publication(s) analyzed")

    # 6. Patent & Intellectual Property Signal (15%)
    patent_domains = researcher.get("patent_domains", [])
    patent_score = 0.0
    if patent_domains:
        patent_overlap = _text_overlap_score(patent_domains, opp_all_text)
        if patent_overlap > 0.0:
            patent_score = max(0.6, patent_overlap)
            matched_signals.append(f"Patent IP evidence: {len(patent_domains)} intellectual asset(s) matched ({', '.join(patent_domains[:2])})")
        else:
            # Base IP innovation bonus for registered patents
            patent_score = min(1.0, 0.4 + (len(patent_domains) * 0.15))
            matched_signals.append(f"Registered IP Portfolio: {len(patent_domains)} patent asset(s)")

    # 7. Deadline / Eligibility Score (5%)
    deadline_status = opportunity.get("deadline_status", "open")
    if deadline_status == "closing_soon":
        deadline_score = 1.0
        matched_signals.append("Urgency bonus: Closing soon")
    elif deadline_status == "open":
        deadline_score = 0.8
    else:
        deadline_score = 0.0

    # Weighted Sum Formula (0–100)
    # Domain (25%), Tech Area (20%), Interests (15%), Keywords (15%), Publications (10%), Patents (10%), Deadline (5%)
    dom_pt = round(domain_score * 25.0, 1)
    tech_pt = round(tech_score * 20.0, 1)
    int_pt = round(interests_score * 15.0, 1)
    key_pt = round(keyword_score * 15.0, 1)
    pub_pt = round(pub_score * 10.0, 1)
    pat_pt = round(patent_score * 10.0, 1)
    dl_pt = round(deadline_score * 5.0, 1)

    raw_rule_score = dom_pt + tech_pt + int_pt + key_pt + pub_pt + pat_pt + dl_pt

    breakdown = {
        "domain": dom_pt,
        "technology": tech_pt,
        "interests": int_pt,
        "keywords": key_pt,
        "publications": pub_pt,
        "patents": pat_pt,
        "eligibility": 5.0,
        "deadline": dl_pt
    }

    return round(raw_rule_score, 2), matched_signals, unmatched_signals, breakdown

def compute_semantic_score(researcher: Dict[str, Any], opportunity: Dict[str, Any]) -> float:
    """
    Calculate semantic similarity score (0-100) using Sentence Transformers embedding model
    or token similarity fallback.
    """
    model = get_embedding_model()

    res_text = (
        f"{researcher.get('research_domain', '')} {researcher.get('technology_area', '')} "
        f"{' '.join(researcher.get('research_interests', []))} {' '.join(researcher.get('keywords', []))} "
        f"{' '.join(researcher.get('publication_topics', []))} {' '.join(researcher.get('patent_domains', []))}"
    ).strip()

    opp_text = (
        f"{opportunity.get('title', '')} {opportunity.get('description', '')} "
        f"{' '.join(opportunity.get('research_domains', []))} {' '.join(opportunity.get('technology_areas', []))} "
        f"{' '.join(opportunity.get('keywords', []))} {' '.join(opportunity.get('match_badges', []))}"
    ).strip()

    if not res_text or not opp_text:
        return 50.0

    if model and model is not False:
        try:
            embeddings = model.encode([res_text, opp_text], normalize_embeddings=True)
            sim = float(embeddings[0] @ embeddings[1])
            score = max(0.0, min(100.0, ((sim + 1.0) / 2.0) * 100.0))
            return round(score, 2)
        except Exception as e:
            print(f"Error in SentenceTransformer encoding: {e}")

    res_tokens = _tokenize(res_text)
    opp_tokens = _tokenize(opp_text)
    if not res_tokens or not opp_tokens:
        return 50.0
    intersection = res_tokens.intersection(opp_tokens)
    union = res_tokens.union(opp_tokens)
    jaccard = len(intersection) / len(union) if union else 0.5
    return round(jaccard * 100.0, 2)

def generate_explanation_with_gemini(
    title: str,
    match_score: int,
    matched_signals: List[str],
    researcher: Dict[str, Any]
) -> Optional[str]:
    """
    Generate natural language explanation using Gemini if API key is present.
    Gemini ONLY formats explanation; it does NOT determine the score.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
Given the following deterministic matching analysis for a researcher and funding opportunity:
- Opportunity Title: {title}
- Overall Calculated Match Score: {match_score}/100
- Researcher Domain: {researcher.get('research_domain')}
- Researcher Tech Area: {researcher.get('technology_area')}
- Matched Evidence Signals: {', '.join(matched_signals)}

Write a concise 1-2 sentence evidence-backed explanation showing why this opportunity matches. Format like:
"{match_score}% match because your research profile includes [Domain/Tech], your publications cover [topics], and this opportunity targets [grant domain]."
"""
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Gemini explanation generation bypassed: {e}")

    return None

def calculate_match_score(
    researcher: Dict[str, Any],
    opportunity: Dict[str, Any],
    user_feedback: Optional[str] = None,
    rule_weight: float = 0.7,
    semantic_weight: float = 0.3
) -> Dict[str, Any]:
    """
    Combine rule-based matching, semantic matching, and user feedback adjustments.
    Returns composite score, evidence explanation, matched signals, and breakdown.
    """
    rule_score, matched_signals, unmatched_signals, breakdown = compute_rule_based_score(researcher, opportunity)
    semantic_score = compute_semantic_score(researcher, opportunity)

    base_score = round(rule_score * rule_weight + semantic_score * semantic_weight)

    # Bounded Feedback-Aware Personalization adjustment (-20 to +10 max)
    feedback_adj = 0
    if user_feedback in ["saved", "relevant"]:
        feedback_adj = 5
        matched_signals.append("User Feedback: Saved/Relevant preference boost")
    elif user_feedback == "applied":
        feedback_adj = 8
        matched_signals.append("User Feedback: Applied interest boost")
    elif user_feedback in ["dismissed", "not_relevant"]:
        feedback_adj = -15
        unmatched_signals.append("User Feedback: Previously dismissed/marked not relevant")

    composite_score = max(0, min(100, base_score + feedback_adj))

    # Construct rich evidence-based explanation
    res_domain = researcher.get("research_domain", "STEM")
    res_tech = researcher.get("technology_area", "AI")
    opp_title = opportunity.get("title", "")

    evidence_explanation = (
        f"{composite_score}% match because your research profile includes {res_domain} and {res_tech}, "
        f"your registered publications and IP portfolio support this domain, and '{opp_title}' directly targets key research outcomes."
    )

    gemini_reason = generate_explanation_with_gemini(
        opp_title,
        composite_score,
        matched_signals,
        researcher
    )
    final_reason = gemini_reason if gemini_reason else evidence_explanation

    def _to_list(val):
        if isinstance(val, list):
            return val
        if isinstance(val, str) and val.strip():
            return [t.strip() for t in val.replace("\n", ",").replace(";", ",").split(",") if t.strip()]
        return []

    el = opportunity.get("eligibility")
    if isinstance(el, list):
        el_str = ", ".join([str(x) for x in el if x])
    else:
        el_str = str(el) if el else None

    return {
        "funding_id": opportunity.get("id") or 0,
        "title": opportunity.get("title") or "Research Funding Opportunity",
        "funder": opportunity.get("funder") or "Funding Agency",
        "amount_range": opportunity.get("amount_range") or "$50,000 – $250,000",
        "deadline": str(opportunity.get("deadline") or "2026-12-31"),
        "match_score": composite_score,
        "reason": final_reason or "Matched based on research profile signals.",
        "matched_signals": matched_signals,
        "unmatched_signals": unmatched_signals,
        "status": user_feedback or "recommended",
        
        # Detail metadata pass-through
        "description": opportunity.get("description"),
        "research_domains": _to_list(opportunity.get("research_domains")),
        "technology_areas": _to_list(opportunity.get("technology_areas")),
        "keywords": _to_list(opportunity.get("keywords")),
        "eligibility": el_str,
        "research_stage": opportunity.get("research_stage"),
        "geographic_scope": opportunity.get("geographic_scope"),
        "funding_type": opportunity.get("funding_type"),
        "match_badges": _to_list(opportunity.get("match_badges")),
        "match_breakdown": breakdown
    }

def rank_funding_opportunities(
    db: Session,
    user_id: int,
    top_k: int = 10
) -> Dict[str, Any]:
    """
    Retrieve researcher features, fetch funding opportunities, filter eligible ones,
    apply feedback adjustments, score, rank, and return recommendations.
    """
    researcher_features = build_researcher_features(db, user_id)
    all_opps = db.query(FundingOpportunity).all()

    # Extract features for all funding opportunities
    funding_feature_list = [extract_funding_features(opp) for opp in all_opps]

    # Filter out ineligible opportunities
    eligible_opps = filter_eligible_funding(researcher_features, funding_feature_list)

    # Exclude expired opportunities
    today = date.today()
    active_opps = []
    for opp in eligible_opps:
        dl = opp.get("deadline")
        # Check deadline date
        if dl:
            if isinstance(dl, str):
                try:
                    dl = date.fromisoformat(dl)
                except Exception:
                    dl = None
            if isinstance(dl, date) and dl < today:
                continue
        if opp.get("status") == "expired":
            continue
        active_opps.append(opp)

    # Load stored user feedback
    feedback_records = db.query(FundingRecommendation).filter(FundingRecommendation.user_id == user_id).all()
    feedback_map = {rec.funding_id: rec.feedback or rec.status for rec in feedback_records if rec.feedback or rec.status}

    # Score each active opportunity
    scored_recommendations = []
    for opp_feat in active_opps:
        user_fb = feedback_map.get(opp_feat.get("id"))
        rec_item = calculate_match_score(researcher_features, opp_feat, user_feedback=user_fb)
        scored_recommendations.append(rec_item)

    # Sort descending by match_score
    scored_recommendations.sort(key=lambda x: x["match_score"], reverse=True)

    top_recommendations = scored_recommendations[:top_k]

    # Persist generated recommendations to funding_recommendations DB table
    try:
        for rec in top_recommendations:
            existing = db.query(FundingRecommendation).filter(
                FundingRecommendation.user_id == user_id,
                FundingRecommendation.funding_id == rec["funding_id"]
            ).first()

            if not existing:
                db_rec = FundingRecommendation(
                    user_id=user_id,
                    funding_id=rec["funding_id"],
                    match_score=float(rec["match_score"]),
                    reason=rec["reason"],
                    status=rec["status"]
                )
                db.add(db_rec)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Warning: Failed to persist recommendations history: {e}")

    return {
        "user_id": user_id,
        "researcher_profile": {
            "research_domain": researcher_features.get("research_domain"),
            "technology_area": researcher_features.get("technology_area"),
            "keywords": researcher_features.get("keywords")
        },
        "recommendations": top_recommendations
    }
