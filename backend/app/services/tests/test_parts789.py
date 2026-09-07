# backend/app/services/tests/test_parts789.py

from app.services.collaboration_service import (
    _filter_generic_words,
    _calculate_exact_set_overlap,
    _calculate_semantic_similarity
)
from app.services.patent_intelligence_service import _normalize_tech_name
from app.services.researcher_intelligence_service import _calculate_profile_completeness

def test_generic_stopwords_filtering():
    raw = ["Machine Learning", "research", "system", "Natural Language Processing", "data"]
    filtered = _filter_generic_words(raw)
    assert "Machine Learning" in filtered
    assert "Natural Language Processing" in filtered
    assert "research" not in filtered
    assert "system" not in filtered
    assert "data" not in filtered
    print("[PASS] test_generic_stopwords_filtering")

def test_exact_set_overlap_preserves_concepts():
    list_a = ["Artificial Intelligence", "Large Language Models", "Quantum Computing"]
    list_b = ["Large Language Models", "Quantum Computing", "Robotics"]
    
    shared, ratio = _calculate_exact_set_overlap(list_a, list_b)
    assert len(shared) == 2
    assert "Large Language Models" in shared
    assert "Quantum Computing" in shared
    assert ratio > 0.0
    print("[PASS] test_exact_set_overlap_preserves_concepts")

def test_profile_completeness_calculation():
    full_profile = {
        "research_domain": ["Artificial Intelligence"],
        "technology_areas": ["Machine Learning"],
        "research_interests": ["Deep Learning"],
        "keywords": ["AI"],
        "bio": "Experienced AI Researcher",
        "publication_count": 5,
        "patent_count": 2
    }
    result = _calculate_profile_completeness(full_profile)
    assert result["completeness_score"] == 100
    assert len(result["missing_fields"]) == 0

    partial_profile = {
        "research_domain": ["Artificial Intelligence"],
        "publication_count": 2
    }
    result_partial = _calculate_profile_completeness(partial_profile)
    assert result_partial["completeness_score"] < 100
    assert "technology_areas" in result_partial["missing_fields"]
    print("[PASS] test_profile_completeness_calculation")

def test_tech_normalization():
    assert _normalize_tech_name("  Natural Language Processing  ") == "Natural Language Processing"
    assert _normalize_tech_name(None) == "Uncategorized"
    print("[PASS] test_tech_normalization")

if __name__ == "__main__":
    test_generic_stopwords_filtering()
    test_exact_set_overlap_preserves_concepts()
    test_profile_completeness_calculation()
    test_tech_normalization()
    print("ALL UNIT TESTS FOR PARTS 7, 8, AND 9 PASSED!")
