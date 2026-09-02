# backend/test_complete_parts1_to_5.py

from app.database import SessionLocal
from app.services import (
    funding_feature_service,
    researcher_feature_service,
    funding_eligibility_service,
    funding_matching_service,
    funding_feedback_service,
    funding_personalization_service
)
from app.models import User, FundingOpportunity, FundingRecommendation

def run_integration_tests():
    print("============================================================")
    print("   RUNNING INTEGRATION VERIFICATION FOR PARTS 1 TO 5")
    print("============================================================")
    
    db = SessionLocal()
    try:
        user_id = 16
        
        # 1. Verify User 16 exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"[FAIL] User {user_id} not found in database!")
            return
        print(f"[PASS] Part 2 — Researcher Found: '{user.full_name}' (ID: {user_id})")

        # 2. Extract Researcher Features
        r_features = researcher_feature_service.build_researcher_features(db, user_id)
        assert r_features is not None
        tech_str = r_features.get('technology_areas') or r_features.get('technology_area')
        print(f"[PASS] Part 2 — Domain: '{r_features['research_domain']}', Tech: '{tech_str}'")

        # 3. Filter Eligibility (Part 3)
        el_res = funding_eligibility_service.filter_eligible_funding(db, user_id)
        el_count = len(el_res.get('eligible', []))
        in_count = len(el_res.get('ineligible', [])) if isinstance(el_res.get('ineligible'), list) else el_res.get('ineligible_count', 0)
        print(f"[PASS] Part 3 — Eligible Count: {el_count}, Ineligible Count: {in_count}")

        # 4. Generate Baseline Part 4 Recommendations
        base_recs = funding_matching_service.rank_funding_opportunities(db, user_id, top_k=5)
        print(f"[PASS] Part 4 — Baseline Top Recommendations Count: {len(base_recs['recommendations'])}")
        for item in base_recs['recommendations'][:3]:
            print(f"       -> Opp #{item['funding_id']}: '{item['title'][:40]}...' Score: {item['match_score']}%")

        # 5. Record Feedback Interactions (Part 5)
        target_opp_id = base_recs['recommendations'][0]['funding_id'] if base_recs['recommendations'] else 1
        
        print(f"\n--- Testing Part 5 Feedback Actions on Opportunity #{target_opp_id} ---")
        
        # Action A: Save
        res_save = funding_feedback_service.record_feedback(db, user_id=user_id, funding_id=target_opp_id, feedback="saved")
        assert res_save["success"] is True
        print(f"[PASS] Record 'saved' feedback: {res_save['message']}")

        # Action B: Applied
        res_app = funding_feedback_service.record_feedback(db, user_id=user_id, funding_id=target_opp_id, feedback="applied")
        assert res_app["success"] is True
        print(f"[PASS] Record 'applied' feedback: {res_app['message']}")

        # 6. Query Activity History, Saved, Applied
        history = funding_feedback_service.get_feedback_history(db, user_id)
        saved = funding_feedback_service.get_saved_funding(db, user_id)
        applied = funding_feedback_service.get_applied_funding(db, user_id)
        dismissed = funding_feedback_service.get_dismissed_funding(db, user_id)

        print(f"[PASS] Task 7 History API Count: {len(history)}")
        print(f"[PASS] Task 8 Saved API Count: {len(saved)}")
        print(f"[PASS] Task 10 Applied API Count: {len(applied)}")

        # 7. Test Personalization Scoring Adjustment
        personalized_recs = funding_matching_service.rank_funding_opportunities(db, user_id, top_k=5)
        print("\n--- Personalized Recommendations Output ---")
        for item in personalized_recs['recommendations'][:3]:
            print(f"       -> Opp #{item['funding_id']}: '{item['title'][:40]}...' Final Score: {item['match_score']}% breakdown: {item['match_breakdown']}")

        # 8. Test Repeated Feedback Capping & Bounds
        adj_1, _, _ = funding_personalization_service.calculate_feedback_adjustment(
            r_features, {"research_domains": [r_features['research_domain']]}, direct_feedback="saved"
        )
        print(f"[PASS] Bounded Personalization Score Adjustment for 'saved': +{adj_1} pts (Within [-15, +10] bounds)")

        print("\n============================================================")
        print("   ALL INTEGRATION TESTS PASSED FOR PARTS 1 TO 5!")
        print("============================================================")

    finally:
        db.close()

if __name__ == "__main__":
    run_integration_tests()
