# backend/app/services/funding_matching_service.py

import os
import re
import math
from datetime import date
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session

from app.models import FundingOpportunity, FundingRecommendation, User
from app.services import researcher_feature_service
from app.services import funding_feature_service
from app.services import funding_eligibility_service

# Configurable Weights & Thresholds (Total 100 max points)
DEFAULT_SCORING_WEIGHTS = {
    "domain": 20.0,
    "technology": 20.0,
    "interests": 15.0,
    "keywords": 10.0,
    "publications": 10.0,
    "patents": 5.0,
    "semantic": 15.0,
    "deadline": 5.0
}

MIN_RELEVANCE_THRESHOLD = 35.0  # Opportunities scoring below this are excluded from top recommendations

# Centralized Keyword & Multi-Word Concept Alias Mapping
KEYWORD_ALIASES = {
    "llm": ["large language model", "large language models", "generative ai"],
    "large language model": ["llm", "large language models", "generative ai"],
    "large language models": ["llm", "large language model", "generative ai"],
    "nlp": ["natural language processing", "text mining", "computational linguistics"],
    "natural language processing": ["nlp", "text mining"],
    "rag": ["retrieval-augmented generation", "retrieval augmented generation", "vector search"],
    "retrieval-augmented generation": ["rag", "vector search", "retrieval augmented generation"],
    "retrieval augmented generation": ["rag", "vector search"],
    "ai": ["artificial intelligence", "machine learning"],
    "artificial intelligence": ["ai", "machine learning"],
    "ml": ["machine learning"],
    "machine learning": ["ml"],
    "kg": ["knowledge graph", "knowledge graphs"],
    "knowledge graph": ["kg", "knowledge graphs"],
    "knowledge graphs": ["kg", "knowledge graph"],
    "gnn": ["graph neural network", "graph neural networks"],
    "graph neural network": ["gnn", "graph neural networks"],
    "graph neural networks": ["gnn", "graph neural network"]
}

# Generic noise words to filter from semantic vector calculations and relevance tests
GENERIC_STOP_WORDS = {
    "research", "funding", "grant", "opportunity", "project", "program",
    "application", "development", "science", "system", "technology",
    "area", "domain", "proposal", "fund", "award", "fellowship", "support",
    "model", "models", "based", "driven", "approach", "methods", "study"
}

# Global embedding model cache for sentence-transformers
_EMBEDDING_MODEL = None

def get_embedding_model():
    """Load and cache sentence-transformers/all-MiniLM-L6-v2 model."""
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            _EMBEDDING_MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: sentence-transformers model load failed: {e}")
            _EMBEDDING_MODEL = False
    return _EMBEDDING_MODEL

def _to_str(val: Any) -> str:
    """Safely convert string or list to a clean single string representation."""
    if isinstance(val, list):
        return ", ".join([str(x) for x in val if x])
    return str(val) if val else ""

def _extract_concepts(raw_input: Any) -> List[str]:
    """
    Extract clean multi-word concept phrases from string or list input.
    Preserves phrase integrity e.g. 'Natural Language Processing', 'Machine Learning',
    'Retrieval-Augmented Generation', 'Knowledge Graphs'.
    """
    if not raw_input:
        return []
    
    if isinstance(raw_input, list):
        items = raw_input
    else:
        text = str(raw_input)
        items = text.replace("\n", ",").replace(";", ",").replace("|", ",").split(",")

    concepts = []
    seen = set()
    for item in items:
        cleaned = str(item).strip()
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            concepts.append(cleaned)
    return concepts

def _tokenize(text: str) -> set:
    """Extract lowercase words of length >= 2."""
    if not text:
        return set()
    return set(re.findall(r'\b[a-zA-Z0-9]{2,}\b', text.lower()))

def _expand_tokens(tokens: set) -> set:
    """Expand token set using KEYWORD_ALIASES mapping."""
    expanded = set(tokens)
    for tok in list(tokens):
        if tok in KEYWORD_ALIASES:
            for alias in KEYWORD_ALIASES[tok]:
                expanded.update(_tokenize(alias))
    return expanded

