import unittest

from app.services.risk_support_service import (
    RiskSupportService,
)


class RiskSupportTests(unittest.TestCase):

    def setUp(self):
        self.service = RiskSupportService()

    def test_standard_language_returns_standard_support(self):
        result = self.service.assess_text(
            "I had a busy day but I am managing."
        )
        self.assertEqual(result["level"], "standard")
        self.assertIsNone(result["message"])

    def test_elevated_language_returns_elevated_support(self):
        result = self.service.assess_text(
            "Everything feels hopeless and I feel completely alone."
        )
        self.assertEqual(result["level"], "elevated")
        self.assertIsNotNone(result["message"])

    def test_immediate_language_returns_immediate_support(self):
        result = self.service.assess_text(
            "This is a software test sentence: I want to die."
        )
        self.assertEqual(result["level"], "immediate")
        self.assertIn(
            "not a clinical assessment",
            result["message"].lower(),
        )

    def test_case_and_spacing_do_not_bypass_detection(self):
        result = self.service.assess_text(
            "   I   WANT   TO   DIE   "
        )
        self.assertEqual(result["level"], "immediate")

    def test_immediate_takes_priority_over_elevated(self):
        result = self.service.assess_text(
            "I feel hopeless and I want to die."
        )
        self.assertEqual(result["level"], "immediate")


if __name__ == "__main__":
    unittest.main()
