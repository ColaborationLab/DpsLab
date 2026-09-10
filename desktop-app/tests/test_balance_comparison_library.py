from pathlib import Path
import tempfile
import unittest

from dpslab.balance_comparison_library import BalanceComparisonLibraryError, list_cases, save_case
from dpslab.druid_balance_recommendation import DruidBalanceComparison
from dpslab.balance_stat_weights import BalanceStatWeights


class BalanceComparisonLibraryTests(unittest.TestCase):
    def test_player_requested_case_is_saved_and_reopened_without_runner(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = DruidBalanceComparison("Usa el loadout 2", ((1, 100.0), (2, 110.0)), 2)
            saved = save_case(Path(temporary).resolve(), "Prueba Balance", "DPSLAB-LIVE-ANALYSIS-0.1\n{}", result, now=1)
            self.assertEqual(saved, list_cases(Path(temporary).resolve())[0])

    def test_library_rejects_unselected_or_invalid_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(BalanceComparisonLibraryError, "input_invalid"):
                save_case(Path(temporary).resolve(), "", "", object())

    def test_case_keeps_real_stat_weights_for_later_review(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = DruidBalanceComparison("Usa el loadout 2", ((1, 100.0), (2, 110.0)), 2, BalanceStatWeights((("Intellect", 1.2),)))
            saved = save_case(Path(temporary).resolve(), "Pesos", "DPSLAB-LIVE-ANALYSIS-0.1\n{}", result, now=1)
            self.assertEqual((("Intellect", 1.2),), saved.stat_weights)
            self.assertEqual(saved, list_cases(Path(temporary).resolve())[0])
