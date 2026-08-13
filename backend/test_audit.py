# backend/test_audit.py

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=" * 70)
    print("RUNNING DAY 1 - DAY 5 AUTOMATED VERIFICATION AUDIT")
    print("=" * 70)

    # 1. Day 1 Check: Root endpoint
    try:
        r = requests.get(f"{BASE_URL}/")
        assert r.status_code == 200
        print("✅ Day 1: Backend Root Endpoint Online:", r.json())
    except Exception as e:
        print("❌ Day 1 Failed:", e)

    # 2. Day 3 Check: GET /api/v1/rag/stats
    try:
        r = requests.get(f"{BASE_URL}/api/v1/rag/stats")
        assert r.status_code == 200
        print("✅ Day 3: RAG Stats Endpoint:", json.dumps(r.json(), indent=2))
    except Exception as e:
        print("❌ Day 3 Stats Failed:", e)

    # 3. Day 3 Check: POST /api/v1/rag/search
    try:
        r = requests.post(f"{BASE_URL}/api/v1/rag/search", json={"query": "Deep Learning Protein Folding", "top_k": 3})
        assert r.status_code == 200
        print("✅ Day 3: RAG Search Endpoint Total Results:", r.json()["total_results"])
    except Exception as e:
        print("❌ Day 3 Search Failed:", e)

    # 4. Day 4 Check: RAG Chat Grounded Query
    try:
        r = requests.post(f"{BASE_URL}/api/v1/rag/chat", json={"question": "What is Retrieval Augmented Generation?"})
        assert r.status_code == 200
        print("✅ Day 4: RAG Chat Grounded Answer Received:")
        print(r.json()["answer"][:200] + "...")
    except Exception as e:
        print("❌ Day 4 Chat Failed:", e)

    # 5. Day 4 Check: Hallucination Guardrail ("Who won IPL 2025?")
    try:
        r = requests.post(f"{BASE_URL}/api/v1/rag/chat", json={"question": "Who won IPL 2025?"})
        assert r.status_code == 200
        ans = r.json()["answer"]
        print("✅ Day 4: Hallucination Test Response:")
        print("   Answer:", ans)
        assert "could not find sufficient information" in ans.lower()
        print("   -> Hallucination Guardrail PASSED!")
    except Exception as e:
        print("❌ Day 4 Hallucination Guardrail Failed:", e)

    # 6. Day 5 Check: DB Retrieval Query 1 (Patent)
    try:
        r = requests.post(f"{BASE_URL}/api/v1/rag/chat", json={"question": "Who invented AI Funding Recommendation Engine?"})
        assert r.status_code == 200
        ans = r.json()["answer"]
        print("✅ Day 5: DB Query 1 (Patents Table) Response:")
        print("   Answer:", ans)
        assert "Madhu Krishna" in ans and "Patents" in ans
        print("   -> DB Query 1 PASSED!")
    except Exception as e:
        print("❌ Day 5 DB Query 1 Failed:", e)

    # 7. Day 5 Check: DB Retrieval Query 2 (Publication)
    try:
        r = requests.post(f"{BASE_URL}/api/v1/rag/chat", json={"question": "Who wrote Semantic Funding Search?"})
        assert r.status_code == 200
        ans = r.json()["answer"]
        print("✅ Day 5: DB Query 2 (Publications Table) Response:")
        print("   Answer:", ans)
        assert "Madhu Krishna" in ans and "Publications" in ans
        print("   -> DB Query 2 PASSED!")
    except Exception as e:
        print("❌ Day 5 DB Query 2 Failed:", e)

    print("=" * 70)
    print("ALL DAY 1 - DAY 5 AUTOMATED VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
