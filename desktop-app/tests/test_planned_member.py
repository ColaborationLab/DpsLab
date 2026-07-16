from __future__ import annotations

import json
import unittest
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, replace
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

from dpslab.comparator import _new_result
from dpslab.comparison_models import (
    ComparisonResultError,
    PairAttempt,
    SimulationCraftIdentity,
    StateEvent,
)
from dpslab.comparison_result_io import result_to_document
from dpslab.comparison_spec import load_comparison_spec
from dpslab.planned_member import (
    PlannedMemberCreationPlan,
    planned_member_candidate,
    prepare_planned_member_creation,
    validate_planned_member_candidate,
    validate_planned_member_creation_plan,
)
from dpslab.run_identity import RunIdentityPlan


ROOT = Path(__file__).resolve().parents[2]
SPEC = load_comparison_spec(
    ROOT / "comparisons/flasil_neck_50228_vs_249368_v1.toml",
    root=ROOT,
)
PREVIOUS_TIME = "2026-07-16T00:00:00Z"
EVENT_TIME = "2026-07-16T00:00:01Z"
LATER_TIME = "2026-07-16T00:00:02Z"
TOKEN_A = "a" * 32
TOKEN_B = "b" * 32
RUN_A = "20260716T000001.000000Z-aaaaaaaa"
RUN_B = "20260716T000002.000000Z-bbbbbbbb"


