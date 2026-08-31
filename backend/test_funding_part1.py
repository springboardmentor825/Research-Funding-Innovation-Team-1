import sys
import os
import json
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import engine, SessionLocal
from sqlalchemy import inspect, text
from app.models.funding_opportunity import FundingOpportunity
from app.schemas.funding import (
    FundingOpportunityBase,
    FundingOpportunityCreate,
    FundingOpportunitySchema,
    FundingOpportunityNormalized,
    ALLOWED_STATUSES,
    ALLOWED_RESEARCH_STAGES,
    ALLOWED_FUNDING_TYPES
)
from app.services import funding_data_service
from fastapi.testclient import TestClient
from app.main import app

def test_database_schema():
    print("\n--- 1. Testing Database Schema ---")
    inspector = inspect(engine)
    cols = {c['name']: c for c in inspector.get_columns('funding_opportunities')}
    
    required_cols = [
        'id', 'title', 'funder', 'amount_range', 'deadline', 'semantic_fit',
        'match_badges', 'description', 'research_domains', 'technology_areas',
        'keywords', 'eligibility', 'research_stage', 'geographic_scope',
        'funding_type', 'status'
    ]
    for col in required_cols:
        assert col in cols, f"Missing column: {col}"
        
    print(f"✓ All {len(required_cols)} required columns present in MySQL table!")
    print(f"  research_domains type: {cols['research_domains']['type']}")
    print(f"  technology_areas type: {cols['technology_areas']['type']}")
    print(f"  keywords type: {cols['keywords']['type']}")
    print(f"  status default: {cols['status']['default']}")

def test_sql_integrity_checks():
    print("\n--- 2. Testing SQL Integrity Checks ---")
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities")).scalar()
        print(f"✓ Total Funding Records: {count}")
        assert count >= 25, f"Expected at least 25 records, got {count}"
        
        statuses = [r[0] for r in conn.execute(text("SELECT DISTINCT status FROM funding_opportunities")).all()]
        print(f"✓ Distinct Statuses: {statuses}")
        
        stages = [r[0] for r in conn.execute(text("SELECT DISTINCT research_stage FROM funding_opportunities")).all()]
        print(f"✓ Distinct Research Stages ({len(stages)}): {stages}")
        
        types = [r[0] for r in conn.execute(text("SELECT DISTINCT funding_type FROM funding_opportunities")).all()]
        print(f"✓ Distinct Funding Types ({len(types)}): {types}")
        
        null_titles = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE title IS NULL OR title = ''")).scalar()
        null_funders = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE funder IS NULL OR funder = ''")).scalar()
        null_deadlines = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE deadline IS NULL")).scalar()
        
        assert null_titles == 0, "Found NULL or empty titles"
        assert null_funders == 0, "Found NULL or empty funders"
        assert null_deadlines == 0, "Found NULL deadlines"
        print("✓ Zero NULL values found in mandatory fields (title, funder, deadline)!")

def test_sqlalchemy_orm():
    print("\n--- 3. Testing SQLAlchemy ORM ---")
    db = SessionLocal()
    try:
        opps = db.query(FundingOpportunity).all()
        print(f"✓ ORM retrieved {len(opps)} FundingOpportunity objects.")
        first = opps[0]
        print(f"  Sample Record #1: ID={first.id} | Title='{first.title}' | Funder='{first.funder}'")
        print(f"  Domains='{first.research_domains}'")
        print(f"  Tech Areas='{first.technology_areas}'")
        print(f"  Keywords='{first.keywords}'")
    finally:
        db.close()

def test_funding_data_service():
    print("\n--- 4. Testing Funding Data Service & Normalization ---")
    db = SessionLocal()
    try:
        all_opps = funding_data_service.get_all_funding_opportunities(db)
        assert len(all_opps) >= 25, "Data service get_all_funding_opportunities failed"
        
        active_opps = funding_data_service.get_active_funding_opportunities(db)
        print(f"✓ Active opportunities count: {len(active_opps)}")
        
        opp_id1 = funding_data_service.get_funding_by_id(db, 1)
        assert opp_id1 is not None, "get_funding_by_id(1) returned None"
        
        norm_rec = funding_data_service.normalize_funding_record(opp_id1)
        print("✓ Sample Normalized Record Structure:")
        print(json.dumps(norm_rec, indent=2))
        
        assert isinstance(norm_rec["domains"], list), "Normalized domains must be a list"
        assert isinstance(norm_rec["technologies"], list), "Normalized technologies must be a list"
        assert isinstance(norm_rec["keywords"], list), "Normalized keywords must be a list"
        assert norm_rec["deadline_status"] in ["active", "closing_soon", "expired"]
        
        duplicates = funding_data_service.detect_duplicate_funding(db)
        print(f"✓ Duplicate Detection Check: {len(duplicates)} duplicate groups found.")
    finally:
        db.close()

def test_pydantic_validation():
    print("\n--- 5. Testing Pydantic Schema Validation ---")
    valid_data = {
        "title": "Test AI Grant",
        "funder": "Test Funder",
        "amount_range": "$10K-$20K",
        "deadline": date(2026, 12, 31),
        "status": "active",
        "research_stage": "Applied Research",
        "funding_type": "Research Grant"
    }
    schema = FundingOpportunityCreate(**valid_data)
    assert schema.title == "Test AI Grant"
    print("✓ Valid Pydantic schema instantiated successfully.")
    
    # Test invalid title
    try:
        FundingOpportunityCreate(**{**valid_data, "title": "   "})
        assert False, "Should have raised ValueError for empty title"
    except ValueError:
        print("✓ Empty title correctly rejected by validator.")

def test_api_endpoints():
    print("\n--- 6. Testing FastAPI Endpoints ---")
    client = TestClient(app)
    
    res1 = client.get("/api/funding/opportunities")
    assert res1.status_code == 200
    data1 = res1.json()
    print(f"✓ GET /api/funding/opportunities returned 200 OK with {len(data1)} items.")
    
    res2 = client.get("/api/funding/opportunities/1")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["id"] == 1
    print(f"✓ GET /api/funding/opportunities/1 returned 200 OK for '{data2['title']}'.")
    
    res3 = client.get("/api/funding/duplicates")
    assert res3.status_code == 200
    print("✓ GET /api/funding/duplicates returned 200 OK.")
    
    res4 = client.get("/api/funding/")
    assert res4.status_code == 200
    print("✓ GET /api/funding/ (legacy compatible recommendation route) returned 200 OK.")

def run_all_tests():
    print("==================================================")
    print("      STARTING PART 1 VERIFICATION TEST SUITE     ")
    print("==================================================")
    test_database_schema()
    test_sql_integrity_checks()
    test_sqlalchemy_orm()
    test_funding_data_service()
    test_pydantic_validation()
    test_api_endpoints()
    print("==================================================")
    print("  ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!  ")
    print("==================================================")

if __name__ == "__main__":
    run_all_tests()
