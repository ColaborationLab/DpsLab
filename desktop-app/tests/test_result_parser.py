from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from tests.strict_temporary_cleanup import strict_temporary_cleanup
from unittest.mock import patch

from dpslab.result_parser import ResultSummaryError, summarize_run


FIXTURES = Path(__file__).parent / "fixtures"


class ResultParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run_dir = self.root / "results" / "runs" / "test-run"
        self.run_dir.mkdir(parents=True)
        shutil.copyfile(FIXTURES / "minimal_simc_result.json", self.run_dir / "simc.json")
        shutil.copyfile(FIXTURES / "minimal_run_metadata.json", self.run_dir / "metadata.json")
        (self.run_dir / "stderr.txt").write_text("", encoding="utf-8")

    def tearDown(self) -> None:
        strict_temporary_cleanup(self.temporary, self.root)

    def _metadata(self) -> dict[str, object]:
        return json.loads((self.run_dir / "metadata.json").read_text(encoding="utf-8"))

    def _write_metadata(self, metadata: dict[str, object]) -> None:
        (self.run_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    def test_valid_run_creates_versioned_summary(self) -> None:
        summary = summarize_run(self.run_dir, root=self.root)
        self.assertEqual(summary.schema_version, "0.3")
        self.assertEqual(summary.identification.character, "Anonymous")
        self.assertEqual(summary.identification.character_class, "mage")
        self.assertEqual(summary.identification.specialization, "frost")
        self.assertEqual(summary.scenario.fight_style, "Patchwerk")
        self.assertEqual(summary.dps.mean, 1000.0)
        self.assertEqual(summary.dps.mean_error, 10.0)
        self.assertEqual(summary.dps.observed_relative_error_percent, 1.0)
        self.assertIsNone(summary.dps.simc_displayed_error)
        self.assertEqual(summary.execution.duration_seconds, 1.5)
        self.assertEqual(summary.execution.simc_elapsed_seconds, 0.25)
        self.assertEqual(summary.execution.total_simulated_combat_seconds, 4500.0)
        self.assertEqual(summary.summary_generation.status, "completed")

    def test_optional_fields_and_incomplete_metadata_become_null(self) -> None:
        document = {
            "sim": {
                "players": [
                    {"name": "Anonymous", "collected_data": {"dps": {}}}
                ]
            }
        }
        (self.run_dir / "simc.json").write_text(json.dumps(document), encoding="utf-8")
        self._write_metadata({})
        summary = summarize_run(self.run_dir, root=self.root)
        self.assertIsNone(summary.identification.simc_version)
        self.assertIsNone(summary.identification.character_class)
        self.assertIsNone(summary.scenario.iterations_requested)
        self.assertIsNone(summary.dps.mean)
        self.assertIsNone(summary.execution.simulation_status)
        self.assertIsNone(summary.execution.simc_elapsed_seconds)
        self.assertIsNone(summary.execution.total_simulated_combat_seconds)
        self.assertIsNone(summary.diagnostics.profile_hash_verified)

    def test_mean_combat_length_is_not_used_as_elapsed_or_total_time(self) -> None:
        document = json.loads((self.run_dir / "simc.json").read_text(encoding="utf-8"))
        statistics = document["sim"]["statistics"]
        statistics.pop("elapsed_time_seconds")
        statistics["simulation_length"].pop("sum")
        (self.run_dir / "simc.json").write_text(json.dumps(document), encoding="utf-8")
        summary = summarize_run(self.run_dir, root=self.root)
        self.assertIsNone(summary.execution.simc_elapsed_seconds)
        self.assertIsNone(summary.execution.total_simulated_combat_seconds)

    def test_total_combat_sum_is_never_assigned_to_simc_elapsed(self) -> None:
        summary = summarize_run(self.run_dir, root=self.root)
        self.assertEqual(summary.execution.total_simulated_combat_seconds, 4500.0)
        self.assertEqual(summary.execution.simc_elapsed_seconds, 0.25)
        self.assertNotEqual(
            summary.execution.total_simulated_combat_seconds,
            summary.execution.simc_elapsed_seconds,
        )

    def test_missing_internal_elapsed_time_remains_null_without_stdout(self) -> None:
        document = json.loads((self.run_dir / "simc.json").read_text(encoding="utf-8"))
        document["sim"]["statistics"].pop("elapsed_time_seconds")
        (self.run_dir / "simc.json").write_text(json.dumps(document), encoding="utf-8")
        summary = summarize_run(self.run_dir, root=self.root)
        self.assertIsNone(summary.execution.simc_elapsed_seconds)
        self.assertEqual(summary.execution.total_simulated_combat_seconds, 4500.0)

    def test_tolerant_wall_seconds_stdout_fallback(self) -> None:
        document = json.loads((self.run_dir / "simc.json").read_text(encoding="utf-8"))
        document["sim"]["statistics"].pop("elapsed_time_seconds")
        (self.run_dir / "simc.json").write_text(json.dumps(document), encoding="utf-8")
        (self.run_dir / "stdout.txt").write_text(
            "  Wall Seconds : 0.75  \nSimSeconds = 4500.0\n", encoding="utf-8"
        )
        summary = summarize_run(self.run_dir, root=self.root)
        self.assertEqual(summary.execution.simc_elapsed_seconds, 0.75)
        self.assertEqual(summary.execution.total_simulated_combat_seconds, 4500.0)

    def test_invalid_json_is_rejected_without_partial_summary(self) -> None:
        (self.run_dir / "simc.json").write_text("not json", encoding="utf-8")
        with self.assertRaisesRegex(ResultSummaryError, "JSON válido"):
            summarize_run(self.run_dir, root=self.root)
        self.assertFalse((self.run_dir / "run_summary.json").exists())

    def test_empty_player_list_is_rejected(self) -> None:
        (self.run_dir / "simc.json").write_text('{"sim":{"players":[]}}', encoding="utf-8")
        with self.assertRaisesRegex(ResultSummaryError, "ningún personaje"):
            summarize_run(self.run_dir, root=self.root)

    def test_100_requested_and_99_samples_adds_informative_warning(self) -> None:
        summary = summarize_run(self.run_dir, root=self.root)
        self.assertEqual(summary.scenario.iterations_requested, 100)
        self.assertEqual(summary.scenario.iteration_mode, "fixed")
        self.assertEqual(summary.scenario.iterations_parameter, 100)
        self.assertEqual(summary.scenario.dps_sample_count, 99)
        self.assertTrue(summary.diagnostics.requested_iterations_differ_from_sample_count)
        self.assertIn("100", summary.diagnostics.warnings[-1])
        self.assertIn("99", summary.diagnostics.warnings[-1])

    def test_adaptive_iterations_are_not_compared_with_samples(self) -> None:
        metadata = self._metadata()
        metadata.update(iterations=0, target_error=0.1)
        self._write_metadata(metadata)
        summary = summarize_run(self.run_dir, root=self.root)
        self.assertEqual(summary.scenario.iteration_mode, "adaptive")
        self.assertEqual(summary.scenario.iterations_parameter, 0)
        self.assertIsNone(summary.scenario.iterations_requested)
        self.assertEqual(summary.scenario.iterations_completed, 100)
        self.assertEqual(summary.scenario.dps_sample_count, 99)
        self.assertEqual(summary.scenario.target_error_percent, 0.1)
        self.assertIsNone(summary.diagnostics.requested_iterations_differ_from_sample_count)
        self.assertTrue(summary.diagnostics.completed_iterations_differ_from_dps_sample_count)
        self.assertFalse(any("solicitadas" in item for item in summary.diagnostics.warnings))

    def test_reported_error_is_distinct_from_target_and_observed_error(self) -> None:
        metadata = self._metadata()
        metadata.update(iterations=0, target_error=0.1)
        self._write_metadata(metadata)
        (self.run_dir / "stdout.txt").write_text(
            "DPS=1000 DPS-Error=20/0.25%\nIterations = 100 (50, 50)\n",
            encoding="utf-8",
        )
        summary = summarize_run(self.run_dir, root=self.root)
        self.assertEqual(summary.scenario.target_error_percent, 0.1)
        self.assertEqual(summary.dps.observed_relative_error_percent, 1.0)
        self.assertEqual(summary.dps.simc_displayed_error.absolute_value, 20.0)
        self.assertEqual(summary.dps.simc_displayed_error.value_percent, 0.25)
        self.assertEqual(summary.dps.simc_displayed_error.source, "stdout")
        self.assertEqual(summary.dps.simc_displayed_error.locator, "DPS-Error=<absolute>/<percent>%")
        self.assertEqual(summary.dps.simc_displayed_error.semantic_role, "observed_error")

    def test_stderr_empty_and_nonempty_preserve_warning_text(self) -> None:
        empty = summarize_run(self.run_dir, root=self.root)
        self.assertFalse(empty.diagnostics.stderr_nonempty)
        warning = "Original warning text: field failed verification."
        (self.run_dir / "stderr.txt").write_text(warning + "\n", encoding="utf-8")
        nonempty = summarize_run(self.run_dir, root=self.root)
        self.assertTrue(nonempty.diagnostics.stderr_nonempty)
        self.assertIn(warning, nonempty.diagnostics.warnings)

    def test_summarize_is_idempotent_and_preserves_source_hashes(self) -> None:
        sources = [self.run_dir / "simc.json", self.run_dir / "metadata.json"]
        before = [sha256(path.read_bytes()).hexdigest() for path in sources]
        first = summarize_run(self.run_dir, root=self.root)
        first_bytes = (self.run_dir / "run_summary.json").read_bytes()
        second = summarize_run(self.run_dir, root=self.root)
        after = [sha256(path.read_bytes()).hexdigest() for path in sources]
        self.assertEqual(first, second)
        self.assertEqual((self.run_dir / "run_summary.json").read_bytes(), first_bytes)
        self.assertEqual(before, after)

    def test_atomic_replace_is_used(self) -> None:
        output = self.run_dir / "run_summary.json"
        output.write_text("old summary", encoding="utf-8")
        real_replace = os.replace
        with patch("dpslab.result_parser.os.replace", wraps=real_replace) as replace:
            summarize_run(self.run_dir, root=self.root)
        replace.assert_called_once()
        self.assertTrue(json.loads(output.read_text(encoding="utf-8")))
        self.assertEqual(list(self.run_dir.glob(".run_summary.*.tmp")), [])

    def test_failed_atomic_replace_keeps_previous_summary(self) -> None:
        output = self.run_dir / "run_summary.json"
        output.write_text("old summary", encoding="utf-8")
        with patch("dpslab.result_parser.os.replace", side_effect=OSError("replace failed")):
            with self.assertRaisesRegex(ResultSummaryError, "atómicamente"):
                summarize_run(self.run_dir, root=self.root)
        self.assertEqual(output.read_text(encoding="utf-8"), "old summary")
        self.assertEqual(list(self.run_dir.glob(".run_summary.*.tmp")), [])

    def test_profile_hash_verified_true_false_and_null(self) -> None:
        profile = self.root / "profiles" / "anonymous.simc"
        profile.parent.mkdir()
        profile.write_text("profile", encoding="utf-8")
        digest = sha256(profile.read_bytes()).hexdigest()
        metadata = self._metadata()
        metadata.update(profile_sha256_before=digest, profile_sha256_after=digest)
        self._write_metadata(metadata)
        self.assertTrue(summarize_run(self.run_dir, root=self.root).diagnostics.profile_hash_verified)

        metadata["profile_sha256_after"] = "0" * 64
        self._write_metadata(metadata)
        self.assertFalse(summarize_run(self.run_dir, root=self.root).diagnostics.profile_hash_verified)

        metadata.pop("profile_sha256_before")
        self._write_metadata(metadata)
        self.assertIsNone(summarize_run(self.run_dir, root=self.root).diagnostics.profile_hash_verified)

    def test_old_schema_01_has_null_scenario_fields(self) -> None:
        metadata = self._metadata()
        metadata["schema_version"] = "0.1"
        self._write_metadata(metadata)
        summary = summarize_run(self.run_dir, root=self.root)
        self.assertEqual(summary.schema_version, "0.3")
        self.assertIsNone(summary.scenario.scenario_id)
        self.assertIsNone(summary.scenario.scenario_sha256)
        self.assertIsNone(summary.scenario.scenario_hash_verified)
        self.assertIsNone(summary.variant.variant_id)

    def test_schema_02_without_variant_has_null_variant_fields(self) -> None:
        metadata = self._metadata()
        metadata["schema_version"] = "0.2"
        self._write_metadata(metadata)
        summary = summarize_run(self.run_dir, root=self.root)
        self.assertEqual(summary.schema_version, "0.3")
        self.assertIsNone(summary.variant.variant_id)
        self.assertIsNone(summary.variant.effective_profile)

    def test_summary_scenario_hash_verified_true_false_and_null(self) -> None:
        metadata = self._metadata()
        metadata.update(
            scenario_id="anonymous",
            scenario_name="Anonymous",
            scenario_file="scenarios/anonymous.toml",
            scenario_sha256_before="a" * 64,
            scenario_sha256_after="a" * 64,
            scenario_hash_verified=True,
            scenario_effective_parameters={"iterations": 0, "target_error": 0.05},
        )
        self._write_metadata(metadata)
        verified = summarize_run(self.run_dir, root=self.root)
        self.assertTrue(verified.scenario.scenario_hash_verified)
        self.assertEqual(verified.scenario.scenario_sha256, "a" * 64)

        metadata["scenario_sha256_after"] = "b" * 64
        metadata["scenario_hash_verified"] = False
        self._write_metadata(metadata)
        self.assertFalse(summarize_run(self.run_dir, root=self.root).scenario.scenario_hash_verified)

        for key in ("scenario_sha256_before", "scenario_sha256_after", "scenario_hash_verified"):
            metadata.pop(key)
        self._write_metadata(metadata)
        self.assertIsNone(summarize_run(self.run_dir, root=self.root).scenario.scenario_hash_verified)


if __name__ == "__main__":
    unittest.main()
