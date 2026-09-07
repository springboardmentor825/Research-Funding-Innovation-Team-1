# backend/debug_p12.py
import traceback
import sys

with open("debug_p12.log", "w", encoding="utf-8") as f:
    try:
        from test_part12_dashboard_alerts import verify_part12
        verify_part12()
        f.write("SUCCESS\n")
    except Exception as e:
        f.write("--- EXCEPTION TRACEBACK ---\n")
        traceback.print_exc(file=f)
