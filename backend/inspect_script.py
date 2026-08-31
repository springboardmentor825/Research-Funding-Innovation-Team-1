import json
from app.database import engine
from sqlalchemy import inspect, text

def run_audit():
    inspector = inspect(engine)
    cols = inspector.get_columns('funding_opportunities')
    
    out = []
    out.append("=== MYSQL TABLE COLUMNS ===")
    for c in cols:
        out.append(f"Column: {c['name']:<20} Type: {str(c['type']):<20} Nullable: {c['nullable']} Default: {c['default']}")
        
    with engine.connect() as conn:
        count_res = conn.execute(text("SELECT COUNT(*) FROM funding_opportunities")).scalar()
        out.append(f"\nTotal rows in funding_opportunities: {count_res}")
        
        sample_rows = conn.execute(text("SELECT * FROM funding_opportunities LIMIT 10")).mappings().all()
        out.append(f"\n=== SAMPLE ROWS ({len(sample_rows)}) ===")
        for i, row in enumerate(sample_rows):
            out.append(f"\nRow {i+1}:")
            for k, v in row.items():
                out.append(f"  {k}: {v}")

    with open("audit_output.txt", "w") as f:
        f.write("\n".join(out))
    print("Audit written to audit_output.txt")

if __name__ == "__main__":
    run_audit()

