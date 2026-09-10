import unittest
from pathlib import Path


class BalanceStatWeightsAddonTests(unittest.TestCase):
    def test_advisor_uses_simulated_weights_and_keeps_standard_fallback(self):
        root = Path(__file__).parents[2]
        lua = (root / "addon/DpsLab/DpsLab.lua").read_text(encoding="utf-8")
        self.assertIn("realAdvisorWeights", lua)
        self.assertIn("simulatedBalanceWeights", lua)
        self.assertIn("GetSyntheticAdvisorGuidance(role)", lua)