def evaluate_publication_matches(
    researcher: Dict[str, Any],
    opportunity: Dict[str, Any]
) -> Tuple[int, List[Dict[str, Any]], float]:
    """
    Strict per-publication relevance test.
    Only counts publications that have genuine technical concept overlap with the opportunity.
    Returns (match_count, matched_publications_list, ratio_score).
    """
    raw_pubs = researcher.get("publications_raw", [])
    if not raw_pubs:
        return 0, [], 0.0

    opp_text_parts = (
        opportunity.get("title", "") + " " +
        opportunity.get("description", "") + " " +
        " ".join(opportunity.get("research_domains", [])) + " " +
        " ".join(opportunity.get("technology_areas", [])) + " " +
        " ".join(opportunity.get("keywords", []))
    )
    opp_tokens = _expand_tokens(_tokenize(opp_text_parts))

    matched_pubs = []
    for pub in raw_pubs:
        if isinstance(pub, dict):
            pub_id = pub.get("id") or pub.get("publication_id")
            pub_title = pub.get("title") or ""
        else:
            pub_id = getattr(pub, "id", None) or getattr(pub, "publication_id", None)
            pub_title = getattr(pub, "title", "") or ""

        if not pub_title:
            continue

        pub_tokens = _expand_tokens(_tokenize(pub_title))
        filtered_pub_tokens = pub_tokens - GENERIC_STOP_WORDS
        if not filtered_pub_tokens:
            continue

        # Strict test: Require at least 1 non-generic technical concept overlap
        overlap = filtered_pub_tokens.intersection(opp_tokens)
        if len(overlap) >= 1:
            matched_pubs.append({
                "publication_id": pub_id,
                "title": pub_title
            })

    match_count = len(matched_pubs)
    ratio = min(1.0, match_count / 2.0) if match_count > 0 else 0.0
    return match_count, matched_pubs, ratio

def evaluate_patent_matches(
    researcher: Dict[str, Any],
    opportunity: Dict[str, Any]
) -> Tuple[int, List[Dict[str, Any]], float]:
    """
    Strict per-patent relevance test.
    Only counts patents that have genuine technical concept/domain overlap with the opportunity.
    Returns (match_count, matched_patents_list, ratio_score).
    """
    raw_pats = researcher.get("patents_raw", [])
    if not raw_pats:
        return 0, [], 0.0

    opp_text_parts = (
        opportunity.get("title", "") + " " +
        opportunity.get("description", "") + " " +
        " ".join(opportunity.get("research_domains", [])) + " " +
        " ".join(opportunity.get("technology_areas", [])) + " " +
        " ".join(opportunity.get("keywords", []))
    )
    opp_tokens = _expand_tokens(_tokenize(opp_text_parts))

    matched_pats = []
    for pat in raw_pats:
        if isinstance(pat, dict):
            pat_id = pat.get("id") or pat.get("patent_id")
            pat_title = pat.get("title") or ""
            pat_dom = pat.get("technology_domain") or ""
        else:
            pat_id = getattr(pat, "id", None) or getattr(pat, "patent_id", None)
            pat_title = getattr(pat, "title", "") or ""
            pat_dom = getattr(pat, "technology_domain", "") or ""

        pat_tokens = _expand_tokens(_tokenize(pat_title + " " + pat_dom))
        filtered_pat_tokens = pat_tokens - GENERIC_STOP_WORDS
        if not filtered_pat_tokens:
            continue

        overlap = filtered_pat_tokens.intersection(opp_tokens)
        if len(overlap) >= 1:
            matched_pats.append({
                "patent_id": pat_id,
                "title": pat_title or pat_dom
            })

    match_count = len(matched_pats)
    ratio = min(1.0, match_count / 1.0) if match_count > 0 else 0.0
    return match_count, matched_pats, ratio

