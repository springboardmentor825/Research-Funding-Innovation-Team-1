# backend/app/services/tests/test_funding_matching.py

import unittest
from app.services.funding_matching_service import (
    compute_rule_based_score,
    compute_semantic_score,
    calculate_match_score,
    evaluate_publication_matches,
    evaluate_patent_matches,
    DEFAULT_SCORING_WEIGHTS
)

class TestFundingMatchingServicePrecision(unittest.TestCase):

    def setUp(self):
        self.ai_researcher = {
            "user_id": 16,
            "research_domain": ["Artificial Intelligence", "Computer Science"],
            "technology_areas": ["Natural Language Processing", "Machine Learning", "Deep Learning"],
            "research_interests": ["Large Language Models", "Retrieval-Augmented Generation", "Semantic Search"],
            "keywords": ["ai", "nlp", "rag", "llm", "vector search"],
            "publication_topics": [
                "RAG Based Research Assistant",
                "AI Driven Research Discovery",
                "Quantum Computing Algorithms"
            ],
            "publications_raw": [
                {"id": 101, "title": "RAG Based Research Assistant"},
                {"id": 102, "title": "AI Driven Research Discovery"},
                {"id": 103, "title": "Quantum Computing Algorithms"}
            ],
            "patents_raw": [
                {"id": 201, "title": "AI Funding Recommendation Engine", "technology_domain": "Artificial Intelligence"},
                {"id": 202, "title": "Drip Irrigation Valve Controller", "technology_domain": "Agriculture"}
            ],
            "publication_count": 3,
            "patent_count": 2
        }

        self.ai_funding = {
            "id": 1,
            "title": "Generative AI and Natural Language Processing Research Grant",
            "funder": "Tech Foundation",
            "amount_range": "$100,000 - $500,000",
            "deadline": "2026-12-31",
            "research_domains": ["Artificial Intelligence", "Computer Science"],
            "technology_areas": ["Natural Language Processing", "Machine Learning", "Large Language Models"],
            "keywords": ["ai", "rag", "llm", "nlp"],
            "description": "Funding for advanced generative AI and natural language processing techniques.",
            "status": "active",
            "deadline_status": "open"
        }

        self.agri_funding = {
            "id": 2,
            "title": "Sustainable Crop Irrigation Fellowship",
            "funder": "Agri World",
            "amount_range": "$50,000 - $150,000",
            "deadline": "2026-12-31",
            "research_domains": ["Agriculture", "Soil Science"],
            "technology_areas": ["Drip Irrigation", "Soil Moisture Sensing"],
            "keywords": ["irrigation", "crops", "farming", "soil"],
            "description": "Grant for sustainable agriculture and irrigation efficiency.",
            "status": "active",
            "deadline_status": "open"
        }

    def test_multiword_concept_preservation(self):
        """Test that technology signals preserve intact multi-word concepts (e.g. Natural Language Processing)."""
        match_res = calculate_match_score(self.ai_researcher, self.ai_funding)
        signals = match_res["matched_signals"]
        
        # Must contain phrase 'Natural Language Processing' or 'Machine Learning', NOT split 'PROCESSING, LANGUAGE, NATURAL'
        tech_signal = next((s for s in signals if "Technology match:" in s), "")
        self.assertTrue(bool(tech_signal))
        self.assertIn("Natural Language Processing", tech_signal)
        self.assertNotIn("PROCESSING, LANGUAGE, NATURAL", tech_signal)

    def test_exact_mathematical_score_reconciliation(self):
        """Test that sum(match_breakdown.values()) EXACTLY equals match_score."""
        match_res = calculate_match_score(self.ai_researcher, self.ai_funding)
        breakdown = match_res["match_breakdown"]
        score = match_res["match_score"]

        # Exact mathematical reconciliation
        expected_sum = round(sum(breakdown.values()))
        self.assertEqual(score, expected_sum)

    def test_publication_match_count_strictness(self):
        """Verify publication relevance count is strict and accurate."""
        match_count, matched_pubs, _ = evaluate_publication_matches(self.ai_researcher, self.ai_funding)
        self.assertEqual(match_count, 2)
        
        match_count_agri, matched_pubs_agri, _ = evaluate_publication_matches(self.ai_researcher, self.agri_funding)
        self.assertEqual(match_count_agri, 0)

    def test_unrelated_grant_score_suppression(self):
        """Verify unrelated grants receive low score (< 35) and LOW match_level."""
        match_agri = calculate_match_score(self.ai_researcher, self.agri_funding)
        self.assertLess(match_agri["match_score"], 35)
        self.assertEqual(match_agri["match_level"], "LOW")

if __name__ == "__main__":
    unittest.main()
