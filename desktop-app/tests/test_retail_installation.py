from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dpslab.retail_installation import (
    RetailInstallationError,
    RetailInstallationSelection,
    validate_retail_installation_root,
)
from tests.strict_temporary_cleanup import strict_temporary_cleanup


class RetailInstallationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.root = self.base / "_retail_"
        self.addCleanup(strict_temporary_cleanup, self.temporary, Path(self.temporary.name))

    def create_valid(self) -> None:
        self.root.mkdir()
        (self.root / "Wow.exe").write_bytes(b"synthetic-not-executable")
        (self.root / "Interface").mkdir()

    def assert_reason(self, reason: str, root: Path) -> None:
        with self.assertRaisesRegex(RetailInstallationError, f"^{reason}$"):
            validate_retail_installation_root(root)

    def test_valid_selection_is_runtime_only_immutable_and_path_redacted(self) -> None:
        self.create_valid()
        selection = validate_retail_installation_root(self.root)
        self.assertIsInstance(selection, RetailInstallationSelection)
        self.assertEqual(self.root, selection.root)
        self.assertEqual("retail", selection.product)
        self.assertNotIn(str(self.root), repr(selection))
        self.assertIn("<redacted>", str(selection))
        with self.assertRaisesRegex(AttributeError, "selection_immutable"):
            selection._root = self.base  # type: ignore[misc]

    def test_selection_constructor_cannot_be_used_without_validator(self) -> None:
        with self.assertRaisesRegex(TypeError, "selection_factory_required"):
            RetailInstallationSelection(object(), self.root)

    def test_root_must_be_absolute_existing_and_exactly_named_retail(self) -> None:
        for root in (Path("_retail_"), self.base / "missing" / "_retail_", self.base / "retail"):
            with self.subTest(root=root.name):
                self.assert_reason("retail_installation_root_invalid", root)

    def test_exact_direct_executable_and_interface_are_required(self) -> None:
        self.root.mkdir()
        with self.subTest(component="executable"):
            self.assert_reason("retail_installation_executable_missing", self.root)
        (self.root / "Wow.exe").write_bytes(b"x")
        with self.subTest(component="interface"):
            self.assert_reason("retail_installation_interface_missing", self.root)

    def test_similar_or_wrong_case_executable_name_is_not_selected(self) -> None:
        self.root.mkdir()
        (self.root / "WOW.EXE").write_bytes(b"x")
        (self.root / "WowT.exe").write_bytes(b"x")
        (self.root / "Interface").mkdir()
        self.assert_reason("retail_installation_executable_missing", self.root)

    def test_executable_must_be_nonempty_and_regular(self) -> None:
        self.root.mkdir()
        (self.root / "Interface").mkdir()
        executable = self.root / "Wow.exe"
        executable.write_bytes(b"")
        self.assert_reason("retail_installation_executable_invalid", self.root)
        executable.unlink()
        executable.mkdir()
        self.assert_reason("retail_installation_executable_invalid", self.root)

    def test_interface_must_be_a_directory(self) -> None:
        self.root.mkdir()
        (self.root / "Wow.exe").write_bytes(b"x")
        (self.root / "Interface").write_bytes(b"x")
        self.assert_reason("retail_installation_interface_invalid", self.root)

    def test_reparse_metadata_is_rejected_before_selection(self) -> None:
        self.create_valid()
        with patch("dpslab.retail_installation._lstat", side_effect=RetailInstallationError("retail_installation_reparse_rejected")):
            self.assert_reason("retail_installation_reparse_rejected", self.root)

    def test_source_has_no_discovery_execution_persistence_or_network_surface(self) -> None:
        source = (Path(__file__).parents[1] / "src" / "dpslab" / "retail_installation.py").read_text(encoding="utf-8")
        for forbidden in (
            "subprocess", "ctypes", "winreg", "registry", "os.environ", "expandvars",
            "glob(", "rglob(", "walk(", "socket", "http", "write_text", "write_bytes", "read_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
