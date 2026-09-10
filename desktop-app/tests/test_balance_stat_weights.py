import json
from pathlib import Path
import tempfile
import unittest

from dpslab.balance_stat_weights import load_balance_stat_weights


class BalanceStatWeightsTests(unittest.TestCase):
    def test_reads_only_positive_finite_simc_scale_factors(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "simc.json"
            path.write_text(json.dumps({"sim": {"players": [{"scale_factors": {"intellect": 1.2, "crit_rating": 0.8, "haste_rating": -1, "mastery_rating": True}}]}}), encoding="utf-8")
            weights = load_balance_stat_weights(path.parent)
            self.assertEqual((("Intellect", 1.2), ("CritRating", 0.8)), weights.values)
            self.assertIn("CritRating=0.800", weights.pawn_compatible())
            self.assertEqual(16.0, weights.score_item((("Intellect", 10), ("CritRating", 5))))

    def test_missing_scale_factors_stays_unavailable(self):
        with tempfile.TemporaryDirectory() as temporary:
            (Path(temporary) / "simc.json").write_text("{}", encoding="utf-8")
            self.assertIsNone(load_balance_stat_weights(Path(temporary)))

    def test_reads_current_simc_short_stat_names(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "simc.json"
            path.write_text(json.dumps({"sim": {"players": [{"scale_factors": {"Agi": 0.6, "Crit": 17.9, "Haste": 12.9, "Mastery": 17.6, "Vers": 14.3}}]}}), encoding="utf-8")
            weights = load_balance_stat_weights(path.parent)
            self.assertEqual(("Agility", "CritRating", "HasteRating", "MasteryRating", "VersatilityRating"), tuple(name for name, _ in weights.values))
            self.assertEqual(179.0, weights.score_item((("CritRating", 10),)))
