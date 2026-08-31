import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine
from sqlalchemy import text

def run_alter():
    sqls = [
        "ALTER TABLE funding_opportunities MODIFY COLUMN research_domains TEXT NULL;",
        "ALTER TABLE funding_opportunities MODIFY COLUMN technology_areas TEXT NULL;",
        "ALTER TABLE funding_opportunities MODIFY COLUMN keywords TEXT NULL;",
        "ALTER TABLE funding_opportunities MODIFY COLUMN eligibility TEXT NULL;",
        "ALTER TABLE funding_opportunities MODIFY COLUMN geographic_scope VARCHAR(255) NULL;",
        "ALTER TABLE funding_opportunities ALTER COLUMN status SET DEFAULT 'active';",
        "UPDATE funding_opportunities SET status = 'active' WHERE status = 'open';"
    ]
    
    with engine.connect() as conn:
        for sql in sqls:
            print(f"Executing: {sql}")
            conn.execute(text(sql))
        conn.commit()
    print("Database schema successfully altered and status values normalized to 'active'.")

if __name__ == "__main__":
    run_alter()
