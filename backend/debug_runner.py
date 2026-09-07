import sys
import traceback

sys.path.insert(0, ".")

try:
    from test_all_parts_1_to_9 import verify_all_parts
    verify_all_parts()
except Exception as e:
    with open("debug_error.log", "w") as f:
        traceback.print_exc(file=f)
    print("LOGGED EXCEPTION TO debug_error.log")
    traceback.print_exc()
