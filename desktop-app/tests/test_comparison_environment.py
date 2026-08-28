from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.strict_temporary_cleanup import strict_temporary_directory
from unittest.mock import patch

from dpslab.comparison_environment import dpslab_source_identity, software_record, source_tree_inventory, source_tree_sha256


ROOT = Path(__file__).resolve().parents[2]


class ComparisonEnvironmentTests(unittest.TestCase):
    def test_source_tree_hash_is_deterministic_and_content_sensitive(self) -> None:
        with strict_temporary_directory() as source:
            (source / "b.py").write_text("b", encoding="utf-8")
            (source / "a.py").write_text("a", encoding="utf-8")
            first = source_tree_sha256(source)
            self.assertEqual(first, source_tree_sha256(source))
            (source / "a.py").write_text("changed", encoding="utf-8")
        self.assertNotEqual(first, source_tree_sha256(source))

    def test_source_inventory_is_portable_and_sorted(self) -> None:
        with strict_temporary_directory() as temporary:
            source = temporary / "src"
            (source / "nested").mkdir(parents=True)
            (source / "z.py").write_text("z", encoding="utf-8")
            (source / "nested/a.py").write_text("a", encoding="utf-8")
            self.assertEqual(source_tree_inventory(source), ("nested/a.py", "z.py"))

    @patch("dpslab.comparison_environment.shutil.which", return_value=None)
    def test_missing_git_uses_tree_identity(self, _which: object) -> None:
        identity = dpslab_source_identity(ROOT)
        self.assertEqual(identity.source_identity_kind, "dpslab_source_tree_sha256_v1")
        self.assertEqual(len(identity.source_tree_sha256), 64)

    def test_software_record_contains_scipy_and_platform(self) -> None:
        record = software_record(ROOT)
        self.assertRegex(record.scipy.version, r"^\d+\.\d+")
        self.assertEqual(record.scipy.requirement, ">=1.11.0,<2.0.0")
        self.assertTrue(record.platform.system)


if __name__ == "__main__":
    unittest.main()
