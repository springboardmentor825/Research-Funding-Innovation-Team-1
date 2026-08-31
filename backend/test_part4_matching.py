# backend/test_part4_matching.py

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models import User, FundingOpportunity
from app.services import funding_matching_service, funding_eligibility_service

def test_part4_recommendations_and_integration():
    print("==================================================")
    print("      STARTING PART 4 MATCHING & SCORING TESTS    ")
    print("==================================================")
    
    db = SessionLocal()
    try:
        # 1. Test User 16 Recommendations
        print("\n--- 1. Testing Recommendations for User 16 (Dr. Sarah Jenkins - AI Researcher) ---")
        recs_data = funding_matching_service.rank_funding_opportunities(db, user_id=16, top_k=10)
        
        user_id = recs_data["user_id"]
        profile = recs_data["researcher_profile"]
        recommendations = recs_data["recommendations"]

        print(f"User ID: {user_id}")
        print(f"Researcher Profile Domain: {profile.get('research_domain')}")
        print(f"Researcher Tech Area:     {profile.get('technology_area')}")
        print(f"Total Recommendations Returned (top_k=10): {len(recommendations)}")
        
        assert len(recommendations) > 0, "No recommendations returned for User 16!"
        
        # 2. Check for Score Diversity (No Hardcoded 60s!)
        print("\n--- 2. Score Diversity & Ranking Verification ---")
        scores = [rec["match_score"] for rec in recommendations]
        print(f"Calculated Match Scores: {scores}")
        
        # Ensure scores are not all identical (e.g. not all 60)
        assert len(set(scores)) > 1, f"ERROR: All scores are identical! Scores: {scores}"
        assert all(isinstance(s, (int, float)) for s in scores)
        
        # Ensure sorted descending
        assert scores == sorted(scores, reverse=True), "ERROR: Recommendations are not sorted descending by match_score!"
        print("✓ Verified recommendations are sorted descending by score with diverse, dynamic values!")

        # 3. Check Match Breakdown, Signals & Explanations
        print("\n--- 3. Detailed Recommendation Breakdown & Evidence Signals ---")
        top_rec = recommendations[0]
        print(f"Top Recommended Grant: [{top_rec['funding_id']}] {top_rec['title']}")
        print(f"  - Match Score: {top_rec['match_score']}/100")
        print(f"  - Score Breakdown: {top_rec['match_breakdown']}")
        print(f"  - Matched Signals: {top_rec['matched_signals']}")
        print(f"  - Match Reason:    {top_rec['reason']}")
        
        assert "domain" in top_rec["match_breakdown"]
        assert "technology" in top_rec["match_breakdown"]
        assert len(top_rec["matched_signals"]) > 0
        assert len(top_rec["reason"]) > 10

        # 4. Check Exclusion of Expired & Closed Opportunities (Part 3 -> Part 4 Pipeline Verification)
        print("\n--- 4. Verification: Part 3 -> Part 4 Pipeline Integration ---")
        recommended_ids = {rec["funding_id"] for rec in recommendations}
        
        # Query expired or closed funding IDs from DB
        expired_closed_db_opps = db.query(FundingOpportunity).filter(
            (FundingOpportunity.status == "closed") | (FundingOpportunity.deadline < "2026-08-30")
        ).all()
        expired_closed_ids = {opp.id for opp in expired_closed_db_opps}
        
        intersection = recommended_ids.intersection(expired_closed_ids)
        print(f"Expired/Closed IDs in DB: {expired_closed_ids}")
        print(f"Expired/Closed IDs in Recommendations: {intersection}")
        assert len(intersection) == 0, f"ERROR: Expired or closed funding opportunities leaked into Part 4 recommendations! Leaked IDs: {intersection}"
        print("✓ Verified NO expired or closed funding opportunities reached Part 4 recommendations!")

        print("\n==================================================")
        print("  ALL PART 4 MATCHING & SCORING TESTS PASSED 100%! ")
        print("==================================================")

    finally:
        db.close()

if __name__ == "__main__":
    test_part4_recommendations_and_integration()
