# backend/audit_complete_parts1_to_4.py

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal, engine
from sqlalchemy import text
from app.models import User, ResearchProfile, Publication, Patent, FundingOpportunity
from app.services import researcher_feature_service, funding_eligibility_service, funding_matching_service

def run_full_validation_audit():
    print("==========================================================================")
    print("      MILESTONE 3: COMPLETE VALIDATION AUDIT (PARTS 1, 2, 3, AND 4)      ")
    print("==========================================================================")

    db = SessionLocal()
    try:
        # ----------------------------------------------------------------------
        # PART 1 AUDIT: Funding Data Preparation
        # ----------------------------------------------------------------------
        print("\n[PART 1 AUDIT] Checking MySQL Funding Opportunities Schema & Records...")
        
        with engine.connect() as conn:
            columns_res = conn.execute(text("DESCRIBE funding_opportunities;")).fetchall()
            col_names = [col[0] for col in columns_res]
            print(f"✓ MySQL Columns detected ({len(col_names)}): {', '.join(col_names)}")

        total_opps = db.query(FundingOpportunity).count()
        active_opps = db.query(FundingOpportunity).filter(FundingOpportunity.status == "active").count()
        closed_opps = db.query(FundingOpportunity).filter(FundingOpportunity.status == "closed").count()
        draft_opps = db.query(FundingOpportunity).filter(FundingOpportunity.status == "draft").count()

        print(f"Total Funding Opportunities: {total_opps}")
        print(f"  - Active Status: {active_opps}")
        print(f"  - Closed Status: {closed_opps}")
        print(f"  - Draft Status:  {draft_opps}")

        assert total_opps >= 25, "ERROR: Insufficient funding records!"
        assert "research_domains" in col_names and "technology_areas" in col_names
        print("✓ PART 1 AUDIT: PASS")

        # ----------------------------------------------------------------------
        # PART 2 AUDIT: Researcher Feature Extraction
        # ----------------------------------------------------------------------
        print("\n[PART 2 AUDIT] Checking Researcher Feature Extraction for User 16...")
        feat16 = researcher_feature_service.build_researcher_features(db, 16)
        
        print(f"User ID: {feat16.get('user_id')}")
        print(f"Research Domain: {feat16.get('research_domain')}")
        print(f"Technology Area: {feat16.get('technology_area')}")
        print(f"Keywords ({len(feat16.get('keywords', []))}): {feat16.get('keywords', [])[:5]}")
        print(f"Publications Count: {feat16.get('publication_count')}")
        print(f"Patents Count:      {feat16.get('patent_count')}")

        assert feat16.get("user_id") == 16
        assert feat16.get("research_domain") != "General"
        assert feat16.get("publication_count") > 0
        assert feat16.get("patent_count") > 0
        print("✓ PART 2 AUDIT: PASS")

        # ----------------------------------------------------------------------
        # PART 3 AUDIT: Eligibility Filtering
        # ----------------------------------------------------------------------
        print("\n[PART 3 AUDIT] Checking Eligibility Filtering for User 16...")
        el_res = funding_eligibility_service.filter_eligible_funding(db, 16)
        
        tot_opps = el_res.get("total_opportunities")
        el_cnt = el_res.get("eligible_count")
        ex_cnt = el_res.get("excluded_count")
        
        print(f"Evaluated Opportunities: {tot_opps}")
        print(f"  - Eligible Count: {el_cnt}")
        print(f"  - Excluded Count: {ex_cnt}")

        assert tot_opps == total_opps
        assert el_cnt > 0 and ex_cnt > 0
        
        # Verify reasons in excluded opportunities
        for ex_item in el_res.get("excluded", []):
            assert ex_item["eligible"] is False
            assert len(ex_item["reason"]) > 5
        print("✓ PART 3 AUDIT: PASS")

        # ----------------------------------------------------------------------
        # PART 4 AUDIT: Matching, Scoring, and Recommendation Engine
        # ----------------------------------------------------------------------
        print("\n[PART 4 AUDIT] Checking Matching, Scoring & Recommendations for User 16...")
        recs_res = funding_matching_service.rank_funding_opportunities(db, user_id=16, top_k=10)
        recs = recs_res.get("recommendations", [])
        
        print(f"Total Recommendations Returned: {len(recs)}")
        scores = [r["match_score"] for r in recs]
        print(f"Dynamic Calculated Match Scores: {scores}")

        assert len(recs) > 0
        assert len(set(scores)) > 1, "Scores must be dynamic, not all 60!"
        assert scores == sorted(scores, reverse=True), "Scores must be sorted descending!"
        
        top_grant = recs[0]
        print(f"Top Recommendation: [{top_grant['funding_id']}] {top_grant['title']} (Score: {top_grant['match_score']})")
        print(f"  - Breakdown: {top_grant['match_breakdown']}")
        print(f"  - Signals:   {top_grant['matched_signals']}")
        print(f"  - Reason:    {top_grant['reason']}")

        assert "domain" in top_grant["match_breakdown"]
        assert len(top_grant["matched_signals"]) > 0
        assert len(top_grant["reason"]) > 10
        print("✓ PART 4 AUDIT: PASS")

        # ----------------------------------------------------------------------
        # INTEGRATION AUDIT: Part 1 -> Part 2 -> Part 3 -> Part 4 Pipeline
        # ----------------------------------------------------------------------
        print("\n[INTEGRATION AUDIT] Verifying End-to-End Pipeline Integrity...")
        rec_ids = {r["funding_id"] for r in recs}
        ex_ids = {r["funding_id"] for r in el_res.get("excluded", [])}
        
        leaks = rec_ids.intersection(ex_ids)
        assert len(leaks) == 0, f"Leakage detected! Excluded IDs {leaks} appeared in Part 4 recommendations."
        print("✓ INTEGRATION AUDIT: PASS (0 Leakage of Expired/Closed records into Part 4 Recommendations)")

        print("\n==========================================================================")
        print("    ALL VALIDATION AUDITS PASSED 100% (PARTS 1, 2, 3 & 4 OPERATIONAL)     ")
        print("==========================================================================")

    finally:
        db.close()

if __name__ == "__main__":
    run_full_validation_audit()
