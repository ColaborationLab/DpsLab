from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtTest, QtWidgets

from dpslab.item_score_profiles import ScoreWeights
from dpslab.loadout_recommendation import LoadoutComparison
from dpslab.qt_loadout_ui import ComparisonTableWidget, QtLoadoutWorkspace, _load_language, _save_language
from dpslab.addon_live_analysis_transport import PREFIX, canonical_live_analysis_bytes


def _export(loadouts=3):
    document = {"schema_version":"0.9","observation_type":"live_manual_analysis_export","compatibility":{"wow_product":"retail","build":69587,"interface_version":120100},"subject":{"class_id":11,"specialization_id":102,"role":"damage","level":90,"max_level":90,"race_id":4,"character_name":"Drena","realm_name":"Quel'Thalas"},"analysis_context":{"talent_loadouts":[{"config_id":index,"name":f"Build {index}","talent_string":f"ABC{chr(64 + index)}","simulatable":True,"unavailable_reason":""} for index in range(1, loadouts + 1)]},"equipment":{"equipped":[{"item_id":1,"item_level":100,"item_link":"item:1","location":1,"slot":"slot_1","source":"equipped","stats":{"Intellect":10,"CritRating":5}}]},"safety":{"contains_direct_identifiers":True,"executable":False,"no_automation":True}}
    return PREFIX + canonical_live_analysis_bytes(document).decode()


class QtLoadoutUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_native_table_displays_side_by_side_results(self):
        widget = ComparisonTableWidget()
        result = LoadoutComparison("Listo", ((1, 900.0), (2, 1000.0)), 2, 11, 102, "dps", score_weights=(ScoreWeights("personalized", 11, 102, 1, (("CritRating", 1.0),), "simc", "Patchwerk", "a" * 64), ScoreWeights("personalized", 11, 102, 2, (("CritRating", 2.0),), "simc", "Patchwerk", "b" * 64)))
        from dpslab.comparison_table import comparison_table
        widget.show_table(comparison_table(result, {1: "A", 2: "B"}))
        self.assertEqual(3, widget.columnCount())
        self.assertEqual("A", widget.horizontalHeaderItem(1).text())
        self.assertIn("DPS", " ".join(widget.item(row, 0).text() for row in range(widget.rowCount())))
        self.assertIn("(-100)", widget.item(0, 1).text())
        widget.show_table(comparison_table(result, {1: "A", 2: "B"}), "Statistic")
        self.assertEqual("Statistic", widget.horizontalHeaderItem(0).text())

    def test_workspace_is_a_native_qt_window(self):
        workspace = QtLoadoutWorkspace(Path("C:/workspace"))
        self.assertIsInstance(workspace, QtWidgets.QMainWindow)
        self.assertIsInstance(workspace._table, ComparisonTableWidget)
        workspace.close()

    def test_language_preference_preserves_auto_and_explicit_locale(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "language.json"
            _save_language(path, "auto")
            self.assertEqual(_load_language(path), "auto")
            _save_language(path, "ptBR")
            self.assertEqual(_load_language(path), "pt-BR")

    def test_workspace_keeps_profile_and_external_build_actions(self):
        with TemporaryDirectory() as temporary:
            workspace = QtLoadoutWorkspace(Path(temporary).resolve())
            workspace._show_export(_export())
            self.assertEqual(3, workspace._builds.count())
            workspace._save_profile()
            self.assertEqual(1, workspace._profiles.count())
            workspace._imports.setText("Externa|EFGH")
            workspace._save_imports()
            self.assertIn("Externa", tuple(workspace._names.values()))
            workspace._export = ""
            workspace._open_profile()
            self.assertTrue(workspace._export)
            workspace.close()

    def test_workspace_rejects_five_selected_builds_before_simulation(self):
        workspace = QtLoadoutWorkspace(Path("C:/workspace").resolve())
        workspace._show_export(_export(5))
        for index in range(workspace._builds.count()):
            workspace._builds.item(index).setSelected(True)
        workspace._start_run()
        self.assertIn("entre una y cuatro", workspace._status.text())
        workspace.close()

    def test_workspace_runs_without_blocking_and_renders_result(self):
        def runner(_export, _simc, _addon, **_kwargs):
            return LoadoutComparison("Simulación lista", ((1, 900.0), (2, 1000.0), (3, 950.0)), 2, 11, 102, "dps", score_weights=(ScoreWeights("personalized", 11, 102, 1, (("CritRating", 1.0),), "simc", "Patchwerk", "a" * 64), ScoreWeights("personalized", 11, 102, 2, (("CritRating", 2.0),), "simc", "Patchwerk", "b" * 64), ScoreWeights("personalized", 11, 102, 3, (("CritRating", 1.5),), "simc", "Patchwerk", "c" * 64)))
        with TemporaryDirectory() as temporary:
            workspace = QtLoadoutWorkspace(Path(temporary).resolve(), recommendation_runner=runner)
            workspace._show_export(_export())
            workspace._simc_path.setText(__file__)
            workspace._start_run()
            for _ in range(40):
                self.app.processEvents()
                if not workspace._running: break
                QtTest.QTest.qWait(10)
            self.assertFalse(workspace._running)
            self.assertEqual(4, workspace._table.columnCount())
            self.assertIn("Simulación lista", workspace._status.text())
            workspace.close()


if __name__ == "__main__":
    unittest.main()
