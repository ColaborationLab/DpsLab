from __future__ import annotations

import json
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from tests.strict_temporary_cleanup import strict_temporary_cleanup

from dpslab.comparison_adapter import AdapterMemberRequest, ComparisonMemberExecutionRequest, execute_comparison_member, execute_member, validate_artifact_references, validate_simc_identity
from dpslab.comparison_models import PlannedParameters, RunArtifactReference, SimulationCraftIdentity
from dpslab.config import SimulationConfig
from dpslab.runner import RunArtifacts, RunResult, reserve_run
from dpslab.scenario import load_scenario


class ComparisonAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(strict_temporary_cleanup, self.temp, Path(self.temp.name))
        self.root = Path(self.temp.name)
        self.profile = self.root / "effective.simc"
        self.profile.write_text("neck=,id=1\n", encoding="utf-8")
        self.base = self.root / "base.simc"
        self.base.write_text("neck=,id=0\n", encoding="utf-8")
        scenario_file = self.root / "scenario.toml"
        scenario_file.write_text('[scenario]\nid="s"\nname="S"\ndescription=""\nfight_style="Patchwerk"\ndesired_targets=1\nmax_time=300\nvary_combat_length=0.2\n[precision]\niterations=5000\n', encoding="utf-8")
        self.scenario = load_scenario(scenario_file)
        self.exe = self.root / "simc.exe"
        self.exe.touch()
        self.runs = self.root / "runs"
        self.reservation = reserve_run(self.runs)
        self.config = SimulationConfig(self.exe, self.runs, timeout_seconds=900, threads=2, iterations=5000, seed=1367750201, scenario=self.scenario)
        self.request = AdapterMemberRequest(self.reservation.run_id, "a", 50228, 1367750201, 5000, 2, self.scenario.source_sha256, sha256(self.base.read_bytes()).hexdigest(), sha256(self.profile.read_bytes()).hexdigest(), "1205-01", "a81c39d")

    def _runner(self, profile, config, *, root, reservation):
        reservation.consume(comparison_execution_id=reservation.comparison_execution_id, member_id=reservation.member_id)
        directory = reservation.run_directory
        metadata = {
            "run_id": reservation.run_id,
            "simc_version": "1205-01",
            "simc_revision": "a81c39d",
            "effective_parameters": {"iterations": 5000, "threads": 2, "target_error": None, "seed": 1367750201, "timeout_seconds": 900},
            "invocation": {"portable_argv": ["<SIMC_EXE>", "effective.simc", "threads=2", "iterations=5000", "seed=1367750201"], "portable_argv_sha256": "a" * 64, "process_argv_sha256": "b" * 64, "executable_sha256": sha256(self.exe.read_bytes()).hexdigest(), "executable_source": "test", "argument_list": True, "shell": False},
            "exit_code": 0,
        }
        (directory / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
        (directory / "run_summary.json").write_text(json.dumps({"dps": {"mean": 100000.0}}), encoding="utf-8")
        (directory / "simc.json").write_text("{}", encoding="utf-8")
        (directory / "stdout.txt").write_text("ok", encoding="utf-8")
        (directory / "stderr.txt").write_text("", encoding="utf-8")
        (directory / "effective_profile.simc").write_bytes(self.profile.read_bytes())
        artifacts = RunArtifacts(directory, directory / "simc.json", None, directory / "metadata.json", directory / "stdout.txt", directory / "stderr.txt")
        return RunResult(reservation.run_id, "completed", 0, 1.0, "1205-01", artifacts)

    def test_validated_boundary_returns_structured_outcome(self) -> None:
        outcome = execute_member(self.request, self.reservation, self.base, self.profile, self.config, root=self.root, runner=self._runner)
        self.assertTrue(outcome.valid)
        self.assertEqual(outcome.run_id, self.request.planned_run_id)
        self.assertEqual(outcome.mean_dps, 100000.0)

    def test_explicit_cli_is_an_authorized_executable_source(self) -> None:
        identity = SimulationCraftIdentity(
            "1205-01", "a81c39d", "a" * 64
        )
        self.assertEqual(
            validate_simc_identity(identity, identity, "explicit_cli"),
            (),
        )

    def test_parameter_mismatch_blocks_before_runner(self) -> None:
        called = False
        def runner(*args, **kwargs):
            nonlocal called
            called = True
            raise AssertionError
        bad = SimulationConfig(self.exe, self.runs, threads=2, iterations=5000, target_error=0.1, seed=1367750201, scenario=self.scenario)
        outcome = execute_member(self.request, self.reservation, self.base, self.profile, bad, root=self.root, runner=runner)
        self.assertFalse(outcome.valid)
        self.assertFalse(called)
        self.assertIn("effective_precision_mismatch", outcome.invalid_reasons)

    def test_final_typed_adapter_contract_and_simc_mismatch(self) -> None:
        request = ComparisonMemberExecutionRequest(
            "comparison", "execution", "f" * 64, 1, 1, "a", 1, 50228,
            self.reservation, self.base, self.profile, self.scenario.source_sha256,
            "m" * 64, "tree", PlannedParameters(1367750201, 5000, 2, None, 900),
            SimulationCraftIdentity("1205-01", "a81c39d", sha256(self.exe.read_bytes()).hexdigest()),
            sha256(self.base.read_bytes()).hexdigest(), sha256(self.profile.read_bytes()).hexdigest(),
        )
        response = execute_comparison_member(request, self.config, root=self.root, runner=self._runner)
        self.assertEqual(response.status, "completed")
        self.assertTrue(response.integrity.valid)
        self.assertEqual({item.kind for item in response.artifacts}, {"metadata", "simc_json", "stdout", "stderr", "summary", "effective_profile"})

    def test_different_simc_revision_invalidates_typed_response(self) -> None:
        request = ComparisonMemberExecutionRequest(
            "comparison", "execution", "f" * 64, 1, 1, "a", 1, 50228,
            self.reservation, self.base, self.profile, self.scenario.source_sha256,
            "m" * 64, "tree", PlannedParameters(1367750201, 5000, 2, None, 900),
            SimulationCraftIdentity("1205-01", "different", sha256(self.exe.read_bytes()).hexdigest()),
            sha256(self.base.read_bytes()).hexdigest(), sha256(self.profile.read_bytes()).hexdigest(),
        )
        response = execute_comparison_member(request, self.config, root=self.root, runner=self._runner)
        self.assertEqual(response.status, "invalid")
        self.assertFalse(response.integrity.simc_identity_verified)

    def test_simc_identity_matrix(self) -> None:
        expected = SimulationCraftIdentity("1205-01", "a81c39d", "a" * 64)
        cases = (
            (None, "test", "simc_identity_missing"),
            (SimulationCraftIdentity("other", "a81c39d", "a" * 64), "test", "simc_version_mismatch"),
            (SimulationCraftIdentity("1205-01", "other", "a" * 64), "test", "simc_revision_mismatch"),
            (SimulationCraftIdentity("1205-01", "a81c39d", "b" * 64), "test", "simc_executable_sha256_mismatch"),
            (SimulationCraftIdentity("1205-01", None, "a" * 64), "test", "simc_revision_missing"),
            (expected, "unknown", "executable_source_invalid"),
        )
        for observed, source, code in cases:
            with self.subTest(code=code):
                self.assertIn(code, {error.code for error in validate_simc_identity(expected, observed, source)})
        self.assertEqual(validate_simc_identity(expected, expected, "test"), ())

    def test_artifact_reference_matrix(self) -> None:
        run = self.root / "artifact-run"
        run.mkdir()
        names = {"metadata": "metadata.json", "simc_json": "simc.json", "stdout": "stdout.txt", "stderr": "stderr.txt", "summary": "run_summary.json", "effective_profile": "effective_profile.simc"}
        references = []
        for kind, name in names.items():
            path = run / name
            path.write_text("{}" if kind in {"metadata", "simc_json", "summary"} else "x", encoding="utf-8")
            references.append(RunArtifactReference(kind, name, sha256(path.read_bytes()).hexdigest(), True, True if kind in {"metadata", "simc_json", "summary"} else None))
        self.assertEqual(validate_artifact_references(run, tuple(references)), ())
        mutations = (
            (RunArtifactReference("metadata", "metadata.json", "0" * 64, True, True), "artifact_hash_mismatch"),
            (RunArtifactReference("metadata", "missing.json", None, True, True), "artifact_existence_mismatch"),
            (RunArtifactReference("metadata", "../other.json", None, False, True), "artifact_path_outside_run"),
            (RunArtifactReference("metadata", "C:/Users/name/file.json", None, False, True), "artifact_path_not_portable"),
            (RunArtifactReference("metadata", "metadata.json", "bad", True, True), "artifact_hash_format_invalid"),
        )
        for replacement, code in mutations:
            changed = tuple([replacement] + references[1:])
            with self.subTest(code=code):
                self.assertIn(code, {error.code for error in validate_artifact_references(run, changed)})
        duplicate = tuple(references + [references[0]])
        self.assertIn("artifact_reference_duplicate", {error.code for error in validate_artifact_references(run, duplicate)})
