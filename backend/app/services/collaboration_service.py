# backend/app/services/collaboration_service.py

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import User, ResearchProfile, Publication, Patent
from app.services import researcher_feature_service
from sentence_transformers import SentenceTransformer, util

# Shared embedding model cache
_sentence_model = None

def _get_sentence_model():
    global _sentence_model
    if _sentence_model is None:
        try:
            _sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"[CollaborationService] Warning: Could not load sentence-transformer: {e}")
            _sentence_model = None
    return _sentence_model

GENERIC_STOPWORDS = {
    "research", "system", "data", "technology", "analysis", 
    "development", "study", "project", "approach", "method",
    "application", "process", "framework", "model", "science"
}

def _filter_generic_words(items: List[str]) -> List[str]:
    """Filter out standalone generic words so they are not treated as specialist expertise evidence."""
    filtered = []
    for item in items:
        clean = item.strip()
        if clean.lower() not in GENERIC_STOPWORDS:
            filtered.append(clean)
    return filtered

def _calculate_exact_set_overlap(list_a: List[str], list_b: List[str]) -> Tuple[List[str], float]:
    """
    Calculate normalized exact case-insensitive concept overlap.
    Returns (shared_items, match_percentage 0.0-1.0).
    """
    clean_a = [x.strip().lower() for x in _filter_generic_words(list_a) if x.strip()]
    clean_b = [x.strip().lower() for x in _filter_generic_words(list_b) if x.strip()]
    
    if not clean_a or not clean_b:
        return [], 0.0
    
    set_a = set(clean_a)
    set_b = set(clean_b)
    
    intersection = set_a.intersection(set_b)
    if not intersection:
        return [], 0.0
    
    # Map back to original casing from list_a or list_b
    orig_map = {x.strip().lower(): x.strip() for x in list_a + list_b}
    shared_items = [orig_map[item] for item in intersection]
    
    # Jaccard / Overlap ratio relative to min set size for fair scoring
    union_size = max(len(set_a.union(set_b)), 1)
    overlap_ratio = len(intersection) / union_size
    
    return shared_items, min(1.0, overlap_ratio * 1.8)  # Boost moderate overlap

def _calculate_semantic_similarity(text_a: str, text_b: str) -> float:
    """Compute semantic similarity using sentence-transformers (0.0 to 1.0)."""
    if not text_a or not text_b:
        return 0.0
    
    model = _get_sentence_model()
    if model is None:
        return 0.0
    
    try:
        emb_a = model.encode(text_a, convert_to_tensor=True)
        emb_b = model.encode(text_b, convert_to_tensor=True)
        cos_sim = util.cos_sim(emb_a, emb_b).item()
        return max(0.0, min(1.0, cos_sim))
    except Exception:
        return 0.0

