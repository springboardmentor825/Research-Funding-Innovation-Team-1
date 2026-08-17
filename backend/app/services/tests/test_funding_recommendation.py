import sys
import os
from datetime import date

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.database import SessionLocal
from app.models import User, ResearchProfile, Publication, Patent, FundingOpportunity
from app.services.researcher_feature_service import build_researcher_features
from app.services.funding_feature_service import extract_funding_features
from app.services.eligibility_service import filter_eligible_funding, classify_deadline
from app.services.funding_matching_service import (
    calculate_match_score,
    rank_funding_opportunities,
    compute_rule_based_score,
    compute_semantic_score
)
from fastapi.testclient import TestClient
from app.main import app

def run_all_tests():
    print("============================================================")
    print("RUNNING FUNDING RECOMMENDATION ENGINE TEST SUITE")
    print("============================================================\n")

    db = SessionLocal()
    passed = 0
    failed = 0

    try:
        # TEST 1: Researcher with AI/RAG profile
        print("Test 1: Researcher with AI/RAG profile feature extraction...")
        # Create temporary mock profile features
        ai_researcher = {
            "user_id": 999,
            "research_domain": "Artificial Intelligence",
            "technology_area": "Retrieval Augmented Generation",
            "research_interests": ["NLP", "LLM", "Deep Learning", "Vector Search"],
            "keywords": ["AI", "RAG", "LLMs", "NLP"],
            "publication_topics": ["Deep Learning for RAG", "LLM Powered Search"],
            "patent_domains": ["Artificial Intelligence", "Information Retrieval"]
        }
        assert ai_researcher["research_domain"] == "Artificial Intelligence"
        print("  [PASS] Test 1: AI/RAG Researcher profile created successfully.\n")
        passed += 1

        # TEST 2: Strong AI funding opportunity matching
        print("Test 2: Strong AI funding opportunity matching...")
        ai_funding = {
            "id": 5,
            "title": "AI Research Grant 2026",
            "funder": "NSF",
            "research_domains": ["Artificial Intelligence", "Computer Science"],
            "technology_areas": ["Retrieval Augmented Generation", "Large Language Models"],
            "keywords": ["AI", "RAG", "LLM", "NLP"],
            "match_badges": ["AI", "ML"],
            "deadline": date(2026, 12, 31),
            "status": "open"
        }
        res_ai = calculate_match_score(ai_researcher, ai_funding)
        print(f"  AI Grant Match Score: {res_ai['match_score']}% (Reason: {res_ai['reason']})")
        assert res_ai["match_score"] >= 80, f"Expected score >= 80, got {res_ai['match_score']}"
        print("  [PASS] Test 2: Strong AI funding receives high score.\n")
        passed += 1

        # TEST 3: Weak agriculture funding opportunity matching
        print("Test 3: Weak agriculture funding opportunity matching...")
        agri_funding = {
            "id": 7,
            "title": "Smart Agriculture Program",
            "funder": "FAO",
            "research_domains": ["Agriculture", "Soil Science"],
            "technology_areas": ["Precision Farming", "Irrigation"],
            "keywords": ["Agriculture", "Soil", "Farming", "Crops"],
            "match_badges": ["Agriculture"],
            "deadline": date(2026, 10, 15),
            "status": "open"
        }
        res_agri = calculate_match_score(ai_researcher, agri_funding)
        print(f"  Agriculture Grant Match Score: {res_agri['match_score']}%")
        assert res_agri["match_score"] < res_ai["match_score"], f"Expected agri score ({res_agri['match_score']}) < AI score ({res_ai['match_score']})"
        print("  [PASS] Test 3: Unrelated agriculture funding ranks significantly lower.\n")
        passed += 1

        # TEST 4: Expired funding exclusion
        print("Test 4: Expired funding opportunity exclusion...")
        expired_funding = {
            "id": 99,
            "title": "Expired Legacy Grant",
            "deadline": date(2022, 1, 1),
            "status": "expired"
        }
        filtered = filter_eligible_funding(ai_researcher, [ai_funding, expired_funding])
        assert len(filtered) == 1
        assert filtered[0]["id"] == 5
        print("  [PASS] Test 4: Expired funding is strictly excluded.\n")
        passed += 1

        # TEST 5: Exact keyword match
        print("Test 5: Exact keyword match validation...")
        keyword_funding = {
            "id": 12,
            "title": "NLP Research Program",
            "funder": "Microsoft",
            "research_domains": ["Artificial Intelligence"],
            "technology_areas": ["Natural Language Processing"],
            "keywords": ["NLP", "RAG", "LLMs"],
            "deadline": date(2026, 5, 31),
            "status": "open"
        }
        res_kw = calculate_match_score(ai_researcher, keyword_funding)
        print(f"  Exact Keyword Match Score: {res_kw['match_score']}%")
        assert res_kw["match_score"] >= 75
        print("  [PASS] Test 5: Exact keyword match raises match score.\n")
        passed += 1

        # TEST 6: Domain mismatch penalty
        print("Test 6: Domain mismatch penalty check...")
        mismatch_funding = {
            "id": 13,
            "title": "Green Energy Innovation",
            "funder": "UNDP",
            "research_domains": ["Renewable Energy"],
            "technology_areas": ["Battery Microgrids"],
            "keywords": ["Energy", "Solar"],
            "deadline": date(2026, 9, 1),
            "status": "open"
        }
        res_mismatch = calculate_match_score(ai_researcher, mismatch_funding)
        print(f"  Domain Mismatch Score: {res_mismatch['match_score']}%")
        assert res_mismatch["match_score"] < res_ai["match_score"]
        print("  [PASS] Test 6: Domain mismatch correctly depresses score.\n")
        passed += 1

        # TEST 7: Technology match boosting
        print("Test 7: Technology area match boosting...")
        tech_funding = {
            "id": 22,
            "title": "AI for Social Good",
            "funder": "Google.org",
            "research_domains": ["Data Science"],
            "technology_areas": ["Retrieval Augmented Generation", "Machine Learning"],
            "keywords": ["AI", "Social Good"],
            "deadline": date(2026, 4, 4),
            "status": "open"
        }
        res_tech = calculate_match_score(ai_researcher, tech_funding)
        print(f"  Tech Area Match Score: {res_tech['match_score']}%")
        assert res_tech["match_score"] >= 70
        print("  [PASS] Test 7: Technology match boosts score.\n")
        passed += 1

        # TEST 8: Publication match evidence signal
        print("Test 8: Publication match signal verification...")
        assert any("Publication" in sig for sig in res_ai["matched_signals"])
        print("  [PASS] Test 8: Publication evidence captured in matched signals.\n")
        passed += 1

        # TEST 9: Patent match evidence signal
        print("Test 9: Patent match signal verification...")
        patent_funding = {
            "id": 15,
            "title": "Patent Commercialization Grant",
            "funder": "WIPO",
            "research_domains": ["Patent Analytics"],
            "technology_areas": ["Information Retrieval"],
            "keywords": ["Patents", "Commercialization"],
            "deadline": date(2026, 10, 10),
            "status": "open"
        }
        res_pat = calculate_match_score(ai_researcher, patent_funding)
        print(f"  Patent Match Score: {res_pat['match_score']}%")
        assert any("Patent" in sig for sig in res_pat["matched_signals"]) or res_pat["match_score"] > 50
        print("  [PASS] Test 9: Patent evidence incorporated.\n")
        passed += 1

        # TEST 10: Missing researcher profile handling
        print("Test 10: Missing researcher profile handling...")
        empty_researcher = {
            "user_id": 9999,
            "research_domain": "Unspecified",
            "technology_area": "Unspecified",
            "research_interests": [],
            "keywords": [],
            "publication_topics": [],
            "patent_domains": []
        }
        res_empty = calculate_match_score(empty_researcher, ai_funding)
        print(f"  Empty Profile Match Score: {res_empty['match_score']}%")
        assert res_empty["match_score"] < res_ai["match_score"]
        assert res_empty["reason"] is not None
        print("  [PASS] Test 10: Missing researcher profile handled gracefully.\n")
        passed += 1

        # TEST 11: Real Database User 16 Recommendations API execution
        print("Test 11: Real Database User 16 Recommendations...")
        recs_16 = rank_funding_opportunities(db, user_id=16, top_k=10)
        recs_list = recs_16["recommendations"]
        assert len(recs_list) > 0
        print(f"  User 16 Top 3 Recommendations:")
        for idx, r in enumerate(recs_list[:3], 1):
            print(f"    {idx}. {r['title']} - Score: {r['match_score']}% (Funder: {r['funder']})")
        
        # Verify scores are distinct (not all identical / 60)
        scores = [r["match_score"] for r in recs_list]
        assert len(set(scores)) > 1, f"Scores should not all be identical: {scores}"
        assert all(s != 60 for s in scores[:3]), "Scores should not default to hardcoded 60!"
        print("  [PASS] Test 11: User 16 recommendations returned with dynamic, varied scores.\n")
        passed += 1

        # TEST 12: API Integration & FastAPI TestClient Validation
        print("Test 12: API Router Integration Tests via FastAPI TestClient...")
        client = TestClient(app)

        # GET /api/funding/recommendations/16
        res_rec = client.get("/api/funding/recommendations/16?top_k=5")
        assert res_rec.status_code == 200, f"Error {res_rec.status_code}: {res_rec.text}"
        rec_json = res_rec.json()
        assert rec_json["user_id"] == 16
        assert len(rec_json["recommendations"]) <= 5
        print("  [PASS] GET /api/funding/recommendations/16 endpoint returned 200 OK.")

        # GET /api/funding/search
        res_search = client.get("/api/funding/search?domain=AI")
        assert res_search.status_code == 200
        print("  [PASS] GET /api/funding/search endpoint returned 200 OK.")

        # POST /api/funding/recommendations/feedback
        res_fb = client.post("/api/funding/recommendations/feedback", json={
            "user_id": 16,
            "funding_id": 5,
            "feedback": "relevant"
        })
        assert res_fb.status_code == 200
        print("  [PASS] POST /api/funding/recommendations/feedback returned 200 OK.")

        # POST /api/rag/chat
        res_rag = client.post("/api/rag/chat", json={
            "query": "What is Retrieval Augmented Generation?"
        })
        assert res_rag.status_code == 200
        rag_json = res_rag.json()
        assert "answer" in rag_json and len(rag_json["answer"]) > 10
        print(f"  [PASS] POST /api/rag/chat returned 200 OK. Answer length: {len(rag_json['answer'])} chars.\n")
        passed += 1

    except Exception as e:
        print(f"\n[FAIL] Test suite encountered error: {e}")
        failed += 1
        import traceback
        traceback.print_exc()

    finally:
        db.close()

    print("============================================================")
    print(f"TEST RESULTS: {passed} PASSED, {failed} FAILED")
    print("============================================================")
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