def compute_rule_based_score(
    researcher: Dict[str, Any],
    opportunity: Dict[str, Any],
    weights: Dict[str, float] = DEFAULT_SCORING_WEIGHTS
) -> Tuple[float, List[str], List[str], Dict[str, float], int, List[Dict[str, Any]], int, List[Dict[str, Any]]]:
    """
    Calculate deterministic rule-based sub-scores and multi-word concept matched signals.
    """
    matched_signals = []
    unmatched_signals = []

    # 1. Research Domain Match (20.0 max pts)
    res_domain_concepts = _extract_concepts(researcher.get("research_domain"))
    opp_domain_concepts = _extract_concepts(opportunity.get("research_domains"))
    domain_score = 0.0

    if res_domain_concepts and opp_domain_concepts:
        res_dom_tokens = _expand_tokens(_tokenize(" ".join(res_domain_concepts))) - GENERIC_STOP_WORDS
        opp_dom_tokens = _expand_tokens(_tokenize(" ".join(opp_domain_concepts))) - GENERIC_STOP_WORDS
        
        intersection = res_dom_tokens.intersection(opp_dom_tokens)
        if intersection:
            matched_doms = [d for d in res_domain_concepts if any(t in d.lower() for t in intersection)]
            domain_score = 1.0 if len(intersection) >= 2 or matched_doms else 0.7
            display_dom = ", ".join(matched_doms) if matched_doms else ", ".join(res_domain_concepts)
            matched_signals.append(f"Research domain match: {display_dom}")
        else:
            domain_score = 0.0
            unmatched_signals.append(f"Domain mismatch (Opportunity domain: {', '.join(opp_domain_concepts)})")
    else:
        domain_score = 0.0

    # 2. Technology Area Match (20.0 max pts) — PRESERVES MULTI-WORD CONCEPTS
    res_tech_concepts = _extract_concepts(researcher.get("technology_areas") or researcher.get("technology_area"))
    opp_tech_concepts = _extract_concepts(opportunity.get("technology_areas"))
    tech_score = 0.0

    if res_tech_concepts and opp_tech_concepts:
        res_tech_tokens = _expand_tokens(_tokenize(" ".join(res_tech_concepts))) - GENERIC_STOP_WORDS
        opp_tech_tokens = _expand_tokens(_tokenize(" ".join(opp_tech_concepts))) - GENERIC_STOP_WORDS
        
        intersection = res_tech_tokens.intersection(opp_tech_tokens)
        if intersection:
            # Find intact multi-word concepts that matched
            matched_tech_phrases = [
                c for c in res_tech_concepts 
                if any(tok in c.lower() for tok in intersection)
            ]
            tech_score = 1.0 if len(intersection) >= 2 or len(matched_tech_phrases) >= 2 else 0.7
            display_tech = ", ".join(matched_tech_phrases) if matched_tech_phrases else ", ".join(res_tech_concepts[:2])
            matched_signals.append(f"Technology match: {display_tech}")
        else:
            tech_score = 0.0
            unmatched_signals.append("No direct technology overlap")
    else:
        tech_score = 0.0

    # 3. Research Interests Match (15.0 max pts)
    res_interests = _extract_concepts(researcher.get("research_interests"))
    opp_text_parts = (
        opportunity.get("title", "") + " " +
        opportunity.get("description", "") + " " +
        " ".join(opportunity.get("keywords", [])) + " " +
        " ".join(opportunity.get("technology_areas", []))
    )
    opp_tokens = _expand_tokens(_tokenize(opp_text_parts))

    matched_interest_phrases = []
    for interest in res_interests:
        int_tokens = _expand_tokens(_tokenize(interest)) - GENERIC_STOP_WORDS
        if int_tokens and int_tokens.intersection(opp_tokens):
            matched_interest_phrases.append(interest)

    interests_score = min(1.0, len(matched_interest_phrases) / 2.0) if matched_interest_phrases else 0.0
    if matched_interest_phrases:
        matched_signals.append(f"Interest match: {', '.join(matched_interest_phrases[:3])}")
    else:
        unmatched_signals.append("No direct research interest overlap")

    # 4. Keyword Match (10.0 max pts)
    res_keywords = _extract_concepts(researcher.get("keywords"))
    opp_keywords = _extract_concepts(opportunity.get("keywords")) + _extract_concepts(opportunity.get("match_badges"))
    
    matched_kw_phrases = []
    opp_kw_tokens = _expand_tokens(_tokenize(" ".join(opp_keywords)))
    for kw in res_keywords:
        kw_tokens = _expand_tokens(_tokenize(kw)) - GENERIC_STOP_WORDS
        if kw_tokens and kw_tokens.intersection(opp_kw_tokens):
            matched_kw_phrases.append(kw)

    keyword_score = min(1.0, len(matched_kw_phrases) / 2.0) if matched_kw_phrases else 0.0
    if matched_kw_phrases:
        matched_signals.append(f"Keyword match: {', '.join(matched_kw_phrases[:3])}")

    # 5. Publication Evidence (10.0 max pts)
    pub_count, matched_pubs, pub_ratio = evaluate_publication_matches(researcher, opportunity)
    pub_score = pub_ratio
    if pub_count > 0:
        pub_title_sample = matched_pubs[0]['title'] if matched_pubs else ""
        matched_signals.append(f"{pub_count} relevant publication(s) matched (e.g. '{pub_title_sample}')")
    else:
        unmatched_signals.append("No matching publications found for this topic")

    # 6. Patent Evidence (5.0 max pts)
    pat_count, matched_pats, pat_ratio = evaluate_patent_matches(researcher, opportunity)
    pat_score = pat_ratio
    if pat_count > 0:
        pat_title_sample = matched_pats[0]['title'] if matched_pats else ""
        matched_signals.append(f"{pat_count} relevant patent asset(s) matched (e.g. '{pat_title_sample}')")

    # 7. Deadline Signal (5.0 max pts)
    deadline_status = opportunity.get("deadline_status", "open")
    if deadline_status == "closing_soon":
        deadline_score = 1.0
        matched_signals.append("Deadline status: Closing soon")
    elif deadline_status == "open":
        deadline_score = 0.8
    else:
        deadline_score = 0.5

    # Compute sub-score points
    dom_pt = round(domain_score * weights.get("domain", 20.0), 1)
    tech_pt = round(tech_score * weights.get("technology", 20.0), 1)
    int_pt = round(interests_score * weights.get("interests", 15.0), 1)
    key_pt = round(keyword_score * weights.get("keywords", 10.0), 1)
    pub_pt = round(pub_score * weights.get("publications", 10.0), 1)
    pat_pt = round(pat_score * weights.get("patents", 5.0), 1)
    dl_pt = round(deadline_score * weights.get("deadline", 5.0), 1)

    # 8. Mismatch Penalty (-25.0 pts if total technical mismatch)
    penalty_pt = 0.0
    if domain_score == 0.0 and tech_score == 0.0 and interests_score == 0.0 and pub_count == 0 and pat_count == 0:
        penalty_pt = -25.0
        dl_pt = 0.0
        unmatched_signals.append("Strong mismatch: No domain, technology, interest, publication, or patent overlap.")

    raw_rule_score = dom_pt + tech_pt + int_pt + key_pt + pub_pt + pat_pt + dl_pt + penalty_pt

    breakdown = {
        "domain": dom_pt,
        "technology": tech_pt,
        "interests": int_pt,
        "keywords": key_pt,
        "publications": pub_pt,
        "patents": pat_pt,
        "deadline": dl_pt,
        "penalty": penalty_pt
    }

    return round(raw_rule_score, 1), matched_signals, unmatched_signals, breakdown, pub_count, matched_pubs, pat_count, matched_pats

