# backend/test_complete_parts7to9.py

from app.database import SessionLocal
from app.models import User, Patent, Publication
from app.services import (
    collaboration_service,
    patent_intelligence_service,
    researcher_intelligence_service
)

def run_parts7to9_integration_tests():
    db = SessionLocal()
    print("============================================================")
    print("   PARTS 7, 8 & 9 INTEGRATION VERIFICATION TEST SUITE       ")
    print("============================================================\n")

    test_user_id = 16
    test_user = db.query(User).filter(User.id == test_user_id).first()
    if not test_user:
        # Fallback to first available user in DB
        test_user = db.query(User).first()
        test_user_id = test_user.id if test_user else 1

    print(f"Testing against Target User ID: {test_user_id} ({test_user.full_name if test_user else 'Default'})\n")

    # ------------------------------------------------------------
    # 1. PART 7 — COLLABORATION RECOMMENDATION ENGINE
    # ------------------------------------------------------------
    print("--- 1. Testing Part 7 Collaboration Recommendations ---")
    collab_result = collaboration_service.get_collaboration_recommendations(db, user_id=test_user_id)
    assert collab_result is not None, "Part 7 collaboration returned None!"
    assert collab_result["user_id"] == test_user_id, "Target user_id mismatch!"
    
    collaborators = collab_result.get("collaborators", [])
    print(f"[OK] Evaluated {collab_result.get('total_candidates_evaluated')} candidates. Returned {len(collaborators)} top collaborators.")
    
    for c in collaborators:
        assert c["researcher_id"] != test_user_id, f"Self-exclusion failed! Target user {test_user_id} included in recommendations."
        assert 0 <= c["score"] <= 100, f"Collaboration score {c['score']} out of bounds!"
        assert c["explanation"] != "", "Explanation string is empty!"
        print(f"   -> Collaborator: {c['name']} (ID {c['researcher_id']}) | Score: {c['score']}/100 | Category: {c['match_category']}")
        print(f"      Shared Techs: {c['shared_technologies']} | Comp Expertise: {c['complementary_expertise']}")

    print("[PASS] Part 7 Collaboration Recommendation Engine Verified!\n")

    # ------------------------------------------------------------
    # 2. PART 8 — PATENT & INNOVATION INTELLIGENCE
    # ------------------------------------------------------------
    print("--- 2. Testing Part 8 Patent & Innovation Intelligence ---")
    patent_analytics = patent_intelligence_service.get_patent_intelligence_analytics(db)
    db_patent_count = db.query(Patent).count()
    
    assert patent_analytics["total_patents"] == db_patent_count, f"Patent count mismatch! DB: {db_patent_count}, Analytics: {patent_analytics['total_patents']}"
    assert patent_analytics["active_patents"] + patent_analytics["expired_patents"] == db_patent_count, "Active + Expired does not equal Total patents!"
    
    print(f"[OK] Total DB Patents: {patent_analytics['total_patents']} (Active: {patent_analytics['active_patents']}, Expired: {patent_analytics['expired_patents']})")
    print(f"[OK] Top Technology Distributions: {[t['technology'] for t in patent_analytics['technology_distribution'][:3]]}")
    print(f"[OK] Emerging Technologies Detected: {[e['technology'] for e in patent_analytics['emerging_technologies']]}")

    # Test single patent detail intelligence
    sample_patent = db.query(Patent).first()
    if sample_patent:
        detail = patent_intelligence_service.get_patent_detail_intelligence(db, sample_patent.patent_id)
        assert detail is not None, "Patent detail intelligence returned None!"
        assert 0 <= detail["innovation_score"] <= 100, "Patent innovation score out of bounds!"
        print(f"[OK] Sample Patent Detail (ID {sample_patent.patent_id}): '{detail['title'][:40]}...' | Innovation Score: {detail['innovation_score']}/100")

    print("[PASS] Part 8 Patent & Innovation Intelligence Verified!\n")

    # ------------------------------------------------------------
    # 3. PART 9 — RESEARCHER PROFILE INTELLIGENCE
    # ------------------------------------------------------------
    print("--- 3. Testing Part 9 Researcher Profile Intelligence ---")
    profile_intel = researcher_intelligence_service.get_researcher_intelligence_profile(db, user_id=test_user_id)
    assert profile_intel is not None, "Researcher Profile Intelligence returned None!"
    
    db_pub_count = db.query(Publication).filter(Publication.user_id == test_user_id).count()
    db_pat_count = db.query(Patent).filter(Patent.user_id == test_user_id).count()

    assert profile_intel["publication_count"] == db_pub_count, f"Publication count mismatch! DB: {db_pub_count}, Profile: {profile_intel['publication_count']}"
    assert profile_intel["patent_count"] == db_pat_count, f"Patent count mismatch! DB: {db_pat_count}, Profile: {profile_intel['patent_count']}"
    assert 0 <= profile_intel["profile_completeness"]["completeness_score"] <= 100, "Completeness score out of bounds!"

    print(f"[OK] Researcher Profile: {profile_intel['name']} ({profile_intel['organization']})")
    print(f"[OK] Completeness Score: {profile_intel['profile_completeness']['completeness_score']}/100 (Missing: {profile_intel['profile_completeness']['missing_fields']})")
    print(f"[OK] Research Activity Score: {profile_intel['research_activity_score']}/100")
    print(f"[OK] Funding Intelligence: {profile_intel['funding_intelligence']['strong_funding_matches']} strong matches, Avg Score: {profile_intel['funding_intelligence']['average_match_score']}")

    # Test Researcher Comparison
    cand_users = db.query(User).filter(User.id != test_user_id).all()
    if cand_users:
        user2_id = cand_users[0].id
        comp = researcher_intelligence_service.get_researcher_comparison(db, test_user_id, user2_id)
        assert comp is not None, "Researcher comparison returned None!"
        print(f"[OK] Researcher Comparison: User {test_user_id} vs User {user2_id} | Shared Techs: {comp['shared_technologies']}")

    print("[PASS] Part 9 Researcher Profile Intelligence Verified!\n")

    db.close()
    print("============================================================")
    print("   ALL PARTS 7, 8 & 9 INTEGRATION VERIFICATION CHECKS PASSED!")
    print("============================================================")

if __name__ == "__main__":
    run_parts7to9_integration_tests()
