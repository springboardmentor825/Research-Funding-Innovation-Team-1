# backend/verify_all_modules.py

import sys
import unittest
from app.database import SessionLocal
from app.models import User, ResearchProfile, FundingOpportunity, Publication, Patent
from app.services import (
    researcher_feature_service,
    funding_feature_service,
    funding_eligibility_service,
    funding_matching_service
)

def test_all_modules():
    print("==================================================")
    print("      COMPREHENSIVE ALL-MODULES VERIFICATION      ")
    print("==================================================\n")

    db = SessionLocal()

    # 1. Database & User 16 Verification
    user = db.query(User).filter(User.id == 16).first()
    assert user is not None, "User 16 does not exist in database"
    print(f"[PASSED] Module 0: User Database Record -> {user.full_name} ({user.email})")

    profile = db.query(ResearchProfile).filter(ResearchProfile.user_id == 16).first()
    assert profile is not None, "User 16 profile does not exist"
    print(f"[PASSED] Module 0: Research Profile -> Domain: {profile.research_domain} | Tech: {profile.technology_area}")

    # 2. Part 1: Funding Data Preparation & Feature Extraction
    funding_opps = db.query(FundingOpportunity).all()
    assert len(funding_opps) > 0, "No funding opportunities found in database"
    first_opp = funding_opps[0]
    opp_features = funding_feature_service.extract_funding_features(first_opp)
    assert "title" in opp_features, "Funding features missing title"
    print(f"[PASSED] Part 1: Funding Catalog -> Total Opportunities: {len(funding_opps)} | First: '{opp_features['title']}'")

    # 3. Part 2: Researcher Feature Extraction
    res_features = researcher_feature_service.build_researcher_features(db, 16)
    assert res_features is not None, "Researcher feature extraction returned None"
    assert len(res_features.get("publications_raw", [])) > 0, "No raw publications extracted"
    print(f"[PASSED] Part 2: Feature Extraction -> Pubs Raw Count: {len(res_features['publications_raw'])} | Patents Raw Count: {len(res_features['patents_raw'])}")

    # 4. Part 3: Eligibility Filtering
    eligibility_res = funding_eligibility_service.filter_eligible_funding(db, 16)
    eligible_list = eligibility_res.get("eligible", [])
    assert len(eligible_list) > 0, "Eligibility filtering returned 0 opportunities"
    print(f"[PASSED] Part 3: Eligibility Filtering -> Eligible Count: {len(eligible_list)} / {len(funding_opps)}")

    # 5. Part 4: Recommendation Engine & Mathematical Reconciliation
    rec_res = funding_matching_service.rank_funding_opportunities(db, user_id=16, top_k=10)
    recs = rec_res.get("recommendations", [])
    assert len(recs) > 0, "Recommendation engine returned 0 recommendations"

    math_ok = True
    for r in recs:
        bd = r["match_breakdown"]
        bd_sum = round(sum(bd.values()))
        if r["match_score"] != bd_sum:
            math_ok = False
            print(f"FAILED Math Reconciliation for {r['title']}: score {r['match_score']} != breakdown sum {bd_sum}")

    assert math_ok, "Score breakdown math reconciliation failed"
    top_rec = recs[0]
    print(f"[PASSED] Part 4: Recommendation Engine -> Top: '{top_rec['title']}' ({top_rec['match_score']}% [{top_rec['match_level']}])")
    print(f"         Pub Matches: {top_rec['publication_match_count']} | Pat Matches: {top_rec['patent_match_count']}")
    print(f"         Matched Signals: {top_rec['matched_signals']}")

    db.close()
    print("\n==================================================")
    print("      ALL MODULES VERIFIED & WORKING 100%         ")
    print("==================================================")

if __name__ == "__main__":
    test_all_modules()
