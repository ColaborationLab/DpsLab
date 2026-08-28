from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import Mock, patch

from tests.strict_temporary_cleanup import strict_temporary_cleanup, strict_temporary_directory

from dpslab.config import SimulationConfig
from dpslab.runner import (
    SimulationOutputError,
    SimulationProcessError,
    SimulationTimeoutError,
    SummaryPostprocessingError,
    VariantIntegrityError,
    SimulationRunError,
    reserve_run,
    run_simulation,
)
from dpslab.result_parser import ResultSummaryError
from dpslab.scenario import load_scenario
from dpslab.variant import load_variant


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REAL_PROFILE = REPOSITORY_ROOT / "profiles" / "flasil.simc"


class TemporaryCleanupTests(unittest.TestCase):
    @staticmethod
    def _directory_not_empty_error() -> OSError:
        error = OSError("directory not empty")
        error.winerror = 145  # type: ignore[attr-defined]
        return error

    @patch("tests.strict_temporary_cleanup.time.sleep")
    @patch("tests.strict_temporary_cleanup.shutil.rmtree")
    def test_directory_not_empty_is_retried_strictly(self, remove: Mock, sleep: Mock) -> None:
        temporary = Mock()
        temporary.cleanup.side_effect = self._directory_not_empty_error()
        remove.side_effect = [self._directory_not_empty_error(), None]

        strict_temporary_cleanup(temporary, Path("temporary-root"))

        self.assertEqual(remove.call_count, 2)
        sleep.assert_called_once_with(0.05)

    def test_other_cleanup_errors_are_not_suppressed(self) -> None:
        temporary = Mock()
        temporary.cleanup.side_effect = OSError("unexpected cleanup failure")

        with self.assertRaisesRegex(OSError, "unexpected cleanup failure"):
            strict_temporary_cleanup(temporary, Path("temporary-root"))

    @patch("tests.strict_temporary_cleanup.strict_temporary_cleanup")
    @patch("tests.strict_temporary_cleanup.tempfile.TemporaryDirectory")
    def test_context_manager_delegates_to_strict_cleanup(self, created: Mock, cleanup: Mock) -> None:
        temporary = Mock()
        temporary.name = "temporary-root"
        created.return_value = temporary

        with strict_temporary_directory() as root:
            self.assertEqual(Path("temporary-root"), root)

        cleanup.assert_called_once_with(temporary, Path("temporary-root"))


class SimulationRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.profile = self.root / "profiles" / "test.simc"
        self.profile.parent.mkdir()
        self.profile.write_text('mage="Tester"\n', encoding="utf-8")
        self.exe = self.root / "simc.exe"
        self.exe.touch()
        self.runs_dir = self.root / "results" / "runs"

    def tearDown(self) -> None:
        strict_temporary_cleanup(self.temporary, self.root)

    def _config(self, *, html: bool = False, timeout: float = 600) -> SimulationConfig:
        return SimulationConfig(
            simc_exe=self.exe,
            runs_dir=self.runs_dir,
            timeout_seconds=timeout,
            threads=4,
            generate_html=html,
        )

    @staticmethod
    def _successful_process(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        json_arg = next(argument for argument in args if argument.startswith("json="))
        json_path = Path(json_arg.removeprefix("json=").split(",", 1)[0])
        json_path.write_text(
            '{"version":"1100-01","git_revision":"test-revision",'
            '"sim":{"players":[{"name":"Tester",'
            '"collected_data":{"dps":{"mean":1,"count":1}}}]}}',
            encoding="utf-8",
        )
        html_args = [argument for argument in args if argument.startswith("html=")]
        if html_args:
            Path(html_args[0].removeprefix("html=")).write_text("<html></html>", encoding="utf-8")
        return subprocess.CompletedProcess(args, 0, "SimulationCraft completed", "")

    @patch("dpslab.runner.subprocess.run")
    def test_success_uses_argument_list_and_writes_artifacts(self, process: object) -> None:
        process.side_effect = self._successful_process  # type: ignore[attr-defined]

        result = run_simulation(self.profile, self._config(html=True), root=self.root)

        self.assertEqual(result.status, "completed")
        self.assertEqual(result.simc_version, "1100-01")
        call_args, call_kwargs = process.call_args  # type: ignore[attr-defined]
        self.assertIsInstance(call_args[0], list)
        self.assertFalse(call_kwargs["shell"])
        self.assertEqual(call_kwargs["timeout"], 600)
        self.assertIn("threads=4", call_args[0])
        self.assertTrue(any(arg.endswith(",version=2,pretty_print=1") for arg in call_args[0]))
        self.assertTrue(result.artifacts.json_file.is_file())
        self.assertTrue(result.artifacts.html_file and result.artifacts.html_file.is_file())
        metadata = json.loads(result.artifacts.metadata_file.read_text(encoding="utf-8"))
        self.assertEqual(metadata["profile"], "profiles/test.simc")
        self.assertFalse(any(str(self.root) in arg for arg in metadata["parameters"]))
        self.assertEqual(metadata["simc_version"], "1100-01")
        self.assertEqual(metadata["simc_revision"], "test-revision")

    @patch("dpslab.runner.subprocess.run")
    def test_each_run_uses_a_new_directory(self, process: object) -> None:
        process.side_effect = self._successful_process  # type: ignore[attr-defined]
        first = run_simulation(self.profile, self._config(), root=self.root)
        second = run_simulation(self.profile, self._config(), root=self.root)
        self.assertNotEqual(first.artifacts.run_dir, second.artifacts.run_dir)

    @patch("dpslab.runner.subprocess.run")
    def test_reserved_run_is_exclusive_and_consumed_once(self, process: object) -> None:
        process.side_effect = self._successful_process  # type: ignore[attr-defined]
        reservation = reserve_run(self.runs_dir, run_id="reserved-run")
        self.assertTrue(reservation.run_directory.is_dir())
        with self.assertRaises(SimulationRunError):
            reserve_run(self.runs_dir, run_id="reserved-run")
        result = run_simulation(self.profile, self._config(), root=self.root, reservation=reservation)
        self.assertEqual(result.run_id, "reserved-run")
        self.assertTrue(reservation.consumed)
        with self.assertRaisesRegex(SimulationRunError, "consumida"):
            run_simulation(self.profile, self._config(), root=self.root, reservation=reservation)

    def test_reservation_cannot_be_reassigned_and_can_be_abandoned(self) -> None:
        reservation = reserve_run(self.runs_dir, comparison_execution_id="e1", member_id="m1")
        with self.assertRaisesRegex(SimulationRunError, "pertenece"):
            reservation.consume(comparison_execution_id="e1", member_id="m2")
        reservation.abandon(comparison_execution_id="e1", member_id="m1")
        self.assertEqual(reservation.status, "abandoned")
        self.assertIsNotNone(reservation.abandoned_at)
        with self.assertRaises(SimulationRunError):
            reservation.consume(comparison_execution_id="e1", member_id="m1")

    @patch("dpslab.runner.subprocess.run")
    def test_invocation_is_durable_on_timeout(self, process: object) -> None:
        process.side_effect = subprocess.TimeoutExpired("simc", 3)
        reservation = reserve_run(self.runs_dir)
        with self.assertRaises(SimulationTimeoutError) as caught:
            run_simulation(self.profile, self._config(timeout=3), root=self.root, reservation=reservation)
        metadata = json.loads((caught.exception.run_dir / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["invocation"]["portable_argv"][0], "<SIMC_EXE>")
        self.assertFalse(metadata["invocation"]["shell"])
        self.assertIsNotNone(caught.exception.invocation)

    @patch("dpslab.runner.subprocess.run")
    def test_smoke_parameters_are_individual_list_arguments(self, process: object) -> None:
        process.side_effect = self._successful_process  # type: ignore[attr-defined]
        config = SimulationConfig(
            simc_exe=self.exe,
            runs_dir=self.runs_dir,
            timeout_seconds=180,
            threads=1,
            generate_html=True,
            iterations=100,
            max_time=60,
            vary_combat_length=0,
        )
        run_simulation(self.profile, config, root=self.root)
        command = process.call_args.args[0]  # type: ignore[attr-defined]
        self.assertIsInstance(command, list)
        self.assertIn("threads=1", command)
        self.assertIn("iterations=100", command)
        self.assertIn("max_time=60", command)
        self.assertIn("vary_combat_length=0", command)
        self.assertTrue(any(argument.startswith("html=") for argument in command))
        self.assertFalse(process.call_args.kwargs["shell"])  # type: ignore[attr-defined]
        self.assertFalse(any(argument.startswith("fight_style=") for argument in command))
        self.assertFalse(any(argument.startswith("desired_targets=") for argument in command))
        self.assertFalse(any(argument.startswith("target_error=") for argument in command))

    @patch("dpslab.runner.subprocess.run")
    def test_seed_and_invocation_hashes_are_recorded_without_real_argv(self, process: object) -> None:
        process.side_effect = self._successful_process  # type: ignore[attr-defined]
        config = SimulationConfig(
            simc_exe=self.exe,
            runs_dir=self.runs_dir,
            threads=2,
            iterations=5000,
            seed=1367750201,
            executable_source="local_config",
        )
        result = run_simulation(self.profile, config, root=self.root)
        command = process.call_args.args[0]  # type: ignore[attr-defined]
        self.assertIn("seed=1367750201", command)
        self.assertIsNotNone(result.invocation)
        assert result.invocation is not None
        self.assertEqual(result.invocation.portable_argv[0], "<SIMC_EXE>")
        self.assertFalse(any(str(self.root) in arg for arg in result.invocation.portable_argv))
        self.assertEqual(len(result.invocation.process_argv_sha256), 64)
        self.assertEqual(result.invocation.executable_source, "local_config")

    @patch("dpslab.runner.subprocess.run")
    def test_scenario_arguments_metadata_hashes_and_file_integrity(self, process: object) -> None:
        process.side_effect = self._successful_process  # type: ignore[attr-defined]
        source = self.root / "scenarios" / "valid_scenario.toml"
        source.parent.mkdir()
        source.write_bytes((Path(__file__).parent / "fixtures" / "valid_scenario.toml").read_bytes())
        before = source.read_bytes()
        scenario = load_scenario(source)
        config = SimulationConfig(
            simc_exe=self.exe,
            runs_dir=self.runs_dir,
            threads=2,
            iterations=0,
            max_time=120,
            vary_combat_length=0.1,
            fight_style="Patchwerk",
            desired_targets=1,
            target_error=0.05,
            scenario=scenario,
        )
        result = run_simulation(self.profile, config, root=self.root)
        command = process.call_args.args[0]  # type: ignore[attr-defined]
        for expected in (
            "threads=2",
            "iterations=0",
            "max_time=120",
            "vary_combat_length=0.1",
            "fight_style=Patchwerk",
            "desired_targets=1",
            "target_error=0.05",
        ):
            self.assertIn(expected, command)
        metadata = json.loads(result.artifacts.metadata_file.read_text(encoding="utf-8"))
        self.assertEqual(metadata["schema_version"], "0.3")
        self.assertEqual(metadata["scenario_id"], "anonymous_scenario_v1")
        self.assertEqual(metadata["scenario_file"], "scenarios/valid_scenario.toml")
        self.assertEqual(metadata["scenario_sha256_before"], scenario.source_sha256)
        self.assertEqual(metadata["scenario_sha256_after"], scenario.source_sha256)
        self.assertTrue(metadata["scenario_hash_verified"])
        self.assertEqual(source.read_bytes(), before)

    @patch("dpslab.runner.subprocess.run")
    def test_timeout_is_recorded(self, process: object) -> None:
        process.side_effect = subprocess.TimeoutExpired("simc", 3, output="partial", stderr="slow")  # type: ignore[attr-defined]
        with self.assertRaises(SimulationTimeoutError) as caught:
            run_simulation(self.profile, self._config(timeout=3), root=self.root)
        metadata = json.loads((caught.exception.run_dir / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["status"], "timeout")
        self.assertEqual(metadata["timeout_seconds"], 3)
        self.assertEqual((caught.exception.run_dir / "stdout.txt").read_text(), "partial")

    @patch("dpslab.runner.subprocess.run")
    def test_nonzero_exit_code_is_recorded(self, process: object) -> None:
        process.return_value = subprocess.CompletedProcess([], 2, "out", "bad input")  # type: ignore[attr-defined]
        with self.assertRaises(SimulationProcessError) as caught:
            run_simulation(self.profile, self._config(), root=self.root)
        metadata = json.loads((caught.exception.run_dir / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["exit_code"], 2)
        self.assertEqual((caught.exception.run_dir / "stderr.txt").read_text(), "bad input")

    @patch("dpslab.runner.subprocess.run")
    def test_missing_json_is_rejected(self, process: object) -> None:
        process.return_value = subprocess.CompletedProcess([], 0, "", "")  # type: ignore[attr-defined]
        with self.assertRaises(SimulationOutputError):
            run_simulation(self.profile, self._config(), root=self.root)

    @patch("dpslab.runner.subprocess.run")
    def test_invalid_json_is_rejected(self, process: object) -> None:
        def invalid_json(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            json_arg = next(argument for argument in args if argument.startswith("json="))
            json_path = Path(json_arg.removeprefix("json=").split(",", 1)[0])
            json_path.write_text("not json", encoding="utf-8")
            return subprocess.CompletedProcess(args, 0, "", "")

        process.side_effect = invalid_json  # type: ignore[attr-defined]
        with self.assertRaises(SimulationOutputError):
            run_simulation(self.profile, self._config(), root=self.root)

    @patch("dpslab.runner.subprocess.run")
    def test_unknown_simc_version_is_null(self, process: object) -> None:
        def no_version(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            json_arg = next(argument for argument in args if argument.startswith("json="))
            json_path = Path(json_arg.removeprefix("json=").split(",", 1)[0])
            json_path.write_text(
                '{"sim":{"players":[{"name":"Tester","collected_data":{"dps":{}}}]}}',
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(args, 0, "completed", "")

        process.side_effect = no_version  # type: ignore[attr-defined]
        result = run_simulation(self.profile, self._config(), root=self.root)
        metadata = json.loads(result.artifacts.metadata_file.read_text(encoding="utf-8"))
        self.assertIsNone(result.simc_version)
        self.assertIsNone(metadata["simc_version"])
        self.assertIsNone(metadata["simc_revision"])

    @patch("dpslab.runner.subprocess.run")
    def test_simc_revision_requires_nonempty_top_level_string(
        self, process: object
    ) -> None:
        player = {
            "players": [
                {
                    "name": "Tester",
                    "collected_data": {"dps": {"mean": 1, "count": 1}},
                }
            ]
        }
        cases = (
            ("root", {"version": "1100-01", "git_revision": " revision ", "sim": player}, "revision"),
            ("blank", {"version": "1100-01", "git_revision": " ", "sim": player}, None),
            ("nested", {"version": "1100-01", "sim": {**player, "git_revision": "nested"}}, None),
        )
        for label, document, expected in cases:
            with self.subTest(label=label):
                def completed(
                    args: list[str], **kwargs: object
                ) -> subprocess.CompletedProcess[str]:
                    json_arg = next(
                        argument for argument in args if argument.startswith("json=")
                    )
                    json_path = Path(
                        json_arg.removeprefix("json=").split(",", 1)[0]
                    )
                    json_path.write_text(json.dumps(document), encoding="utf-8")
                    return subprocess.CompletedProcess(args, 0, "", "")

                process.side_effect = completed  # type: ignore[attr-defined]
                result = run_simulation(self.profile, self._config(), root=self.root)
                metadata = json.loads(
                    result.artifacts.metadata_file.read_text(encoding="utf-8")
                )
                self.assertEqual(metadata["simc_revision"], expected)

    @patch("dpslab.runner.summarize_run")
    @patch("dpslab.runner.subprocess.run")
    def test_summary_failure_keeps_completed_simulation_status(
        self, process: object, summarize: object
    ) -> None:
        process.side_effect = self._successful_process  # type: ignore[attr-defined]
        summarize.side_effect = ResultSummaryError("broken summary")  # type: ignore[attr-defined]
        with self.assertRaises(SummaryPostprocessingError) as caught:
            run_simulation(self.profile, self._config(), root=self.root)
        metadata = json.loads((caught.exception.run_dir / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["status"], "completed")
        self.assertEqual(metadata["exit_code"], 0)
        self.assertIn("postprocesamiento", str(caught.exception))

    @patch("dpslab.runner.subprocess.run")
    def test_real_profile_sha256_is_unchanged(self, process: object) -> None:
        process.side_effect = self._successful_process  # type: ignore[attr-defined]
        before = sha256(REAL_PROFILE.read_bytes()).hexdigest()
        config = SimulationConfig(self.exe, self.runs_dir)
        run_simulation(REAL_PROFILE, config, root=REPOSITORY_ROOT)
        after = sha256(REAL_PROFILE.read_bytes()).hexdigest()
        self.assertEqual(after, before)
        self.assertEqual(after, "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738")

    @patch("dpslab.runner.subprocess.run")
    def test_variant_uses_effective_profile_and_records_integrity(self, process: object) -> None:
        process.side_effect = self._successful_process  # type: ignore[attr-defined]
        source = self.root / "variants" / "test.toml"
        source.parent.mkdir()
        source.write_text(
            '[variant]\nid="test_v1"\nname="Test"\n\n[[overrides]]\n'
            'key="warlock.soul_shards"\nvalue="0"\n', encoding="utf-8"
        )
        base = self.profile.read_bytes()
        config = SimulationConfig(self.exe, self.runs_dir, variant=load_variant(source))
        result = run_simulation(self.profile, config, root=self.root)
        command = process.call_args.args[0]  # type: ignore[attr-defined]
        effective = result.artifacts.run_dir / "effective_profile.simc"
        self.assertEqual(Path(command[1]), effective)
        self.assertTrue(effective.read_bytes().startswith(base))
        metadata = json.loads(result.artifacts.metadata_file.read_text(encoding="utf-8"))
        self.assertEqual(metadata["schema_version"], "0.3")
        self.assertEqual(metadata["variant_id"], "test_v1")
        self.assertTrue(metadata["variant_hash_verified"])
        self.assertTrue(metadata["base_profile_hash_verified"])
        self.assertEqual(metadata["overrides"][0]["status"], "applied")
        self.assertEqual(metadata["overrides"][0]["order"], 1)
        summary = json.loads((result.artifacts.run_dir / "run_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["variant"]["variant_id"], "test_v1")

    @patch("dpslab.runner.subprocess.run")
    def test_without_variant_keeps_base_profile_argument(self, process: object) -> None:
        process.side_effect = self._successful_process  # type: ignore[attr-defined]
        result = run_simulation(self.profile, self._config(), root=self.root)
        self.assertEqual(Path(process.call_args.args[0][1]), self.profile.resolve())  # type: ignore[attr-defined]
        self.assertFalse((result.artifacts.run_dir / "effective_profile.simc").exists())

    @patch("dpslab.runner.subprocess.run")
    def test_variant_and_scenario_can_be_used_together(self, process: object) -> None:
        process.side_effect = self._successful_process  # type: ignore[attr-defined]
        scenario_file = self.root / "scenarios" / "scenario.toml"
        scenario_file.parent.mkdir()
        scenario_file.write_bytes((Path(__file__).parent / "fixtures" / "valid_scenario.toml").read_bytes())
        variant_file = self.root / "variants" / "variant.toml"
        variant_file.parent.mkdir()
        variant_file.write_text('[variant]\nid="v1"\nname="V1"\n[[overrides]]\nkey="warlock.soul_shards"\nvalue="0"\n', encoding="utf-8")
        scenario = load_scenario(scenario_file)
        config = SimulationConfig(
            self.exe, self.runs_dir, iterations=0, max_time=120,
            vary_combat_length=0.1, fight_style="Patchwerk", desired_targets=1,
            target_error=0.05, scenario=scenario, variant=load_variant(variant_file)
        )
        result = run_simulation(self.profile, config, root=self.root)
        metadata = json.loads(result.artifacts.metadata_file.read_text(encoding="utf-8"))
        self.assertEqual(metadata["scenario_id"], "anonymous_scenario_v1")
        self.assertEqual(metadata["variant_id"], "v1")
        self.assertTrue(metadata["scenario_hash_verified"])
        self.assertTrue(metadata["variant_hash_verified"])

    @patch("dpslab.runner.create_effective_profile")
    @patch("dpslab.runner.subprocess.run")
    def test_integrity_failure_before_subprocess(self, process: object, create: object) -> None:
        from dpslab.variant import create_effective_profile as real_create

        variant_file = self.root / "variant.toml"
        variant_file.write_text('[variant]\nid="v1"\nname="V1"\n[[overrides]]\nkey="warlock.soul_shards"\nvalue="0"\n', encoding="utf-8")
        loaded = load_variant(variant_file)

        def mutate(base: bytes, variant: object, destination: Path) -> object:
            result = real_create(base, variant, destination)  # type: ignore[arg-type]
            self.profile.write_bytes(self.profile.read_bytes() + b"# changed\n")
            return result

        create.side_effect = mutate  # type: ignore[attr-defined]
        with self.assertRaises(VariantIntegrityError) as caught:
            run_simulation(self.profile, SimulationConfig(self.exe, self.runs_dir, variant=loaded), root=self.root)
        process.assert_not_called()  # type: ignore[attr-defined]
        metadata = json.loads((caught.exception.run_dir / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["status"], "integrity_error")


if __name__ == "__main__":
    unittest.main()
