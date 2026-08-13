# backend/test_audit_client.py

import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("=" * 70)
    print("RUNNING IN-PROCESS FASTAPI TESTCLIENT AUDIT")
    print("=" * 70)

    # 1. Day 1 Check: Root endpoint
    r = client.get("/")
    assert r.status_code == 200, f"Day 1 Root failed: {r.text}"
    print("✅ Day 1: Root Endpoint Response:", r.json())

    # 2. Day 3 Check: GET /api/v1/rag/stats
    r = client.get("/api/v1/rag/stats")
    assert r.status_code == 200, f"Day 3 Stats failed: {r.text}"
    stats = r.json()
    print("✅ Day 3: RAG Stats Endpoint:", json.dumps(stats, indent=2))

    # 3. Day 3 Check: POST /api/v1/rag/search
    r = client.post("/api/v1/rag/search", json={"query": "Deep Learning Protein Folding", "top_k": 3})
    assert r.status_code == 200, f"Day 3 Search failed: {r.text}"
    search_data = r.json()
    print(f"✅ Day 3: RAG Search Endpoint Total Results: {search_data['total_results']}")

    # 4. Day 4 Check: Grounded Query
    r = client.post("/api/v1/rag/chat", json={"question": "What is Retrieval Augmented Generation?"})
    assert r.status_code == 200, f"Day 4 Chat failed: {r.text}"
    chat_data = r.json()
    print("✅ Day 4: Grounded Answer Snippet:")
    print("  ", chat_data["answer"][:150] + "...")

    # 5. Day 4 Check: Hallucination Guardrail ("Who won IPL 2025?")
    r = client.post("/api/v1/rag/chat", json={"question": "Who won IPL 2025?"})
    assert r.status_code == 200, f"Day 4 Hallucination check failed: {r.text}"
    ans = r.json()["answer"]
    print("✅ Day 4: Hallucination Guardrail Check:")
    print("   Response:", ans)
    assert "could not find sufficient information" in ans.lower()
    print("   -> Hallucination Guardrail PASSED!")

    # 6. Day 5 Check: DB Retrieval Query 1 (Patent)
    r = client.post("/api/v1/rag/chat", json={"question": "Who invented AI Funding Recommendation Engine?"})
    assert r.status_code == 200, f"Day 5 DB Query 1 failed: {r.text}"
    ans1 = r.json()["answer"]
    print("✅ Day 5: DB Query 1 (Patents Table) Response:")
    print("   Response:", ans1)
    assert "Madhu Krishna" in ans1 and "Patents" in ans1
    print("   -> DB Query 1 PASSED!")

    # 7. Day 5 Check: DB Retrieval Query 2 (Publication)
    r = client.post("/api/v1/rag/chat", json={"question": "Who wrote Semantic Funding Search?"})
    assert r.status_code == 200, f"Day 5 DB Query 2 failed: {r.text}"
    ans2 = r.json()["answer"]
    print("✅ Day 5: DB Query 2 (Publications Table) Response:")
    print("   Response:", ans2)
    assert "Madhu Krishna" in ans2 and "Publications" in ans2
    print("   -> DB Query 2 PASSED!")

    print("=" * 70)
    print("ALL DAY 1 - DAY 5 AUDIT REQUIREMENTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