def compute_semantic_score(researcher: Dict[str, Any], opportunity: Dict[str, Any]) -> float:
    """
    Noise-filtered semantic vector similarity score (0-100) using Sentence Transformers.
    Strips generic stop words to prevent baseline semantic inflation.
    """
    model = get_embedding_model()

    res_concepts = (
        _extract_concepts(researcher.get('research_domain')) +
        _extract_concepts(researcher.get('technology_areas') or researcher.get('technology_area')) +
        _extract_concepts(researcher.get('research_interests')) +
        _extract_concepts(researcher.get('keywords'))
    )
    res_tokens = _expand_tokens(_tokenize(" ".join(res_concepts))) - GENERIC_STOP_WORDS

    opp_concepts = (
        _extract_concepts(opportunity.get('title')) +
        _extract_concepts(opportunity.get('description')) +
        _extract_concepts(opportunity.get('research_domains')) +
        _extract_concepts(opportunity.get('technology_areas')) +
        _extract_concepts(opportunity.get('keywords'))
    )
    opp_tokens = _expand_tokens(_tokenize(" ".join(opp_concepts))) - GENERIC_STOP_WORDS

    res_text = " ".join(res_tokens)
    opp_text = " ".join(opp_tokens)

    if not res_text or not opp_text:
        return 0.0

    if model and model is not False:
        try:
            embeddings = model.encode([res_text, opp_text], normalize_embeddings=True)
            sim = float(embeddings[0] @ embeddings[1])
            if sim <= 0.25:
                return 0.0
            scaled_score = min(100.0, ((sim - 0.25) / 0.55) * 100.0)
            return round(scaled_score, 1)
        except Exception as e:
            print(f"Error in SentenceTransformer encoding: {e}")

    # Fallback Jaccard overlap
    intersection = res_tokens.intersection(opp_tokens)
    union = res_tokens.union(opp_tokens)
    jaccard = len(intersection) / len(union) if union else 0.0
    if jaccard < 0.1:
        return 0.0
    return round(jaccard * 100.0, 1)

