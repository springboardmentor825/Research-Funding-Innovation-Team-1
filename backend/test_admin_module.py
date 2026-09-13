import requests
import sys
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_public_registration_blocks_administrator():
    print("\n--- 1. Testing Public Signup Security Guard ---")
    random_email = f"hacker_{uuid.uuid4().hex[:6]}@example.com"
    res = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "full_name": "Hacker User",
            "email": random_email,
            "password": "password123",
            "role": "administrator"
        }
    )
    print("Register role=administrator response:", res.status_code, res.json())
    assert res.status_code == 403
    assert "Public self-registration as Administrator is strictly prohibited" in res.json()["detail"]
    print("✓ Public registration guard passed.")


def test_admin_authentication_and_authorization():
    print("\n--- 2. Testing Login & Role Authorization ---")
    
    # Login as researcher test user
    res_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "test@example.com", "password": "password123", "selected_role": "researcher"}
    )
    assert res_login.status_code == 200, f"Researcher login failed: {res_login.text}"
    res_token = res_login.json()["access_token"]
    res_headers = {"Authorization": f"Bearer {res_token}"}

    # Login as admin user
    admin_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@example.com", "password": "password123", "selected_role": "administrator"}
    )
    assert admin_login.status_code == 200, f"Admin login failed: {admin_login.text}"
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Researcher attempts admin route -> 403 Forbidden
    res_denied = requests.get(f"{BASE_URL}/admin/dashboard", headers=res_headers)
    print("Researcher accessing /admin/dashboard status code:", res_denied.status_code)
    assert res_denied.status_code == 403
    print("✓ Non-admin authorization block passed.")

    # Admin attempts admin route -> 200 OK
    admin_allowed = requests.get(f"{BASE_URL}/admin/dashboard", headers=admin_headers)
    print("Admin accessing /admin/dashboard status code:", admin_allowed.status_code)
    assert admin_allowed.status_code == 200
    data = admin_allowed.json()
    assert "summary" in data
    assert "users_by_role" in data
    print("✓ Admin dashboard authorization passed.")
    return admin_headers


def test_last_admin_protection(admin_headers):
    print("\n--- 3. Testing Last Admin Demotion & Deactivation Protection ---")
    
    # Fetch admin user ID
    u_list = requests.get(f"{BASE_URL}/admin/users?role=administrator", headers=admin_headers).json()
    admin_users = u_list.get("users", [])
    assert len(admin_users) > 0, "No administrator users found in system!"
    target_admin_id = admin_users[0]["id"]

    # Attempt to demote sole admin to researcher
    res_demote = requests.patch(
        f"{BASE_URL}/admin/users/{target_admin_id}/role",
        headers=admin_headers,
        json={"role": "researcher"}
    )
    print("Demoting sole administrator status code:", res_demote.status_code, res_demote.json())
    assert res_demote.status_code == 400
    assert "Cannot remove or change the last administrator account" in res_demote.json()["detail"]
    print("✓ Last admin role demotion protection passed.")

    # Attempt to deactivate sole admin
    res_deactivate = requests.patch(
        f"{BASE_URL}/admin/users/{target_admin_id}/status",
        headers=admin_headers,
        json={"status": "deactivated"}
    )
    print("Deactivating sole administrator status code:", res_deactivate.status_code, res_deactivate.json())
    assert res_deactivate.status_code == 400
    assert "Cannot de-activate the last administrator account" in res_deactivate.json()["detail"]
    print("✓ Last admin deactivation protection passed.")


def test_admin_api_endpoints(admin_headers):
    print("\n--- 4. Testing All Admin Sub-Module APIs ---")

    # 1. User Management List
    u_list = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
    assert u_list.status_code == 200
    assert "users" in u_list.json()
    print("✓ /admin/users endpoint passed.")

    # 2. User Details
    u_details = requests.get(f"{BASE_URL}/admin/users/1", headers=admin_headers)
    assert u_details.status_code in [200, 404]
    print("✓ /admin/users/{id} endpoint passed.")

    # 3. Analytics
    analytics = requests.get(f"{BASE_URL}/admin/analytics", headers=admin_headers)
    assert analytics.status_code == 200
    assert "user_analytics" in analytics.json()
    print("✓ /admin/analytics endpoint passed.")

    # 4. Recommendation Monitoring
    recs_mon = requests.get(f"{BASE_URL}/admin/recommendations", headers=admin_headers)
    assert recs_mon.status_code == 200
    assert "score_distribution" in recs_mon.json()
    print("✓ /admin/recommendations endpoint passed.")

    # 5. Reports & Export
    reports = requests.get(f"{BASE_URL}/admin/reports", headers=admin_headers)
    assert reports.status_code == 200
    assert len(reports.json()["reports"]) > 0
    print("✓ /admin/reports endpoint passed.")

    export = requests.get(f"{BASE_URL}/admin/reports/user_management/export", headers=admin_headers)
    assert export.status_code == 200
    assert "User ID,Full Name,Email" in export.text
    print("✓ /admin/reports/user_management/export CSV endpoint passed.")

    print("\n========================================================")
    print("ALL AUTOMATED ADMIN MODULE INTEGRATION TESTS PASSED 100%!")
    print("========================================================")


if __name__ == "__main__":
    test_public_registration_blocks_administrator()
    headers = test_admin_authentication_and_authorization()
    test_last_admin_protection(headers)
    test_admin_api_endpoints(headers)
