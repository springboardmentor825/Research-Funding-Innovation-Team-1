# backend/test_day5_queries.py

import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

QUERIES = [
    "Who is Madhu Krishna?",
    "Who invented AI Funding Recommendation Engine?",
    "Show patents related to AI.",
    "Show funding opportunities.",
    "Show research profiles.",
    "What is Retrieval Augmented Generation?"
]

def test_day5():
    print("=" * 70)
    print("RUNNING DAY 5 HYBRID RAG QUERY SUITE")
    print("=" * 70)

    # 1. Stats Endpoint Check
    r_stats = client.get("/api/v1/rag/stats")
    assert r_stats.status_code == 200, f"Stats failed: {r_stats.text}"
    print("📊 Index Stats:", json.dumps(r_stats.json(), indent=2))

    # 2. Search Endpoint Check
    r_search = client.post("/api/v1/rag/search", json={"query": "AI funding", "top_k": 3})
    assert r_search.status_code == 200, f"Search failed: {r_search.text}"
    print(f"🔍 Search 'AI funding' returned {r_search.json()['total_results']} chunks.")

    # 3. Chat Queries Execution
    for idx, q in enumerate(QUERIES, 1):
        print(f"\n--- Query {idx}: '{q}' ---")
        r = client.post("/api/v1/rag/chat", json={"question": q})
        assert r.status_code == 200, f"Query '{q}' failed: {r.text}"
        data = r.json()
        print("Answer:", data["answer"])
        print("Sources:", json.dumps(data["sources"], indent=2))
        assert len(data["answer"]) > 10, "Answer too short!"
        print(f"✅ Query {idx} PASSED!")

    print("=" * 70)
    print("ALL DAY 5 HYBRID RAG REQUIRED QUERIES EXECUTED & PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    test_day5()
