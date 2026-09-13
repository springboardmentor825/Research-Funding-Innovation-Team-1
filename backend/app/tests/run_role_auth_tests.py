import unittest
import sys
import os

# Add backend root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import User, ResearchProfile
from app.auth import get_password_hash

# Set up clean isolated SQLite in-memory database engine
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestRoleAuthMasterSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=test_engine)
        cls.client = TestClient(app)

    def setUp(self):
        self.db = TestingSessionLocal()

        # Seed demo user accounts requested by user
        self.demo_startup = User(
            full_name="Startup Demo Founder",
            email="startup1@example.com",
            password=get_password_hash("startu1"),
            role="startup_founder",
            auth_provider="email"
        )
        self.demo_startup.account_status = "active"

        self.demo_researcher = User(
            full_name="Researcher Demo User",
            email="test@example.com",
            password=get_password_hash("passowrd123"),
            role="researcher",
            auth_provider="email"
        )
        self.demo_researcher.account_status = "active"

        self.innovation_user = User(
            full_name="Manager User",
            email="manager@example.com",
            password=get_password_hash("password123"),
            role="innovation_manager",
            auth_provider="email"
        )
        self.innovation_user.account_status = "active"

        self.admin_user = User(
            full_name="Admin User",
            email="admin@example.com",
            password=get_password_hash("password123"),
            role="administrator",
            auth_provider="email"
        )
        self.admin_user.account_status = "active"

        self.db.add_all([self.demo_startup, self.demo_researcher, self.innovation_user, self.admin_user])
        self.db.commit()

    def tearDown(self):
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()

    def test_1_signup_as_researcher(self):
        """TEST 1: Signup as Researcher -> DB role = researcher"""
        res = self.client.post("/api/v1/auth/register", json={
            "full_name": "New Researcher",
            "email": "new_res@example.com",
            "password": "Password123!",
            "role": "researcher"
        })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["role"], "researcher")

    def test_2_signup_as_startup_founder(self):
        """TEST 2: Signup as Startup Founder -> DB role = startup_founder"""
        res = self.client.post("/api/v1/auth/register", json={
            "full_name": "New Founder",
            "email": "new_founder@example.com",
            "password": "Password123!",
            "role": "startup_founder"
        })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["role"], "startup_founder")

    def test_3_signup_as_innovation_manager_rejected(self):
        """TEST 3: Signup as Innovation Manager -> Rejected 400 Bad Request"""
        res = self.client.post("/api/v1/auth/register", json={
            "full_name": "New Manager",
            "email": "new_manager@example.com",
            "password": "Password123!",
            "role": "innovation_manager"
        })
        self.assertEqual(res.status_code, 400)

    def test_4_signup_legacy_funder_normalizes_to_startup_founder(self):
        """TEST 4: Try signup with legacy funder -> Normalized to startup_founder"""
        res = self.client.post("/api/v1/auth/register", json={
            "full_name": "Legacy Funder",
            "email": "legacy_funder@example.com",
            "password": "Password123!",
            "role": "funder"
        })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["role"], "startup_founder")

    def test_5_signup_admin_rejected(self):
        """TEST 5: Try signup with admin/administrator -> Forbidden 403"""
        res = self.client.post("/api/v1/auth/register", json={
            "full_name": "Admin Attempt",
            "email": "admin_attempt@example.com",
            "password": "Password123!",
            "role": "administrator"
        })
        self.assertEqual(res.status_code, 403)

    def test_6_login_demo_startup_founder(self):
        """TEST 6: Login startup1@example.com / startu1 -> Success 200 & role=startup_founder"""
        res = self.client.post("/api/v1/auth/login", json={
            "email": "startup1@example.com",
            "password": "startu1",
            "selected_role": "startup_founder"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["role"], "startup_founder")

    def test_7_login_demo_researcher(self):
        """TEST 7: Login test@example.com / passowrd123 -> Success 200 & role=researcher"""
        res = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "passowrd123",
            "selected_role": "researcher"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["role"], "researcher")

    def test_8_startup_dashboard_authorization(self):
        """TEST 8: Startup Founder accesses /api/v1/startup/dashboard -> 200 OK"""
        login_res = self.client.post("/api/v1/auth/login", json={
            "email": "startup1@example.com",
            "password": "startu1",
            "selected_role": "startup_founder"
        })
        token = login_res.json()["access_token"]

        dash_res = self.client.get("/api/v1/startup/dashboard", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(dash_res.status_code, 200)
        self.assertEqual(dash_res.json()["status"], "success")
        self.assertIn("summary", dash_res.json())

    def test_9_startup_sub_endpoints_authorization(self):
        """TEST 9: Startup Founder accesses sub-endpoints -> 200 OK"""
        login_res = self.client.post("/api/v1/auth/login", json={
            "email": "startup1@example.com",
            "password": "startu1",
            "selected_role": "startup_founder"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        self.assertEqual(self.client.get("/api/v1/startup/funding-opportunities", headers=headers).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/startup/technology-opportunities", headers=headers).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/startup/patent-intelligence", headers=headers).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/startup/commercialization", headers=headers).status_code, 200)

    def test_10_researcher_blocked_from_startup_dashboard(self):
        """TEST 10: Researcher test@example.com attempts Startup dashboard -> 403 Forbidden"""
        r_login = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "passowrd123",
            "selected_role": "researcher"
        })
        token = r_login.json()["access_token"]

        blocked_res = self.client.get("/api/v1/startup/dashboard", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(blocked_res.status_code, 403)

    def test_11_existing_google_user_autologin(self):
        """TEST 11: Existing Google Startup Founder -> Reads stored role"""
        g_user = User(
            full_name="Google Founder",
            email="google_founder@example.com",
            role="startup_founder",
            login_type="google",
            auth_provider="google"
        )
        g_user.account_status = "active"
        self.db.add(g_user)
        self.db.commit()

        res = self.client.post("/api/v1/auth/google", json={"email": "google_founder@example.com"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["role"], "startup_founder")

    def test_12_new_google_user_onboarding(self):
        """TEST 12: New Google user -> pending_role_selection -> complete with startup_founder"""
        init_res = self.client.post("/api/v1/auth/google", json={"email": "new_g_user@example.com"})
        self.assertEqual(init_res.json()["status"], "pending_role_selection")
        pending_token = init_res.json()["pending_token"]

        comp_res = self.client.post("/api/v1/auth/google/complete-registration", json={
            "pending_token": pending_token,
            "selected_role": "startup_founder"
        })
        self.assertEqual(comp_res.status_code, 200)
        self.assertEqual(comp_res.json()["role"], "startup_founder")

    def test_13_new_google_user_admin_rejected(self):
        """TEST 13: New Google user -> Attempts Administrator -> 403 Forbidden"""
        init_res = self.client.post("/api/v1/auth/google", json={"email": "new_g_user2@example.com"})
        pending_token = init_res.json()["pending_token"]

        comp_res = self.client.post("/api/v1/auth/google/complete-registration", json={
            "pending_token": pending_token,
            "selected_role": "administrator"
        })
        self.assertEqual(comp_res.status_code, 403)

if __name__ == "__main__":
    unittest.main()
