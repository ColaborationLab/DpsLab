from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from dpslab.comparison_environment import software_record
from dpslab.comparison_execution import (
    ComparisonExecutionError,
    _prepare_member,
    _run_member,
    execute_frozen_comparison,
)
from dpslab.comparator import MemberPlan
from dpslab.comparison_readiness import ComparisonReadiness
from dpslab.comparison_models import SimulationCraftIdentity
from dpslab.comparison_spec import load_comparison_spec
from dpslab.config import SimulationConfig
from dpslab.runner import reserve_run


ROOT = Path(__file__).resolve().parents[2]
SPEC = load_comparison_spec(
    ROOT / "comparisons/flasil_neck_50228_vs_249368_v1.toml",
    root=ROOT,
)
EXECUTION_ID = "cmp-" + "a" * 32


class ComparisonExecutionBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.exe = self.root / "simc.exe"
        self.exe.write_bytes(b"synthetic")
        self.config = SimulationConfig(
            self.exe,
            self.root / "results" / "runs",
            timeout_seconds=900,
            threads=2,
            iterations=5000,
            max_time=300,
            vary_combat_length=0.2,
            fight_style="LightMovement",
            desired_targets=1,
            executable_source="explicit_cli",
        )
        software = replace(
            software_record(ROOT),
            simulationcraft=SimulationCraftIdentity(
                "1205-01", "a81c39d", "7" * 64
            ),
        )
        self.readiness = ComparisonReadiness(
            preflight=SimpleNamespace(
                comparison_id=SPEC.comparison_id,
                comparison_spec_sha256=SPEC.source_sha256,
                software=software,
            ),
            simulationcraft_branch="midnight",
            executable_source="explicit_cli",
            portable_probe_argv=("<SIMC_EXE>", "display_build=2"),
        )

    @patch("dpslab.comparison_execution.preflight_comparison_execution")
    @patch("dpslab.comparison_execution.orchestrate")
    def test_closed_bridge_injects_readiness_and_calls_orchestrator_once(
        self, orchestrator: object, preflight: object
    ) -> None:
        preflight.return_value = self.readiness.preflight
        sentinel = object()
        orchestrator.return_value = sentinel
        result = execute_frozen_comparison(
            SPEC,
            self.config,
            self.readiness,
            confirmation=SPEC.comparison_id,
            root=self.root,
            execution_id_source=lambda: EXECUTION_ID,
        )
        self.assertIs(result, sentinel)
        orchestrator.assert_called_once()
        arguments = orchestrator.call_args
        self.assertEqual(arguments.args[1], EXECUTION_ID)
        self.assertEqual(
            arguments.args[2],
            self.root.resolve()
            / "results"
            / "comparisons"
            / EXECUTION_ID
            / "comparison_result.json",
        )
        self.assertIs(
            arguments.kwargs["software"],
            self.readiness.preflight.software,
        )

    @patch("dpslab.comparison_execution.preflight_comparison_execution")
    @patch("dpslab.comparison_execution.orchestrate")
    def test_preconditions_fail_before_any_output(
        self, orchestrator: object, preflight: object
    ) -> None:
        preflight.return_value = self.readiness.preflight
        for label, confirmation, readiness, config in (
            ("confirmation", "wrong", self.readiness, self.config),
            (
                "readiness",
                SPEC.comparison_id,
                replace(self.readiness, ready=False),
                self.config,
            ),
            (
                "source",
                SPEC.comparison_id,
                self.readiness,
                replace(self.config, executable_source="local_config"),
            ),
        ):
            with self.subTest(label=label), self.assertRaisesRegex(
                ComparisonExecutionError,
                "comparison_execution_precondition_failed",
            ):
                execute_frozen_comparison(
                    SPEC,
                    config,
                    readiness,
                    confirmation=confirmation,
                    root=self.root,
                    execution_id_source=lambda: EXECUTION_ID,
                )
            self.assertFalse((self.root / "results").exists())
        orchestrator.assert_not_called()

    @patch("dpslab.comparison_execution.preflight_comparison_execution")
    @patch("dpslab.comparison_execution.orchestrate")
    def test_execution_id_and_existing_output_fail_closed(
        self, orchestrator: object, preflight: object
    ) -> None:
        preflight.return_value = self.readiness.preflight
        with self.assertRaisesRegex(
            ComparisonExecutionError, "comparison_execution_id_invalid"
        ):
            execute_frozen_comparison(
                SPEC,
                self.config,
                self.readiness,
                confirmation=SPEC.comparison_id,
                root=self.root,
                execution_id_source=lambda: "../private",
            )
        existing = (
            self.root / "results" / "comparisons" / EXECUTION_ID
        )
        existing.mkdir(parents=True)
        with self.assertRaisesRegex(
            ComparisonExecutionError, "comparison_execution_output_exists"
        ):
            execute_frozen_comparison(
                SPEC,
                self.config,
                self.readiness,
                confirmation=SPEC.comparison_id,
                root=self.root,
                execution_id_source=lambda: EXECUTION_ID,
            )
        orchestrator.assert_not_called()

    @patch("dpslab.comparison_execution.preflight_comparison_execution")
    @patch("dpslab.comparison_execution.orchestrate")
    def test_falsey_execution_id_source_remains_authoritative(
        self, orchestrator: object, preflight: object
    ) -> None:
        class FalseySource:
            def __bool__(self) -> bool:
                return False

            def __call__(self) -> str:
                return EXECUTION_ID

        preflight.return_value = self.readiness.preflight
        orchestrator.return_value = object()
        execute_frozen_comparison(
            SPEC,
            self.config,
            self.readiness,
            confirmation=SPEC.comparison_id,
            root=self.root,
            execution_id_source=FalseySource(),
        )
        self.assertEqual(orchestrator.call_args.args[1], EXECUTION_ID)

    @patch("dpslab.comparison_execution.execute_comparison_member")
    def test_real_preparation_and_typed_adapter_request_are_exact(
        self, adapter: object
    ) -> None:
        plan = MemberPlan(
            SPEC.comparison_id,
            EXECUTION_ID,
            1,
            SPEC.protocol.seeds[0],
            "AB",
            "b",
            2,
            1,
            SPEC.arm_b.item_id,
            f"{EXECUTION_ID}:block-1:attempt-1:b",
        )
        reservation = reserve_run(
            self.config.runs_dir,
            comparison_execution_id=EXECUTION_ID,
            member_id=plan.member_id,
        )
        preparation = _prepare_member(
            plan,
            reservation,
            spec=SPEC,
            config=self.config,
            root=self.root,
        )
        effective = reservation.run_directory / "effective_profile.simc"
        base_lines = SPEC.base_profile.read_bytes().splitlines(keepends=True)
        effective_lines = effective.read_bytes().splitlines(keepends=True)
        changed = [
            index
            for index, pair in enumerate(zip(base_lines, effective_lines))
            if pair[0] != pair[1]
        ]
        self.assertEqual(changed, [next(
            index
            for index, line in enumerate(base_lines)
            if line.startswith(b"neck=")
        )])
        self.assertEqual(
            preparation.effective_profile_sha256,
            __import__("hashlib").sha256(effective.read_bytes()).hexdigest(),
        )
        sentinel = object()
        adapter.return_value = sentinel
        response = _run_member(
            plan,
            reservation,
            spec=SPEC,
            config=self.config,
            readiness=self.readiness,
            root=self.root,
        )
        self.assertIs(response, sentinel)
        request, member_config = adapter.call_args.args[:2]
        self.assertEqual(
            (request.arm, request.block_index, request.order_position),
            ("b", 1, 2),
        )
        self.assertEqual(
            (
                member_config.seed,
                member_config.iterations,
                member_config.threads,
                member_config.target_error,
            ),
            (SPEC.protocol.seeds[0], 5000, 2, None),
        )
        self.assertEqual(
            request.expected_simc,
            self.readiness.preflight.software.simulationcraft,
        )

    def test_preparation_rejects_changed_or_ambiguous_base(self) -> None:
        plan = MemberPlan(
            SPEC.comparison_id,
            EXECUTION_ID,
            1,
            SPEC.protocol.seeds[0],
            "AB",
            "a",
            1,
            1,
            SPEC.arm_a.item_id,
            f"{EXECUTION_ID}:block-1:attempt-1:a",
        )
        for label, content, digest in (
            ("changed", b"neck=,id=1\n", SPEC.base_profile_sha256),
            (
                "ambiguous",
                b"neck=,id=1\nneck=,id=2\n",
                __import__("hashlib").sha256(
                    b"neck=,id=1\nneck=,id=2\n"
                ).hexdigest(),
            ),
        ):
            base = self.root / f"{label}.simc"
            base.write_bytes(content)
            candidate = replace(
                SPEC,
                base_profile=base,
                base_profile_sha256=digest,
            )
            reservation = reserve_run(
                self.root / label,
                comparison_execution_id=EXECUTION_ID,
                member_id=plan.member_id,
            )
            with self.subTest(label=label), self.assertRaises(Exception):
                _prepare_member(
                    plan,
                    reservation,
                    spec=candidate,
                    config=self.config,
                    root=self.root,
                )


if __name__ == "__main__":
    unittest.main()
