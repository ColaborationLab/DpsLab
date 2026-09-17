from __future__ import annotations

import unittest

from dpslab.comparison_table import comparison_table
from dpslab.item_score_profiles import ScoreWeights
from dpslab.loadout_recommendation import LoadoutComparison


class _Item:
    stats = (("CritRating", 200), ("HasteRating", 100), ("Intellect", 300))


def _weight(build_id: int, crit: float, haste: float) -> ScoreWeights:
    return ScoreWeights("personalized", 11, 102, build_id, (("CritRating", crit), ("HasteRating", haste)), "simc", "Patchwerk", "a" * 64)


class ComparisonTableTests(unittest.TestCase):
    def test_comparison_puts_dps_first_and_combines_equipment_with_weights(self):
        comparison = LoadoutComparison("Listo", ((1, 1000.0), (2, 1100.0)), 2, 11, 102, "dps", score_weights=(_weight(1, 2.0, 1.0), _weight(2, 3.0, 1.0)))
        table = comparison_table(comparison, {1: "Raid", 2: "Raid"}, (_Item(),))
        self.assertEqual(("Raid [1]", "Raid [2] — Mayor DPS"), table.columns)
        rows = {row.label: row for row in table.rows}
        self.assertEqual("DPS resultante", table.rows[0].label)
        self.assertEqual("Equipo: 200\nPeso: 2", rows["Crítico"].cells[0].text)
        self.assertEqual("Equipo: 200\nPeso: 3\nMayor peso", rows["Crítico"].cells[1].text)
        self.assertEqual("-100", rows["DPS resultante"].cells[0].delta)
        self.assertEqual("", rows["DPS resultante"].cells[1].delta)
        self.assertTrue(rows["DPS resultante"].highlighted)
        self.assertEqual("N/D", rows["Maestría"].cells[0].text)

    def test_single_build_has_no_delta_or_comparative_highlight(self):
        comparison = LoadoutComparison("Listo", ((9, 1000.0),), 9, 11, 102, "dps")
        table = comparison_table(comparison, {9: "Solo"})
        rows = {row.label: row for row in table.rows}
        self.assertEqual("", rows["DPS resultante"].cells[0].delta)
        self.assertFalse(rows["DPS resultante"].highlighted)

    def test_table_keeps_at_most_four_build_columns(self):
        comparison = LoadoutComparison("Listo", tuple((index, float(index)) for index in range(1, 6)), 5, 11, 102, "dps")
        table = comparison_table(comparison, {index: f"Build {index}" for index in range(1, 6)})
        self.assertEqual(4, len(table.columns))
        self.assertEqual("Build 4 — Mayor DPS", table.columns[-1])


if __name__ == "__main__":
    unittest.main()