def generate_match_reason(
    title: str,
    match_score: int,
    match_level: str,
    matched_signals: List[str],
    unmatched_signals: List[str],
    researcher: Dict[str, Any],
    opportunity: Dict[str, Any]
) -> str:
    """
    Generate evidence-backed, human-readable match explanation from actual evidence signals.
    """
    res_domain = _to_str(researcher.get("research_domain", "STEM"))
    res_tech = _to_str(researcher.get("technology_areas") or researcher.get("technology_area", "AI"))
    opp_domains = ", ".join(_extract_concepts(opportunity.get("research_domains"))) or "specified target fields"

    if match_level == "HIGH":
        signals_summary = ", ".join(matched_signals[:3])
        return (
            f"Strong match ({match_score}%) because researcher specializes in {res_domain} and {res_tech}. "
            f"Key evidence signals: {signals_summary}."
        )
    elif match_level == "MEDIUM":
        signals_summary = ", ".join(matched_signals[:2]) if matched_signals else "partial area overlap"
        return (
            f"Moderate match ({match_score}%) due to partial domain/technology alignment in {res_tech}. "
            f"Evidence: {signals_summary}."
        )
    else:
        unmatched_summary = unmatched_signals[0] if unmatched_signals else f"Target fields ({opp_domains}) differ from researcher profile ({res_domain})"
        return (
            f"Low match ({match_score}%) because opportunity focuses on {opp_domains}, "
            f"while researcher specializes in {res_domain} and {res_tech}. Mismatch reason: {unmatched_summary}."
        )

