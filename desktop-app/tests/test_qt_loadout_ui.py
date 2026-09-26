from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui, QtTest, QtWidgets

from dpslab.item_score_profiles import ScoreWeights
from dpslab.loadout_recommendation import LoadoutComparison
from dpslab.dpsfoundry_theme import STATE_DETAILS, StatePanel
from dpslab.qt_loadout_ui import ComparisonTableWidget, QtLoadoutWorkspace, _load_language, _save_language, _load_theme, _save_theme
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
        self.assertIn("(-10.00 %)", widget.item(0, 1).text())
        widget.show_table(comparison_table(result, {1: "A", 2: "B"}), "Statistic")
        self.assertEqual("Statistic", widget.horizontalHeaderItem(0).text())

    def test_workspace_is_a_native_qt_window(self):
        workspace = QtLoadoutWorkspace(Path("C:/workspace"))
        self.assertIsInstance(workspace, QtWidgets.QMainWindow)
        from dpslab.foundry_gear import GearCards
        self.assertIsInstance(workspace._table, GearCards)
        self.assertIn("DpsFoundry Core", workspace.windowTitle())
        workspace.close()

    def test_badges_follow_running_error_and_idle_without_simulation(self):
        workspace = QtLoadoutWorkspace(Path('C:/workspace'))
        workspace._running = True
        workspace._sync_shell()
        self.assertEqual('loading', workspace._simulation_badge.property('state'))
        workspace._running = False
        workspace._simulation_error = True
        workspace._sync_shell()
        self.assertEqual('error', workspace._simulation_badge.property('state'))
        workspace._simulation_error = False
        workspace._export = ''
        workspace._comparison = None
        workspace._sync_shell()
        self.assertEqual('empty', workspace._simulation_badge.property('state'))
        self.assertEqual('empty', workspace._import_badge.property('state'))
        workspace.close()

    def test_build_selection_glow_keeps_multiple_selected_rows(self):
        from dpslab.dpsfoundry_theme import FoundrySelectionDelegate
        workspace = QtLoadoutWorkspace(Path('C:/workspace'))
        self.assertIsInstance(workspace._builds.itemDelegate(), FoundrySelectionDelegate)
        workspace._builds.addItems(['A', 'B', 'C'])
        workspace._builds.item(0).setSelected(True)
        workspace._builds.item(2).setSelected(True)
        workspace.show()
        self.app.processEvents()
        self.assertFalse(workspace._builds.grab().isNull())
        self.assertEqual(['A', 'C'], [item.text() for item in workspace._builds.selectedItems()])
        self.assertTrue(workspace._run.property('primary'))
        workspace.close()

    def test_navigation_icon_states_preserve_shapes_and_selection(self):
        from dpslab.dpsfoundry_theme import FoundryNavButton, THEMES
        button = FoundryNavButton('Simulation')
        button.set_icon_theme('simulation', THEMES['foundry'], False)
        keys = [icon.cacheKey() for icon in button._icon_states.values()]
        self.assertEqual(3, len(set(keys)))
        self.assertEqual(button.icon().cacheKey(), button._icon_states['metal'].cacheKey())
        button.set_icon_theme('simulation', THEMES['foundry'], True)
        self.assertEqual(button.icon().cacheKey(), button._icon_states['active'].cacheKey())
        button.set_icon_theme('simulation', THEMES['arcane_vanguard'], False)
        self.assertFalse(button.icon().isNull())
        button.close()

    def test_foundry_wordmark_has_separate_module_and_readable_descriptor(self):
        from dpslab.dpsfoundry_theme import foundry_icon
        workspace = QtLoadoutWorkspace(Path("C:/workspace"))
        labels = workspace.findChildren(QtWidgets.QLabel)
        self.assertEqual(["DPSFOUNDRY"], [label.text() for label in labels if label.property("role") == "brand"])
        self.assertEqual(["/ CORE"], [label.text() for label in labels if label.property("role") == "brandModule"])
        self.assertEqual(1, sum(label.property("role") == "brandDescriptor" for label in labels))
        self.assertFalse(foundry_icon("forge").isNull())
        self.assertFalse(workspace._brand_art.pixmap().isNull())
        self.assertIn('DpsFoundry Core', workspace._brand_art.accessibleName())
        workspace.close()

    def test_resize_cursor_does_not_leak_into_content(self):
        from dpslab.foundry_chrome import FoundryFrame
        window = QtWidgets.QMainWindow()
        frame = FoundryFrame()
        window.setCentralWidget(frame)
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(16,16,16,16)
        panel = QtWidgets.QWidget()
        QtWidgets.QVBoxLayout(panel).addWidget(QtWidgets.QLabel('Content'))
        layout.addWidget(panel)
        window.show()
        self.app.processEvents()
        event = QtGui.QMouseEvent(QtCore.QEvent.Type.MouseMove, QtCore.QPointF(1,80), QtCore.QPointF(1,80), QtCore.Qt.MouseButton.NoButton, QtCore.Qt.MouseButton.NoButton, QtCore.Qt.KeyboardModifier.NoModifier)
        self.app.sendEvent(frame, event)
        self.assertEqual(QtCore.Qt.CursorShape.SizeHorCursor, frame.cursor().shape())
        self.assertEqual(QtCore.Qt.CursorShape.ArrowCursor, panel.cursor().shape())
        self.assertEqual(QtCore.Qt.CursorShape.ArrowCursor, panel.findChild(QtWidgets.QLabel).cursor().shape())
        window.close()

    def test_simc_path_is_never_a_player_input(self):
        from unittest.mock import patch
        with TemporaryDirectory() as temporary, patch('dpslab.qt_loadout_ui._bundled_simc', return_value='packaged/simc.exe'):
            workspace = QtLoadoutWorkspace(Path(temporary))
            self.assertTrue(workspace._simc_path.isHidden())
            self.assertEqual('packaged/simc.exe', workspace._simc_path.text())
            workspace.close()

    def test_language_switch_updates_all_routes_without_losing_user_data(self):
        from unittest.mock import patch
        with TemporaryDirectory() as temporary, patch('dpslab.qt_loadout_ui._save_language'):
            workspace = QtLoadoutWorkspace(Path(temporary))
            workspace._show_export(_export())
            workspace._profile_name.setText('My custom profile')
            workspace._imports.setText('Custom|ABCDEF')
            original_snapshot = workspace._snapshot
            result = LoadoutComparison('Resultado', ((1, 900.0), (2, 1000.0)), 2, 11, 102, 'damage')
            workspace._comparison = result
            for locale, character, run in [('en', 'Character', 'Run real comparison'), ('pt-BR', 'Personagem', 'Executar comparação real'), ('es', 'Personaje', 'Ejecutar comparación real')]:
                workspace._set_language(locale)
                self.app.processEvents()
                self.assertIn(character, workspace._nav['character'].text())
                self.assertEqual(workspace._t('simulation.run', run), workspace._run.text())
                self.assertEqual('My custom profile', workspace._profile_name.text())
                self.assertEqual('Custom|ABCDEF', workspace._imports.text())
                self.assertIs(original_snapshot, workspace._snapshot)
                self.assertIs(result, workspace._comparison)
                self.assertEqual(3, workspace._builds.count())
                self.assertEqual(workspace._t('shell.state.success', ''), workspace._compare_state._title.text())
            workspace.close()

    def test_every_section_has_art_and_alternative_themes_have_no_foundry_frame(self):
        from dpslab.foundry_chrome import FoundryBackdrop
        from unittest.mock import patch
        with TemporaryDirectory() as temporary, patch('dpslab.qt_loadout_ui._save_theme'):
            workspace = QtLoadoutWorkspace(Path(temporary))
            for index in workspace._pages.values():
                page = workspace._stack.widget(index)
                self.assertTrue(isinstance(page, FoundryBackdrop) or page.findChildren(FoundryBackdrop))
            for theme in ('foundry', 'arcane_vanguard', 'runebound_command', 'celestial_foundry'):
                workspace._set_theme(theme)
                workspace.show()
                self.app.processEvents()
                self.assertFalse(workspace.grab().isNull())
            workspace.close()

    def test_foundry_shell_has_all_core_routes_and_preserves_controlled_state(self):
        with TemporaryDirectory() as temporary:
            workspace = QtLoadoutWorkspace(Path(temporary).resolve())
            self.assertEqual({"setup", "home", "character", "simulation", "compare", "recommendations", "link", "settings"}, set(workspace._pages))
            self.assertEqual(workspace._pages["simulation"], workspace._stack.currentIndex())
            self.assertEqual(['simulation', 'compare', 'character'], list(workspace._pages)[:3])
            self.assertTrue(workspace._stack.widget(workspace._pages['simulation']).isAncestorOf(workspace._detect))
            self.assertTrue(workspace._stack.widget(workspace._pages['settings']).isAncestorOf(workspace._addon_path))
            workspace._select_page("setup")
            self.assertEqual(workspace._pages["setup"], workspace._stack.currentIndex())
            self.assertTrue(workspace._nav["setup"].property("active"))
            workspace._show_export(_export())
            self.assertEqual("ready", workspace._home_state.state)
            self.assertEqual("ready", workspace._link_state.state)
            workspace._select_page("simulation")
            self.assertEqual(3, workspace._builds.count())
            workspace.close()

    def test_dashboard_uses_winning_build_weights_and_clears_old_result(self):
        from dpslab.foundry_dashboard import FoundryDashboard
        dashboard = FoundryDashboard(lambda page: None, lambda key, fallback: fallback)
        result = LoadoutComparison("Done", ((1, 900.0), (2, 1000.0)), 2, 11, 102, "damage", score_weights=(ScoreWeights("personalized", 11, 102, 1, (("Intellect", 1.0),), "simc", "Patchwerk", "a" * 64), ScoreWeights("personalized", 11, 102, 2, (("Intellect", 2.0), ("CritRating", 1.5)), "simc", "Patchwerk", "b" * 64)))
        dashboard.update_data(result, {1: "A", 2: "B"}, 2, None, True)
        self.assertEqual("1,000", dashboard.values[0].text())
        self.assertEqual("2", dashboard.values[2].text())
        self.assertEqual("success", dashboard.state.state)
        self.assertEqual(2, dashboard.weight_rows.count())
        result_text = lambda: ' '.join(label.text() for label in dashboard.findChildren(QtWidgets.QLabel) if label.isVisibleTo(dashboard))
        self.assertIn('(-10.00 %)', result_text())
        dashboard.reference.setCurrentIndex(dashboard.reference.findData(1))
        self.assertIn('(+11.11 %)', result_text())
        dashboard.update_data(None, {}, 0, None, False)
        self.assertEqual("—", dashboard.values[0].text())
        self.assertEqual("empty", dashboard.state.state)
        self.assertEqual(1, dashboard.weight_rows.count())
        self.assertFalse(dashboard.reference.isEnabled())
        dashboard.close()

    def test_theme_preference_and_textual_states_are_bounded(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "theme.json"
            self.assertEqual("foundry", _load_theme(path))
            _save_theme(path, "celestial_foundry")
            self.assertEqual("celestial_foundry", _load_theme(path))
        panel = StatePanel()
        for state in STATE_DETAILS:
            panel.set_state(state)
            self.assertEqual(state, panel.state)
            self.assertTrue(panel._title.text())

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
        self.assertEqual(workspace._t('ui.selection', ''), workspace._status.text())
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
            self.assertIn("1,000 DPS", " ".join(label.text() for label in workspace._table.findChildren(QtWidgets.QLabel)))
            self.assertIn(workspace._result_summary(workspace._comparison), workspace._status.text())
            workspace.close()


if __name__ == "__main__":
    unittest.main()