def get_collaboration_recommendations(
    db: Session,
    user_id: int,
    limit: int = 10,
    domain_filter: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Generate Part 7 Research Collaboration Recommendations for a given user_id.
    
    Determines compatible and complementary candidate researchers based on:
    - Domain Overlap (20%)
    - Technology Overlap (20%)
    - Research Interests Overlap (15%)
    - Keywords Overlap (10%)
    - Publication Topics Similarity (10%)
    - Patent / Innovation Similarity (10%)
    - Semantic Similarity (15%)
    """
    # 1. Load target researcher features
    target_features = researcher_feature_service.build_researcher_features(db, user_id)
    if not target_features:
        return None

    # 2. Query all candidate users excluding self
    candidate_users = db.query(User).filter(User.id != user_id).all()
    if not candidate_users:
        return {
            "user_id": user_id,
            "researcher": {
                "id": target_features["user_id"],
                "name": target_features["full_name"],
                "research_domains": target_features["research_domain"],
                "technology_areas": target_features["technology_areas"]
            },
            "total_candidates_evaluated": 0,
            "collaborators": []
        }

    collaborator_results = []

    for cand_user in candidate_users:
        cand_features = researcher_feature_service.build_researcher_features(db, cand_user.id)
        if not cand_features:
            continue
        
        # Apply domain filter if specified
        if domain_filter:
            cand_domains = [d.lower() for d in cand_features.get("research_domain", [])]
            if domain_filter.lower() not in cand_domains:
                continue

        # 3. Calculate dimension overlaps
        shared_domains, score_domain = _calculate_exact_set_overlap(
            target_features["research_domain"], cand_features["research_domain"]
        )
        shared_techs, score_tech = _calculate_exact_set_overlap(
            target_features["technology_areas"], cand_features["technology_areas"]
        )
        shared_interests, score_interests = _calculate_exact_set_overlap(
            target_features["research_interests"], cand_features["research_interests"]
        )
        shared_keywords, score_keywords = _calculate_exact_set_overlap(
            target_features["keywords"], cand_features["keywords"]
        )
        shared_pubs, score_pubs = _calculate_exact_set_overlap(
            target_features["publication_topics"], cand_features["publication_topics"]
        )
        shared_patents, score_patents = _calculate_exact_set_overlap(
            target_features["patent_domains"], cand_features["patent_domains"]
        )
        
        # 4. Semantic Similarity
        semantic_sim = _calculate_semantic_similarity(
            target_features["combined_research_text"],
            cand_features["combined_research_text"]
        )

        # 5. Composite Weighted Score (0 to 100)
        weighted_score = (
            (score_domain * 20.0) +
            (score_tech * 20.0) +
            (score_interests * 15.0) +
            (score_keywords * 10.0) +
            (score_pubs * 10.0) +
            (score_patents * 10.0) +
            (semantic_sim * 15.0)
        )
        
        final_score = int(round(max(0.0, min(100.0, weighted_score))))

        # 6. Identify Complementary Expertise (technologies/interests present in candidate but distinct from target)
        target_tech_set = set(t.lower() for t in target_features["technology_areas"])
        target_interest_set = set(i.lower() for i in target_features["research_interests"])
        
        comp_techs = [
            t for t in cand_features["technology_areas"]
            if t.lower() not in target_tech_set and t.lower() not in GENERIC_STOPWORDS
        ]
        comp_interests = [
            i for i in cand_features["research_interests"]
            if i.lower() not in target_interest_set and i.lower() not in GENERIC_STOPWORDS
        ]
        complementary_expertise = list(dict.fromkeys(comp_techs + comp_interests))[:4]

        # 7. Evidence Collection
        pub_evidence = [
            {"id": p["id"], "title": p["title"], "type": "publication"}
            for p in cand_features["publications_raw"][:3]
        ]
        pat_evidence = [
            {"id": pt["id"], "title": pt["title"], "type": "patent", "technology_domain": pt["technology_domain"]}
            for pt in cand_features["patents_raw"][:3]
        ]

        # 8. Category & Explanation
        if final_score >= 75:
            category = "Strong Collaboration"
        elif final_score >= 60:
            category = "Moderate Collaboration"
        elif final_score >= 45 or len(complementary_expertise) >= 2:
            category = "Complementary Focus"
        else:
            category = "Weak Overlap"

        explanation_parts = []
        if shared_domains:
            explanation_parts.append(f"shared domain expertise in {', '.join(shared_domains[:2])}")
        if shared_techs:
            explanation_parts.append(f"overlapping technology focus on {', '.join(shared_techs[:2])}")
        if complementary_expertise:
            explanation_parts.append(f"complementary capabilities in {', '.join(complementary_expertise[:2])}")
            
        if explanation_parts:
            explanation = f"Recommended based on {'; '.join(explanation_parts)}."
        else:
            explanation = f"Potential research alignment in general {cand_features['research_domain'][0] if cand_features['research_domain'] else 'technology'} area."

        collaborator_results.append({
            "researcher_id": cand_features["user_id"],
            "name": cand_features["full_name"],
            "email": cand_features["email"],
            "organization": cand_features["organization"],
            "designation": cand_features["designation"],
            "bio": cand_features["bio"],
            "score": final_score,
            "match_category": category,
            "shared_domains": shared_domains,
            "shared_technologies": shared_techs,
            "shared_interests": shared_interests,
            "shared_keywords": shared_keywords,
            "complementary_expertise": complementary_expertise,
            "publication_evidence": pub_evidence,
            "patent_evidence": pat_evidence,
            "explanation": explanation
        })

    # Sort collaborators: score descending, then evidence count, then researcher_id
    collaborator_results.sort(
        key=lambda x: (x["score"], len(x["shared_technologies"]) + len(x["shared_domains"]), -x["researcher_id"]),
        reverse=True
    )

    return {
        "user_id": user_id,
        "researcher": {
            "id": target_features["user_id"],
            "name": target_features["full_name"],
            "email": target_features["email"],
            "research_domains": target_features["research_domain"],
            "technology_areas": target_features["technology_areas"],
            "research_interests": target_features["research_interests"]
        },
        "total_candidates_evaluated": len(candidate_users),
        "collaborators": collaborator_results[:limit]
    }
