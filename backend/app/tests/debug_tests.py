import sys, os
sys.path.insert(0, os.path.abspath('c:/Users/MADHU KRISHNA/OneDrive/Documents/project/Research-Funding-Innovation-Team-1/backend'))
from app.tests.run_role_auth_tests import TestRoleAuthAndStartupModule

t = TestRoleAuthAndStartupModule()
t.setUpClass()

tests = [
    "test_1_login_matching_role_succeeds",
    "test_2_login_mismatched_role_fails",
    "test_3_admin_self_registration_blocked",
    "test_4_google_new_user_pending_role_flow",
    "test_5_google_complete_registration_blocks_admin",
    "test_6_google_complete_registration_succeeds_for_allowed_role",
    "test_7_startup_dashboard_authorization_and_data"
]

for name in tests:
    t.setUp()
    try:
        getattr(t, name)()
        print(f"PASS: {name}")
    except Exception as e:
        print(f"FAIL/ERR: {name} -> {e}")
    finally:
        t.tearDown()
