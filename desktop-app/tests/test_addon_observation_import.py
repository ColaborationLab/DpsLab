from __future__ import annotations

from dataclasses import fields
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dpslab.addon_observation_acquisition import AddonObservationAcquisition
from dpslab.addon_character_identity_transport import (
    parse_character_identity_saved_variable,
)
from dpslab.addon_observation_import import (
    AddonObservationImportResult,
    import_addon_observation,
)
from dpslab.retail_installation import validate_retail_installation_root
from dpslab.retail_installation_store import DOCUMENT_NAME, store_retail_installation
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


class AddonObservationImportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.config = self.base / "config"
        self.config.mkdir()
        self.retail = self.base / "game" / "_retail_"
        self.retail.mkdir(parents=True)
        (self.retail / "Wow.exe").write_bytes(b"synthetic-not-executable")
        (self.retail / "Interface").mkdir()
        self.addCleanup(strict_temporary_cleanup, self.temporary, Path(self.temporary.name))

    def configure(self) -> None:
        selection = validate_retail_installation_root(self.retail)
        store_retail_installation(self.config, selection)

    def write_candidate(self, raw: bytes, account: str = "synthetic-account") -> None:
        directory = self.retail / "WTF" / "Account" / account / "SavedVariables"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "DpsLab.lua").write_bytes(raw)

    def import_stopped(self) -> AddonObservationImportResult:
        with patch(
            "dpslab.addon_observation_acquisition.probe_wow_process_state",
            return_value=WoWProcessState("stopped", 0),
        ):
            return import_addon_observation(self.config)

    def test_absent_selection_is_not_configured_without_acquisition(self) -> None:
        with patch(
            "dpslab.addon_observation_import.acquire_addon_observation_from_installation",
            side_effect=AssertionError("acquisition_forbidden"),
        ):
            result = import_addon_observation(self.config)
        self.assertEqual(AddonObservationImportResult("not_configured", None, 0, None, None), result)

    def test_configured_source_without_file_is_absent(self) -> None:
        self.configure()
        self.assertEqual(AddonObservationImportResult("absent", None, 0, None, None), self.import_stopped())

    def test_exact_cleared_source_is_sanitized(self) -> None:
        self.configure()
        raw = b"\r\nDpsLabObservationExport = nil\r\n"
        self.write_candidate(raw)
        result = self.import_stopped()
        self.assertEqual(("cleared", None, len(raw), None), (result.state, result.reason, result.byte_count, result.observation))
        self.assertEqual(64, len(result.source_sha256 or ""))

    def test_available_source_retains_only_parsed_synthetic_observation(self) -> None:
        self.configure()
        raw = b"\r\n" + transport().replace(b"\n", b"\r\n")
        self.write_candidate(raw)
        result = self.import_stopped()
        self.assertEqual("available", result.state)
        self.assertEqual("synthetic.observation.001", result.observation.observation_id)
        self.assertEqual("synthetic_observation", result.observation_type)
        self.assertEqual(len(raw), result.byte_count)
        self.assertFalse(hasattr(result, "path"))
        self.assertFalse(hasattr(result, "raw"))

    def test_identity_source_is_available_without_public_character_fields(self) -> None:
        self.configure()
        raw = identity_transport(identity_document())
        self.write_candidate(raw)
        result = self.import_stopped()
        self.assertEqual("available", result.state)
        self.assertEqual("character_identity_snapshot", result.observation_type)
        self.assertEqual(2, result.observation.class_id)
        self.assertNotIn("class_id", result.__dict__)
        self.assertFalse(hasattr(result, "path"))
        self.assertFalse(hasattr(result, "raw"))

    def test_registry_source_is_available_without_public_observed_fields(self) -> None:
        self.configure()
        raw = registry_transport(registry_document())
        self.write_candidate(raw)
        result = self.import_stopped()
        self.assertEqual("available", result.state)
        self.assertEqual("class_specialization_registry_snapshot", result.observation_type)
        self.assertEqual(801, result.observation.class_id)
        self.assertNotIn("class_id", result.__dict__)
        self.assertFalse(hasattr(result, "path"))
        self.assertFalse(hasattr(result, "raw"))

    def test_invalid_configuration_maps_to_bounded_reason(self) -> None:
        (self.config / DOCUMENT_NAME).write_bytes(b"not-json")
        self.assertEqual(_rejected("configuration_invalid"), import_addon_observation(self.config))

    def test_running_process_maps_to_bounded_reason(self) -> None:
        self.configure()
        with patch(
            "dpslab.addon_observation_acquisition.probe_wow_process_state",
            return_value=WoWProcessState("running", 1),
        ):
            result = import_addon_observation(self.config)
        self.assertEqual(_rejected("wow_not_stopped"), result)

    def test_invalid_or_ambiguous_source_maps_to_bounded_reason(self) -> None:
        self.configure()
        self.write_candidate(transport(), "synthetic-a")
        self.write_candidate(transport(), "synthetic-b")
        self.assertEqual(_rejected("source_invalid"), self.import_stopped())

    def test_result_is_frozen_closed_and_path_redacted(self) -> None:
        result = AddonObservationImportResult("absent", None, 0, None, None)
        self.assertEqual({"state", "reason", "byte_count", "source_sha256", "observation", "observation_type"}, {field.name for field in fields(result)})
        self.assertNotIn(str(self.retail), repr(result))
        with self.assertRaises((AttributeError, TypeError)):
            result.state = "changed"  # type: ignore[misc]

    def test_unexpected_failures_and_invalid_internal_states_are_not_masked(self) -> None:
        self.configure()
        with patch(
            "dpslab.addon_observation_import.acquire_addon_observation_from_installation",
            side_effect=RuntimeError("synthetic_programming_failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "synthetic_programming_failure"):
                import_addon_observation(self.config)
        with patch(
            "dpslab.addon_observation_import.acquire_addon_observation_from_installation",
            return_value=AddonObservationAcquisition("unexpected", 0, None, None),
        ):
            with self.assertRaisesRegex(RuntimeError, "addon_observation_import_state_invalid"):
                import_addon_observation(self.config)

    def test_internal_type_and_parsed_object_mismatch_is_rejected(self) -> None:
        self.configure()
        parsed_identity = parse_character_identity_saved_variable(
            identity_transport(identity_document())
        )
        with patch(
            "dpslab.addon_observation_import.acquire_addon_observation_from_installation",
            return_value=AddonObservationAcquisition(
                "available", 7, "a" * 64, parsed_identity, "synthetic_observation"
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "addon_observation_import_state_invalid"):
                import_addon_observation(self.config)

    def test_source_has_no_automatic_privileged_or_cross_project_surface(self) -> None:
        source = (Path(__file__).parents[1] / "src" / "dpslab" / "addon_observation_import.py").read_text(encoding="utf-8").lower()
        for forbidden in (
            "print(", "logging", "subprocess", "socket", "http", "winreg",
            "os.environ", "watch", "poll", "thread", "timer", "unlink", "write_",
            "fallout", "simulationcraft",
        ):
            self.assertNotIn(forbidden, source)


def _rejected(reason: str) -> AddonObservationImportResult:
    return AddonObservationImportResult("rejected", reason, 0, None, None)


if __name__ == "__main__":
    unittest.main()