class PlannedMemberTests(unittest.TestCase):
    def _previous(
        self,
        *,
        block_index: int = 1,
        attempt_number: int = 1,
    ):
        result = _new_result(SPEC, "execution")
        result.status = "running"
        result.started_at = PREVIOUS_TIME
        result.events = [
            StateEvent(
                1,
                "historical-event",
                PREVIOUS_TIME,
                "attempt",
                "historical-attempt",
                "planned",
                "running",
                "historical",
            )
        ]
        result.updated_at = PREVIOUS_TIME
        block = result.blocks[block_index - 1]
        block.status = "running"
        block.attempts = [
            PairAttempt(
                attempt_number,
                f"execution:block-{block_index}:attempt-{attempt_number}",
                "execution",
                status="running",
                planned_at=PREVIOUS_TIME,
            )
        ]
        return result

    @staticmethod
    def _identity(
        arm: str = "a",
        *,
        run_id: str = RUN_A,
        block_index: int = 1,
        attempt: int = 1,
        execution: str = "execution",
    ) -> RunIdentityPlan:
        member_id = (
            f"{execution}:block-{block_index}:attempt-{attempt}:{arm}"
        )
        return RunIdentityPlan(
            execution,
            member_id,
            block_index,
            attempt,
            arm,  # type: ignore[arg-type]
            run_id,
            f"results/runs/{run_id}",
        )

    def _plan(
        self,
        arm: str = "a",
        *,
        run_id: str = RUN_A,
        token: str = TOKEN_A,
        block_index: int = 1,
        attempt: int = 1,
        execution: str = "execution",
    ) -> PlannedMemberCreationPlan:
        return prepare_planned_member_creation(
            self._identity(
                arm,
                run_id=run_id,
                block_index=block_index,
                attempt=attempt,
                execution=execution,
            ),
            SPEC,
            SimulationCraftIdentity(
                SPEC.simc_version,
                SPEC.simc_revision,
                "c" * 64,
            ),
            token_source=lambda: token,
        )

    def _candidate(self, previous, plan, *, event_id="member-created"):
        return planned_member_candidate(
            previous,
            plan,
            EVENT_TIME,
            event_id,
            "planned member and reservation created",
        )

    @staticmethod
    def _member(result, member_id):
        return next(
            member
            for block in result.blocks
            for attempt in block.attempts
            for member in attempt.members
            if member.member_id == member_id
        )

    def test_creation_plan_is_frozen_ephemeral_and_hides_plaintext_token(self) -> None:
        plan = self._plan()
        self.assertEqual(
            set(plan.__dataclass_fields__),
            {
                "run_identity",
                "comparison_spec",
                "reservation_token",
                "token_sha256",
                "comparison_id",
                "comparison_spec_sha256",
                "planned_order",
                "order_position",
                "seed",
                "candidate_item_id",
                "base_profile_sha256",
                "scenario_sha256",
                "evidence_manifest_sha256",
                "planned_parameters",
                "expected_simc",
            },
        )
        self.assertNotIn(TOKEN_A, repr(plan))
        self.assertFalse(hasattr(plan, "status"))
        self.assertFalse(hasattr(plan, "run_directory"))
        with self.assertRaises(FrozenInstanceError):
            plan.token_sha256 = "0" * 64  # type: ignore[misc]

    def test_prepare_calls_injected_token_source_once_and_hashes_exactly(self) -> None:
        calls: list[str] = []
        plan = prepare_planned_member_creation(
            self._identity(),
            SPEC,
            SimulationCraftIdentity(SPEC.simc_version, SPEC.simc_revision, None),
            token_source=lambda: calls.append("called") or TOKEN_A,
        )
        self.assertEqual(calls, ["called"])
        self.assertEqual(plan.reservation_token, TOKEN_A)
        self.assertEqual(
            plan.token_sha256,
            sha256(TOKEN_A.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(plan.run_id, RUN_A)
        self.assertEqual(plan.run_identity.portable_path, f"results/runs/{RUN_A}")

    def test_secure_default_and_token_validation(self) -> None:
        plan = prepare_planned_member_creation(
            self._identity(),
            SPEC,
            SimulationCraftIdentity(SPEC.simc_version, SPEC.simc_revision, None),
        )
        self.assertGreaterEqual(len(plan.reservation_token), 32)
        self.assertEqual(len(plan.token_sha256), 64)
        for token in ("", "short", "contains spaces " + "x" * 32, "!" * 32):
            with self.subTest(token=token), self.assertRaises(ComparisonResultError):
                self._plan(token=token)
        with self.assertRaises(ComparisonResultError):
            prepare_planned_member_creation(
                self._identity(),
                SPEC,
                SimulationCraftIdentity(
                    SPEC.simc_version,
                    SPEC.simc_revision,
                    None,
                ),
                token_source="invalid",  # type: ignore[arg-type]
            )

    def test_different_tokens_produce_different_hashes_and_incoherence_fails(self) -> None:
        first, second = self._plan(token=TOKEN_A), self._plan(token=TOKEN_B)
        self.assertNotEqual(first.token_sha256, second.token_sha256)
        invalid = replace(first, token_sha256="0" * 64)
        with self.assertRaises(ComparisonResultError):
            validate_planned_member_creation_plan(invalid)
        with self.assertRaises(ComparisonResultError):
            validate_planned_member_creation_plan(
                replace(first, candidate_item_id=SPEC.arm_b.item_id)
            )

    def test_success_builds_joint_initial_state_and_one_event(self) -> None:
        previous = self._previous()
        snapshot = deepcopy(previous)
        plan = self._plan()
        candidate = self._candidate(previous, plan)
        member = self._member(candidate, plan.run_identity.member_id)
        self.assertEqual(previous, snapshot)
        self.assertIsNot(candidate, previous)
        self.assertEqual(member.status, "planned")
        self.assertEqual(member.planned_run_id, RUN_A)
        self.assertIsNone(member.run_id)
        self.assertIsNone(member.started_at)
        self.assertIsNone(member.finished_at)
        self.assertIsNone(member.duration_seconds)
        self.assertEqual(member.reservation.status, "reserved")
        self.assertEqual(member.reservation.owner_execution_id, "execution")
        self.assertEqual(
            member.reservation.owner_member_id,
            plan.run_identity.member_id,
        )
        self.assertEqual(member.reservation.token_sha256, plan.token_sha256)
        self.assertEqual(member.invocation.status, "not_built")
        self.assertTrue(
            all(
                getattr(member.invocation, item.name) is None
                for item in fields(member.invocation)
                if item.name != "status"
            )
        )
        self.assertEqual(member.artifacts.references, ())
        self.assertIsNone(member.integrity)
        self.assertIsNone(member.dps)
        self.assertEqual(member.errors, [])
        self.assertEqual(member.warnings, [])
        self.assertEqual(candidate.updated_at, EVENT_TIME)
        self.assertEqual(len(candidate.events), len(previous.events) + 1)
        event = candidate.events[-1]
        self.assertEqual(
            (
                event.entity_type,
                event.entity_id,
                event.previous_status,
                event.new_status,
            ),
            ("comparison_member", member.member_id, None, "planned"),
        )

    def test_ba_order_and_second_arm_are_derived_from_frozen_spec(self) -> None:
        previous = self._previous(block_index=2)
        plan_b = self._plan(
            "b",
            run_id=RUN_A,
            block_index=2,
        )
        first = self._candidate(previous, plan_b)
        self.assertEqual(
            self._member(first, plan_b.run_identity.member_id).order_position,
            1,
        )
        plan_a = self._plan(
            "a",
            run_id=RUN_B,
            token=TOKEN_B,
            block_index=2,
        )
        second = planned_member_candidate(
            first,
            plan_a,
            LATER_TIME,
            "second-member",
            "second planned member",
        )
        members = second.blocks[1].attempts[0].members
        self.assertEqual([(member.arm, member.order_position) for member in members], [("b", 1), ("a", 2)])

    def test_block_and_attempt_precondition_matrix(self) -> None:
        mutations = {
            "global": lambda r: setattr(r, "status", "ready"),
            "block_status": lambda r: setattr(r.blocks[0], "status", "planned"),
            "block_execution": lambda r: setattr(
                r.blocks[0], "comparison_execution_id", "other"
            ),
            "block_seed": lambda r: setattr(r.blocks[0], "seed", 1),
            "block_order": lambda r: setattr(r.blocks[0], "planned_order", "BA"),
            "attempt_absent": lambda r: setattr(r.blocks[0], "attempts", []),
            "attempt_status": lambda r: setattr(
                r.blocks[0].attempts[0], "status", "valid"
            ),
            "attempt_execution": lambda r: setattr(
                r.blocks[0].attempts[0], "comparison_execution_id", "other"
            ),
            "attempt_id": lambda r: setattr(
                r.blocks[0].attempts[0], "attempt_id", "other"
            ),
        }
        for label, mutation in mutations.items():
            previous = self._previous()
            snapshot = deepcopy(previous)
            mutation(previous)
            mutated = deepcopy(previous)
            with self.subTest(case=label), self.assertRaises(ComparisonResultError):
                self._candidate(previous, self._plan())
            self.assertEqual(previous, mutated)
            self.assertNotEqual(previous, snapshot) if label != "global" else None

    def test_wrong_execution_block_attempt_and_noncanonical_path_fail(self) -> None:
        cases = (
            self._plan(execution="other"),
            self._plan(block_index=2),
            self._plan(attempt=2),
            replace(
                self._plan(),
                run_identity=replace(
                    self._plan().run_identity,
                    portable_path=f"results/runs/{RUN_B}",
                ),
            ),
        )
        previous = self._previous()
        for plan in cases:
            with self.subTest(plan=plan.run_identity), self.assertRaises(ValueError):
                self._candidate(previous, plan)

    def test_arm_must_be_inserted_in_planned_order(self) -> None:
        previous = self._previous()
        with self.assertRaisesRegex(ComparisonResultError, "siguiente posicion"):
            self._candidate(
                previous,
                self._plan("b", run_id=RUN_B, token=TOKEN_B),
            )

    def test_run_token_arm_and_position_collisions_are_rejected(self) -> None:
        first_plan = self._plan()
        first = self._candidate(self._previous(), first_plan)
        cases = {
            "run": self._plan("b", run_id=RUN_A, token=TOKEN_B),
            "token": self._plan("b", run_id=RUN_B, token=TOKEN_A),
        }
        for label, plan in cases.items():
            with self.subTest(case=label), self.assertRaises(ComparisonResultError):
                planned_member_candidate(
                    first,
                    plan,
                    LATER_TIME,
                    f"event-{label}",
                    label,
                )
        duplicated_arm = deepcopy(first)
        duplicated_arm.blocks[0].attempts[0].members[0].arm = "b"
        with self.assertRaises(ComparisonResultError):
            planned_member_candidate(
                duplicated_arm,
                self._plan("b", run_id=RUN_B, token=TOKEN_B),
                LATER_TIME,
                "event-arm",
                "arm",
            )

    def test_exact_idempotence_returns_previous_without_event_or_token_call(self) -> None:
        calls: list[str] = []
        plan = prepare_planned_member_creation(
            self._identity(),
            SPEC,
            SimulationCraftIdentity(SPEC.simc_version, SPEC.simc_revision, None),
            token_source=lambda: calls.append("token") or TOKEN_A,
        )
        previous = self._candidate(self._previous(), plan)
        snapshot = deepcopy(previous)
        with patch(
            "dpslab.planned_member._initial_member",
            side_effect=AssertionError("idempotence must not build a member"),
        ):
            repeated = planned_member_candidate(
                previous,
                plan,
                "ignored because no event is created",
                "historical-event",
                "",
            )
        self.assertIs(repeated, previous)
        self.assertEqual(repeated, snapshot)
        self.assertEqual(calls, ["token"])

    def test_idempotence_requires_exact_physical_location(self) -> None:
        plan = self._plan()
        valid = self._candidate(self._previous(), plan)
        snapshot = deepcopy(valid)
        repeated = planned_member_candidate(
            valid,
            plan,
            "ignored",
            "ignored",
            "",
        )
        self.assertIs(repeated, valid)
        self.assertEqual(valid, snapshot)

        cases = {}

        other_block = deepcopy(valid)
        member = other_block.blocks[0].attempts[0].members.pop()
        other_block.blocks[1].status = "running"
        other_block.blocks[1].attempts = [
            PairAttempt(
                1,
                "execution:block-2:attempt-1",
                "execution",
                status="running",
                planned_at=PREVIOUS_TIME,
                members=[member],
            )
        ]
        cases["other_block"] = other_block

        other_attempt = deepcopy(valid)
        member = other_attempt.blocks[0].attempts[0].members.pop()
        other_attempt.blocks[0].attempts.append(
            PairAttempt(
                2,
                "execution:block-1:attempt-2",
                "execution",
                status="running",
                planned_at=PREVIOUS_TIME,
                members=[member],
            )
        )
        cases["other_attempt"] = other_attempt

        wrong_position = deepcopy(valid)
        member = wrong_position.blocks[0].attempts[0].members.pop()
        placeholder = deepcopy(member)
        placeholder.member_id = "other-member"
        placeholder.arm = "a"
        placeholder.order_position = 1
        placeholder.reservation = replace(
            placeholder.reservation,
            owner_member_id=placeholder.member_id,
            planned_run_id=RUN_B,
            token_sha256="d" * 64,
        )
        member.arm = "b"
        member.order_position = 2
        wrong_position.blocks[0].planned_order = "AB"
        wrong_position.blocks[0].attempts[0].members = [placeholder, member]
        cases["wrong_position"] = wrong_position

        duplicate = deepcopy(valid)
        duplicate.blocks[1].status = "running"
        duplicate.blocks[1].attempts = [
            PairAttempt(
                1,
                "execution:block-2:attempt-1",
                "execution",
                status="running",
                planned_at=PREVIOUS_TIME,
                members=[
                    deepcopy(duplicate.blocks[0].attempts[0].members[0])
                ],
            )
        ]
        cases["duplicate"] = duplicate

        for label, previous in cases.items():
            before = deepcopy(previous)
            with self.subTest(case=label), patch(
                "dpslab.planned_member.secrets.token_urlsafe",
                side_effect=AssertionError("token source"),
            ), self.assertRaises(ComparisonResultError):
                planned_member_candidate(
                    previous,
                    plan,
                    LATER_TIME,
                    f"event-{label}",
                    "must reject",
                )
            self.assertEqual(previous, before)

    def test_oversized_attempt_is_a_controlled_domain_error(self) -> None:
        plan = self._plan()
        first = self._candidate(self._previous(), plan)
        template = first.blocks[0].attempts[0].members[0]
        previous = self._previous()
        members = []
        for index, (arm, position) in enumerate(
            (("a", 1), ("b", 2), ("a", 3)),
            1,
        ):
            member = deepcopy(template)
            member.member_id = f"other-{index}"
            member.arm = arm
            member.order_position = position
            member.reservation = replace(
                member.reservation,
                owner_member_id=member.member_id,
                planned_run_id=f"other-run-{index}",
                token_sha256=f"{index:064x}",
            )
            members.append(member)
        previous.blocks[0].attempts[0].members = members
        snapshot = deepcopy(previous)
        with patch(
            "dpslab.planned_member.secrets.token_urlsafe",
            side_effect=AssertionError("token source"),
        ), self.assertRaisesRegex(
            ComparisonResultError,
            "mas miembros que brazos planificados",
        ):
            planned_member_candidate(
                previous,
                plan,
                EVENT_TIME,
                "oversized",
                "oversized",
            )
        self.assertEqual(previous, snapshot)

    def test_partial_identity_match_is_rejected_without_repair(self) -> None:
        plan = self._plan()
        previous = self._candidate(self._previous(), plan)
        member = self._member(previous, plan.run_identity.member_id)
        member.reservation = replace(
            member.reservation,
            token_sha256="0" * 64,
        )
        snapshot = deepcopy(previous)
        with self.assertRaisesRegex(ComparisonResultError, "parcialmente"):
            planned_member_candidate(
                previous,
                plan,
                LATER_TIME,
                "retry",
                "retry",
            )
        self.assertEqual(previous, snapshot)

    def test_event_validation_matrix_rejects_every_structural_mutation(self) -> None:
        previous = self._previous()
        plan = self._plan()
        valid = self._candidate(previous, plan)
        mutations = {
            "previous_status": lambda c: c.events.__setitem__(
                -1, replace(c.events[-1], previous_status="reserved")
            ),
            "new_status": lambda c: c.events.__setitem__(
                -1, replace(c.events[-1], new_status="running")
            ),
            "entity_type": lambda c: c.events.__setitem__(
                -1, replace(c.events[-1], entity_type="member")
            ),
            "entity_id": lambda c: c.events.__setitem__(
                -1, replace(c.events[-1], entity_id="other")
            ),
            "sequence_repeat": lambda c: c.events.__setitem__(
                -1, replace(c.events[-1], sequence=1)
            ),
            "sequence_jump": lambda c: c.events.__setitem__(
                -1, replace(c.events[-1], sequence=9)
            ),
            "event_id_empty": lambda c: c.events.__setitem__(
                -1, replace(c.events[-1], event_id="")
            ),
            "event_id_duplicate": lambda c: c.events.__setitem__(
                -1, replace(c.events[-1], event_id=c.events[0].event_id)
            ),
            "occurred_invalid": lambda c: c.events.__setitem__(
                -1, replace(c.events[-1], occurred_at="invalid")
            ),
            "occurred_early": lambda c: (
                c.events.__setitem__(
                    -1,
                    replace(
                        c.events[-1],
                        occurred_at="2026-07-15T23:59:59Z",
                    ),
                ),
                setattr(c, "updated_at", "2026-07-15T23:59:59Z"),
                setattr(
                    c.blocks[0].attempts[0].members[-1],
                    "planned_at",
                    "2026-07-15T23:59:59Z",
                ),
                setattr(
                    c.blocks[0].attempts[0].members[-1],
                    "reservation",
                    replace(
                        c.blocks[0].attempts[0].members[-1].reservation,
                        created_at="2026-07-15T23:59:59Z",
                    ),
                ),
            ),
            "reason_empty": lambda c: c.events.__setitem__(
                -1, replace(c.events[-1], reason="")
            ),
            "two_new": lambda c: c.events.append(
                replace(c.events[-1], sequence=3, event_id="extra")
            ),
            "historical_altered": lambda c: c.events.__setitem__(
                0, replace(c.events[0], reason="changed")
            ),
            "historical_removed": lambda c: setattr(c, "events", c.events[1:]),
            "reordered": lambda c: setattr(c, "events", list(reversed(c.events))),
            "inserted_middle": lambda c: setattr(
                c,
                "events",
                [
                    c.events[0],
                    replace(c.events[-1], event_id="middle"),
                    c.events[-1],
                ],
            ),
        }
        for label, mutation in mutations.items():
            candidate = deepcopy(valid)
            mutation(candidate)
            with self.subTest(case=label), self.assertRaises(ComparisonResultError):
                validate_planned_member_candidate(previous, candidate, plan)

    def test_builder_argument_timestamp_and_event_validation(self) -> None:
        previous = self._previous()
        plan = self._plan()
        cases = (
            ("invalid", "event", "reason"),
            ("2026-07-15T23:59:59Z", "event", "reason"),
            (EVENT_TIME, "", "reason"),
            (EVENT_TIME, "historical-event", "reason"),
            (EVENT_TIME, "event", ""),
        )
        for occurred_at, event_id, reason in cases:
            with self.subTest(
                occurred_at=occurred_at,
                event_id=event_id,
            ), self.assertRaises(ComparisonResultError):
                planned_member_candidate(
                    previous,
                    plan,
                    occurred_at,
                    event_id,
                    reason,
                )

    def test_copy_on_write_changes_only_target_attempt_event_and_updated_at(self) -> None:
        previous = self._previous()
        snapshot = deepcopy(previous)
        plan = self._plan()
        candidate = self._candidate(previous, plan)
        self.assertEqual(previous, snapshot)
        self.assertEqual(candidate.blocks[1:], previous.blocks[1:])
        self.assertEqual(
            candidate.blocks[0].attempts[0].status,
            previous.blocks[0].attempts[0].status,
        )
        self.assertEqual(candidate.status, previous.status)
        self.assertEqual(candidate.software, previous.software)
        self.assertEqual(candidate.inputs, previous.inputs)
        self.assertEqual(candidate.normalization, previous.normalization)
        self.assertEqual(candidate.precision, previous.precision)
        self.assertEqual(candidate.protocol, previous.protocol)
        self.assertEqual(candidate.validation, previous.validation)
        self.assertEqual(candidate.analysis, previous.analysis)
        self.assertEqual(candidate.blocking_errors, previous.blocking_errors)
        self.assertEqual(candidate.protocol_failures, previous.protocol_failures)
        self.assertEqual(candidate.analysis_warnings, previous.analysis_warnings)
        self.assertEqual(candidate.advisory_warnings, previous.advisory_warnings)

    def test_delta_validator_rejects_collateral_state(self) -> None:
        previous = self._previous()
        plan = self._plan()
        mutations = {
            "other_member": lambda c: c.blocks[0].attempts[0].members.append(
                deepcopy(c.blocks[0].attempts[0].members[-1])
            ),
            "attempt_status": lambda c: setattr(
                c.blocks[0].attempts[0], "status", "invalid"
            ),
            "block_status": lambda c: setattr(c.blocks[0], "status", "valid"),
            "selected_attempt": lambda c: setattr(
                c.blocks[0], "selected_attempt", 1
            ),
            "global_status": lambda c: setattr(c, "status", "completed"),
            "validation": lambda c: setattr(
                c,
                "validation",
                replace(c.validation, valid_blocks=1),
            ),
            "analysis": lambda c: setattr(c.analysis, "status", "failed"),
            "warning": lambda c: c.advisory_warnings.append(
                __import__(
                    "dpslab.comparison_models",
                    fromlist=["StructuredWarning"],
                ).StructuredWarning("x", "x", "advisory_warning")
            ),
            "invocation_built": lambda c: setattr(
                c.blocks[0].attempts[0].members[-1],
                "invocation",
                replace(
                    c.blocks[0].attempts[0].members[-1].invocation,
                    status="built",
                ),
            ),
            "reservation_consumed": lambda c: setattr(
                c.blocks[0].attempts[0].members[-1],
                "reservation",
                replace(
                    c.blocks[0].attempts[0].members[-1].reservation,
                    status="consumed",
                ),
            ),
            "member_running": lambda c: setattr(
                c.blocks[0].attempts[0].members[-1],
                "status",
                "running",
            ),
        }
        for label, mutation in mutations.items():
            candidate = self._candidate(previous, plan)
            mutation(candidate)
            with self.subTest(case=label), self.assertRaises(ComparisonResultError):
                validate_planned_member_candidate(previous, candidate, plan)

    def test_plaintext_token_never_enters_member_event_or_json(self) -> None:
        plan = self._plan()
        candidate = self._candidate(self._previous(), plan)
        member = self._member(candidate, plan.run_identity.member_id)
        document = result_to_document(candidate)
        serialized = json.dumps(document, sort_keys=True)
        self.assertNotIn(TOKEN_A, serialized)
        self.assertNotIn(TOKEN_A, repr(member))
        self.assertNotIn(TOKEN_A, repr(candidate.events[-1]))
        self.assertEqual(member.reservation.token_sha256, plan.token_sha256)

    def test_layer_has_no_filesystem_store_runner_adapter_or_process_effects(self) -> None:
        previous = self._previous()
        plan = self._plan()
        patches = (
            patch("pathlib.Path.exists", side_effect=AssertionError("exists")),
            patch("pathlib.Path.mkdir", side_effect=AssertionError("mkdir")),
            patch("pathlib.Path.open", side_effect=AssertionError("open")),
            patch(
                "tempfile.NamedTemporaryFile",
                side_effect=AssertionError("tempfile"),
            ),
            patch("os.link", side_effect=AssertionError("link")),
            patch("os.replace", side_effect=AssertionError("replace")),
            patch("pathlib.Path.unlink", side_effect=AssertionError("unlink")),
            patch(
                "dpslab.runner.reserve_run",
                side_effect=AssertionError("reserve_run"),
            ),
            patch(
                "dpslab.runner.run_simulation",
                side_effect=AssertionError("runner"),
            ),
            patch(
                "dpslab.comparison_adapter.execute_comparison_member",
                side_effect=AssertionError("adapter"),
            ),
            patch(
                "dpslab.comparison_result_io.ComparisonResultStore.create",
                side_effect=AssertionError("store.create"),
            ),
            patch(
                "dpslab.comparison_result_io.ComparisonResultStore.commit",
                side_effect=AssertionError("store.commit"),
            ),
            patch(
                "dpslab.comparison_result_io.ComparisonResultStore.commit_member",
                side_effect=AssertionError("store.commit_member"),
            ),
            patch("subprocess.run", side_effect=AssertionError("subprocess")),
        )
        entered = []
        try:
            for item in patches:
                entered.append(item)
                item.start()
            candidate = self._candidate(previous, plan)
        finally:
            for item in reversed(entered):
                item.stop()
        self.assertEqual(
            self._member(candidate, plan.run_identity.member_id).status,
            "planned",
        )


if __name__ == "__main__":
    unittest.main()
