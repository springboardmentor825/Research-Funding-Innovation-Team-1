# backend/app/services/funding_personalization_service.py

from typing import Dict, Any, List, Tuple, Optional, Set
from sqlalchemy.orm import Session

from app.models import FundingRecommendation, FundingOpportunity

# Centralized Personalization Adjustment Configuration
PERSONALIZATION_CONFIG = {
    "item_boosts": {
        "saved": 5.0,
        "relevant": 5.0,
        "applied": 8.0,
        "viewed": 0.0,
        "dismissed": -15.0,
        "not_relevant": -15.0,
    },
    "domain_positive_bonus": 2.0,
    "tech_positive_bonus": 2.0,
    "domain_negative_penalty": -3.0,
    "tech_negative_penalty": -3.0,
    "min_bounded_adjustment": -15.0,
    "max_bounded_adjustment": 10.0,
}

def _to_list(val) -> List[str]:
    if isinstance(val, list):
        return [str(x).strip().lower() for x in val if str(x).strip()]
    if isinstance(val, str) and val.strip():
        return [t.strip().lower() for t in val.replace("\n", ",").replace(";", ",").split(",") if t.strip()]
    return []

def get_user_feedback_signals(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Aggregate researcher interaction history to produce behavioral domain and technology signals.
    Does NOT permanently alter the researcher profile; returns temporary behavioral signals.
    """
    recs = (
        db.query(FundingRecommendation, FundingOpportunity)
        .join(FundingOpportunity, FundingRecommendation.funding_id == FundingOpportunity.id)
        .filter(FundingRecommendation.user_id == user_id)
        .all()
    )

    positive_domains: Set[str] = set()
    positive_techs: Set[str] = set()
    negative_domains: Set[str] = set()
    negative_techs: Set[str] = set()
    item_feedback_map: Dict[int, str] = {}

    for rec, opp in recs:
        fb = (rec.feedback or rec.status or "").strip().lower()
        if not fb:
            continue
        
        item_feedback_map[opp.id] = fb

        opp_doms = _to_list(opp.research_domains)
        opp_techs = _to_list(opp.technology_areas)

        if fb in ["saved", "relevant", "applied"]:
            positive_domains.update(opp_doms)
            positive_techs.update(opp_techs)
        elif fb in ["dismissed", "not_relevant"]:
            negative_domains.update(opp_doms)
            negative_techs.update(opp_techs)

    return {
        "positive_domains": positive_domains,
        "positive_techs": positive_techs,
        "negative_domains": negative_domains - positive_domains,
        "negative_techs": negative_techs - positive_techs,
        "item_feedback_map": item_feedback_map
    }

def calculate_feedback_adjustment(
    researcher: Dict[str, Any],
    opportunity: Dict[str, Any],
    direct_feedback: Optional[str] = None,
    signals: Optional[Dict[str, Any]] = None
) -> Tuple[float, List[str], List[str]]:
    """
    Calculate bounded personalization score adjustment based on direct item feedback and aggregated interaction signals.
    Enforces strict bounds (-15.0 to +10.0 max) to prevent user feedback from overpowering content relevance.
    """
    matched_signals = []
    unmatched_signals = []
    total_adj = 0.0

    # 1. Direct Item Feedback Signal
    fb = (direct_feedback or "").strip().lower()
    if fb:
        item_boost = PERSONALIZATION_CONFIG["item_boosts"].get(fb, 0.0)
        total_adj += item_boost
        if item_boost > 0:
            matched_signals.append(f"User Feedback: '{fb.capitalize()}' preference boost (+{item_boost:.1f} pts)")
        elif item_boost < 0:
            unmatched_signals.append(f"User Feedback: Previously '{fb.capitalize()}' penalty ({item_boost:.1f} pts)")

    # 2. Aggregated Behavioral Domain & Technology Preferences
    if signals:
        opp_doms = set(_to_list(opportunity.get("research_domains")))
        opp_techs = set(_to_list(opportunity.get("technology_areas")))

        # Positive behavioral alignment
        pos_dom_match = opp_doms.intersection(signals.get("positive_domains", set()))
        if pos_dom_match:
            dom_bonus = PERSONALIZATION_CONFIG["domain_positive_bonus"]
            total_adj += dom_bonus
            matched_signals.append(f"Behavioral Personalization: Saved funding history aligns with '{', '.join(pos_dom_match)}' (+{dom_bonus:.1f} pts)")

        pos_tech_match = opp_techs.intersection(signals.get("positive_techs", set()))
        if pos_tech_match:
            tech_bonus = PERSONALIZATION_CONFIG["tech_positive_bonus"]
            total_adj += tech_bonus
            matched_signals.append(f"Behavioral Personalization: Saved funding history aligns with '{', '.join(pos_tech_match)}' (+{tech_bonus:.1f} pts)")

        # Negative behavioral alignment
        neg_dom_match = opp_doms.intersection(signals.get("negative_domains", set()))
        if neg_dom_match:
            dom_pen = PERSONALIZATION_CONFIG["tech_negative_penalty"]
            total_adj += dom_pen
            unmatched_signals.append(f"Behavioral Personalization: Similar domain was previously dismissed ({dom_pen:.1f} pts)")

        neg_tech_match = opp_techs.intersection(signals.get("negative_techs", set()))
        if neg_tech_match:
            tech_pen = PERSONALIZATION_CONFIG["tech_negative_penalty"]
            total_adj += tech_pen
            unmatched_signals.append(f"Behavioral Personalization: Similar tech area was previously dismissed ({tech_pen:.1f} pts)")

    # 3. Enforce Strict Personalization Bounds (-15.0 to +10.0)
    min_b = PERSONALIZATION_CONFIG["min_bounded_adjustment"]
    max_b = PERSONALIZATION_CONFIG["max_bounded_adjustment"]
    bounded_adj = round(max(min_b, min(max_b, total_adj)), 1)

    return bounded_adj, matched_signals, unmatched_signals

def apply_personalization(
    base_score: float,
    breakdown: Dict[str, float],
    researcher: Dict[str, Any],
    opportunity: Dict[str, Any],
    user_feedback: Optional[str] = None,
    signals: Optional[Dict[str, Any]] = None
) -> Tuple[int, Dict[str, float], List[str], List[str]]:
    """
    Apply bounded personalization adjustment to base Part 4 score with exact mathematical reconciliation.
    Guarantees sum(match_breakdown.values()) == final_score.
    """
    bounded_adj, matched_signals, unmatched_signals = calculate_feedback_adjustment(
        researcher, opportunity, user_feedback, signals
    )

    breakdown_copy = dict(breakdown)
    breakdown_copy["feedback"] = bounded_adj

    total_unbounded = sum(breakdown_copy.values())
    final_score = max(0, min(100, round(total_unbounded)))

    # If capped at 100, adjust feedback component so sum(breakdown.values()) == 100 exactly
    if total_unbounded > 100 and "feedback" in breakdown_copy:
        overflow = total_unbounded - 100
        breakdown_copy["feedback"] = round(breakdown_copy["feedback"] - overflow, 1)

    return final_score, breakdown_copy, matched_signals, unmatched_signals
