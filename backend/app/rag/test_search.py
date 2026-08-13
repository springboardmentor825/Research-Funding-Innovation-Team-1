# backend/app/rag/test_search.py

import sys
import os

# Ensure backend root is in sys.path so 'app' module imports work seamlessly from any directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.rag.retrieval import search

query = "AI Funding Recommendation Engine"

results = search(query, top_k=10)

print(f"\nQuery: {query}\n")

for i, r in enumerate(results, 1):
    print("=" * 60)
    print("Result:", i)
    print("Source Type:", r.get("source_type"))
    print("Source Name:", r.get("source_name"))
    print("Table:", r.get("table"))
    print("Record ID:", r.get("record_id"))
    print("Content:")
    print(r.get("content"))
    print("=" * 60)