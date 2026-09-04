import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dpslab.__main__ import _arguments, main


class _Protector:
    pass


class _Workspace:
    controller = None

    def __init__(self, controller):
        type(self).controller = controller

    def run(self):
        return None


class ProfileWorkspaceLauncherTests(unittest.TestCase):
    def test_command_requires_explicit_profile_root(self):
        with self.assertRaises(SystemExit):
            _arguments(["profile-workspace"])

    def test_relative_root_is_rejected_before_protection_or_ui(self):
        with patch("dpslab.__main__.WindowsProfileProtector") as protector:
            code = main(["profile-workspace", "--profile-root", "relative"])
        self.assertEqual(1, code)
        protector.assert_not_called()

    def test_validated_explicit_root_opens_workspace_without_source_supplier(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("dpslab.__main__.WindowsProfileProtector", return_value=_Protector()), patch(
                "dpslab.__main__.inspect_profile"
            ), patch("dpslab.__main__.TkLocalProfileManualWorkspace", _Workspace):
                code = main(["profile-workspace", "--profile-root", str(root)])
        self.assertEqual(0, code)
        self.assertIsNone(_Workspace.controller._snapshot_supplier)
        self.assertEqual(root, _Workspace.controller._root)

    def test_protection_or_root_failure_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("dpslab.__main__.WindowsProfileProtector", side_effect=Exception("raw")):
                self.assertEqual(1, main(["profile-workspace", "--profile-root", str(root)]))
            with patch("dpslab.__main__.WindowsProfileProtector", return_value=_Protector()), patch(
                "dpslab.__main__.inspect_profile", side_effect=Exception("raw")
            ):
                self.assertEqual(1, main(["profile-workspace", "--profile-root", str(root)]))


if __name__ == "__main__":
    unittest.main()
