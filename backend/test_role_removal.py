import sys
import os
import unittest
import requests
import uuid

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User

BASE_URL = "http://127.0.0.1:8000/api/v1"

class TestInnovationManagerRoleRemoval(unittest.TestCase):

    def test_1_researcher_login_success(self):
        """TEST 1: Researcher login -> 200 OK & role=researcher"""
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "test@example.com",
            "password": "password123",
            "selected_role": "researcher"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["role"], "researcher")

    def test_2_startup_founder_login_success(self):
        """TEST 2: Startup Founder login -> 200 OK & role=startup_founder"""
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "startup1@example.com",
            "password": "password123",
            "selected_role": "startup_founder"
        })
        # If startup1@example.com password is startu1 or password123
        if res.status_code != 200:
            res = requests.post(f"{BASE_URL}/auth/login", json={
                "email": "startup1@example.com",
                "password": "startu1",
                "selected_role": "startup_founder"
            })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["role"], "startup_founder")

    def test_3_administrator_login_success(self):
        """TEST 3: Administrator login -> 200 OK & role=administrator"""
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "admin@example.com",
            "password": "password123",
            "selected_role": "administrator"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["role"], "administrator")

    def test_4_public_signup_researcher_allowed(self):
        """TEST 4: Public signup with role=researcher -> 201 Created"""
        rnd_email = f"res_{uuid.uuid4().hex[:6]}@example.com"
        res = requests.post(f"{BASE_URL}/auth/register", json={
            "full_name": "Test Researcher",
            "email": rnd_email,
            "password": "password123",
            "role": "researcher"
        })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["role"], "researcher")

    def test_5_public_signup_startup_founder_allowed(self):
        """TEST 5: Public signup with role=startup_founder -> 201 Created"""
        rnd_email = f"founder_{uuid.uuid4().hex[:6]}@example.com"
        res = requests.post(f"{BASE_URL}/auth/register", json={
            "full_name": "Test Founder",
            "email": rnd_email,
            "password": "password123",
            "role": "startup_founder"
        })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["role"], "startup_founder")

    def test_6_public_signup_innovation_manager_strictly_rejected(self):
        """TEST 6: Public signup with role=innovation_manager -> 400 Bad Request"""
        rnd_email = f"im_{uuid.uuid4().hex[:6]}@example.com"
        res = requests.post(f"{BASE_URL}/auth/register", json={
            "full_name": "Test Manager",
            "email": rnd_email,
            "password": "password123",
            "role": "innovation_manager"
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid user role", res.json()["detail"])

    def test_7_public_signup_administrator_forbidden(self):
        """TEST 7: Public signup with role=administrator -> 403 Forbidden"""
        rnd_email = f"admin_reg_{uuid.uuid4().hex[:6]}@example.com"
        res = requests.post(f"{BASE_URL}/auth/register", json={
            "full_name": "Test Admin",
            "email": rnd_email,
            "password": "password123",
            "role": "administrator"
        })
        self.assertEqual(res.status_code, 403)

    def test_8_google_oauth_complete_innovation_manager_rejected(self):
        """TEST 8: Google role selection with innovation_manager -> 400 Bad Request"""
        init_res = requests.post(f"{BASE_URL}/auth/google", json={
            "email": f"g_im_{uuid.uuid4().hex[:6]}@example.com",
            "full_name": "Google IM Attempt"
        })
        pending_token = init_res.json()["pending_token"]
        comp_res = requests.post(f"{BASE_URL}/auth/google/complete-registration", json={
            "pending_token": pending_token,
            "selected_role": "innovation_manager"
        })
        self.assertEqual(comp_res.status_code, 400)

    def test_9_zero_active_innovation_manager_users_in_database(self):
        """TEST 9: Database check -> Zero active users with role=innovation_manager"""
        db = SessionLocal()
        im_count = db.query(User).filter(User.role == "innovation_manager").count()
        db.close()
        self.assertEqual(im_count, 0, f"Found {im_count} legacy innovation_manager accounts in database!")

if __name__ == "__main__":
    print("========================================================")
    print("RUNNING INNOVATION MANAGER ROLE REMOVAL TEST SUITE")
    print("========================================================")
    unittest.main()
