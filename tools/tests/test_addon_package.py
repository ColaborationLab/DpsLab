from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "installer"))
from build_addon_zip import ADDON_FILES, build  # noqa: E402


class AddonPackageTests(unittest.TestCase):
    def test_public_zip_has_one_addon_root_and_no_saved_variables(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = build(ROOT / "addon" / "DpsLab", Path(temporary) / "DpsLab-0.2.0.zip")
            with ZipFile(output) as archive:
                self.assertEqual(tuple(archive.namelist()), tuple(f"DpsLab/{name}" for name in ADDON_FILES))
                toc = archive.read("DpsLab/DpsLab.toc").decode("utf-8")
                self.assertIn("## Version: 0.2.0", toc)
                self.assertNotIn("SyntheticGuidance.lua", toc)
                self.assertNotIn("DpsLabObservationExport", tuple(archive.namelist()))
