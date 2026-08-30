from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dpslab.retail_installation import validate_retail_installation_root
from dpslab.retail_installation_store import (
    DOCUMENT_NAME,
    MAX_DOCUMENT_BYTES,
    RetailInstallationStoreError,
    load_retail_installation,
    store_retail_installation,
)
from tests.strict_temporary_cleanup import strict_temporary_cleanup


class RetailInstallationStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.config = self.base / "config"
        self.config.mkdir()
        self.retail = self.base / "game" / "_retail_"
        self.retail.mkdir(parents=True)
        (self.retail / "Wow.exe").write_bytes(b"synthetic-not-executable")
        (self.retail / "Interface").mkdir()
        self.selection = validate_retail_installation_root(self.retail)
        self.addCleanup(strict_temporary_cleanup, self.temporary, Path(self.temporary.name))

    @property
    def target(self) -> Path:
        return self.config / DOCUMENT_NAME

    def assert_reason(self, reason: str, function, *args) -> None:
        with self.assertRaisesRegex(RetailInstallationStoreError, f"^{reason}$"):
            function(*args)

    def test_atomic_round_trip_is_canonical_and_results_are_path_redacted(self) -> None:
        receipt = store_retail_installation(self.config, self.selection)
        self.assertEqual("stored", receipt.state)
        self.assertEqual(self.target.stat().st_size, receipt.byte_count)
        document = json.loads(self.target.read_text(encoding="utf-8"))
        self.assertEqual({"product", "retail_root", "schema_version"}, set(document))
        loaded = load_retail_installation(self.config)
        self.assertEqual("selected", loaded.state)
        self.assertEqual(self.retail, loaded.selection.root)
        self.assertNotIn(str(self.retail), repr(loaded))
        self.assertEqual([], list(self.config.glob("*.tmp")))

    def test_absent_document_is_an_explicit_sanitized_state(self) -> None:
        loaded = load_retail_installation(self.config)
        self.assertEqual(("absent", 0, None), (loaded.state, loaded.byte_count, loaded.selection))

    def test_config_root_must_be_absolute_existing_and_regular_directory(self) -> None:
        for root in (Path("relative"), self.base / "missing"):
            with self.subTest(root=root.name):
                self.assert_reason("retail_installation_store_root_invalid", load_retail_installation, root)
        file_root = self.base / "file-root"
        file_root.write_bytes(b"x")
        self.assert_reason("retail_installation_store_root_invalid", load_retail_installation, file_root)

    def test_reparse_metadata_is_rejected(self) -> None:
        with patch(
            "dpslab.retail_installation_store._lstat",
            side_effect=RetailInstallationStoreError("retail_installation_store_reparse_rejected"),
        ):
            self.assert_reason("retail_installation_store_reparse_rejected", load_retail_installation, self.config)

    def test_duplicate_unknown_and_noncanonical_documents_fail_closed(self) -> None:
        documents = (
            (b'{"product":"retail","product":"retail","retail_root":"x","schema_version":"0.1"}\n', "duplicate_key"),
            (b'{"extra":0,"product":"retail","retail_root":"x","schema_version":"0.1"}\n', "document_fields_invalid"),
            (b'{ "product":"retail","retail_root":"x","schema_version":"0.1"}\n', "document_noncanonical"),
        )
        for raw, reason in documents:
            with self.subTest(reason=reason):
                self.target.write_bytes(raw)
                self.assert_reason(f"retail_installation_store_{reason}", load_retail_installation, self.config)

    def test_malformed_incompatible_and_oversized_documents_fail_closed(self) -> None:
        for raw, reason in (
            (b"not-json", "document_invalid"),
            (b'{"product":"classic","retail_root":"x","schema_version":"0.1"}\n', "document_incompatible"),
            (b"x" * (MAX_DOCUMENT_BYTES + 1), "file_invalid"),
        ):
            with self.subTest(reason=reason):
                self.target.write_bytes(raw)
                self.assert_reason(f"retail_installation_store_{reason}", load_retail_installation, self.config)

    def test_loaded_selection_is_revalidated_and_moved_installation_is_rejected(self) -> None:
        store_retail_installation(self.config, self.selection)
        (self.retail / "Wow.exe").unlink()
        self.assert_reason("retail_installation_store_selection_invalid", load_retail_installation, self.config)

    def test_existing_nonregular_target_is_rejected(self) -> None:
        self.target.mkdir()
        self.assert_reason(
            "retail_installation_store_file_invalid",
            store_retail_installation,
            self.config,
            self.selection,
        )

    def test_failed_replace_preserves_prior_document_and_removes_temporary(self) -> None:
        store_retail_installation(self.config, self.selection)
        before = self.target.read_bytes()
        with patch("dpslab.retail_installation_store.os.replace", side_effect=OSError("synthetic")):
            self.assert_reason(
                "retail_installation_store_write_failed",
                store_retail_installation,
                self.config,
                self.selection,
            )
        self.assertEqual(before, self.target.read_bytes())
        self.assertEqual([], list(self.config.glob("*.tmp")))

    def test_source_has_no_discovery_logging_network_secret_or_delete_surface(self) -> None:
        source = (Path(__file__).parents[1] / "src" / "dpslab" / "retail_installation_store.py").read_text(encoding="utf-8")
        for forbidden in (
            "print(", "logging", "subprocess", "socket", "http", "winreg", "registry",
            "os.environ", "expandvars", "DPAPI", "unlink(target", "rmtree", "remove(target",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
