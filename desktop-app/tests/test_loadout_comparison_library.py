from pathlib import Path
import tempfile
import unittest

from dpslab.loadout_comparison_library import list_cases, save_case
from dpslab.loadout_recommendation import LoadoutComparison


class LoadoutComparisonLibraryTests(unittest.TestCase):
    def test_case_keeps_the_class_spec_metric_context(self):
        comparison = LoadoutComparison("Usa Furia: 120 DPS frente a 100 DPS (20.0% mejor).", ((1, 100.0), (2, 120.0)), 2, 1, 72, "damage")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            saved = save_case(root, "Guerrero", "DPSLAB-LIVE-ANALYSIS-0.1\n{}", comparison, now=1)
            self.assertEqual(saved, list_cases(root)[0])
