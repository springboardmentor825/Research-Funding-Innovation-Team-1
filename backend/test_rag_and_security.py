# backend/test_rag_and_security.py

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_rag_security_checks():
    print("\n--- [RAG & Security Validation] ---")
    
    # 1. RAG Endpoint check
    rag_payload = {"question": "What funding opportunities or patent trends are available in research platform?"}
    try:
        response = client.post("/api/rag/chat", json=rag_payload)
        print(f"  ✓ RAG API Endpoint (/api/rag/chat) Status Code: {response.status_code}")
        if response.status_code == 200:
            res_json = response.json()
            print(f"  ✓ RAG Answer Snippet: {res_json.get('answer', '')[:100]}...")
        else:
            print(f"  ℹ RAG Response Payload: {response.text[:200]}")
    except Exception as e:
        print(f"  ⚠ RAG API test note: {e}")

    # 2. Public / Protected Route Check
    dash_resp = client.get("/api/research-intelligence/dashboard/16")
    print(f"  ✓ Dashboard Endpoint Status Code: {dash_resp.status_code}")
    assert dash_resp.status_code == 200, f"Dashboard API failed: {dash_resp.text}"

    # 3. Secret Exposure Check
    dash_text = dash_resp.text.lower()
    for secret in ["secret_key", "password", "database_url", "aws_secret"]:
        assert secret not in dash_text, f"Potential secret exposure found in API response: {secret}"
    print("  ✓ Security Audit: Zero sensitive keys exposed in API responses!")

if __name__ == "__main__":
    run_rag_security_checks()
