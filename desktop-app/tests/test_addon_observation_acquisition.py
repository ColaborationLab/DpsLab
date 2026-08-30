from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dpslab.addon_observation_acquisition import (
    AddonObservationAcquisitionError,
    MAX_TRANSPORT_BYTES,
    SyntheticObservationAcquisition,
    acquire_synthetic_observation,
)
from tests.strict_temporary_cleanup import strict_temporary_cleanup
from tests.test_addon_observation_transport import transport


class AddonObservationAcquisitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve() / "_retail_"
        self.root.mkdir()
        self.addCleanup(strict_temporary_cleanup, self.temporary, Path(self.temporary.name))

    def write_candidate(self, account: str, raw: bytes) -> Path:
        directory = self.root / "WTF" / "Account" / account / "SavedVariables"
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / "DpsLab.lua"
        target.write_bytes(raw)
        return target

    def assert_reason(self, reason: str, function, *args, **kwargs) -> None:
        with self.assertRaisesRegex(AddonObservationAcquisitionError, f"^{reason}$"):
            function(*args, **kwargs)

    def test_available_export_returns_only_sanitized_immutable_result(self) -> None:
        raw = b"\r\n" + transport().replace(b"\n", b"\r\n")
        self.write_candidate("synthetic-account", raw)
        result = acquire_synthetic_observation(self.root, wow_process_state="stopped")
        self.assertIsInstance(result, SyntheticObservationAcquisition)
        self.assertEqual("available", result.state)
        self.assertEqual(len(raw), result.byte_count)
        self.assertEqual(64, len(result.source_sha256 or ""))
        self.assertEqual("synthetic.observation.001", result.observation.observation_id)
        self.assertFalse(hasattr(result, "path"))
        self.assertFalse(hasattr(result, "raw"))
        with self.assertRaises((AttributeError, TypeError)):
            result.state = "changed"  # type: ignore[misc]

    def test_no_file_is_absent_without_creating_state(self) -> None:
        result = acquire_synthetic_observation(self.root, wow_process_state="stopped")
        self.assertEqual(SyntheticObservationAcquisition("absent", 0, None, None), result)
        self.assertFalse((self.root / "WTF").exists())

    def test_exact_observed_nil_assignment_is_cleared(self) -> None:
        raw = b"\r\nDpsLabObservationExport = nil\r\n"
        self.write_candidate("synthetic-account", raw)
        result = acquire_synthetic_observation(self.root, wow_process_state="stopped")
        self.assertEqual("cleared", result.state)
        self.assertEqual(len(raw), result.byte_count)
        self.assertIsNone(result.observation)
        self.assertEqual(64, len(result.source_sha256 or ""))

    def test_nonexact_nil_assignment_is_rejected(self) -> None:
        for raw in (
            b"DpsLabObservationExport = nil\r\n",
            b"\r\nDpsLabObservationExport=nil\r\n",
            b"\r\nDpsLabObservationExport = nil\n",
        ):
            with self.subTest(raw=raw):
                target = self.write_candidate("synthetic-account", raw)
                self.assert_reason(
                    "addon_observation_acquisition_transport_invalid",
                    acquire_synthetic_observation,
                    self.root,
                    wow_process_state="stopped",
                )
                target.unlink()

    def test_running_unknown_and_non_string_process_states_fail_closed(self) -> None:
        for state in ("running", "unknown", "", False, None):
            with self.subTest(state=state):
                self.assert_reason(
                    "addon_observation_acquisition_wow_not_stopped",
                    acquire_synthetic_observation,
                    self.root,
                    wow_process_state=state,
                )

    def test_root_must_be_an_existing_absolute_directory(self) -> None:
        for root in (Path("relative"), self.root / "missing"):
            with self.subTest(root=root.name):
                self.assert_reason(
                    "addon_observation_acquisition_root_invalid",
                    acquire_synthetic_observation,
                    root,
                    wow_process_state="stopped",
                )

    def test_multiple_account_candidates_are_ambiguous(self) -> None:
        self.write_candidate("synthetic-a", transport())
        self.write_candidate("synthetic-b", transport())
        self.assert_reason(
            "addon_observation_acquisition_ambiguous",
            acquire_synthetic_observation,
            self.root,
            wow_process_state="stopped",
        )

    def test_nonregular_and_oversized_candidates_are_rejected(self) -> None:
        target = self.write_candidate("synthetic-account", b"x" * (MAX_TRANSPORT_BYTES + 1))
        self.assert_reason(
            "addon_observation_acquisition_file_size_invalid",
            acquire_synthetic_observation,
            self.root,
            wow_process_state="stopped",
        )
        target.unlink()
        target.mkdir()
        self.assert_reason(
            "addon_observation_acquisition_file_invalid",
            acquire_synthetic_observation,
            self.root,
            wow_process_state="stopped",
        )

    def test_reparse_or_symlink_metadata_is_rejected_before_read(self) -> None:
        self.write_candidate("synthetic-account", transport())
        with patch("dpslab.addon_observation_acquisition._is_reparse", return_value=True):
            self.assert_reason(
                "addon_observation_acquisition_reparse_rejected",
                acquire_synthetic_observation,
                self.root,
                wow_process_state="stopped",
            )

    def test_file_replacement_during_open_is_rejected(self) -> None:
        self.write_candidate("synthetic-account", transport())
        real_fstat = os.fstat
        calls = 0

        def changed(descriptor: int):
            nonlocal calls
            value = real_fstat(descriptor)
            calls += 1
            if calls == 2:
                values = list(value)
                values[6] += 1
                return os.stat_result(values)
            return value

        with patch("dpslab.addon_observation_acquisition.os.fstat", side_effect=changed):
            self.assert_reason(
                "addon_observation_acquisition_file_changed",
                acquire_synthetic_observation,
                self.root,
                wow_process_state="stopped",
            )


if __name__ == "__main__":
    unittest.main()
