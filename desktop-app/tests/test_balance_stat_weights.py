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

    def test_missing_scale_factors_stays_unavailable(self):
        with tempfile.TemporaryDirectory() as temporary:
            (Path(temporary) / "simc.json").write_text("{}", encoding="utf-8")
            self.assertIsNone(load_balance_stat_weights(Path(temporary)))
