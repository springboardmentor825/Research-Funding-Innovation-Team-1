# backend/app/services/tests/test_funding_eligibility.py

import unittest
from datetime import date, timedelta
from app.services.funding_eligibility_service import (
    is_deadline_valid,
    is_status_active,
    check_research_stage,
    check_geographic_scope,
    check_basic_eligibility
)

class TestFundingEligibilityService(unittest.TestCase):

    def test_deadline_filtering(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # 1. Expired deadline -> Excluded
        passed, status, msg = is_deadline_valid(yesterday)
        self.assertFalse(passed)
        self.assertEqual(status, "expired")
        self.assertIn("has passed", msg)

        # 2. Deadline today -> Open/closing_soon -> Passed
        passed, status, msg = is_deadline_valid(today)
        self.assertTrue(passed)
        self.assertEqual(status, "closing_soon")

        # 3. Deadline future -> Open -> Passed
        passed, status, msg = is_deadline_valid(tomorrow)
        self.assertTrue(passed)
        self.assertEqual(status, "open")

        # 4. Missing deadline -> Unknown -> Passed with flag
        passed, status, msg = is_deadline_valid(None)
        self.assertTrue(passed)
        self.assertEqual(status, "unknown")

    def test_status_filtering(self):
        # 1. Active status -> Passed
        passed, status, msg = is_status_active("active")
        self.assertTrue(passed)
        self.assertEqual(status, "passed")

        # 2. Open status -> Passed
        passed, status, msg = is_status_active("open")
        self.assertTrue(passed)

        # 3. Closed status -> Failed / Excluded
        passed, status, msg = is_status_active("closed")
        self.assertFalse(passed)
        self.assertEqual(status, "failed")

        # 4. Draft status -> Failed / Excluded
        passed, status, msg = is_status_active("draft")
        self.assertFalse(passed)

        # 5. Missing status -> Failed / Excluded
        passed, status, msg = is_status_active(None)
        self.assertFalse(passed)

    def test_geographic_scope_filtering(self):
        us_researcher = {
            "organization": "Stanford University",
            "email": "sarah.jenkins@stanford.edu"
        }
        india_researcher = {
            "organization": "IISc Bangalore",
            "email": "priya.sharma@iisc.ac.in"
        }

        # 1. Global funding -> Passed for both
        passed, status, _ = check_geographic_scope(us_researcher, "Global")
        self.assertTrue(passed)
        passed, status, _ = check_geographic_scope(india_researcher, "International")
        self.assertTrue(passed)

        # 2. US only funding -> Passed for US researcher, Failed for India researcher
        passed, status, msg = check_geographic_scope(us_researcher, "United States only")
        self.assertTrue(passed)
        
        passed, status, msg = check_geographic_scope(india_researcher, "United States only")
        self.assertFalse(passed)
        self.assertIn("does not match researcher location", msg)

    def test_eligibility_text_filtering(self):
        student_researcher = {
            "designation": "Undergraduate Student",
            "organization": "Stanford University"
        }
        
        passed, status, msg = check_basic_eligibility(student_researcher, "Postdoctoral researchers only")
        self.assertFalse(passed)
        self.assertIn("requires postdoctoral status", msg)

if __name__ == "__main__":
    unittest.main()
