# backend/test_part12_dashboard_alerts.py

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import User, Alert, FundingOpportunity, Publication, Patent
from app.services import dashboard_service, alert_service

def verify_part12():
    print("\n==========================================================================")
    print("      PART 12 — INTEGRATED RESEARCH INTELLIGENCE DASHBOARD & ALERTS       ")
    print("==========================================================================")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email.like("%lin%")).first()
        if not user:
            user = db.query(User).first()
        assert user is not None, "No user found in database for testing Part 12!"

        test_user_id = user.id
        print(f"\n[TARGET TEST USER]: ID {test_user_id} - '{user.full_name}' ({user.email})")

        # --------------------------------------------------------------------------
        # 1. ALERT GENERATION & DEDUPLICATION TEST
        # --------------------------------------------------------------------------
        print("\n--- [PART 12.1] Alert Generation & Deduplication ---")
        alerts_1 = alert_service.generate_user_alerts(db, test_user_id)
        assert alerts_1 is not None, "Alert generation returned None!"
        print(f"  ✓ Initial generated alerts count: {len(alerts_1)}")

        # Deduplication test: run generation again and verify count does not multiply
        alerts_2 = alert_service.generate_user_alerts(db, test_user_id)
        assert len(alerts_2) == len(alerts_1), f"Deduplication failed! Alert count changed from {len(alerts_1)} to {len(alerts_2)}"
        print(f"  ✓ Deduplication verified! Alert count remains stable: {len(alerts_2)}")

        # --------------------------------------------------------------------------
        # 2. ALERT LIFECYCLE (MARK READ & DISMISS) TEST
        # --------------------------------------------------------------------------
        print("\n--- [PART 12.2] Alert Lifecycle (Read & Dismiss) ---")
        if alerts_1:
            target_alert = alerts_1[0]
            alert_id = target_alert["id"]

            # Mark Read
            read_res = alert_service.mark_alert_as_read(db, alert_id, test_user_id)
            assert read_res.get("success") is True, f"Failed to mark alert #{alert_id} as read"
            print(f"  ✓ Alert #{alert_id} marked as read.")

            # Dismiss
            dismiss_res = alert_service.dismiss_alert(db, alert_id, test_user_id)
            assert dismiss_res.get("success") is True, f"Failed to dismiss alert #{alert_id}"
            print(f"  ✓ Alert #{alert_id} dismissed.")

            active_alerts = alert_service.get_user_alerts(db, test_user_id)
            assert not any(a["id"] == alert_id for a in active_alerts), f"Dismissed alert #{alert_id} still present in active list!"
            print(f"  ✓ Dismissed alert #{alert_id} excluded from active list.")
        else:
            print("  ✓ (No alerts generated for user, lifecycle test skipped)")

        # --------------------------------------------------------------------------
        # 3. INTEGRATED DASHBOARD AGGREGATION TEST
        # --------------------------------------------------------------------------
        print("\n--- [PART 12.3] Integrated Dashboard Aggregation ---")
        dash_data = dashboard_service.get_integrated_dashboard_data(db, test_user_id)

        assert "kpis" in dash_data, "Dashboard data missing 'kpis' key!"
        assert "researcher" in dash_data, "Dashboard data missing 'researcher' key!"
        assert "funding" in dash_data, "Dashboard data missing 'funding' key!"
        assert "collaboration" in dash_data, "Dashboard data missing 'collaboration' key!"
        assert "patents" in dash_data, "Dashboard data missing 'patents' key!"
        assert "innovation" in dash_data, "Dashboard data missing 'innovation' key!"
        assert "analytics" in dash_data, "Dashboard data missing 'analytics' key!"
        assert "recent_activity" in dash_data, "Dashboard data missing 'recent_activity' key!"
        assert "alerts" in dash_data, "Dashboard data missing 'alerts' key!"

        kpis = dash_data["kpis"]
        print("  ✓ Aggregated KPIs:")
        print(f"    - Active Funding: {kpis.get('active_funding')}")
        print(f"    - Strong Matches: {kpis.get('strong_matches')}")
        print(f"    - Upcoming Deadlines (30d): {kpis.get('upcoming_deadlines')}")
        print(f"    - Potential Collaborators: {kpis.get('potential_collaborators')}")
        print(f"    - Network Size: {kpis.get('network_size')}")
        print(f"    - Publications: {kpis.get('publications')}")
        print(f"    - Patents: {kpis.get('patents')}")
        print(f"    - Emerging Techs: {kpis.get('emerging_technologies')}")
        print(f"    - Saved Opportunities: {kpis.get('saved_opportunities')}")

        # KPI DB Cross-Validation
        db_pub_count = db.query(Publication).filter(Publication.user_id == test_user_id).count()
        assert kpis.get('publications') == db_pub_count, f"Publication KPI mismatch! DB: {db_pub_count}, KPI: {kpis.get('publications')}"

        db_pat_count = db.query(Patent).filter(Patent.user_id == test_user_id).count()
        assert kpis.get('patents') == db_pat_count, f"Patent KPI mismatch! DB: {db_pat_count}, KPI: {kpis.get('patents')}"

        print("  ✓ Database vs Dashboard KPI Validation PASSED!")

        print("\n==========================================================================")
        print("   🎉 PART 12 (INTEGRATED DASHBOARD & ALERTS) VERIFIED 100% OPERATIONAL!  ")
        print("==========================================================================")

    finally:
        db.close()

if __name__ == "__main__":
    verify_part12()
