# backend/app/services/tests/test_funding_personalization.py

from app.services.funding_personalization_service import (
    calculate_feedback_adjustment,
    apply_personalization,
    PERSONALIZATION_CONFIG
)
from app.schemas.funding_recommendation import FundingFeedbackRequest

def test_pydantic_schema_feedback_validation():
    """Verify that allowed feedback values pass and invalid feedback values raise ValueError."""
    for valid_fb in ["viewed", "saved", "relevant", "not_relevant", "dismissed", "applied"]:
        req = FundingFeedbackRequest(user_id=16, funding_id=5, feedback=valid_fb)
        assert req.feedback == valid_fb

    try:
        FundingFeedbackRequest(user_id=16, funding_id=5, feedback="invalid_action")
        assert False, "Should have raised ValueError for invalid feedback"
    except ValueError:
        pass

def test_direct_item_boost_saved():
    """Verify direct item feedback adjustment for 'saved' status."""
    res_prof = {"research_domain": "Artificial Intelligence", "technology_areas": ["NLP"]}
    opp = {"research_domains": ["Artificial Intelligence"], "technology_areas": ["NLP"]}
    
    adj, pos_s, neg_s = calculate_feedback_adjustment(res_prof, opp, direct_feedback="saved")
    assert adj == 5.0
    assert any("Saved" in s for s in pos_s)

def test_direct_item_boost_applied():
    """Verify direct item feedback adjustment for 'applied' status."""
    res_prof = {"research_domain": "Artificial Intelligence"}
    opp = {"research_domains": ["Artificial Intelligence"]}
    
    adj, pos_s, neg_s = calculate_feedback_adjustment(res_prof, opp, direct_feedback="applied")
    assert adj == 8.0
    assert any("Applied" in s for s in pos_s)

def test_direct_item_penalty_dismissed():
    """Verify direct item feedback penalty for 'dismissed' status."""
    res_prof = {"research_domain": "Agriculture"}
    opp = {"research_domains": ["Quantum Computing"]}
    
    adj, pos_s, neg_s = calculate_feedback_adjustment(res_prof, opp, direct_feedback="dismissed")
    assert adj == -15.0
    assert any("Dismissed" in s for s in neg_s)

def test_behavioral_signal_aggregation():
    """Verify behavioral domain and tech alignment boost when user has positive saved history."""
    res_prof = {"research_domain": "Computer Science"}
    opp = {"research_domains": ["Robotics"], "technology_areas": ["Autonomous Systems"]}
    
    signals = {
        "positive_domains": {"robotics"},
        "positive_techs": {"autonomous systems"},
        "negative_domains": set(),
        "negative_techs": set()
    }
    
    adj, pos_s, neg_s = calculate_feedback_adjustment(res_prof, opp, direct_feedback=None, signals=signals)
    # domain (+2) + tech (+2) = +4.0
    assert adj == 4.0
    assert len(pos_s) == 2

def test_bounded_adjustment_limits():
    """Verify that cumulative adjustments cannot exceed max (+10.0) or min (-15.0) bounds."""
    res_prof = {"research_domain": "AI"}
    opp = {"research_domains": ["AI"], "technology_areas": ["NLP"]}
    
    signals = {
        "positive_domains": {"ai"},
        "positive_techs": {"nlp"},
        "negative_domains": set(),
        "negative_techs": set()
    }
    
    # Applied (+8) + Domain (+2) + Tech (+2) = +12.0 raw -> Capped at +10.0
    adj, _, _ = calculate_feedback_adjustment(res_prof, opp, direct_feedback="applied", signals=signals)
    assert adj == PERSONALIZATION_CONFIG["max_bounded_adjustment"]
    assert adj == 10.0

def test_mathematical_reconciliation():
    """Verify exact mathematical reconciliation: sum(match_breakdown.values()) == final_score."""
    base_breakdown = {
        "domain": 30.0,
        "technology": 20.0,
        "interests": 15.0,
        "keywords": 10.0,
        "publications": 5.0,
        "patents": 0.0,
        "deadline": 4.0,
        "penalty": 0.0,
        "semantic": 12.0
    }
    res_prof = {"research_domain": "AI"}
    opp = {"research_domains": ["AI"]}
    
    final_score, breakdown, _, _ = apply_personalization(
        base_score=96.0,
        breakdown=base_breakdown,
        researcher=res_prof,
        opportunity=opp,
        user_feedback="saved"
    )
    
    assert "feedback" in breakdown
    assert breakdown["feedback"] == 4.0
    assert sum(breakdown.values()) == final_score
    assert final_score == 100 # Capped at 100
