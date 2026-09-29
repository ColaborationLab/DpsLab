from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "installer"))
from build_installer import REQUIRED, build  # noqa: E402


class InstallerPackageTests(TestCase):
    def test_rejects_an_incomplete_package_before_starting_the_compiler(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "installer_input_invalid"):
                build(root / "ISCC.exe", root / "package", root / "output")

    def test_invokes_the_local_compiler_for_a_complete_package(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary); package = root / "package"; package.mkdir()
            iscc = root / "ISCC.exe"; iscc.touch()
            for item in REQUIRED:
                path = package / item; path.parent.mkdir(parents=True, exist_ok=True); path.touch()
            with patch("build_installer.subprocess.run") as run:
                run.return_value.returncode = 0
                self.assertEqual(0, build(iscc, package, root / "output"))
            self.assertIn("/DSourceDir=", " ".join(run.call_args.args[0]))
