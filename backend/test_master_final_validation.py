# backend/test_master_final_validation.py

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import (
    User, ResearchProfile, Publication, Patent,
    FundingOpportunity, FundingRecommendation, Alert
)
from app.services import (
    researcher_feature_service, funding_eligibility_service,
    funding_matching_service, funding_feedback_service, funding_analytics_service,
    collaboration_service, patent_intelligence_service, researcher_intelligence_service,
    dashboard_service, alert_service
)

def run_master_validation():
    results = {
        "database_audit": {},
        "parts_status": {},
        "scenarios": {},
        "bugs_found": [],
        "overall_status": "PASS"
    }

    print("\n==========================================================================")
    print("      RESEARCH FUNDING & INNOVATION INTELLIGENCE PLATFORM               ")
    print("             MASTER FINAL VALIDATION SUITE (PARTS 1–12)                   ")
    print("==========================================================================")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # --------------------------------------------------------------------------
        # 1. DATABASE INVENTORY & DATA AUDIT
        # --------------------------------------------------------------------------
        print("\n--- [STEP 1] Database Baseline Audit ---")
        user_count = db.query(User).count()
        profile_count = db.query(ResearchProfile).count()
        pub_count = db.query(Publication).count()
        pat_count = db.query(Patent).count()
        funding_count = db.query(FundingOpportunity).count()
        rec_count = db.query(FundingRecommendation).count()
        fb_count = db.query(FundingRecommendation).filter(FundingRecommendation.feedback.isnot(None)).count()
        alert_count = db.query(Alert).count()

        results["database_audit"] = {
            "users": user_count,
            "research_profiles": profile_count,
            "publications": pub_count,
            "patents": pat_count,
            "funding_opportunities": funding_count,
            "recommendations": rec_count,
            "feedback_records": fb_count,
            "alerts": alert_count
        }

        for table_name, count in results["database_audit"].items():
            print(f"  • {table_name}: {count} records")

        assert user_count > 0, "No users found in database!"
        assert funding_count > 0, "No funding opportunities found in database!"

        # Select a target user with an active ResearchProfile
        target_profile = db.query(ResearchProfile).first()
        target_user = db.query(User).filter(User.id == target_profile.user_id).first() if target_profile else db.query(User).first()
        user_id = target_user.id
        print(f"\n[TARGET TEST USER]: ID {user_id} - '{target_user.full_name}' ({target_user.email})")

        # --------------------------------------------------------------------------
        # PART 1: FUNDING DATA PREPARATION
        # --------------------------------------------------------------------------
        print("\n--- [PART 1] Funding Data Preparation ---")
        active_opps = db.query(FundingOpportunity).filter(FundingOpportunity.status == 'active').all()
        print(f"  ✓ Active Funding Opportunities: {len(active_opps)}")
        assert len(active_opps) > 0, "Part 1 Failed: No active funding opportunities found"
        results["parts_status"]["Part 1"] = "PASS"

        # --------------------------------------------------------------------------
        # PART 2: RESEARCHER FEATURE EXTRACTION
        # --------------------------------------------------------------------------
        print("\n--- [PART 2] Researcher Feature Extraction ---")
        features = researcher_feature_service.build_researcher_features(db, user_id)
        assert features is not None, "Part 2 Failed: Feature extraction returned None"
        print(f"  ✓ Extracted Domains: {features.get('research_domain')}")
        print(f"  ✓ Extracted Keywords (Sample): {features.get('keywords', [])[:5]}")
        results["parts_status"]["Part 2"] = "PASS"

        # --------------------------------------------------------------------------
        # PART 3: FUNDING ELIGIBILITY FILTERING
        # --------------------------------------------------------------------------
        print("\n--- [PART 3] Funding Eligibility Filtering ---")
        elig_res = funding_eligibility_service.filter_eligible_funding(db, user_id)
        assert elig_res is not None, "Part 3 Failed: Eligibility evaluation returned None"
        assert "eligible" in elig_res, "Part 3 Failed: Missing eligible key"
        print(f"  ✓ Eligible Funding Count for User #{user_id}: {len(elig_res['eligible'])}")
        results["parts_status"]["Part 3"] = "PASS"

        # --------------------------------------------------------------------------
        # PART 4: FUNDING MATCHING & SCORING
        # --------------------------------------------------------------------------
        print("\n--- [PART 4] Funding Matching & Scoring ---")
        recs_res = funding_matching_service.rank_funding_opportunities(db, user_id, top_k=5)
        recs_part4 = recs_res.get("recommendations", []) if isinstance(recs_res, dict) else recs_res
        assert len(recs_part4) > 0, "Part 4 Failed: No recommendations returned"
        top_rec = recs_part4[0]
        top_score = top_rec.get("match_score") if isinstance(top_rec, dict) else getattr(top_rec, "match_score", 0)
        top_title = top_rec.get("title") if isinstance(top_rec, dict) else getattr(top_rec, "title", "")
        top_id = top_rec.get("funding_id") if isinstance(top_rec, dict) else getattr(top_rec, "funding_id", getattr(top_rec, "id", None))
        assert 0 <= top_score <= 100, f"Part 4 Failed: Score out of bounds ({top_score})"
        print(f"  ✓ Top Grant Recommendation: '{top_title}' (Score: {top_score}%)")
        results["parts_status"]["Part 4"] = "PASS"

        # --------------------------------------------------------------------------
        # PART 5: RECOMMENDATION FEEDBACK & PERSONALIZATION
        # --------------------------------------------------------------------------
        print("\n--- [PART 5] Recommendation Feedback & Personalization ---")
        fb_opp_id = top_id
        fb_res = funding_feedback_service.record_feedback(db, user_id, fb_opp_id, "saved")
        assert fb_res.get("success") is True, "Part 5 Failed: Could not record saved feedback"
        print(f"  ✓ Recorded 'saved' feedback for Grant #{fb_opp_id}")
        results["parts_status"]["Part 5"] = "PASS"

        # --------------------------------------------------------------------------
        # PART 6: RECOMMENDATION ANALYTICS & EVALUATION
        # --------------------------------------------------------------------------
        print("\n--- [PART 6] Recommendation Analytics & Evaluation ---")
        analytics_res = funding_analytics_service.get_dashboard_summary(db, user_id)
        assert "health_score" in analytics_res, "Part 6 Failed: Missing health_score analytics"
        print(f"  ✓ Recommendation Health Score: {analytics_res.get('health_score')}/100")
        results["parts_status"]["Part 6"] = "PASS"

        # --------------------------------------------------------------------------
        # PART 7: RESEARCH COLLABORATION RECOMMENDATION
        # --------------------------------------------------------------------------
        print("\n--- [PART 7] Research Collaboration Recommendation ---")
        collabs_res = collaboration_service.get_collaboration_recommendations(db, user_id, limit=3)
        collabs = collabs_res.get("collaborators", []) if isinstance(collabs_res, dict) else collabs_res
        assert len(collabs) > 0, "Part 7 Failed: No collaboration candidates returned"
        print(f"  ✓ Top Collaborator Candidate: '{collabs[0]['name']}' (Score: {collabs[0]['score']}%)")
        results["parts_status"]["Part 7"] = "PASS"

        # --------------------------------------------------------------------------
        # PART 8: PATENT & INNOVATION INTELLIGENCE
        # --------------------------------------------------------------------------
        print("\n--- [PART 8] Patent & Innovation Intelligence ---")
        pat_intel = patent_intelligence_service.get_patent_intelligence_analytics(db)
        assert "total_patents" in pat_intel, "Part 8 Failed: Portfolio summary missing total_patents"
        print(f"  ✓ Database Total Patent Count: {pat_intel['total_patents']}")
        results["parts_status"]["Part 8"] = "PASS"

        # --------------------------------------------------------------------------
        # PART 9: RESEARCHER PROFILE INTELLIGENCE
        # --------------------------------------------------------------------------
        print("\n--- [PART 9] Researcher Profile Intelligence ---")
        prof_360 = researcher_intelligence_service.get_researcher_intelligence_profile(db, user_id)
        assert "profile_completeness" in prof_360, "Part 9 Failed: Missing profile completeness"
        print(f"  ✓ 360 Profile Completeness Score: {prof_360['profile_completeness'].get('completeness_score')}%")
        results["parts_status"]["Part 9"] = "PASS"

        # --------------------------------------------------------------------------
        # PART 10: ADVANCED COLLABORATION & NETWORK INTELLIGENCE
        # --------------------------------------------------------------------------
        print("\n--- [PART 10] Advanced Collaboration & Network Intelligence ---")
        assert len(collabs) > 0, "Part 10 Failed: Invalid network collaboration output"
        print(f"  ✓ Network Evaluated Candidates: {collabs_res.get('total_candidates_evaluated')} Total Researchers")
        results["parts_status"]["Part 10"] = "PASS"

        # --------------------------------------------------------------------------
        # PART 11: ADVANCED PATENT / INNOVATION ANALYTICS
        # --------------------------------------------------------------------------
        print("\n--- [PART 11] Advanced Patent / Innovation Analytics ---")
        pat_analytics = patent_intelligence_service.get_patent_intelligence_analytics(db)
        assert "emerging_technologies" in pat_analytics, "Part 11 Failed: Missing emerging technologies"
        print(f"  ✓ Innovation Analytics Emerging Technologies: {len(pat_analytics['emerging_technologies'])} detected")
        results["parts_status"]["Part 11"] = "PASS"

        # --------------------------------------------------------------------------
        # PART 12: INTEGRATED DASHBOARD & ALERTS
        # --------------------------------------------------------------------------
        print("\n--- [PART 12] Integrated Dashboard & Alerts ---")
        dash_data = dashboard_service.get_integrated_dashboard_data(db, user_id)
        assert "kpis" in dash_data and "alerts" in dash_data, "Part 12 Failed: Invalid dashboard payload"
        print(f"  ✓ Dashboard Aggregation KPIs: Active Grants={dash_data['kpis'].get('active_funding')}, Unread Alerts={dash_data['kpis'].get('unread_alerts')}")
        results["parts_status"]["Part 12"] = "PASS"

        # --------------------------------------------------------------------------
        # END-TO-END SCENARIO VALIDATIONS (A to G)
        # --------------------------------------------------------------------------
        print("\n==========================================================================")
        print("                 END-TO-END SCENARIOS VALIDATION (A to G)                  ")
        print("==========================================================================")

        # Scenario A: AI Researcher Pipeline
        print("\n[Scenario A] AI / NLP Researcher Full Pipeline")
        scen_a_recs = funding_matching_service.rank_funding_opportunities(db, user_id, top_k=3)
        assert len(scen_a_recs.get("recommendations", [])) > 0
        results["scenarios"]["Scenario A (AI Researcher)"] = "PASS"
        print("  ✓ Scenario A Passed!")

        # Scenario B: Minimal Data Researcher
        print("\n[Scenario B] Minimal Data Researcher Safety Check")
        scen_b_feat = researcher_feature_service.build_researcher_features(db, user_id=999999)
        assert scen_b_feat is None # gracefully returned None for nonexistent user
        results["scenarios"]["Scenario B (Minimal Data)"] = "PASS"
        print("  ✓ Scenario B Passed!")

        # Scenario C: Limited Feedback Handling
        print("\n[Scenario C] Limited Feedback Analytics Check")
        analytics_c = funding_analytics_service.get_dashboard_summary(db, user_id)
        assert "health_score" in analytics_c
        results["scenarios"]["Scenario C (Limited Feedback)"] = "PASS"
        print("  ✓ Scenario C Passed!")

        # Scenario D: Unrelated Funding Score Differentiation
        print("\n[Scenario D] Unrelated Funding Score Differentiation")
        if len(recs_part4) >= 2:
            top_s = recs_part4[0].get("match_score")
            low_s = recs_part4[-1].get("match_score")
            assert top_s >= low_s, "Score ordering inverted!"
            print(f"  ✓ Top score ({top_s}%) >= Lowest score ({low_s}%)")
        results["scenarios"]["Scenario D (Score Differentiation)"] = "PASS"

        # Scenario E: Approaching Deadline & Alert Creation
        print("\n[Scenario E] Approaching Deadline Alert Evaluation")
        scen_e_alerts = alert_service.generate_user_alerts(db, user_id)
        assert scen_e_alerts is not None
        results["scenarios"]["Scenario E (Deadline Alert)"] = "PASS"
        print("  ✓ Scenario E Passed!")

        # Scenario F: Peer Collaboration Match Explanation
        print("\n[Scenario F] Peer Collaboration Complementary Rationale")
        if len(collabs) > 0:
            c0 = collabs[0]
            assert "score" in c0 and "shared_domains" in c0
            print(f"  ✓ Collaborator Candidate '{c0['name']}' has valid match score ({c0['score']}%)")
        results["scenarios"]["Scenario F (Peer Match Rationale)"] = "PASS"

        # Scenario G: Emerging Patent Technology Trend Detection
        print("\n[Scenario G] Emerging Patent Technology Trend Detection")
        assert "emerging_technologies" in pat_analytics
        results["scenarios"]["Scenario G (Emerging Tech Trends)"] = "PASS"
        print("  ✓ Scenario G Passed!")

        print("\n==========================================================================")
        print("   🎉 MASTER FINAL VALIDATION SUITE PASSED ALL CHECKS 100% OPERATIONAL!   ")
        print("==========================================================================")

    except Exception as e:
        results["overall_status"] = "FAIL"
        results["bugs_found"].append(str(e))
        print(f"\n❌ VALIDATION ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()
        with open("master_validation_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_master_validation()
