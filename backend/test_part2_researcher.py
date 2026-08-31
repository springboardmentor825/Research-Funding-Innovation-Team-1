# backend/test_part2_researcher.py

import sys
import os
import json
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import engine, SessionLocal
from sqlalchemy import text
from app.models import User, ResearchProfile, Publication, Patent
from app.services import researcher_feature_service, funding_data_service
from app.routes.researcher import get_researcher_features
from app.routes.funding import get_all_normalized_opportunities
from fastapi import HTTPException

def test_part1_audit_revalidation():
    print("\n--- 1. Part 1 Funding Dataset & API Re-Audit ---")
    db = SessionLocal()
    try:
        # Check database records
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities")).scalar()
            assert count >= 25, f"Expected >= 25 funding records, got {count}"
            print(f"✓ Funding records count: {count} (Target >= 25)")
            
            null_titles = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE title IS NULL OR title = ''")).scalar()
            assert null_titles == 0, "Found null titles"
            
            null_funders = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE funder IS NULL OR funder = ''")).scalar()
            assert null_funders == 0, "Found null funders"
            
            null_deadlines = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE deadline IS NULL")).scalar()
            assert null_deadlines == 0, "Found null deadlines"
            print("✓ Zero NULL values found in mandatory title, funder, deadline fields!")
            
            statuses = [r[0] for r in conn.execute(text("SELECT DISTINCT status FROM funding_opportunities")).all()]
            print(f"✓ Standardized statuses: {statuses}")
            assert set(statuses).issubset({"active", "closed", "draft"})

        # Route check
        norm_opps = get_all_normalized_opportunities(active_only=True, db=db)
        assert len(norm_opps) > 0
        print(f"✓ Funding API Route get_all_normalized_opportunities returned {len(norm_opps)} active records.")
    finally:
        db.close()

def test_user16_feature_extraction():
    print("\n--- 2. Part 2 Researcher Feature Extraction for User 16 ---")
    db = SessionLocal()
    try:
        res = get_researcher_features(user_id=16, db=db)
        # res can be ResearcherProfileSummary schema or dict
        data = res if isinstance(res, dict) else res.model_dump()
        
        print("✓ Full Feature Extraction Response for User 16:")
        print(json.dumps(data, indent=2))
        
        assert data["user_id"] == 16
        assert data["has_profile"] is True
        assert data["organization"] == "Stanford University"
        assert data["designation"] == "Associate Professor"
        
        # Must not be default "General"
        assert data["research_domain"] != ["General"]
        assert "Artificial Intelligence" in data["research_domain"]
        assert "Computer Science" in data["research_domain"]
        
        assert "Natural Language Processing" in data["technology_areas"]
        assert "Machine Learning" in data["technology_areas"]
        assert "Deep Learning" in data["technology_areas"]
        
        assert data["publication_count"] == 10
        assert data["patent_count"] == 10
        assert data["interest_count"] == 5
        assert data["keyword_count"] == 7
        
        assert len(data["publication_topics"]) == 10
        assert len(data["patent_domains"]) > 0
        
        # Verify combined text representation
        text_rep = data["combined_research_text"]
        print(f"\n✓ Combined Research Text Sample:\n  \"{text_rep[:150]}...\"")
        assert "Artificial Intelligence" in text_rep
        assert "Natural Language Processing" in text_rep
        assert "Stanford University" not in text_rep or "Artificial Intelligence" in text_rep
        
    finally:
        db.close()

def test_edge_cases():
    print("\n--- 3. Part 2 Edge Cases Verification ---")
    db = SessionLocal()
    try:
        # Edge Case 1: Non-existent user ID (9999)
        print("Testing Edge Case 1: Invalid User ID (9999)...")
        try:
            get_researcher_features(user_id=9999, db=db)
            assert False, "Should have raised HTTPException 404 for invalid user ID"
        except HTTPException as exc:
            assert exc.status_code == 404
            print(f"✓ Correctly raised HTTP 404: {exc.detail}")

        # Edge Case 2: User with Profile but 0 Publications
        print("Testing Edge Case 2: User with profile but 0 publications...")
        # Create a temporary user with profile
        temp_user = User(full_name="Dr. Test NoPubs", email="nopubs@test.edu", role="researcher", login_type="email")
        db.add(temp_user)
        db.commit()
        db.refresh(temp_user)
        
        temp_profile = ResearchProfile(
            user_id=temp_user.id,
            organization="Test University",
            designation="Assistant Professor",
            research_domain="Quantum Computing",
            technology_area="Superconducting Qubits",
            research_interests="Error Correction, Qubit Control",
            keywords="Quantum, Qubit, Qiskit"
        )
        db.add(temp_profile)
        db.commit()
        
        features = researcher_feature_service.build_researcher_features(db, temp_user.id)
        assert features["has_profile"] is True
        assert features["publication_count"] == 0
        assert features["publication_topics"] == []
        assert features["patent_count"] == 0
        assert "Quantum Computing" in features["research_domain"]
        print("✓ Successfully handled user with profile but 0 publications!")

        # Edge Case 3: User with No Profile
        print("Testing Edge Case 3: User with no research profile...")
        noprof_user = User(full_name="Dr. No Profile", email="noprofile@test.edu", role="researcher", login_type="email")
        db.add(noprof_user)
        db.commit()
        db.refresh(noprof_user)
        
        noprof_feat = researcher_feature_service.build_researcher_features(db, noprof_user.id)
        assert noprof_feat["has_profile"] is False
        assert noprof_feat["research_domain"] == []
        assert noprof_feat["technology_areas"] == []
        assert noprof_feat["research_interests"] == []
        assert noprof_feat["keywords"] == []
        print("✓ Successfully returned explicit empty features (no hardcoded 'General') for profile-less user!")

        # Edge Case 4: Token Normalization with Multi-Word Concept Preservation
        print("Testing Edge Case 4: Token Normalization...")
        raw = "AI, Artificial Intelligence, artificial intelligence, Natural Language Processing, natural language processing, Knowledge Graphs"
        tokens = researcher_feature_service._normalize_tokens(raw)
        print(f"  Input:  '{raw}'")
        print(f"  Tokens: {tokens}")
        assert "Artificial Intelligence" in tokens
        assert "Natural Language Processing" in tokens
        assert "Knowledge Graphs" in tokens
        assert len(tokens) == 4 # AI, Artificial Intelligence, Natural Language Processing, Knowledge Graphs
        print("✓ Token normalization correctly deduplicated while preserving multi-word concepts!")

        # Cleanup temporary test users
        db.delete(temp_profile)
        db.delete(temp_user)
        db.delete(noprof_user)
        db.commit()
        print("✓ Temporary test records cleaned up.")
        
    finally:
        db.close()

def run_all_part2_tests():
    print("==================================================")
    print("      STARTING PART 2 VERIFICATION TEST SUITE     ")
    print("==================================================")
    test_part1_audit_revalidation()
    test_user16_feature_extraction()
    test_edge_cases()
    print("==================================================")
    print("  ALL PART 2 VERIFICATION TESTS PASSED SUCCESSFULLY! ")
    print("==================================================")

if __name__ == "__main__":
    run_all_part2_tests()