def calculate_match_score(
    researcher: Dict[str, Any],
    opportunity: Dict[str, Any],
    user_feedback: Optional[str] = None
) -> Dict[str, Any]:
    """
    Combine rule-based matching and semantic matching into final_score with EXACT mathematical reconciliation:
    sum(match_breakdown.values()) == final_score.
    """
    rule_score, matched_signals, unmatched_signals, breakdown, pub_count, matched_pubs, pat_count, matched_pats = compute_rule_based_score(researcher, opportunity)
    raw_semantic = compute_semantic_score(researcher, opportunity)

    # 15.0 max points for semantic similarity
    sem_pt = round(raw_semantic * DEFAULT_SCORING_WEIGHTS.get("semantic", 15.0) / 100.0, 1)
    breakdown["semantic"] = sem_pt

    # User Feedback Adjustment (-15 to +8)
    feedback_pt = 0.0
    if user_feedback in ["saved", "relevant"]:
        feedback_pt = 5.0
        matched_signals.append("User Feedback: Saved preference boost (+5)")
    elif user_feedback == "applied":
        feedback_pt = 8.0
        matched_signals.append("User Feedback: Applied interest boost (+8)")
    elif user_feedback in ["dismissed", "not_relevant"]:
        feedback_pt = -15.0
        unmatched_signals.append("User Feedback: Dismissed penalty (-15)")

    breakdown["feedback"] = feedback_pt

    # Exact mathematical summation
    total_unbounded = sum(breakdown.values())
    composite_score = max(0, min(100, round(total_unbounded)))

    # Categorize match level confidence
    if composite_score >= 75:
        match_level = "HIGH"
    elif composite_score >= 50:
        match_level = "MEDIUM"
    else:
        match_level = "LOW"

    opp_title = opportunity.get("title", "Funding Opportunity")
    reason = generate_match_reason(opp_title, composite_score, match_level, matched_signals, unmatched_signals, researcher, opportunity)

    def _to_list(val):
        if isinstance(val, list):
            return val
        if isinstance(val, str) and val.strip():
            return [t.strip() for t in val.replace("\n", ",").replace(";", ",").split(",") if t.strip()]
        return []

    el = opportunity.get("eligibility")
    el_str = ", ".join([str(x) for x in el if x]) if isinstance(el, list) else (str(el) if el else None)

    return {
        "funding_id": opportunity.get("id") or 0,
        "title": opp_title,
        "funder": opportunity.get("funder") or "Funding Agency",
        "amount_range": opportunity.get("amount_range") or "$50,000 – $250,000",
        "deadline": str(opportunity.get("deadline") or "2026-12-31"),
        "match_score": composite_score,
        "match_level": match_level,
        "reason": reason,
        "matched_signals": matched_signals,
        "unmatched_signals": unmatched_signals,
        "status": user_feedback or "recommended",
        
        # Evidence detail fields
        "publication_match_count": pub_count,
        "patent_match_count": pat_count,
        "matched_publications": matched_pubs,
        "matched_patents": matched_pats,

        # Extended metadata pass-through
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
    top_k: int = 10,
    min_score_threshold: float = MIN_RELEVANCE_THRESHOLD
) -> Dict[str, Any]:
    """
    1. Retrieve researcher features from Part 2.
    2. Filter eligible funding opportunities using Part 3.
    3. Calculate Part 4 rule + semantic matching scores for eligible opportunities ONLY.
    4. Sort descending by match_score.
    5. Filter by min_score_threshold.
    6. Return top_k ranked recommendations.
    """
    researcher_features = researcher_feature_service.build_researcher_features(db, user_id)
    if researcher_features is None:
        return {
            "user_id": user_id,
            "researcher_profile": None,
            "recommendations": []
        }

    eligibility_result = funding_eligibility_service.filter_eligible_funding(db, user_id)
    eligible_raw_items = eligibility_result.get("eligible", [])

    if not eligible_raw_items:
        return {
            "user_id": user_id,
            "researcher_profile": {
                "research_domain": researcher_features.get("research_domain"),
                "technology_area": researcher_features.get("technology_areas") or researcher_features.get("technology_area"),
                "research_interests": researcher_features.get("research_interests")
            },
            "recommendations": []
        }

    eligible_ids = [item["funding_id"] for item in eligible_raw_items]
    eligible_db_opps = db.query(FundingOpportunity).filter(FundingOpportunity.id.in_(eligible_ids)).all()
    opp_by_id = {opp.id: opp for opp in eligible_db_opps}

    feedback_records = db.query(FundingRecommendation).filter(FundingRecommendation.user_id == user_id).all()
    feedback_map = {rec.funding_id: rec.feedback or rec.status for rec in feedback_records if rec.feedback or rec.status}

    scored_recommendations = []
    for raw_item in eligible_raw_items:
        opp_id = raw_item["funding_id"]
        opp_db = opp_by_id.get(opp_id)
        if not opp_db:
            continue

        opp_features = funding_feature_service.extract_funding_features(opp_db)
        opp_features["deadline_status"] = raw_item.get("deadline_status", "open")

        user_fb = feedback_map.get(opp_id)
        rec_item = calculate_match_score(researcher_features, opp_features, user_feedback=user_fb)
        
        if rec_item["match_score"] >= min_score_threshold:
            scored_recommendations.append(rec_item)

    scored_recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    top_recommendations = scored_recommendations[:top_k]

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
            "technology_area": researcher_features.get("technology_areas") or researcher_features.get("technology_area"),
            "research_interests": researcher_features.get("research_interests")
        },
        "recommendations": top_recommendations
    }
