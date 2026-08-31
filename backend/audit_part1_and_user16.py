import sys
import os
from datetime import date
from sqlalchemy import inspect, text

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import engine

def audit_funding_opportunities():
    print("==================================================")
    print("          PART 1 DATABASE AUDIT REPORT            ")
    print("==================================================")
    
    inspector = inspect(engine)
    cols = {c['name']: c for c in inspector.get_columns('funding_opportunities')}
    
    required_cols = [
        'id', 'title', 'funder', 'description', 'amount_range', 'deadline',
        'research_domains', 'technology_areas', 'keywords', 'eligibility',
        'research_stage', 'geographic_scope', 'funding_type', 'status'
    ]
    
    print("\n--- 1. Column Presence & Types ---")
    missing_cols = []
    for col in required_cols:
        if col in cols:
            print(f"  [OK] Column '{col}': {cols[col]['type']}")
        else:
            print(f"  [MISSING] Column '{col}' IS MISSING!")
            missing_cols.append(col)
            
    with engine.connect() as conn:
        # Count total records
        count = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities")).scalar()
        print(f"\n--- 2. Record Count & Quality ---")
        print(f"  Total records in funding_opportunities: {count}")
        
        # Missing required values
        missing_titles = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE title IS NULL OR title = ''")).scalar()
        missing_funders = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE funder IS NULL OR funder = ''")).scalar()
        missing_deadlines = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE deadline IS NULL")).scalar()
        missing_descriptions = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE description IS NULL OR description = ''")).scalar()
        missing_domains = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE research_domains IS NULL OR research_domains = ''")).scalar()
        missing_techs = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE technology_areas IS NULL OR technology_areas = ''")).scalar()
        missing_keywords = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE keywords IS NULL OR keywords = ''")).scalar()

        print(f"  Missing titles: {missing_titles}")
        print(f"  Missing funders: {missing_funders}")
        print(f"  Missing deadlines: {missing_deadlines}")
        print(f"  Missing descriptions: {missing_descriptions}")
        print(f"  Missing domains: {missing_domains}")
        print(f"  Missing technology areas: {missing_techs}")
        print(f"  Missing keywords: {missing_keywords}")
        
        # Duplicate title check
        dups = conn.execute(text("SELECT title, COUNT(*) FROM funding_opportunities GROUP BY title HAVING COUNT(*) > 1")).all()
        print(f"  Duplicate titles found: {len(dups)}")
        for d in dups:
            print(f"    - Title: '{d[0]}' appears {d[1]} times")

        # Distinct statuses
        statuses = [r[0] for r in conn.execute(text("SELECT DISTINCT status FROM funding_opportunities")).all()]
        print(f"  Distinct statuses: {statuses}")

        # Distinct stages
        stages = [r[0] for r in conn.execute(text("SELECT DISTINCT research_stage FROM funding_opportunities")).all()]
        print(f"  Distinct research stages ({len(stages)}): {stages}")

        # Distinct funding types
        types = [r[0] for r in conn.execute(text("SELECT DISTINCT funding_type FROM funding_opportunities")).all()]
        print(f"  Distinct funding types ({len(types)}): {types}")

        # Check deadlines (expired vs active)
        expired = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE deadline < CURDATE()")).scalar()
        active = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities WHERE deadline >= CURDATE()")).scalar()
        print(f"  Active deadlines (>= today): {active}")
        print(f"  Expired deadlines (< today): {expired}")

def audit_user16_and_tables():
    print("\n==================================================")
    print("          RESEARCHER TABLES & USER 16 AUDIT       ")
    print("==================================================")
    with engine.connect() as conn:
        # Check users table
        users = conn.execute(text("SELECT id, email, full_name FROM users LIMIT 10")).all()
        print(f"Users found ({len(users)} shown):")
        for u in users:
            print(f"  User ID={u[0]} | Email='{u[1]}' | Name='{u[2]}'")
            
        # Check user 16 specifically
        u16 = conn.execute(text("SELECT * FROM users WHERE id = 16")).first()
        if u16:
            print(f"\nUser 16 Details: {u16}")
        else:
            print("\nUser 16 does NOT exist in `users` table!")
            
        # Check research profiles
        print("\nResearch Profiles:")
        profiles = conn.execute(text("SELECT * FROM research_profile")).all()
        for p in profiles:
            print(f"  Profile: {dict(p._mapping)}")
            
        # Check publications
        print(f"\nPublications (Total count):")
        pub_count = conn.execute(text("SELECT COUNT(*) FROM publications")).scalar()
        print(f"  Total publications: {pub_count}")
        u16_pubs = conn.execute(text("SELECT publication_id, title, journal, publication_year FROM publications WHERE user_id = 16")).all()
        print(f"  User 16 publications ({len(u16_pubs)}):")
        for pub in u16_pubs:
            print(f"    - [{pub[0]}] {pub[1]} ({pub[2]}, {pub[3]})")

        # Check patents
        print(f"\nPatents (Total count):")
        pat_count = conn.execute(text("SELECT COUNT(*) FROM patents")).scalar()
        print(f"  Total patents: {pat_count}")
        u16_pats = conn.execute(text("SELECT patent_id, title, technology_domain, filing_date FROM patents WHERE user_id = 16")).all()
        print(f"  User 16 patents ({len(u16_pats)}):")
        for pat in u16_pats:
            print(f"    - [{pat[0]}] {pat[1]} (Domain: {pat[2]})")

if __name__ == "__main__":
    audit_funding_opportunities()
    audit_user16_and_tables()
