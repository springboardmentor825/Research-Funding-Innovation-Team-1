# backend/val_runner.py
import traceback
import sys

with open("val.log", "w", encoding="utf-8") as f:
    try:
        from test_master_final_validation import run_master_validation
        run_master_validation()
        f.write("VALIDATION COMPLETED SUCCESSFULLY\n")
    except Exception as e:
        f.write("--- EXCEPTION TRACEBACK ---\n")
        traceback.print_exc(file=f)
