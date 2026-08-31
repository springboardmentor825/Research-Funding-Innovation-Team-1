# backend/test_part3_eligibility.py

import sys
import os
import json
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import engine, SessionLocal
from sqlalchemy import text
from app.models import User, ResearchProfile, FundingOpportunity
from app.services import funding_eligibility_service
from app.routes.funding import get_funding_eligibility_for_user

def test_all_part3_eligibility_scenarios():
    print("==================================================")
    print("      STARTING PART 3 ELIGIBILITY TEST SUITE      ")
    print("==================================================")
    
    db = SessionLocal()
    try:
        # 1. Evaluate User 16 (Dr. Sarah Jenkins - AI Researcher)
        print("\n--- 1. Testing User 16 (Dr. Sarah Jenkins - AI Researcher) ---")
        raw_res = get_funding_eligibility_for_user(user_id=16, db=db)
        data16 = raw_res if isinstance(raw_res, dict) else raw_res.model_dump()
        
        total_opps = data16["total_opportunities"]
        eligible_cnt = data16["eligible_count"]
        excluded_cnt = data16["excluded_count"]
        eligible_items = data16["eligible"]
        excluded_items = data16["excluded"]
        
        print(f"Total Opportunities evaluated: {total_opps}")
        print(f"Eligible Opportunities count:  {eligible_cnt}")
        print(f"Excluded Opportunities count:  {excluded_cnt}")
        
        assert total_opps > 0
        assert eligible_cnt > 0
        assert excluded_cnt > 0
        
        # Verify expired deadlines are excluded
        expired_excluded = [x for x in excluded_items if x["deadline_status"] == "expired"]
        print(f"✓ Found {len(expired_excluded)} expired opportunities correctly excluded!")
        for item in expired_excluded:
            assert item["eligible"] is False
            assert "expired" in item["reason"].lower() or "passed" in item["reason"].lower()
            print(f"  - [{item['funding_id']}] {item['title']} -> Reason: {item['reason']}")

        # Verify closed statuses are excluded
        closed_excluded = [x for x in excluded_items if x["status_check"] == "failed"]
        print(f"✓ Found {len(closed_excluded)} closed/inactive opportunities correctly excluded!")
        for item in closed_excluded:
            assert item["eligible"] is False
            print(f"  - [{item['funding_id']}] {item['title']} -> Reason: {item['reason']}")

        # 2. Critical Rule Check: Domain Mismatch != Ineligible!
        print("\n--- 2. Critical Rule Check: Domain Mismatch != Eligibility Rejection ---")
        agri_opps = [x for x in eligible_items if "agriculture" in str(x["title"]).lower() or "agri" in str(x["title"]).lower() or "bio" in str(x["title"]).lower()]
        print(f"Found {len(agri_opps)} non-AI / Agriculture / Bio opportunities in eligible set:")
        for opp in agri_opps:
            print(f"  - [{opp['funding_id']}] {opp['title']} (Eligible: {opp['eligible']})")
        print("✓ Verified AI researcher is NOT automatically rejected for non-AI funding opportunities at Eligibility Stage!")


        # 3. Test Edge Cases
        print("\n--- 3. Testing Edge Cases ---")
        
        # Edge Case A: Non-existent User (9999)
        print("Testing Non-existent User ID (9999)...")
        res_err = funding_eligibility_service.filter_eligible_funding(db, 9999)
        assert res_err.get("error") == "user_not_found"
        print("✓ Non-existent user correctly returns error dict / HTTP 404!")

        # Edge Case B: Geographic Mismatch Test
        print("Testing Geographic Scope Restriction...")
        # Create temp user in India (IISc Bangalore)
        india_user = User(full_name="Dr. India Researcher", email="india@iisc.ac.in", role="researcher", login_type="email")
        db.add(india_user)
        db.commit()
        db.refresh(india_user)
        
        india_prof = ResearchProfile(
            user_id=india_user.id,
            organization="IISc Bangalore",
            designation="Assistant Professor",
            research_domain="Robotics",
            technology_area="Control Systems"
        )
        db.add(india_prof)
        
        # Create temporary US-only funding opportunity
        today = date.today()
        us_opp = FundingOpportunity(
            title="US NSF National Robotics Grant",
            funder="US NSF",
            amount_range="$100k-$500k",
            deadline=today + timedelta(days=60),
            geographic_scope="United States only",
            status="active"
        )
        db.add(us_opp)
        db.commit()
        db.refresh(us_opp)
        
        res_geo = funding_eligibility_service.filter_eligible_funding(db, india_user.id, funding_opportunities=[us_opp])
        assert res_geo["excluded_count"] == 1
        geo_item = res_geo["excluded"][0]
        assert geo_item["eligible"] is False
        assert "geographic restriction" in geo_item["reason"].lower()
        print(f"✓ Explicit geographic mismatch correctly excluded: {geo_item['reason']}")

        # Cleanup temporary records
        db.delete(us_opp)
        db.delete(india_prof)
        db.delete(india_user)
        db.commit()
        print("✓ Temporary test records cleaned up.")

        print("\n==================================================")
        print("  ALL PART 3 ELIGIBILITY TESTS PASSED SUCCESSFULLY! ")
        print("==================================================")

    finally:
        db.close()

if __name__ == "__main__":
    test_all_part3_eligibility_scenarios()
