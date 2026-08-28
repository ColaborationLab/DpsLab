from __future__ import annotations

import tempfile
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from tests.strict_temporary_cleanup import strict_temporary_cleanup

from dpslab.comparator import _new_result as _new_result_impl
from dpslab.comparison_environment import software_record
from dpslab.comparison_models import (
    ComparisonMember,
    ComparisonResultError,
    EffectiveParameters,
    InvocationRecord,
    MemberDps,
    MemberIntegrity,
    PairAttempt,
    PlannedParameters,
    RunArtifactReference,
    RunArtifactSet,
    RunReservationRecord,
    SimulationCraftIdentity,
    StateEvent,
    StructuredError,
    StructuredWarning,
)
from dpslab.comparison_result_io import ComparisonResultStore
from dpslab.comparison_spec import load_comparison_spec
from dpslab.comparison_transitions import member_transition_candidate


ROOT = Path(__file__).resolve().parents[2]
SPEC = load_comparison_spec(
    ROOT / "comparisons/flasil_neck_50228_vs_249368_v1.toml",
    root=ROOT,
)
SOFTWARE = software_record(ROOT)


def _new_result(spec, execution_id):
    return _new_result_impl(spec, execution_id, SOFTWARE)


PREVIOUS_TIME = "2026-07-16T00:00:00Z"
STARTED_TIME = "2026-07-16T00:00:01Z"
EVENT_TIME = "2026-07-16T00:00:02Z"
TRANSITIONS = (
    ("planned", "running"),
    ("planned", "invalid"),
    ("planned", "interrupted"),
    ("running", "completed"),
    ("running", "invalid"),
    ("running", "interrupted"),
)


def _integrity(value: bool) -> MemberIntegrity:
    return MemberIntegrity(*(value for _ in range(9)))


def _artifacts(valid: bool = True) -> RunArtifactSet:
    names = (
        ("metadata", "metadata.json"),
        ("simc_json", "simc.json"),
        ("stdout", "stdout.txt"),
        ("stderr", "stderr.txt"),
        ("summary", "run_summary.json"),
        ("effective_profile", "effective_profile.simc"),
    )
    return RunArtifactSet(
        tuple(
            RunArtifactReference(
                kind,
                path,
                "f" * 64,
                True,
                valid if kind in {"metadata", "simc_json", "summary"} else None,
            )
            for kind, path in names
        )
    )


class ComparisonMemberTransactionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(strict_temporary_cleanup, self.temp, Path(self.temp.name))

    def _result_for(self, initial: str, final: str, identity: str = "execution"):
        result = _new_result(SPEC, identity)
        result.events = [
            StateEvent(
                1,
                f"{identity}-historical",
                PREVIOUS_TIME,
                "attempt",
                f"{identity}:historical",
                "planned",
                "running",
                "historical",
            )
        ]
        result.updated_at = PREVIOUS_TIME
        member_id = f"{identity}:block-1:attempt-1:a"
        planned = PlannedParameters(SPEC.protocol.seeds[0], 5000, 2, None, 900)
        reservation_status = "reserved"
        invocation = InvocationRecord(
            "built",
            ("<SIMC_EXE>", "effective_profile.simc"),
            "a" * 64,
            "b" * 64,
            "c" * 64,
            "test",
            True,
            False,
            PREVIOUS_TIME,
        )
        effective = None
        observed = None
        artifacts = RunArtifactSet()
        dps = None
        integrity = None
        errors: list[StructuredError] = []
        run_id = None
        started_at = None

        if initial == "planned" and final in {"invalid", "interrupted"}:
            reservation_status = "abandoned"
            invocation = InvocationRecord(
                "failed_before_start",
                failure_stage="synthetic",
                failure_reason="synthetic",
            )
            errors = [StructuredError("alpha", "beta", "gamma")]
        elif initial == "running":
            reservation_status = "consumed"
            started_at = STARTED_TIME
            if final == "completed":
                invocation = InvocationRecord(
                    "completed",
                    ("<SIMC_EXE>",),
                    "a" * 64,
                    "b" * 64,
                    "c" * 64,
                    "test",
                    True,
                    False,
                    PREVIOUS_TIME,
                    STARTED_TIME,
                )
                effective = EffectiveParameters(SPEC.protocol.seeds[0], 5000, 2, None, 900)
                observed = SimulationCraftIdentity("1205-01", "a81c39d", "c" * 64)
                artifacts = _artifacts()
                dps = MemberDps(100000.0)
                integrity = _integrity(True)
                run_id = f"{identity}-run"
            else:
                invocation = InvocationRecord(
                    "failed_after_start",
                    ("<SIMC_EXE>",),
                    "a" * 64,
                    "b" * 64,
                    "c" * 64,
                    "test",
                    True,
                    False,
                    PREVIOUS_TIME,
                    STARTED_TIME,
                    failure_stage="synthetic",
                    failure_reason="synthetic",
                )
                integrity = _integrity(False)
                errors = [StructuredError("alpha", "beta", "gamma")]

        reservation = RunReservationRecord(
            f"{identity}-run",
            identity,
            member_id,
            "d" * 64,
            reservation_status,
            PREVIOUS_TIME,
        )
        member = ComparisonMember(
            member_id,
            SPEC.comparison_id,
            identity,
            SPEC.source_sha256,
            1,
            1,
            "a",
            1,
            SPEC.protocol.seeds[0],
            SPEC.arm_a.item_id,
            reservation,
            SPEC.base_profile_sha256,
            "e" * 64,
            SPEC.scenario_sha256,
            SPEC.evidence_sha256,
            planned,
            effective,
            invocation,
            SimulationCraftIdentity("1205-01", "a81c39d", "c" * 64),
            observed,
            artifacts,
            dps,
            integrity,
            errors,
            [],
            initial,
            PREVIOUS_TIME,
            run_id,
            started_at,
            None,
            None,
        )
        attempt = PairAttempt(1, f"{identity}:block-1:attempt-1", identity, status="running")
        attempt.members = [member]
        result.blocks[0].status = "running"
        result.blocks[0].attempts = [attempt]
        return result, member_id

    @staticmethod
    def _member(result, member_id):
        return next(
            member
            for block in result.blocks
            for attempt in block.attempts
            for member in attempt.members
            if member.member_id == member_id
        )

    def _candidate(self, previous, member_id, final, suffix="event"):
        return member_transition_candidate(
            previous,
            member_id,
            final,
            EVENT_TIME,
            f"{member_id}:{suffix}",
            "synthetic transition",
        )

    def test_six_transition_success_matrix_is_copy_on_write_and_durable(self) -> None:
        for index, (initial, final) in enumerate(TRANSITIONS):
            with self.subTest(transition=f"{initial}->{final}"):
                previous, member_id = self._result_for(initial, final, f"success-{index}")
                snapshot = deepcopy(previous)
                candidate = self._candidate(previous, member_id, final)
                previous_member = self._member(previous, member_id)
                candidate_member = self._member(candidate, member_id)
                self.assertEqual(previous, snapshot)
                self.assertIsNot(previous, candidate)
                self.assertIsNot(previous_member, candidate_member)
                self.assertEqual(candidate_member.reservation, previous_member.reservation)
                self.assertEqual(candidate_member.invocation, previous_member.invocation)
                self.assertEqual(candidate_member.errors, previous_member.errors)
                self.assertEqual(candidate_member.status, final)
                self.assertEqual(candidate.updated_at, EVENT_TIME)
                self.assertEqual(candidate.events[-1].occurred_at, EVENT_TIME)
                if (initial, final) == ("planned", "running"):
                    self.assertEqual(candidate_member.started_at, EVENT_TIME)
                    self.assertIsNone(candidate_member.finished_at)
                elif initial == "planned":
                    self.assertIsNone(candidate_member.started_at)
                    self.assertEqual(candidate_member.finished_at, EVENT_TIME)
                else:
                    self.assertEqual(candidate_member.started_at, STARTED_TIME)
                    self.assertEqual(candidate_member.finished_at, EVENT_TIME)

                path = Path(self.temp.name) / f"success-{index}.json"
                store = ComparisonResultStore(path)
                store.create(previous)
                confirmed = store.commit_member(previous, candidate, member_id)
                self.assertEqual(confirmed, candidate)
                self.assertEqual(store.read(), candidate)

    def test_confirmed_is_exactly_the_generic_commit_result_and_called_once(self) -> None:
        previous, member_id = self._result_for("planned", "running", "confirmed")
        candidate = self._candidate(previous, member_id, "running")
        confirmed = object()
        store = ComparisonResultStore(Path(self.temp.name) / "unused.json")
        with patch.object(store, "commit", return_value=confirmed) as commit:
            returned = store.commit_member(previous, candidate, member_id)
        self.assertIs(returned, confirmed)
        commit.assert_called_once_with(previous, candidate)

    def test_all_forbidden_real_status_transitions_are_rejected(self) -> None:
        real_statuses = ("planned", "running", "completed", "invalid", "interrupted")
        allowed = set(TRANSITIONS)
        for initial in real_statuses:
            for final in real_statuses:
                if (initial, final) in allowed:
                    continue
                previous, member_id = self._result_for("planned", "running", f"{initial}-{final}")
                member = self._member(previous, member_id)
                member.status = initial
                member.started_at = STARTED_TIME if initial == "running" else member.started_at
                with self.subTest(transition=f"{initial}->{final}"), self.assertRaises(ComparisonResultError):
                    self._candidate(previous, member_id, final)

    def test_member_must_be_unique_and_present(self) -> None:
        previous, member_id = self._result_for("planned", "running", "identity")
        with self.assertRaisesRegex(ComparisonResultError, "ausente"):
            self._candidate(previous, "missing", "running")
        duplicate = deepcopy(self._member(previous, member_id))
        previous.blocks[0].attempts[0].members.append(duplicate)
        with self.assertRaisesRegex(ComparisonResultError, "duplicado"):
            self._candidate(previous, member_id, "running")

    def test_planned_running_precondition_matrix(self) -> None:
        mutations = {
            "reservation_missing_owner": lambda m: setattr(
                m, "reservation", replace(m.reservation, owner_member_id="other")
            ),
            "reservation_abandoned": lambda m: setattr(
                m, "reservation", replace(m.reservation, status="abandoned")
            ),
            "reservation_consumed": lambda m: setattr(
                m, "reservation", replace(m.reservation, status="consumed")
            ),
            "invocation_not_built": lambda m: setattr(m, "invocation", InvocationRecord("not_built")),
            "invocation_process_started": lambda m: setattr(
                m, "invocation", replace(m.invocation, status="process_started", process_started_at=STARTED_TIME)
            ),
            "preexisting_run_id": lambda m: setattr(m, "run_id", m.planned_run_id),
            "preexisting_dps": lambda m: setattr(m, "dps", MemberDps(1.0)),
            "preexisting_integrity": lambda m: setattr(m, "integrity", _integrity(False)),
            "preexisting_error": lambda m: m.errors.append(StructuredError("a", "b", "c")),
        }
        for index, (label, mutation) in enumerate(mutations.items()):
            previous, member_id = self._result_for("planned", "running", f"start-{index}")
            mutation(self._member(previous, member_id))
            with self.subTest(case=label), self.assertRaises(ComparisonResultError):
                self._candidate(previous, member_id, "running")

    def test_planned_terminal_reservation_and_cause_matrix(self) -> None:
        for final in ("invalid", "interrupted"):
            for reservation_status in ("reserved", "consumed"):
                previous, member_id = self._result_for("planned", final, f"{final}-{reservation_status}")
                member = self._member(previous, member_id)
                member.reservation = replace(member.reservation, status=reservation_status)
                with self.subTest(final=final, reservation=reservation_status), self.assertRaises(ComparisonResultError):
                    self._candidate(previous, member_id, final)

            previous, member_id = self._result_for("planned", final, f"{final}-cause")
            self._member(previous, member_id).errors = []
            with self.subTest(final=final, cause="missing"), self.assertRaises(ComparisonResultError):
                self._candidate(previous, member_id, final)

            previous, member_id = self._result_for("planned", final, f"{final}-owner")
            member = self._member(previous, member_id)
            member.reservation = replace(member.reservation, owner_execution_id="other")
            with self.subTest(final=final, cause="owner"), self.assertRaises(ComparisonResultError):
                self._candidate(previous, member_id, final)

    def test_structured_error_is_presence_only_and_text_is_not_interpreted(self) -> None:
        errors = (
            StructuredError("one", "two", "three"),
            StructuredError("completely_unrelated", "arbitrary prose", "elsewhere"),
        )
        for final in ("invalid", "interrupted"):
            for index, error in enumerate(errors):
                previous, member_id = self._result_for("planned", final, f"text-{final}-{index}")
                self._member(previous, member_id).errors = [error]
                candidate = self._candidate(previous, member_id, final)
                self.assertEqual(self._member(candidate, member_id).errors, [error])

            previous, member_id = self._result_for("planned", final, f"blank-{final}")
            self._member(previous, member_id).errors = [StructuredError("", "", "")]
            with self.assertRaises(ComparisonResultError):
                self._candidate(previous, member_id, final)

    def test_completed_requires_the_full_preexisting_result_and_integrity(self) -> None:
        mutations = {
            "run_id": lambda m: setattr(m, "run_id", "other"),
            "dps_absent": lambda m: setattr(m, "dps", None),
            "dps_nonpositive": lambda m: setattr(m, "dps", MemberDps(0.0)),
            "parameters_absent": lambda m: setattr(m, "effective_parameters", None),
            "parameters_mismatch": lambda m: setattr(
                m, "effective_parameters", replace(m.effective_parameters, iterations=4999)
            ),
            "simc_absent": lambda m: setattr(m, "observed_simc", None),
            "artifacts_incomplete": lambda m: setattr(m, "artifacts", RunArtifactSet()),
            "integrity_absent": lambda m: setattr(m, "integrity", None),
            "integrity_failed": lambda m: setattr(m, "integrity", _integrity(False)),
            "invocation_not_completed": lambda m: setattr(
                m, "invocation", replace(m.invocation, status="process_started")
            ),
            "blocking_error": lambda m: m.errors.append(StructuredError("a", "b", "c")),
        }
        for index, (label, mutation) in enumerate(mutations.items()):
            previous, member_id = self._result_for("running", "completed", f"complete-{index}")
            mutation(self._member(previous, member_id))
            with self.subTest(case=label), self.assertRaises(ComparisonResultError):
                self._candidate(previous, member_id, "completed")

    def test_running_noneligible_terminals_require_cause_and_reject_accepted_result(self) -> None:
        for final in ("invalid", "interrupted"):
            previous, member_id = self._result_for("running", final, f"{final}-missing")
            self._member(previous, member_id).errors = []
            with self.subTest(final=final, case="missing_cause"), self.assertRaises(ComparisonResultError):
                self._candidate(previous, member_id, final)

            accepted, member_id = self._result_for("running", "completed", f"{final}-accepted")
            self._member(accepted, member_id).errors = [StructuredError("x", "y", "z")]
            with self.subTest(final=final, case="accepted_result"), self.assertRaises(ComparisonResultError):
                self._candidate(accepted, member_id, final)

            previous, member_id = self._result_for("running", final, f"{final}-not-started")
            member = self._member(previous, member_id)
            member.invocation = replace(member.invocation, status="built", process_started_at=None)
            with self.subTest(final=final, case="not_started"), self.assertRaises(ComparisonResultError):
                self._candidate(previous, member_id, final)

    def test_timestamp_policy_matrix_is_exact(self) -> None:
        cases = {
            "updated_at_mismatch": lambda c, m: setattr(c, "updated_at", STARTED_TIME),
            "occurred_at_before_previous": lambda c, m: (
                c.events.__setitem__(
                    -1,
                    replace(c.events[-1], occurred_at="2026-07-15T23:59:59Z"),
                ),
                setattr(c, "updated_at", "2026-07-15T23:59:59Z"),
                setattr(m, "finished_at", "2026-07-15T23:59:59Z"),
            ),
            "terminal_timestamp_mismatch": lambda c, m: setattr(m, "finished_at", STARTED_TIME),
            "started_at_modified": lambda c, m: setattr(m, "started_at", PREVIOUS_TIME),
            "finished_before_started": lambda c, m: (
                c.events.__setitem__(-1, replace(c.events[-1], occurred_at=PREVIOUS_TIME)),
                setattr(c, "updated_at", PREVIOUS_TIME),
                setattr(m, "finished_at", PREVIOUS_TIME),
            ),
        }
        for index, (label, mutation) in enumerate(cases.items()):
            previous, member_id = self._result_for("running", "invalid", f"time-{index}")
            candidate = self._candidate(previous, member_id, "invalid")
            mutation(candidate, self._member(candidate, member_id))
            store = ComparisonResultStore(Path(self.temp.name) / f"time-{index}.json")
            with self.subTest(case=label), patch.object(store, "commit") as commit, self.assertRaises(ComparisonResultError):
                store.commit_member(previous, candidate, member_id)
            commit.assert_not_called()

        previous, member_id = self._result_for("planned", "running", "running-finished")
        candidate = self._candidate(previous, member_id, "running")
        self._member(candidate, member_id).finished_at = EVENT_TIME
        with self.assertRaises(ComparisonResultError):
            ComparisonResultStore(Path(self.temp.name) / "running-finished.json").commit_member(
                previous, candidate, member_id
            )

    def test_single_delta_rejects_every_other_durable_family(self) -> None:
        mutations = {
            "reservation": lambda c, m: setattr(m, "reservation", replace(m.reservation, token_sha256="0" * 64)),
            "invocation": lambda c, m: setattr(m, "invocation", replace(m.invocation, executable_source="other")),
            "dps": lambda c, m: setattr(m, "dps", MemberDps(1.0)),
            "parameters": lambda c, m: setattr(m, "effective_parameters", EffectiveParameters(1, 1, 1, None, 1)),
            "artifacts": lambda c, m: setattr(m, "artifacts", _artifacts()),
            "integrity": lambda c, m: setattr(m, "integrity", _integrity(False)),
            "errors": lambda c, m: m.errors.append(StructuredError("a", "b", "c")),
            "warnings": lambda c, m: m.warnings.append(StructuredWarning("a", "b", "advisory_warning")),
            "attempt": lambda c, m: setattr(c.blocks[0].attempts[0], "status", "invalid"),
            "block": lambda c, m: setattr(c.blocks[0], "seed", c.blocks[0].seed + 1),
            "global_status": lambda c, m: setattr(c, "status", "running"),
            "software": lambda c, m: setattr(c, "software", replace(c.software, simulationcraft=SimulationCraftIdentity("x", "y", "z"))),
            "inputs": lambda c, m: setattr(c, "inputs", replace(c.inputs, base_profile=replace(c.inputs.base_profile, hash_verified=False))),
            "protocol": lambda c, m: setattr(c, "protocol", replace(c.protocol, threads=3)),
            "validation": lambda c, m: setattr(c, "validation", replace(c.validation, valid_blocks=1)),
            "analysis": lambda c, m: setattr(c.analysis, "status", "failed"),
            "previous_event": lambda c, m: c.events.__setitem__(0, replace(c.events[0], reason="changed")),
        }
        for index, (label, mutation) in enumerate(mutations.items()):
            previous, member_id = self._result_for("planned", "running", f"delta-{index}")
            candidate = self._candidate(previous, member_id, "running")
            mutation(candidate, self._member(candidate, member_id))
            store = ComparisonResultStore(Path(self.temp.name) / f"delta-{index}.json")
            with self.subTest(case=label), patch.object(store, "commit") as commit, self.assertRaises(ComparisonResultError):
                store.commit_member(previous, candidate, member_id)
            commit.assert_not_called()

    def test_member_event_matrix_is_validated_before_generic_commit(self) -> None:
        mutations = {
            "missing": lambda c: setattr(c, "events", c.events[:-1]),
            "two": lambda c: c.events.append(replace(c.events[-1], sequence=3, event_id="extra")),
            "entity_type": lambda c: c.events.__setitem__(-1, replace(c.events[-1], entity_type="block")),
            "entity_id": lambda c: c.events.__setitem__(-1, replace(c.events[-1], entity_id="other")),
            "previous_status": lambda c: c.events.__setitem__(-1, replace(c.events[-1], previous_status="running")),
            "new_status": lambda c: c.events.__setitem__(-1, replace(c.events[-1], new_status="invalid")),
            "sequence": lambda c: c.events.__setitem__(-1, replace(c.events[-1], sequence=99)),
            "empty_id": lambda c: c.events.__setitem__(-1, replace(c.events[-1], event_id="")),
            "duplicate_id": lambda c: c.events.__setitem__(-1, replace(c.events[-1], event_id=c.events[0].event_id)),
            "invalid_time": lambda c: c.events.__setitem__(-1, replace(c.events[-1], occurred_at="bad")),
            "empty_reason": lambda c: c.events.__setitem__(-1, replace(c.events[-1], reason="")),
            "historical_changed": lambda c: c.events.__setitem__(0, replace(c.events[0], reason="changed")),
            "historical_removed": lambda c: setattr(c, "events", c.events[1:]),
            "reordered": lambda c: setattr(c, "events", list(reversed(c.events))),
            "inserted_middle": lambda c: setattr(c, "events", [c.events[0], replace(c.events[-1], event_id="middle"), c.events[-1]]),
        }
        for index, (label, mutation) in enumerate(mutations.items()):
            previous, member_id = self._result_for("planned", "running", f"event-{index}")
            candidate = self._candidate(previous, member_id, "running")
            mutation(candidate)
            store = ComparisonResultStore(Path(self.temp.name) / f"event-{index}.json")
            with self.subTest(case=label), patch.object(store, "commit") as commit, self.assertRaises(ComparisonResultError):
                store.commit_member(previous, candidate, member_id)
            commit.assert_not_called()

    def test_failure_has_no_retry_fallback_or_candidate_adoption(self) -> None:
        for index, (initial, final) in enumerate(TRANSITIONS):
            previous, member_id = self._result_for(initial, final, f"failure-{index}")
            snapshot = deepcopy(previous)
            candidate = self._candidate(previous, member_id, final)
            store = ComparisonResultStore(Path(self.temp.name) / f"unused-failure-{index}.json")
            with self.subTest(transition=f"{initial}->{final}"), patch.object(
                store, "commit", side_effect=OSError("injected")
            ) as commit:
                with self.assertRaisesRegex(OSError, "injected"):
                    store.commit_member(previous, candidate, member_id)
            commit.assert_called_once_with(previous, candidate)
            self.assertEqual(previous, snapshot)
            self.assertEqual(self._member(previous, member_id).status, initial)

    def test_each_transition_rejects_a_missing_precondition_and_extra_delta(self) -> None:
        for index, (initial, final) in enumerate(TRANSITIONS):
            missing, member_id = self._result_for(initial, final, f"missing-{index}")
            member = self._member(missing, member_id)
            if (initial, final) == ("planned", "running"):
                member.invocation = InvocationRecord("not_built")
            elif initial == "planned" or final in {"invalid", "interrupted"}:
                member.errors = []
            else:
                member.integrity = None
            with self.subTest(transition=f"{initial}->{final}", case="precondition"), self.assertRaises(ComparisonResultError):
                self._candidate(missing, member_id, final)

            previous, member_id = self._result_for(initial, final, f"extra-{index}")
            candidate = self._candidate(previous, member_id, final)
            self._member(candidate, member_id).warnings.append(
                StructuredWarning("extra", "extra", "advisory_warning")
            )
            store = ComparisonResultStore(Path(self.temp.name) / f"extra-{index}.json")
            with self.subTest(transition=f"{initial}->{final}", case="delta"), patch.object(
                store, "commit"
            ) as commit, self.assertRaises(ComparisonResultError):
                store.commit_member(previous, candidate, member_id)
            commit.assert_not_called()

    def test_representative_physical_rollback_preserves_confirmed_bytes(self) -> None:
        previous, member_id = self._result_for("planned", "running", "rollback")
        snapshot = deepcopy(previous)
        candidate = self._candidate(previous, member_id, "running")
        path = Path(self.temp.name) / "rollback.json"
        store = ComparisonResultStore(path)
        store.create(previous)
        before = path.read_bytes()
        with patch("dpslab.comparison_result_io.os.replace", side_effect=OSError("injected")):
            with self.assertRaisesRegex(OSError, "injected"):
                store.commit_member(previous, candidate, member_id)
        self.assertEqual(previous, snapshot)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(store.read(), previous)
        self.assertEqual(list(path.parent.glob(".comparison_result.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
