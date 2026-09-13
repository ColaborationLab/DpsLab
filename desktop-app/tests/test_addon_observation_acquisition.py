from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dpslab.addon_observation_acquisition import (
    AddonObservationAcquisitionError,
    MAX_LIVE_ANALYSIS_AGE_SECONDS,
    MAX_TRANSPORT_BYTES,
    SyntheticObservationAcquisition,
    acquire_addon_observation,
    acquire_recent_live_analysis_export,
    acquire_synthetic_observation,
    acquire_synthetic_observation_from_installation,
    acquire_synthetic_observation_with_probe,
)
from dpslab.retail_installation import validate_retail_installation_root
from dpslab.wow_process_state import WoWProcessState
from tests.strict_temporary_cleanup import strict_temporary_cleanup
from tests.test_addon_observation_transport import transport
from tests.test_addon_character_identity_transport import (
    document as identity_document,
    transport as identity_transport,
)
from tests.test_addon_specialization_registry_transport import (
    document as registry_document,
    transport as registry_transport,
)
from tests.test_addon_live_analysis_saved_variable import transport as live_analysis_transport


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
        self.assertEqual("synthetic_observation", result.observation_type)
        self.assertFalse(hasattr(result, "path"))
        self.assertFalse(hasattr(result, "raw"))
        with self.assertRaises((AttributeError, TypeError)):
            result.state = "changed"  # type: ignore[misc]

    def test_no_file_is_absent_without_creating_state(self) -> None:
        result = acquire_synthetic_observation(self.root, wow_process_state="stopped")
        self.assertEqual(SyntheticObservationAcquisition("absent", 0, None, None), result)
        self.assertFalse((self.root / "WTF").exists())

    def test_identity_export_is_strictly_selected_and_retained_only_in_memory(self) -> None:
        raw = identity_transport(identity_document())
        self.write_candidate("synthetic-account", raw)
        result = acquire_addon_observation(self.root, wow_process_state="stopped")
        self.assertEqual("available", result.state)
        self.assertEqual("character_identity_snapshot", result.observation_type)
        self.assertEqual(2, result.observation.class_id)
        self.assertFalse(hasattr(result, "path"))
        self.assertFalse(hasattr(result, "raw"))

    def test_unsupported_identity_type_has_no_parser_fallback(self) -> None:
        value = identity_document()
        value["observation_type"] = "character_identity_future"
        self.write_candidate("synthetic-account", identity_transport(value))
        self.assert_reason(
            "addon_observation_acquisition_transport_invalid",
            acquire_addon_observation,
            self.root,
            wow_process_state="stopped",
        )

    def test_registry_export_is_strictly_selected_and_retained_only_in_memory(self) -> None:
        raw = registry_transport(registry_document())
        self.write_candidate("synthetic-account", raw)
        result = acquire_addon_observation(self.root, wow_process_state="stopped")
        self.assertEqual("available", result.state)
        self.assertEqual("class_specialization_registry_snapshot", result.observation_type)
        self.assertEqual(801, result.observation.class_id)
        self.assertEqual(4, len(result.observation.specializations))
        self.assertFalse(hasattr(result, "path"))
        self.assertFalse(hasattr(result, "raw"))

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

    def test_live_export_must_be_recent(self) -> None:
        target = self.write_candidate("live-account", live_analysis_transport())
        modified = target.stat().st_mtime_ns
        with patch(
            "dpslab.addon_observation_acquisition.time.time_ns",
            return_value=modified + (MAX_LIVE_ANALYSIS_AGE_SECONDS * 1_000_000_000) + 1,
        ):
            self.assert_reason(
                "live_analysis_acquisition_stale",
                acquire_recent_live_analysis_export,
                self.root,
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

    def test_probed_entry_acquires_only_after_stopped_result(self) -> None:
        raw = b"\r\nDpsLabObservationExport = nil\r\n"
        self.write_candidate("synthetic-account", raw)
        with patch(
            "dpslab.addon_observation_acquisition.probe_wow_process_state",
            return_value=WoWProcessState("stopped", 0),
        ):
            result = acquire_synthetic_observation_with_probe(self.root)
        self.assertEqual("cleared", result.state)

    def test_probed_entry_blocks_running_and_unknown_before_file_discovery(self) -> None:
        for state, count in (("running", 1), ("unknown", 0)):
            with self.subTest(state=state):
                with patch(
                    "dpslab.addon_observation_acquisition.probe_wow_process_state",
                    return_value=WoWProcessState(state, count),
                ):
                    with patch(
                        "dpslab.addon_observation_acquisition._candidate_files",
                        side_effect=AssertionError("file_discovery_forbidden"),
                    ):
                        self.assert_reason(
                            "addon_observation_acquisition_wow_not_stopped",
                            acquire_synthetic_observation_with_probe,
                            self.root,
                        )

    def test_validated_installation_is_rechecked_before_probed_acquisition(self) -> None:
        (self.root / "Wow.exe").write_bytes(b"synthetic-not-executable")
        (self.root / "Interface").mkdir()
        raw = b"\r\nDpsLabObservationExport = nil\r\n"
        self.write_candidate("synthetic-account", raw)
        selection = validate_retail_installation_root(self.root)
        with patch(
            "dpslab.addon_observation_acquisition.probe_wow_process_state",
            return_value=WoWProcessState("stopped", 0),
        ):
            result = acquire_synthetic_observation_from_installation(selection)
        self.assertEqual("cleared", result.state)
        self.assert_reason(
            "addon_observation_acquisition_selection_invalid",
            acquire_synthetic_observation_from_installation,
            self.root,
        )


if __name__ == "__main__":
    unittest.main()
