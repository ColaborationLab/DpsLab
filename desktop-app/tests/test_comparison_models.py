from __future__ import annotations

import json
import math
import tempfile
import unittest
from copy import deepcopy
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from tests.strict_temporary_cleanup import strict_temporary_cleanup

from dpslab.comparator import _new_result as _new_result_impl
from dpslab.comparison_environment import software_record
from dpslab.comparison_models import (
    AnalysisDiagnostics, ComparisonAnalysis, ComparisonMember, ComparisonResultError,
    EffectiveParameters, InvocationRecord, MemberDps, PairedSensitivityResult,
    PairAttempt, PlannedParameters, PrimaryAnalysisResult, RunArtifactSet,
    RunReservationRecord, SimulationCraftIdentity, StructuredError,
    StateEvent, StructuredWarning, execution_transition_candidate, recover_from_json,
    recover_interrupted, transition, utc_now,
)
from dpslab.comparison_result_io import (
    ComparisonResultStore, _ComparisonFileOperations, result_from_document,
    result_to_document,
)
from dpslab.comparison_spec import load_comparison_spec


ROOT = Path(__file__).resolve().parents[2]
SPEC = load_comparison_spec(ROOT / "comparisons/flasil_neck_50228_vs_249368_v1.toml", root=ROOT)
SOFTWARE = software_record(ROOT)


def _new_result(spec, execution_id):
    return _new_result_impl(spec, execution_id, SOFTWARE)


class RecordingFileOperations(_ComparisonFileOperations):
    def __init__(self, failure: str | None = None, *, cleanup_failure: bool = False) -> None:
        self.failure = failure
        self.cleanup_failure = cleanup_failure
        self.calls: list[str] = []

    def _record(self, operation: str) -> None:
        self.calls.append(operation)
        if self.failure == operation:
            if operation == "link": raise PermissionError("injected link permission")
            raise OSError(f"injected {operation}")

    def exists(self, path): self._record("exists"); return super().exists(path)
    def read_text(self, path): self._record("read_text"); return super().read_text(path)
    def make_directory(self, path): self._record("make_directory"); return super().make_directory(path)
    def temporary_file(self, directory): self._record("temporary_file"); return super().temporary_file(directory)
    def serialize(self, document, stream):
        self._record("serialize")
        if self.failure == "partial_write":
            stream.write("{\n"); raise OSError("injected partial_write")
        return super().serialize(document, stream)
    def flush(self, stream): self._record("flush"); return super().flush(stream)
    def sync(self, stream): self._record("sync"); return super().sync(stream)
    def close(self, stream):
        self.calls.append("close")
        if self.failure == "close":
            super().close(stream); raise OSError("injected close")
        return super().close(stream)
    def link(self, source, destination): self._record("link"); return super().link(source, destination)
    def replace(self, source, destination): self._record("replace"); return super().replace(source, destination)
    def unlink(self, path, *, missing_ok=False):
        self.calls.append("unlink")
        if self.cleanup_failure: raise OSError("injected cleanup")
        return super().unlink(path, missing_ok=missing_ok)


class ComparisonModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(strict_temporary_cleanup, self.temp, Path(self.temp.name))
        self.path = Path(self.temp.name) / "comparison_result.json"
        self.result = _new_result(SPEC, "execution")

    def _running_member(self) -> ComparisonMember:
        member_id = "execution:block-1:attempt-1:a"
        return ComparisonMember(
            member_id, SPEC.comparison_id, "execution", SPEC.source_sha256, 1, 1, "a", 1,
            SPEC.protocol.seeds[0], SPEC.arm_a.item_id,
            RunReservationRecord("run", "execution", member_id, "a" * 64, "consumed", utc_now()),
            SPEC.base_profile_sha256, "b" * 64, SPEC.scenario_sha256, SPEC.evidence_sha256,
            PlannedParameters(SPEC.protocol.seeds[0], 5000, 2, None, 900),
            EffectiveParameters(SPEC.protocol.seeds[0], 5000, 2, None, 900),
            InvocationRecord("process_started", ("<SIMC_EXE>",), "c" * 64, "d" * 64, "e" * 64, "test", True, False, utc_now(), utc_now()),
            SimulationCraftIdentity("x", "y", "e" * 64), None, RunArtifactSet(), MemberDps(None), None, [], [], "running",
        )

    def _set_running(self) -> None:
        self.result.transition_execution("running", "started")
        block = self.result.blocks[0]; transition(block, "block", "block", "running", "started", self.result)
        attempt = PairAttempt(1, "attempt", "execution"); transition(attempt, "attempt", "attempt", "running", "started", self.result)
        attempt.members = [self._running_member()]; block.attempts = [attempt]

    def _historical_previous(self, initial: str, identity: str) -> object:
        result = _new_result(SPEC, identity)
        result.status = initial
        result.started_at = utc_now() if initial == "running" else None
        result.events = [
            StateEvent(1, f"{identity}-event-1", utc_now(), "block", "historical-1", "planned", "running", "history_one"),
            StateEvent(2, f"{identity}-event-2", utc_now(), "attempt", "historical-2", "planned", "running", "history_two"),
        ]
        result.updated_at = result.events[-1].occurred_at
        return result

    def _assert_logical_rejection(self, previous, candidate, label: str) -> None:
        path = Path(self.temp.name) / f"logical-{label}.json"
        ComparisonResultStore(path).create(previous)
        before, snapshot = path.read_bytes(), deepcopy(previous)
        operations = RecordingFileOperations()
        with self.assertRaises(ComparisonResultError):
            ComparisonResultStore(path, file_operations=operations).commit_execution(previous, candidate)
        forbidden = {"make_directory", "temporary_file", "serialize", "flush", "sync", "close", "replace", "unlink", "link"}
        self.assertFalse(forbidden.intersection(operations.calls), operations.calls)
        self.assertEqual(previous, snapshot); self.assertEqual(path.read_bytes(), before)
        self.assertEqual(ComparisonResultStore(path).read(), previous)
        self.assertEqual(list(path.parent.glob(".comparison_result.*.tmp")), [])

    def test_global_frozen_field_matrix_is_individual_and_prephysical(self) -> None:
        primary = PrimaryAnalysisResult("welch_delta", 1.0, 1.0, 7.0, 2.0, -1.0, 3.0, "inconclusive")
        paired = PairedSensitivityResult("paired_t", 1.0, 1.0, 7.0, 2.0, -1.0, 3.0, "inconclusive")
        cases = {
            "comparison_id": lambda c: setattr(c, "comparison_id", "other_comparison"),
            "comparison_execution_id": lambda c: setattr(c, "comparison_execution_id", "other_execution"),
            "spec_path": lambda c: setattr(c, "spec_path", "comparisons/other.toml"),
            "spec_sha256": lambda c: setattr(c, "spec_sha256", "0" * 64),
            "created_at": lambda c: setattr(c, "created_at", "2026-01-01T00:00:00Z"),
            "software.python.version": lambda c: setattr(c, "software", replace(c.software, python=replace(c.software.python, version="0"))),
            "software.python.implementation": lambda c: setattr(c, "software", replace(c.software, python=replace(c.software.python, implementation="Other"))),
            "software.scipy.requirement": lambda c: setattr(c, "software", replace(c.software, scipy=replace(c.software.scipy, requirement=">=0"))),
            "software.scipy.version": lambda c: setattr(c, "software", replace(c.software, scipy=replace(c.software.scipy, version="0"))),
            "software.dpslab.source_identity_kind": lambda c: setattr(c, "software", replace(c.software, dpslab=replace(c.software.dpslab, source_identity_kind="other"))),
            "software.dpslab.version": lambda c: setattr(c, "software", replace(c.software, dpslab=replace(c.software.dpslab, version="9"))),
            "software.dpslab.commit": lambda c: setattr(c, "software", replace(c.software, dpslab=replace(c.software.dpslab, commit="abc"))),
            "software.dpslab.source_tree_sha256": lambda c: setattr(c, "software", replace(c.software, dpslab=replace(c.software.dpslab, source_tree_sha256="0" * 64))),
            "software.dpslab.source_inventory_method": lambda c: setattr(c, "software", replace(c.software, dpslab=replace(c.software.dpslab, source_inventory_method="other"))),
            "software.dpslab.source_inventory": lambda c: setattr(c, "software", replace(c.software, dpslab=replace(c.software.dpslab, source_inventory=(*c.software.dpslab.source_inventory, "other.py")))),
            "software.platform.system": lambda c: setattr(c, "software", replace(c.software, platform=replace(c.software.platform, system="Other"))),
            "software.platform.release": lambda c: setattr(c, "software", replace(c.software, platform=replace(c.software.platform, release="Other"))),
            "software.platform.machine": lambda c: setattr(c, "software", replace(c.software, platform=replace(c.software.platform, machine="Other"))),
            "software.platform.python_platform": lambda c: setattr(c, "software", replace(c.software, platform=replace(c.software.platform, python_platform="other"))),
            "software.simulationcraft.version": lambda c: setattr(c, "software", replace(c.software, simulationcraft=replace(c.software.simulationcraft, version="1205"))),
            "software.simulationcraft.revision": lambda c: setattr(c, "software", replace(c.software, simulationcraft=replace(c.software.simulationcraft, revision="rev"))),
            "software.simulationcraft.executable_sha256": lambda c: setattr(c, "software", replace(c.software, simulationcraft=replace(c.software.simulationcraft, executable_sha256="0" * 64))),
        }
        for section in ("base_profile", "scenario", "evidence_manifest"):
            for field_name, value in (("path", "other"), ("sha256", "0" * 64), ("hash_verified", False)):
                key = f"inputs.{section}.{field_name}"
                cases[key] = lambda c, section=section, field_name=field_name, value=value: setattr(c, "inputs", replace(c.inputs, **{section: replace(getattr(c.inputs, section), **{field_name: value})}))
        for field_name, value in (("policy", "other"), ("status", "other")):
            cases[f"normalization.{field_name}"] = lambda c, field_name=field_name, value=value: setattr(c, "normalization", replace(c.normalization, **{field_name: value}))
        for field_name, value in (("path", "other"), ("sha256", "0" * 64), ("hash_verified", False)):
            cases[f"normalization.evidence.{field_name}"] = lambda c, field_name=field_name, value=value: setattr(c, "normalization", replace(c.normalization, evidence=replace(c.normalization.evidence, **{field_name: value})))
        for field_name, value in (("precision_source", "other"), ("precision_mode", "other"), ("iterations_per_run", 5001), ("target_error", 0.1)):
            cases[f"precision.{field_name}"] = lambda c, field_name=field_name, value=value: setattr(c, "precision", replace(c.precision, **{field_name: value}))
        protocol_values = {"blocks": 9, "threads": 3, "within_pair_pause_seconds": 31.0, "between_block_pause_seconds": 61.0, "timeout_seconds": 901.0, "max_pair_attempts": 3, "retry_full_pair": False, "require_all_blocks_valid": False, "exclude_dps_outliers": True, "early_stopping": True}
        for field_name, value in protocol_values.items():
            cases[f"protocol.{field_name}"] = lambda c, field_name=field_name, value=value: setattr(c, "protocol", replace(c.protocol, **{field_name: value}))
        validation_values = {"valid_blocks": 1, "required_valid_blocks": 9, "valid_run_ids": ("run",), "duplicate_run_ids": ("run",), "all_seeds_verified": True, "all_orders_verified": True, "all_parameters_verified": True, "only_neck_changed": True, "provenance_complete": True}
        for field_name, value in validation_values.items():
            cases[f"validation.{field_name}"] = lambda c, field_name=field_name, value=value: setattr(c, "validation", replace(c.validation, **{field_name: value}))
        analysis_values = {"status": "failed", "analysis_seed": 1, "stochastic_analysis": True, "primary": primary, "paired_sensitivity": paired, "diagnostics": AnalysisDiagnostics(0.0, False), "final_classification": "inconclusive"}
        for field_name, value in analysis_values.items():
            cases[f"analysis.{field_name}"] = lambda c, field_name=field_name, value=value: setattr(c, "analysis", replace(c.analysis, **{field_name: value}))
        cases["blocks[0].status"] = lambda c: setattr(c.blocks[0], "status", "running")
        cases["blocks[0].attempts"] = lambda c: setattr(c.blocks[0], "attempts", [PairAttempt(1, "other", c.comparison_execution_id)])
        cases["blocks[0].seed"] = lambda c: setattr(c.blocks[0], "seed", c.blocks[0].seed + 1)
        for index, (path_name, mutation) in enumerate(cases.items()):
            previous = _new_result(SPEC, f"frozen-{index}"); candidate = execution_transition_candidate(previous, "running", "start")
            mutation(candidate)
            with self.subTest(path=path_name): self._assert_logical_rejection(previous, candidate, f"frozen-{index}")
        for dirty_state, mutated_dirty_state in ((False, True), (True, False), (None, False)):
            previous = _new_result(SPEC, f"frozen-dirty-{dirty_state}")
            previous.software = replace(previous.software, dpslab=replace(previous.software.dpslab, dirty_state=dirty_state))
            candidate = execution_transition_candidate(previous, "running", "start")
            candidate.software = replace(candidate.software, dpslab=replace(candidate.software.dpslab, dirty_state=mutated_dirty_state))
            with self.subTest(path="software.dpslab.dirty_state", original=dirty_state):
                self._assert_logical_rejection(previous, candidate, f"frozen-dirty-{dirty_state}")

    def test_exhaustive_previous_event_history_matrix_for_all_global_transitions(self) -> None:
        transitions = (("ready", "blocked"), ("ready", "running"), ("running", "completed"), ("running", "inconclusive"), ("running", "failed_protocol"))
        for transition_index, (initial, final) in enumerate(transitions):
            valid_path = Path(self.temp.name) / f"event-valid-{initial}-{final}.json"
            previous = self._historical_previous(initial, f"events-valid-{transition_index}")
            store = ComparisonResultStore(valid_path); store.create(previous)
            candidate = execution_transition_candidate(previous, final, "valid_transition")
            confirmed = store.commit_execution(previous, candidate)
            self.assertEqual(tuple(confirmed.events[:-1]), tuple(previous.events)); self.assertEqual(len(confirmed.events), 3)
            def assign(c, events): c.events = events
            mutations = {
                "previous_modified": lambda c: assign(c, [replace(c.events[0], reason="changed"), c.events[1], c.events[2]]),
                "previous_removed": lambda c: assign(c, [c.events[1], c.events[2]]),
                "previous_reordered": lambda c: assign(c, [c.events[1], c.events[0], c.events[2]]),
                "new_at_start": lambda c: assign(c, [c.events[2], c.events[0], c.events[1]]),
                "new_in_middle": lambda c: assign(c, [c.events[0], c.events[2], c.events[1]]),
                "previous_duplicated": lambda c: assign(c, [c.events[0], c.events[0], c.events[1], c.events[2]]),
                "two_new": lambda c: assign(c, [*c.events, replace(c.events[-1], sequence=4, event_id="extra")]),
                "no_new": lambda c: assign(c, c.events[:-1]),
                "sequence_repeated": lambda c: c.events.__setitem__(-1, replace(c.events[-1], sequence=2)),
                "sequence_lower": lambda c: c.events.__setitem__(-1, replace(c.events[-1], sequence=1)),
                "sequence_jump": lambda c: c.events.__setitem__(-1, replace(c.events[-1], sequence=4)),
                "event_id_duplicated": lambda c: c.events.__setitem__(-1, replace(c.events[-1], event_id=c.events[0].event_id)),
                "event_id_empty": lambda c: c.events.__setitem__(-1, replace(c.events[-1], event_id="")),
                "occurred_at_invalid": lambda c: c.events.__setitem__(-1, replace(c.events[-1], occurred_at="invalid")),
                "entity_type": lambda c: c.events.__setitem__(-1, replace(c.events[-1], entity_type="block")),
                "entity_id": lambda c: c.events.__setitem__(-1, replace(c.events[-1], entity_id="other")),
                "previous_status": lambda c: c.events.__setitem__(-1, replace(c.events[-1], previous_status="other")),
                "new_status": lambda c: c.events.__setitem__(-1, replace(c.events[-1], new_status="other")),
                "reason_empty": lambda c: c.events.__setitem__(-1, replace(c.events[-1], reason="")),
            }
            for mutation_index, (label, mutation) in enumerate(mutations.items()):
                invalid_previous = self._historical_previous(initial, f"events-{transition_index}-{mutation_index}")
                invalid = execution_transition_candidate(invalid_previous, final, "valid_transition"); mutation(invalid)
                with self.subTest(transition=f"{initial}->{final}", mutation=label):
                    self._assert_logical_rejection(invalid_previous, invalid, f"event-{transition_index}-{mutation_index}")

    def test_global_timestamp_field_policy_is_transition_specific(self) -> None:
        transitions = (("ready", "blocked"), ("ready", "running"), ("running", "completed"), ("running", "inconclusive"), ("running", "failed_protocol"))
        for transition_index, (initial, final) in enumerate(transitions):
            mutations = {
                "updated_at": lambda c: setattr(c, "updated_at", "2026-01-01T00:00:00Z"),
                "started_at": lambda c: setattr(c, "started_at", None if c.started_at is not None else "2026-01-01T00:00:00Z"),
                "finished_at": lambda c: setattr(c, "finished_at", None if c.finished_at is not None else "2026-01-01T00:00:00Z"),
            }
            for mutation_index, (label, mutation) in enumerate(mutations.items()):
                previous = self._historical_previous(initial, f"timestamp-{transition_index}-{mutation_index}")
                candidate = execution_transition_candidate(previous, final, "transition"); mutation(candidate)
                with self.subTest(transition=f"{initial}->{final}", field=label):
                    self._assert_logical_rejection(previous, candidate, f"timestamp-{transition_index}-{mutation_index}")

    def test_event_timestamp_is_logically_monotonic_for_wall_clock_matrix(self) -> None:
        cases = (
            ("equal", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00.000001Z"),
            ("earlier", "2025-12-31T23:59:59Z", "2026-01-01T00:00:00.000001Z"),
            ("later", "2026-01-01T00:00:01Z", "2026-01-01T00:00:01Z"),
        )
        transitions = (
            ("ready", "blocked", None),
            ("ready", "running", "started_at"),
            ("running", "completed", "finished_at"),
            ("running", "inconclusive", "finished_at"),
            ("running", "failed_protocol", "finished_at"),
        )
        for transition_index, (initial, final, side_timestamp) in enumerate(transitions):
            for label, sampled, expected in cases:
                previous = self._historical_previous(initial, f"logical-clock-{transition_index}-{label}")
                previous.updated_at = "2026-01-01T00:00:00Z"
                path = Path(self.temp.name) / f"logical-clock-{transition_index}-{label}.json"
                store = ComparisonResultStore(path)
                store.create(previous)
                with self.subTest(transition=f"{initial}->{final}", case=label), patch(
                    "dpslab.comparison_models.utc_now", return_value=sampled
                ) as clock:
                    candidate = execution_transition_candidate(previous, final, label)
                self.assertEqual(clock.call_count, 1)
                self.assertEqual(candidate.updated_at, expected)
                self.assertEqual(candidate.events[-1].occurred_at, expected)
                if side_timestamp is not None:
                    self.assertEqual(getattr(candidate, side_timestamp), expected)
                self.assertGreater(
                    datetime.fromisoformat(candidate.updated_at.replace("Z", "+00:00")),
                    datetime.fromisoformat(previous.updated_at.replace("Z", "+00:00")),
                )
                self.assertEqual(store.commit_execution(previous, candidate), candidate)

    def test_logical_timestamp_rejects_invalid_history_without_partial_mutation(self) -> None:
        invalid_values = (
            None,
            "",
            "not-a-timestamp",
            "2026-01-01T00:00:00",
            "9999-12-31T23:59:59.999999Z",
        )
        for index, invalid in enumerate(invalid_values):
            previous = self._historical_previous("ready", f"invalid-clock-{index}")
            previous.updated_at = invalid
            snapshot = deepcopy(previous)
            with self.subTest(value=invalid), patch(
                "dpslab.comparison_models.utc_now", return_value="2026-01-01T00:00:00Z"
            ), self.assertRaises(ComparisonResultError):
                previous.transition_execution("blocked", "invalid_clock")
            self.assertEqual(previous, snapshot)

    def test_logical_timestamp_accepts_offset_history_and_normalizes_to_utc(self) -> None:
        previous = self._historical_previous("ready", "offset-clock")
        previous.updated_at = "2026-01-01T01:00:00+01:00"
        with patch(
            "dpslab.comparison_models.utc_now", return_value="2026-01-01T00:00:00Z"
        ) as clock:
            candidate = execution_transition_candidate(previous, "blocked", "offset_clock")
        self.assertEqual(clock.call_count, 1)
        self.assertEqual(candidate.updated_at, "2026-01-01T00:00:00.000001Z")
        self.assertEqual(candidate.events[-1].occurred_at, candidate.updated_at)

    def test_durable_boundary_rejects_nonmonotonic_or_divergent_timestamps(self) -> None:
        mutations = {
            "event_and_updated_before_previous": lambda c: (
                setattr(c, "updated_at", "2025-12-31T23:59:59Z"),
                c.events.__setitem__(-1, replace(c.events[-1], occurred_at="2025-12-31T23:59:59Z")),
            ),
            "equivalent_but_not_exact_event": lambda c: c.events.__setitem__(
                -1, replace(c.events[-1], occurred_at="2026-01-01T01:00:01+01:00")
            ),
        }
        for index, (label, mutation) in enumerate(mutations.items()):
            previous = self._historical_previous("ready", f"durable-clock-{index}")
            previous.updated_at = "2026-01-01T00:00:00Z"
            with patch("dpslab.comparison_models.utc_now", return_value="2026-01-01T00:00:01Z"):
                candidate = execution_transition_candidate(previous, "blocked", label)
            mutation(candidate)
            with self.subTest(case=label):
                self._assert_logical_rejection(previous, candidate, f"durable-clock-{index}")

        side_cases = (
            ("ready", "running", "started_at"),
            ("running", "completed", "finished_at"),
            ("running", "inconclusive", "finished_at"),
            ("running", "failed_protocol", "finished_at"),
        )
        for index, (initial, final, field_name) in enumerate(side_cases):
            previous = self._historical_previous(initial, f"durable-side-{index}")
            previous.updated_at = "2026-01-01T00:00:00Z"
            with patch("dpslab.comparison_models.utc_now", return_value="2026-01-01T00:00:01Z"):
                candidate = execution_transition_candidate(previous, final, field_name)
            setattr(candidate, field_name, "2026-01-01T00:00:02Z")
            with self.subTest(transition=f"{initial}->{final}", field=field_name):
                self._assert_logical_rejection(previous, candidate, f"durable-side-{index}")

    def test_offset_normalization_overflow_is_typed_and_nonmutating(self) -> None:
        previous = self._historical_previous("ready", "offset-overflow")
        previous.updated_at = "9999-12-31T23:59:59.999999-23:59"
        snapshot = deepcopy(previous)
        with patch(
            "dpslab.comparison_models.utc_now", return_value="2026-01-01T00:00:00Z"
        ), self.assertRaises(ComparisonResultError):
            previous.transition_execution("blocked", "offset_overflow")
        self.assertEqual(previous, snapshot)

    def test_all_error_warning_collections_are_strict_prefix_append_only(self) -> None:
        collections = {
            "blocking_errors": (StructuredError("a", "first", "x"), StructuredError("b", "second", "y"), StructuredError("c", "third", "z")),
            "protocol_failures": (StructuredError("a", "first", "x"), StructuredError("b", "second", "y"), StructuredError("c", "third", "z")),
            "analysis_warnings": (StructuredWarning("a", "first", "analysis_warning"), StructuredWarning("b", "second", "analysis_warning"), StructuredWarning("c", "third", "analysis_warning")),
            "advisory_warnings": (StructuredWarning("a", "first", "advisory_warning"), StructuredWarning("b", "second", "advisory_warning"), StructuredWarning("c", "third", "advisory_warning")),
        }
        for collection_index, (name, (first, second, added)) in enumerate(collections.items()):
            for allowed_index, extension in enumerate(([], [added], [first])):
                path = Path(self.temp.name) / f"append-valid-{collection_index}-{allowed_index}.json"
                previous = _new_result(SPEC, f"append-valid-{collection_index}-{allowed_index}"); setattr(previous, name, [first, second])
                store = ComparisonResultStore(path); store.create(previous)
                candidate = execution_transition_candidate(previous, "running", "start"); setattr(candidate, name, [first, second, *extension])
                self.assertEqual(store.commit_execution(previous, candidate), candidate)
            changed_first = replace(first, message="modified")
            invalid_values = {
                "delete_first": [second], "delete_last": [first], "modify_previous": [changed_first, second],
                "reorder": [second, first], "replace_all": [added], "insert_start": [added, first, second],
                "insert_middle": [first, added, second], "duplicate_in_prefix": [first, first, second],
                "substitute": [first, added], "internal_field": [changed_first, second],
            }
            for mutation_index, (label, value) in enumerate(invalid_values.items()):
                previous = _new_result(SPEC, f"append-{collection_index}-{mutation_index}"); setattr(previous, name, [first, second])
                candidate = execution_transition_candidate(previous, "running", "start"); setattr(candidate, name, value)
                with self.subTest(collection=name, mutation=label):
                    self._assert_logical_rejection(previous, candidate, f"append-{collection_index}-{mutation_index}")

    def test_event_and_collection_invariants_are_committed_together(self) -> None:
        error_one, error_two = StructuredError("a", "first", "x"), StructuredError("b", "second", "y")
        warning_one, warning_two = StructuredWarning("a", "first", "analysis_warning"), StructuredWarning("b", "second", "analysis_warning")
        mutations = {
            "correct_event_deleted_error": lambda c: setattr(c, "blocking_errors", []),
            "correct_event_changed_warning": lambda c: setattr(c, "analysis_warnings", [replace(warning_one, message="changed")]),
            "collections_valid_bad_event": lambda c: c.events.__setitem__(-1, replace(c.events[-1], entity_id="other")),
            "new_error_without_event": lambda c: setattr(c, "events", c.events[:-1]),
            "new_warning_without_event": lambda c: setattr(c, "events", c.events[:-1]),
        }
        for index, (label, mutation) in enumerate(mutations.items()):
            previous = _new_result(SPEC, f"combined-{index}"); previous.blocking_errors = [error_one]; previous.analysis_warnings = [warning_one]
            candidate = execution_transition_candidate(previous, "running", "start")
            if label == "new_error_without_event": candidate.blocking_errors.append(error_two)
            if label == "new_warning_without_event": candidate.analysis_warnings.append(warning_two)
            mutation(candidate)
            with self.subTest(case=label): self._assert_logical_rejection(previous, candidate, f"combined-{index}")
        for index, (name, entry) in enumerate((("blocking_errors", error_two), ("analysis_warnings", warning_two))):
            path = Path(self.temp.name) / f"combined-valid-{index}.json"; previous = _new_result(SPEC, f"combined-valid-{index}")
            store = ComparisonResultStore(path); store.create(previous); candidate = execution_transition_candidate(previous, "running", "start")
            setattr(candidate, name, [entry]); self.assertEqual(store.commit_execution(previous, candidate), candidate)

    def test_generic_commit_remains_general_and_does_not_require_one_global_event(self) -> None:
        path = Path(self.temp.name) / "generic-commit.json"; previous = _new_result(SPEC, "generic")
        store = ComparisonResultStore(path); store.create(previous); candidate = deepcopy(previous)
        candidate.add_event("block", "one", "planned", "running", "first")
        candidate.add_event("attempt", "two", "planned", "running", "second")
        self.assertEqual(store.commit(previous, candidate), candidate)
        with self.assertRaises(ComparisonResultError): store.commit_execution(previous, candidate)

    def test_atomic_store_and_append_only_events(self) -> None:
        store = ComparisonResultStore(self.path); store.write(self.result)
        self.result.transition_execution("running", "started"); store.write(self.result)
        self.assertEqual([event["sequence"] for event in json.loads(self.path.read_text())["events"]], list(range(1, len(self.result.events) + 1)))

    def test_previous_event_cannot_be_modified(self) -> None:
        store = ComparisonResultStore(self.path); store.write(self.result); self.result.events = []
        with self.assertRaisesRegex(ComparisonResultError, "eventos anteriores"):
            store.write(self.result)

    def test_closed_recursive_matrix(self) -> None:
        original = result_to_document(self.result)
        cases = []
        unknown = deepcopy(original); unknown["unknown"] = True; cases.append(("unknown", unknown))
        missing = deepcopy(original); del missing["software"]; cases.append(("missing", missing))
        wrong = deepcopy(original); wrong["protocol"]["blocks"] = "8"; cases.append(("type", wrong))
        boolean = deepcopy(original); boolean["protocol"]["blocks"] = True; cases.append(("bool-int", boolean))
        enum = deepcopy(original); enum["blocks"][0]["planned_order"] = "XX"; cases.append(("enum", enum))
        null = deepcopy(original); null["comparison_id"] = None; cases.append(("null", null))
        nonfinite = deepcopy(original); nonfinite["protocol"]["timeout_seconds"] = math.inf; cases.append(("nonfinite", nonfinite))
        for label, document in cases:
            with self.subTest(label=label), self.assertRaises(ComparisonResultError): result_from_document(document)

    def test_round_trip_is_fully_typed_and_events_are_append_only(self) -> None:
        store = ComparisonResultStore(self.path); store.write(self.result); loaded = store.read()
        self.assertEqual(result_to_document(loaded), result_to_document(self.result))
        self.assertTrue(all(not isinstance(block, dict) for block in loaded.blocks))
        prefix = tuple(loaded.events); loaded.transition_execution("running", "started"); store.write(loaded)
        reread = store.read(); self.assertEqual(tuple(reread.events[:len(prefix)]), prefix)

    def test_recovery_is_typed_and_idempotent(self) -> None:
        self._set_running(); ComparisonResultStore(self.path).write(self.result)
        first = recover_from_json(self.path, expected_spec_sha256=SPEC.source_sha256, expected_execution_id="execution", orphan_check=lambda: "confirmed_clear")
        count = len(first.events)
        second = recover_from_json(self.path, expected_spec_sha256=SPEC.source_sha256, expected_execution_id="execution", orphan_check=lambda: "confirmed_clear")
        third = recover_from_json(self.path, expected_spec_sha256=SPEC.source_sha256, expected_execution_id="execution", orphan_check=lambda: "confirmed_clear")
        self.assertEqual(len(second.events), count); self.assertEqual(second, third)
        self.assertEqual(second.blocks[0].status, "retry_pending")
        self.assertNotIsInstance(second.blocks[0].attempts[0].members[0], dict)

    def test_orphan_matrix(self) -> None:
        for state in ("active_process_found", "unknown"):
            result = _new_result(SPEC, state)
            self.assertEqual(recover_interrupted(result, lambda state=state: state), "blocked")
            self.assertEqual(result.status, "blocked")

    def test_manual_identity_and_event_tampering_are_rejected(self) -> None:
        store = ComparisonResultStore(self.path); store.write(self.result); original = self.path.read_bytes()
        for label, mutate in (
            ("spec", lambda d: d.__setitem__("spec_sha256", "0" * 64)),
            ("execution", lambda d: d.__setitem__("comparison_execution_id", "other")),
            ("event", lambda d: d["events"][0].__setitem__("sequence", 9)),
        ):
            document = json.loads(self.path.read_text()); mutate(document); self.path.write_text(json.dumps(document))
            with self.subTest(label=label), self.assertRaises(ComparisonResultError):
                recover_from_json(self.path, expected_spec_sha256=SPEC.source_sha256, expected_execution_id="execution", orphan_check=lambda: "confirmed_clear")
            self.path.write_bytes(original)

    def test_terminal_transition_is_rejected(self) -> None:
        self._set_running(); member = self.result.blocks[0].attempts[0].members[0]
        transition(member, "member", member.member_id, "interrupted", "stop", self.result)
        with self.assertRaises(ComparisonResultError): transition(member, "member", member.member_id, "running", "bad", self.result)

    def test_transactional_create_is_exclusive(self) -> None:
        store = ComparisonResultStore(self.path)
        confirmed = store.create(self.result)
        before = self.path.read_bytes()
        with self.assertRaises(ComparisonResultError): store.create(self.result)
        self.assertIs(confirmed, self.result); self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.glob(".comparison_result.*.tmp")), [])

    def test_file_operations_create_order_and_exclusive_publication(self) -> None:
        operations = RecordingFileOperations()
        store = ComparisonResultStore(self.path, file_operations=operations)
        store.create(self.result)
        self.assertEqual(
            operations.calls,
            ["exists", "make_directory", "temporary_file", "serialize", "flush", "sync", "close", "link", "unlink"],
        )
        self.assertEqual(store.read(), self.result)
        self.assertEqual(list(self.path.parent.glob(".comparison_result.*.tmp")), [])

    def test_normal_file_operations_cover_physical_primitives(self) -> None:
        operations = _ComparisonFileOperations()
        directory = Path(self.temp.name) / "physical"
        operations.make_directory(directory); self.assertTrue(directory.is_dir())
        stream = operations.temporary_file(directory); temporary = Path(stream.name)
        self.assertEqual(temporary.parent, directory); self.assertNotEqual(temporary, self.path)
        operations.serialize({"value": "complete"}, stream)
        operations.flush(stream); operations.sync(stream); operations.close(stream)
        self.assertEqual(json.loads(temporary.read_text()), {"value": "complete"})
        linked = directory / "linked.json"; operations.link(str(temporary), linked)
        self.assertEqual(linked.read_bytes(), temporary.read_bytes())
        with self.assertRaises(FileExistsError): operations.link(str(temporary), linked)
        operations.unlink(temporary); self.assertFalse(temporary.exists())
        replacement = operations.temporary_file(directory); replacement_path = Path(replacement.name)
        operations.serialize({"value": "replacement"}, replacement)
        operations.flush(replacement); operations.sync(replacement); operations.close(replacement)
        operations.replace(str(replacement_path), linked)
        self.assertEqual(json.loads(linked.read_text()), {"value": "replacement"})
        self.assertFalse(replacement_path.exists())

    def test_file_operations_create_failure_matrix_leaves_no_publication_or_temp(self) -> None:
        for failure in ("exists", "make_directory", "temporary_file", "serialize", "partial_write", "flush", "sync", "close", "link"):
            path = Path(self.temp.name) / f"create-{failure}.json"
            operations = RecordingFileOperations(failure)
            with self.subTest(failure=failure), self.assertRaises(OSError):
                ComparisonResultStore(path, file_operations=operations).create(_new_result(SPEC, failure))
            self.assertFalse(path.exists())
            self.assertEqual(list(path.parent.glob(".comparison_result.*.tmp")), [])

    def test_file_operations_commit_failure_matrix_preserves_confirmed_bytes(self) -> None:
        from dpslab.comparison_models import execution_transition_candidate
        for failure in ("exists", "read_text", "make_directory", "temporary_file", "serialize", "partial_write", "flush", "sync", "close", "replace"):
            path = Path(self.temp.name) / f"commit-{failure}.json"
            initial = _new_result(SPEC, failure)
            ComparisonResultStore(path).create(initial); before = path.read_bytes()
            operations = RecordingFileOperations(failure)
            store = ComparisonResultStore(path, file_operations=operations)
            candidate = execution_transition_candidate(initial, "running", "start")
            with self.subTest(failure=failure), self.assertRaises((OSError, ComparisonResultError)):
                store.commit_execution(initial, candidate)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(ComparisonResultStore(path).read(), initial)
            self.assertEqual(list(path.parent.glob(".comparison_result.*.tmp")), [])

    def test_injected_replace_and_cleanup_failure_preserves_error_context(self) -> None:
        from dpslab.comparison_models import execution_transition_candidate
        previous = ComparisonResultStore(self.path).create(self.result); before = self.path.read_bytes()
        candidate = execution_transition_candidate(previous, "running", "start")
        operations = RecordingFileOperations("replace", cleanup_failure=True)
        with self.assertRaisesRegex(OSError, "injected cleanup") as caught:
            ComparisonResultStore(self.path, file_operations=operations).commit_execution(previous, candidate)
        self.assertIsNotNone(caught.exception.__context__)
        self.assertIn("injected replace", str(caught.exception.__context__))
        self.assertEqual(self.path.read_bytes(), before); self.assertEqual(previous.status, "ready")
        for temporary in self.path.parent.glob(".comparison_result.*.tmp"): temporary.unlink()

    def test_global_commit_failure_preserves_previous_and_file(self) -> None:
        from dpslab.comparison_models import execution_transition_candidate
        store = ComparisonResultStore(self.path); previous = store.create(self.result)
        snapshot = deepcopy(previous); before = self.path.read_bytes()
        candidate = execution_transition_candidate(previous, "running", "start")
        with patch("dpslab.comparison_result_io.os.replace", side_effect=OSError("injected")):
            with self.assertRaises(OSError): store.commit(previous, candidate)
        self.assertEqual(previous, snapshot); self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.glob(".comparison_result.*.tmp")), [])

    def _confirmed_for(self, initial: str, path: Path):
        from dpslab.comparison_models import execution_transition_candidate
        store = ComparisonResultStore(path); result = _new_result(SPEC, path.stem); result = store.create(result)
        if initial == "running": result = store.commit(result, execution_transition_candidate(result, "running", "prepare"))
        return store, result

    def test_global_transition_success_matrix(self) -> None:
        from dpslab.comparison_models import execution_transition_candidate
        for initial, final in (("ready", "blocked"), ("ready", "running"), ("running", "completed"), ("running", "inconclusive"), ("running", "failed_protocol")):
            with self.subTest(initial=initial, final=final):
                path = Path(self.temp.name) / f"{initial}-{final}.json"; store, previous = self._confirmed_for(initial, path)
                snapshot = deepcopy(previous); candidate = execution_transition_candidate(previous, final, f"to_{final}"); confirmed = store.commit_execution(previous, candidate)
                self.assertEqual(previous, snapshot); self.assertIsNot(previous, candidate); self.assertEqual(confirmed, candidate)
                self.assertEqual(confirmed.status, final); self.assertEqual(len(confirmed.events), len(previous.events) + 1)
                event = confirmed.events[-1]; self.assertEqual((event.sequence, event.previous_status, event.new_status, event.entity_type, event.entity_id), (len(confirmed.events), initial, final, "comparison_execution", previous.comparison_execution_id))
                self.assertEqual(tuple(confirmed.events[:-1]), tuple(previous.events)); self.assertEqual(store.read(), confirmed)
                self.assertEqual(list(path.parent.glob(".comparison_result.*.tmp")), [])

    def test_global_transition_rollback_matrix(self) -> None:
        from dpslab.comparison_models import execution_transition_candidate
        for initial, final in (("ready", "blocked"), ("ready", "running"), ("running", "completed"), ("running", "inconclusive"), ("running", "failed_protocol")):
            with self.subTest(initial=initial, final=final):
                path = Path(self.temp.name) / f"rollback-{initial}-{final}.json"; store, previous = self._confirmed_for(initial, path)
                snapshot, before = deepcopy(previous), path.read_bytes(); candidate = execution_transition_candidate(previous, final, "rollback")
                with patch("dpslab.comparison_result_io.os.replace", side_effect=OSError("injected")):
                    with self.assertRaises(OSError): store.commit_execution(previous, candidate)
                self.assertEqual(previous, snapshot); self.assertEqual(path.read_bytes(), before); self.assertEqual(store.read(), previous)
                self.assertEqual(list(path.parent.glob(".comparison_result.*.tmp")), [])

    def test_forbidden_global_transition_matrix(self) -> None:
        from dpslab.comparison_models import execution_transition_candidate
        cases = (("ready", "completed"), ("ready", "inconclusive"), ("ready", "failed_protocol"), ("running", "ready"), ("completed", "running"), ("inconclusive", "running"), ("failed_protocol", "ready"), ("blocked", "running"))
        for initial, final in cases:
            result = _new_result(SPEC, f"{initial}-{final}")
            if initial == "running": result = execution_transition_candidate(result, "running", "setup")
            elif initial in {"completed", "inconclusive", "failed_protocol"}: result = execution_transition_candidate(execution_transition_candidate(result, "running", "setup"), initial, "setup_terminal")
            elif initial == "blocked": result = execution_transition_candidate(result, "blocked", "setup")
            snapshot = deepcopy(result)
            with self.subTest(initial=initial, final=final), self.assertRaises(ComparisonResultError): execution_transition_candidate(result, final, "forbidden")
            self.assertEqual(result, snapshot)

    def test_commit_execution_rejects_event_matrix_before_replace(self) -> None:
        from dataclasses import replace
        from dpslab.comparison_models import execution_transition_candidate
        mutations = {
            "missing": lambda c: setattr(c, "events", c.events[:-1]),
            "double": lambda c: setattr(c, "events", [*c.events, replace(c.events[-1], sequence=c.events[-1].sequence + 1, event_id="extra")]),
            "sequence": lambda c: c.events.__setitem__(-1, replace(c.events[-1], sequence=99)),
            "empty_id": lambda c: c.events.__setitem__(-1, replace(c.events[-1], event_id="")),
            "previous_status": lambda c: c.events.__setitem__(-1, replace(c.events[-1], previous_status="blocked")),
            "new_status": lambda c: c.events.__setitem__(-1, replace(c.events[-1], new_status="completed")),
            "entity_type": lambda c: c.events.__setitem__(-1, replace(c.events[-1], entity_type="block")),
            "entity_id": lambda c: c.events.__setitem__(-1, replace(c.events[-1], entity_id="other")),
            "timestamp": lambda c: c.events.__setitem__(-1, replace(c.events[-1], occurred_at="bad")),
            "reason": lambda c: c.events.__setitem__(-1, replace(c.events[-1], reason="")),
        }
        for label, mutation in mutations.items():
            path = Path(self.temp.name) / f"event-{label}.json"; store, previous = self._confirmed_for("ready", path); before = path.read_bytes()
            candidate = execution_transition_candidate(previous, "running", "start"); mutation(candidate)
            with self.subTest(label=label), patch("dpslab.comparison_result_io.os.replace") as replacing, self.assertRaises(ComparisonResultError): store.commit_execution(previous, candidate)
            replacing.assert_not_called(); self.assertEqual(path.read_bytes(), before); self.assertEqual(store.read(), previous)

    def test_cleanup_failure_preserves_original_as_context_and_confirmed_bytes(self) -> None:
        from dpslab.comparison_models import execution_transition_candidate
        path = Path(self.temp.name) / "cleanup.json"; store, previous = self._confirmed_for("ready", path); before = path.read_bytes()
        candidate = execution_transition_candidate(previous, "running", "start")
        with patch("dpslab.comparison_result_io.os.replace", side_effect=OSError("replace failed")), patch("dpslab.comparison_result_io.Path.unlink", side_effect=OSError("cleanup failed")):
            with self.assertRaisesRegex(OSError, "cleanup failed") as caught: store.commit_execution(previous, candidate)
        self.assertIsNotNone(caught.exception.__context__); self.assertIn("replace failed", str(caught.exception.__context__))
        self.assertEqual(path.read_bytes(), before); self.assertEqual(previous.status, "ready")

    def test_error_warning_collections_are_append_only(self) -> None:
        from dpslab.comparison_models import StructuredWarning, execution_transition_candidate
        collections = {
            "blocking_errors": [StructuredError("a", "a", "x"), StructuredError("b", "b", "x")],
            "protocol_failures": [StructuredError("a", "a", "x"), StructuredError("b", "b", "x")],
            "analysis_warnings": [StructuredWarning("a", "a", "analysis_warning"), StructuredWarning("b", "b", "analysis_warning")],
            "advisory_warnings": [StructuredWarning("a", "a", "advisory_warning"), StructuredWarning("b", "b", "advisory_warning")],
        }
        for name, entries in collections.items():
            path = Path(self.temp.name) / f"append-{name}.json"; previous = _new_result(SPEC, name); setattr(previous, name, entries); store = ComparisonResultStore(path); previous = store.create(previous); before = path.read_bytes()
            for label, changed in (("delete_first", entries[1:]), ("delete_last", entries[:-1]), ("reverse", list(reversed(entries))), ("insert_first", [entries[0], *entries])):
                candidate = execution_transition_candidate(previous, "running", "start"); setattr(candidate, name, changed)
                with self.subTest(collection=name, mutation=label), patch("dpslab.comparison_result_io.os.replace") as replacing, self.assertRaises(ComparisonResultError): store.commit_execution(previous, candidate)
                replacing.assert_not_called(); self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__": unittest.main()
