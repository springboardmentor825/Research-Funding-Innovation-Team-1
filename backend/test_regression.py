# backend/test_regression.py

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models import User, ResearchProfile, Publication, Patent, FundingOpportunity

def test_regression_suite():
    print("==================================================")
    print("      STARTING REGRESSION TEST SUITE              ")
    print("==================================================")
    
    db = SessionLocal()
    try:
        # 1. Verify User & Profile Models
        print("\n--- 1. Testing User & Profile Models ---")
        user_count = db.query(User).count()
        profile_count = db.query(ResearchProfile).count()
        print(f"Total Users: {user_count}, Total Profiles: {profile_count}")
        assert user_count > 0 and profile_count > 0

        # 2. Verify Publications & Patents Models
        print("\n--- 2. Testing Publications & Patents ---")
        pub_count = db.query(Publication).count()
        patent_count = db.query(Patent).count()
        print(f"Total Publications: {pub_count}, Total Patents: {patent_count}")
        assert pub_count > 0 and patent_count > 0

        # 3. Verify Funding Opportunities Model
        print("\n--- 3. Testing Funding Opportunities ---")
        funding_count = db.query(FundingOpportunity).count()
        print(f"Total Funding Opportunities: {funding_count}")
        assert funding_count >= 25

        # 4. Verify Hybrid RAG Loading Availability
        print("\n--- 4. Testing Hybrid RAG Import ---")
        from app.routes import rag
        print("✓ RAG router imported successfully without errors.")

        print("\n==================================================")
        print("  REGRESSION TEST COMPLETED SUCCESSFULLY!         ")
        print("==================================================")

    finally:
        db.close()

if __name__ == "__main__":
    test_regression_suite()
