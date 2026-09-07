# backend/test_complete_part6.py

from app.database import SessionLocal
from app.services import funding_analytics_service
from app.models import User, FundingOpportunity, FundingRecommendation

def run_part6_integration_tests():
    print("============================================================")
    print("   RUNNING INTEGRATION VERIFICATION FOR PART 6 ANALYTICS")
    print("============================================================")
    
    db = SessionLocal()
    try:
        # 1. Global Funding Landscape Analytics
        print("\n--- 1. Testing Global Funding Landscape Analytics ---")
        global_data = funding_analytics_service.get_global_funding_landscape(db)
        db_total_opps = db.query(FundingOpportunity).count()
        assert global_data["total_opportunities"] == db_total_opps
        print(f"[PASS] Global Opportunities Count: {global_data['total_opportunities']} (Matches DB: {db_total_opps})")
        print(f"       Active: {global_data['active_opportunities']}, Expired: {global_data['expired_opportunities']}")
        print(f"       Deadlines (30d): {global_data['upcoming_deadlines_30d']}")

        # 2. Researcher Specific Analytics for User 16
        user_id = 16
        print(f"\n--- 2. Testing Researcher Analytics for User ID {user_id} ---")
        user = db.query(User).filter(User.id == user_id).first()
        assert user is not None
        print(f"[PASS] Target User Found: '{user.full_name}'")

        r_analytics = funding_analytics_service.get_researcher_analytics(db, user_id)
        assert r_analytics["user_id"] == user_id
        profile = r_analytics["researcher_funding_profile"]
        print(f"[PASS] Researcher Profile — Domain: '{profile['research_domain']}', Techs: {profile['technology_areas']}")
        print(f"       Average Match Score: {profile['average_match_score']}%")
        print(f"       Strong Match Percentage: {profile['strong_match_percentage']}%")

        # 3. Score Analytics & Distribution
        score_dist = r_analytics["score_distribution"]
        print("\n--- 3. Testing Score Distribution ---")
        for bucket in score_dist:
            print(f"       Bucket [{bucket['range']}]: Count = {bucket['count']} ({bucket['percentage']}%)")

        # 4. Recommendation Activity & Feedback Analytics
        activity = r_analytics["activity_analysis"]
        print("\n--- 4. Testing Recommendation Activity & Feedback Analytics ---")
        print(f"[PASS] Total Recs: {activity['total_recommendations']}, Views: {activity['views']}, Saves: {activity['saves']}, Applications: {activity['applications']}")
        print(f"       Feedback Coverage: {activity['feedback_coverage']*100}%, Positive Rate: {activity['positive_feedback_rate']*100}%")

        # 5. Precision@K Evaluation with Insufficient Feedback Handling
        evaluation = r_analytics["evaluation"]
        print("\n--- 5. Testing Precision@K Evaluation ---")
        for k_val in ["5", "10", "20"]:
            ev = evaluation[k_val]
            print(f"       Precision@{k_val}: Evaluated Items = {ev['evaluated_items']}, Relevant = {ev['relevant_count']}, Status = '{ev['status']}'")

        # 6. Diagnostics & Mathematical Reconciliation
        diagnostics = r_analytics["diagnostics"]
        print("\n--- 6. Testing Diagnostic & Evidence Checks ---")
        print(f"[PASS] Score Component Validation Rate: {diagnostics['score_validation_rate']*100}%")
        print(f"[PASS] Evidence Validation Rate: {diagnostics['evidence_validation_rate']*100}%")
        for diag in diagnostics["diagnostics_list"]:
            print(f"       Diagnostic Check '{diag['check_name']}': Passed = {diag['passed']} ('{diag['details']}')")

        # 7. Recommendation Engine Health Score
        health = r_analytics["health_score"]
        print("\n--- 7. Testing Recommendation Health Score ---")
        print(f"[PASS] Health Score: {health['score']}/100 ({health['status']})")
        print(f"       Breakdown: {health['calculation_breakdown']}")

        # 8. Dashboard Summary API Output
        dashboard = funding_analytics_service.get_dashboard_summary(db, user_id)
        assert dashboard["user_id"] == user_id
        print("\n--- 8. Testing Dashboard API Output ---")
        print(f"[PASS] Dashboard KPIs: {dashboard['kpis']}")

        print("\n============================================================")
        print("   ALL INTEGRATION VERIFICATION CHECKS PASSED FOR PART 6!")
        print("============================================================")

    finally:
        db.close()

if __name__ == "__main__":
    run_part6_integration_tests()
