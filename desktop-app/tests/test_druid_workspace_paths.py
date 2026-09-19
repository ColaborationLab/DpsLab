import tempfile
import unittest
from pathlib import Path

from dpslab.druid_restoration_ui import _clear_paths, _remembered_paths, _save_paths


class DruidWorkspacePathTests(unittest.TestCase):
    def test_checked_paths_are_restored(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "workspace_paths.json"
            _save_paths(path, "D:/SimC/simc.exe", "C:/WoW/AddOns/DpsLab")
            self.assertEqual(("D:/SimC/simc.exe", "C:/WoW/AddOns/DpsLab"), _remembered_paths(path))

    def test_clearing_paths_removes_the_remembered_value(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "workspace_paths.json"
            _save_paths(path, "D:/SimC/simc.exe", "C:/WoW/AddOns/DpsLab")
            _clear_paths(path)
            self.assertIsNone(_remembered_paths(path))

    def test_bundled_simc_marker_never_requires_an_external_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "workspace_paths.json"
            _save_paths(path, "bundled", "C:/WoW/AddOns/DpsLab")
            self.assertEqual(("bundled", "C:/WoW/AddOns/DpsLab"), _remembered_paths(path))

    def test_malformed_settings_are_ignored(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "workspace_paths.json"
            path.write_text('{"simc":"D:/SimC/simc.exe"}\n', encoding="utf-8")
            self.assertIsNone(_remembered_paths(path))
