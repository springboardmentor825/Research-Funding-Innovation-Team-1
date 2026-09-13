import unittest
import sys
import os

# Add backend root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from app.models import User, ResearchProfile
from app.auth import get_password_hash

class TestRoleAuthAndStartupModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    def setUp(self):
        # Create dedicated clean test database session
        from app.database import SessionLocal
        self.db = SessionLocal()
        
        # Clean test accounts
        self.db.query(User).filter(User.email.like("test_%@example.com")).delete(synchronize_session=False)
        self.db.commit()

        # Seed test users
        self.researcher_user = User(
            full_name="Test Researcher",
            email="test_researcher@example.com",
            password=get_password_hash("password123"),
            role="researcher",
            auth_provider="email",
            account_status="active"
        )
        self.startup_user = User(
            full_name="Test Startup Founder",
            email="test_founder@example.com",
            password=get_password_hash("password123"),
            role="startup_founder",
            auth_provider="email",
            account_status="active"
        )
        self.db.add(self.researcher_user)
        self.db.add(self.startup_user)
        self.db.commit()
        self.db.refresh(self.researcher_user)
        self.db.refresh(self.startup_user)

    def tearDown(self):
        self.db.close()

    def test_1_login_matching_role_succeeds(self):
        """Validates that login with matching role succeeds."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test_researcher@example.com",
            "password": "password123",
            "selected_role": "researcher"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["role"], "researcher")
        self.assertIn("access_token", data)

    def test_2_login_mismatched_role_fails(self):
        """Validates that login with mismatched role returns 400 Bad Request and does not modify database role."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test_researcher@example.com",
            "password": "password123",
            "selected_role": "startup_founder"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Selected role does not match your account role", response.json()["detail"])

        # Check DB role remains unchanged
        user_in_db = self.db.query(User).filter(User.email == "test_researcher@example.com").first()
        self.assertEqual(user_in_db.role, "researcher")

    def test_3_admin_self_registration_blocked(self):
        """Validates that public self-registration as administrator returns 403 Forbidden."""
        response = self.client.post("/api/v1/auth/register", json={
            "full_name": "Unauthorized Admin Attempt",
            "email": "test_admin_attempt@example.com",
            "password": "Password123!",
            "role": "administrator"
        })
        self.assertEqual(response.status_code, 403)
        self.assertIn("strictly prohibited", response.json()["detail"])

    def test_4_google_new_user_pending_role_flow(self):
        """Validates that a new Google user receives pending_role_selection status and pending_token."""
        response = self.client.post("/api/v1/auth/google", json={
            "email": "test_new_google_user@example.com",
            "full_name": "New Google Founder"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "pending_role_selection")
        self.assertIn("pending_token", data)

    def test_5_google_complete_registration_blocks_admin(self):
        """Validates that complete-registration with administrator returns 403 Forbidden."""
        # 1. Get pending token
        init_res = self.client.post("/api/v1/auth/google", json={
            "email": "test_new_google_user2@example.com",
            "full_name": "New Google User"
        })
        pending_token = init_res.json()["pending_token"]

        # 2. Attempt role completion as administrator
        comp_res = self.client.post("/api/v1/auth/google/complete-registration", json={
            "pending_token": pending_token,
            "selected_role": "administrator"
        })
        self.assertEqual(comp_res.status_code, 403)

    def test_6_google_complete_registration_succeeds_for_allowed_role(self):
        """Validates that complete-registration with startup_founder creates active user."""
        init_res = self.client.post("/api/v1/auth/google", json={
            "email": "test_new_founder@example.com",
            "full_name": "New Founder User"
        })
        pending_token = init_res.json()["pending_token"]

        comp_res = self.client.post("/api/v1/auth/google/complete-registration", json={
            "pending_token": pending_token,
            "selected_role": "startup_founder"
        })
        self.assertEqual(comp_res.status_code, 200)
        data = comp_res.json()
        self.assertEqual(data["role"], "startup_founder")
        self.assertIn("access_token", data)

    def test_7_startup_dashboard_authorization_and_data(self):
        """Validates that startup dashboard requires startup_founder role and returns all 4 section payloads."""
        # 1. Researcher token (should be blocked)
        r_login = self.client.post("/api/v1/auth/login", json={
            "email": "test_researcher@example.com",
            "password": "password123",
            "selected_role": "researcher"
        })
        r_token = r_login.json()["access_token"]

        blocked_res = self.client.get(
            "/api/startup/dashboard",
            headers={"Authorization": f"Bearer {r_token}"}
        )
        self.assertEqual(blocked_res.status_code, 403)

        # 2. Startup Founder token (should succeed)
        s_login = self.client.post("/api/v1/auth/login", json={
            "email": "test_founder@example.com",
            "password": "password123",
            "selected_role": "startup_founder"
        })
        s_token = s_login.json()["access_token"]

        allowed_res = self.client.get(
            "/api/startup/dashboard",
            headers={"Authorization": f"Bearer {s_token}"}
        )
        self.assertEqual(allowed_res.status_code, 200)
        dash_data = allowed_res.json()
        self.assertEqual(dash_data["user_role"], "startup_founder")
        self.assertIn("sections", dash_data)
        self.assertIn("funding_opportunities", dash_data["sections"])
        self.assertIn("technology_opportunities", dash_data["sections"])
        self.assertIn("patent_intelligence", dash_data["sections"])
        self.assertIn("commercialization_insights", dash_data["sections"])

if __name__ == "__main__":
    unittest.main()
