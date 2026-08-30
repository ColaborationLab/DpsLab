from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dpslab.__main__ import _arguments, main
from dpslab.addon_observation_import import AddonObservationImportResult
from dpslab.addon_character_identity_transport import CharacterIdentitySnapshot
from dpslab.retail_installation_store import load_retail_installation
from tests.strict_temporary_cleanup import strict_temporary_cleanup


class AddonObservationCliTests(unittest.TestCase):
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

    def invoke(self, argv: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch("sys.stdout", stdout), patch("sys.stderr", stderr):
            code = main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_arguments_require_explicit_roots(self) -> None:
        configured = _arguments([
            "addon-configure", "--config-root", str(self.config),
            "--retail-root", str(self.retail),
        ])
        imported = _arguments(["addon-import", "--config-root", str(self.config)])
        self.assertEqual(("addon-configure", self.config, self.retail), (configured.command, configured.config_root, configured.retail_root))
        self.assertEqual(("addon-import", self.config), (imported.command, imported.config_root))

    def test_configure_persists_selection_and_never_prints_paths(self) -> None:
        code, stdout, stderr = self.invoke([
            "addon-configure", "--config-root", str(self.config),
            "--retail-root", str(self.retail),
        ])
        payload = json.loads(stdout)
        self.assertEqual((0, "configured"), (code, payload["state"]))
        self.assertGreater(payload["byte_count"], 0)
        self.assertEqual("selected", load_retail_installation(self.config).state)
        self.assertEqual("", stderr)
        self.assertNotIn(str(self.config), stdout)
        self.assertNotIn(str(self.retail), stdout)

    def test_invalid_configuration_uses_static_error_without_private_path(self) -> None:
        private = self.base / "private" / "invalid"
        code, stdout, stderr = self.invoke([
            "addon-configure", "--config-root", str(self.config),
            "--retail-root", str(private),
        ])
        self.assertEqual(1, code)
        self.assertEqual("", stdout)
        self.assertEqual("error: retail_installation_root_invalid\n", stderr)
        self.assertNotIn(str(private), stderr)

    def test_import_not_configured_is_closed_json_without_probe(self) -> None:
        with patch(
            "dpslab.addon_observation_import.acquire_addon_observation_from_installation",
            side_effect=AssertionError("probe_forbidden"),
        ):
            code, stdout, stderr = self.invoke([
                "addon-import", "--config-root", str(self.config)
            ])
        self.assertEqual(0, code)
        self.assertEqual({
            "byte_count": 0,
            "observation_available": False,
            "observation_type": None,
            "reason": None,
            "source_sha256": None,
            "state": "not_configured",
        }, json.loads(stdout))
        self.assertEqual("", stderr)

    def test_available_import_outputs_presence_not_observation_fields(self) -> None:
        result = AddonObservationImportResult(
            "available", None, 7, "a" * 64, object(), "character_identity_snapshot"
        )
        with patch("dpslab.__main__.import_addon_observation", return_value=result):
            code, stdout, stderr = self.invoke([
                "addon-import", "--config-root", str(self.config)
            ])
        payload = json.loads(stdout)
        self.assertEqual(0, code)
        self.assertTrue(payload["observation_available"])
        self.assertEqual("character_identity_snapshot", payload["observation_type"])
        self.assertEqual({"byte_count", "observation_available", "observation_type", "reason", "source_sha256", "state"}, set(payload))
        self.assertNotIn("observation_id", stdout)
        self.assertEqual("", stderr)

    def test_identity_import_never_emits_snapshot_values(self) -> None:
        snapshot = CharacterIdentitySnapshot(987654, 876543, 37, 4567, "healer", 88, 29, 1_999_999_999)
        result = AddonObservationImportResult(
            "available", None, 17, "b" * 64, snapshot, "character_identity_snapshot"
        )
        with patch("dpslab.__main__.import_addon_observation", return_value=result):
            code, stdout, stderr = self.invoke([
                "addon-import", "--config-root", str(self.config)
            ])
        self.assertEqual(0, code)
        self.assertEqual("character_identity_snapshot", json.loads(stdout)["observation_type"])
        for private_value in ("987654", "876543", "4567", "healer", "1999999999"):
            self.assertNotIn(private_value, stdout)
        self.assertEqual("", stderr)

    def test_rejected_import_is_sanitized_and_uses_exit_two(self) -> None:
        result = AddonObservationImportResult("rejected", "wow_not_stopped", 0, None, None)
        with patch("dpslab.__main__.import_addon_observation", return_value=result):
            code, stdout, stderr = self.invoke([
                "addon-import", "--config-root", str(self.config)
            ])
        self.assertEqual(2, code)
        self.assertEqual("wow_not_stopped", json.loads(stdout)["reason"])
        self.assertEqual("", stderr)

    @patch("subprocess.Popen", side_effect=AssertionError("process_forbidden"))
    def test_addon_commands_never_launch_a_process(self, process) -> None:
        self.invoke(["addon-import", "--config-root", str(self.config)])
        self.invoke([
            "addon-configure", "--config-root", str(self.config),
            "--retail-root", str(self.retail),
        ])
        process.assert_not_called()

    def test_handlers_do_not_discover_appdata_or_emit_private_values(self) -> None:
        import inspect
        import dpslab.__main__ as module
        source = inspect.getsource(module._addon_configure) + inspect.getsource(module._addon_import)
        for forbidden in ("environ", "APPDATA", "LOCALAPPDATA", "registry", "winreg", "watch", "poll", "raw", "observation_id"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
