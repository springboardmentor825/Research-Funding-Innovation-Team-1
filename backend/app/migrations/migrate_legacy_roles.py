import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database import engine
from sqlalchemy import text

def migrate_legacy_roles():
    """Migrates legacy DB user role strings to canonical role values."""
    print("Starting legacy role migration...")
    with engine.begin() as conn:
        # 1. Map 'funder' -> 'startup_founder'
        result_funder = conn.execute(text("UPDATE users SET role = 'startup_founder' WHERE role = 'funder' OR role = 'investor'"))
        print(f"Updated {result_funder.rowcount} user records from 'funder'/'investor' to 'startup_founder'.")

        # 2. Map 'admin' -> 'administrator'
        result_admin = conn.execute(text("UPDATE users SET role = 'administrator' WHERE role = 'admin'"))
        print(f"Updated {result_admin.rowcount} user records from 'admin' to 'administrator'.")

    print("Legacy role migration completed successfully.")

if __name__ == "__main__":
    migrate_legacy_roles()
