from __future__ import annotations

import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from dpslab.comparator import MemberPreparation, orchestrate, validate_analysis_preconditions
from dpslab.comparison_adapter import ComparisonMemberExecutionResponse
from dpslab.comparison_models import EffectiveParameters, InvocationRecord, MemberDps, MemberIntegrity, RunArtifactReference, SimulationCraftIdentity, StructuredError, utc_now
from dpslab.comparison_spec import load_comparison_spec
from dpslab.comparison_stats import ComparisonAnalysisError
from dpslab.runner import reserve_run


ROOT = Path(__file__).resolve().parents[2]
SPEC = load_comparison_spec(ROOT / "comparisons/flasil_neck_50228_vs_249368_v1.toml", root=ROOT)


class FakeTime:
    def __init__(self) -> None:
        self.value = 0.0
        self.sleeps: list[float] = []

    def clock(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.value += seconds


class BrokenTime(FakeTime):
    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)


class DistinguishableStore:
    instances = []
    fail_status = None
    timeline = []

    def __init__(self, path):
        self.path = path; self.calls = []; self.commits = []; self.writes = []
        self.confirmed_by_status = {}; self.generic_commit_calls = 0
        type(self).instances.append(self)

    def create(self, candidate):
        confirmed = deepcopy(candidate); self.calls.append(("create", candidate, confirmed)); type(self).timeline.append("create"); return confirmed

    def write(self, candidate):
        self.calls.append(("write", candidate)); self.writes.append(candidate); type(self).timeline.append("write"); return candidate

    def commit(self, previous, candidate):
        self.generic_commit_calls += 1
        raise AssertionError("generic commit fallback")

    def commit_execution(self, previous, candidate):
        previous_snapshot = deepcopy(previous); candidate_snapshot = deepcopy(candidate)
        self.calls.append(("commit_execution", candidate.status, previous, candidate))
        type(self).timeline.append(f"commit:{candidate.status}")
        self.commits.append((candidate.status, previous, candidate, previous_snapshot, candidate_snapshot))
        if candidate.status == type(self).fail_status: raise RuntimeError(f"commit failed:{candidate.status}")
        confirmed = deepcopy(candidate); self.confirmed_by_status[candidate.status] = confirmed
        type(self).timeline.append(f"confirmed:{candidate.status}")
        self.calls.append(("confirmed", candidate.status, confirmed)); return confirmed


class ComparatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "comparison_result.json"
        self.time = FakeTime()

    def _reserve(self, plan):
        return reserve_run(Path(self.temp.name) / "runs", comparison_execution_id=plan.comparison_execution_id, member_id=plan.member_id)

    def _prepare(self, plan, reservation):
        invocation = InvocationRecord("built", ("<SIMC_EXE>", "effective_profile.simc", "threads=2", "iterations=5000", f"seed={plan.seed}"), "a" * 64, "b" * 64, "c" * 64, "test", True, False, utc_now())
        return MemberPreparation("d" * 64, invocation)

    def _response(self, plan, reservation, dps=100000.0, *, valid=True, run_id=None):
        references = tuple(RunArtifactReference(kind, name, "f" * 64, True, True if kind in {"metadata", "simc_json", "summary"} else None) for kind, name in (
            ("metadata", "metadata.json"), ("simc_json", "simc.json"), ("stdout", "stdout.txt"),
            ("stderr", "stderr.txt"), ("summary", "run_summary.json"), ("effective_profile", "effective_profile.simc")))
        integrity = MemberIntegrity(*(valid for _ in range(9)))
        invocation = InvocationRecord("completed" if valid else "failed_after_start", ("<SIMC_EXE>",), "a" * 64, "b" * 64, "c" * 64, "test", True, False)
        errors = () if valid else (StructuredError("simulated_failure", "simulated failure", "test"),)
        return ComparisonMemberExecutionResponse(run_id or reservation.run_id, "completed" if valid else "invalid", True, invocation, references[0], references[4], references, EffectiveParameters(plan.seed, 5000, 2, None, 900), SimulationCraftIdentity("1205-01", "a81c39d", "c" * 64), 0, MemberDps(dps) if dps is not None else None, integrity, errors, ())

    def _orchestrate(self, run, *, time=None, prepare=None, analyzer=None):
        selected = time or self.time
        kwargs = {"reserve_member": self._reserve, "prepare_member": prepare or self._prepare, "clock": selected.clock, "sleeper": selected.sleep}
        if analyzer is not None:
            kwargs["analyzer"] = analyzer
        return orchestrate(SPEC, "execution", self.output, run, **kwargs)

    def _fixed_stats(self, final_classification):
        classification = "inconclusive" if final_classification == "inconclusive" else "winner_b"
        analysis = SimpleNamespace(method="welch_delta", estimate_percent=1.0, standard_error=0.1, degrees_of_freedom=7.0, t_critical=2.0, ci_low=0.8, ci_high=1.2, classification=classification)
        paired = SimpleNamespace(method="paired_t", estimate_percent=1.0, standard_error=0.1, degrees_of_freedom=7.0, t_critical=2.0, ci_low=0.8, ci_high=1.2, classification=classification)
        return SimpleNamespace(primary=analysis, paired_sensitivity=paired, estimate_difference_percent_points=0.0, classification_disagreement=False, final_classification=final_classification)

    def _run_with_distinguishable_store(self, terminal, *, fail_status=None):
        DistinguishableStore.instances = []; DistinguishableStore.fail_status = fail_status; DistinguishableStore.timeline = []
        effects = []
        def reserve(plan): effects.append(("reserve", plan.block_index)); DistinguishableStore.timeline.append("reserve"); return self._reserve(plan)
        def prepare(plan, reservation): effects.append(("prepare", plan.block_index)); DistinguishableStore.timeline.append("prepare"); return self._prepare(plan, reservation)
        def run(plan, reservation):
            effects.append(("run_member", plan.block_index)); DistinguishableStore.timeline.append("run_member"); reservation.consume(comparison_execution_id=plan.comparison_execution_id, member_id=plan.member_id)
            return self._response(plan, reservation, 100000 + plan.block_index + (1000 if plan.arm == "b" else 0))
        def analyzer(*args, **kwargs): effects.append(("analyze", None)); DistinguishableStore.timeline.append("analyze"); return self._fixed_stats(terminal)
        if terminal == "failed_protocol":
            def prepare(plan, reservation): effects.append(("prepare", plan.block_index)); DistinguishableStore.timeline.append("prepare"); raise RuntimeError("preparation")
        with patch("dpslab.comparator.ComparisonResultStore", DistinguishableStore):
            result = orchestrate(SPEC, "execution", self.output, run, reserve_member=reserve, prepare_member=prepare, analyzer=analyzer, clock=self.time.clock, sleeper=self.time.sleep)
        return result, DistinguishableStore.instances[-1], effects

    def test_comparator_adopts_distinguishable_confirmed_objects_for_real_global_routes(self) -> None:
        for terminal in ("completed", "inconclusive", "failed_protocol"):
            self.time = FakeTime()
            with self.subTest(terminal=terminal):
                result, store, effects = self._run_with_distinguishable_store(terminal)
                statuses = [entry[0] for entry in store.commits]
                self.assertEqual(statuses[0], "running"); self.assertEqual(statuses[-1], terminal)
                running_previous, running_candidate = store.commits[0][1:3]
                running_confirmed = store.confirmed_by_status["running"]
                self.assertIsNot(running_previous, running_candidate); self.assertIsNot(running_candidate, running_confirmed)
                self.assertTrue(any(written is running_confirmed for written in store.writes))
                self.assertIs(result, store.confirmed_by_status[terminal])
                self.assertIsNot(result, store.commits[-1][2]); self.assertEqual(result, store.commits[-1][2])
                for _, previous, candidate, snapshot, _ in store.commits:
                    self.assertEqual(previous, snapshot); self.assertIsNot(previous, candidate)
                self.assertEqual(store.generic_commit_calls, 0)
                self.assertTrue(effects)
                timeline = DistinguishableStore.timeline
                self.assertLess(timeline.index("commit:running"), timeline.index("confirmed:running")); self.assertLess(timeline.index("confirmed:running"), timeline.index("reserve"))
                self.assertEqual(timeline[-2:], [f"commit:{terminal}", f"confirmed:{terminal}"])

    def test_comparator_stops_on_commit_failure_without_adopting_candidate_or_fallback(self) -> None:
        for failed_status in ("running", "completed", "inconclusive", "failed_protocol"):
            self.time = FakeTime(); DistinguishableStore.instances = []; DistinguishableStore.fail_status = failed_status; DistinguishableStore.timeline = []
            effects = []
            def reserve(plan): effects.append("reserve"); return self._reserve(plan)
            def prepare(plan, reservation):
                effects.append("prepare")
                if failed_status == "failed_protocol": raise RuntimeError("preparation")
                return self._prepare(plan, reservation)
            def run(plan, reservation):
                effects.append("run_member"); reservation.consume(comparison_execution_id=plan.comparison_execution_id, member_id=plan.member_id)
                return self._response(plan, reservation, 100000 + plan.block_index + (1000 if plan.arm == "b" else 0))
            def analyzer(*args, **kwargs): effects.append("analyze"); return self._fixed_stats("inconclusive" if failed_status == "inconclusive" else "winner_b")
            with self.subTest(status=failed_status), patch("dpslab.comparator.ComparisonResultStore", DistinguishableStore), self.assertRaisesRegex(RuntimeError, f"commit failed:{failed_status}"):
                orchestrate(SPEC, "execution", self.output, run, reserve_member=reserve, prepare_member=prepare, analyzer=analyzer, clock=self.time.clock, sleeper=self.time.sleep)
            store = DistinguishableStore.instances[-1]; failed = store.commits[-1]
            self.assertEqual(failed[0], failed_status); self.assertEqual(failed[1], failed[3]); self.assertIsNot(failed[1], failed[2])
            self.assertNotIn(failed_status, store.confirmed_by_status); self.assertEqual(store.generic_commit_calls, 0)
            self.assertEqual(sum(1 for call in store.commits if call[0] == failed_status), 1)
            call_index = next(index for index, call in enumerate(store.calls) if call[0] == "commit_execution" and call[1] == failed_status)
            self.assertEqual(store.calls[call_index + 1:], [])
            self.assertEqual(DistinguishableStore.timeline[-1], f"commit:{failed_status}")
            if failed_status == "running": self.assertEqual(effects, [])

    def test_eight_blocks_alternate_and_complete_with_simulated_runs(self) -> None:
        plans = []

        def run(plan, reservation):
            plans.append(plan)
            reservation.consume(comparison_execution_id=plan.comparison_execution_id, member_id=plan.member_id)
            base = 100000.0 + plan.block_index * 10
            return self._response(plan, reservation, base if plan.arm == "a" else base * 1.02)

        result = self._orchestrate(run)
        self.assertIn(result.status, {"completed", "inconclusive"})
        self.assertEqual(len(plans), 16)
        self.assertEqual([p.planned_order for p in plans[::2]], list(SPEC.protocol.orders))
        self.assertEqual(sum(1 for value in self.time.sleeps if value == 30), 8)
        self.assertEqual(sum(1 for value in self.time.sleeps if value == 60), 7)
        self.assertTrue(self.output.is_file())
        a, b, run_ids = validate_analysis_preconditions(result, SPEC)
        self.assertEqual((len(a), len(b), len(set(run_ids))), (8, 8, 16))
        self.assertEqual([block.seed for block in result.blocks], list(SPEC.protocol.seeds))
        self.assertEqual([block.planned_order for block in result.blocks], list(SPEC.protocol.orders))

    def test_ab_association_and_analysis_precondition_matrix(self) -> None:
        def run(plan, reservation):
            reservation.consume(comparison_execution_id=plan.comparison_execution_id, member_id=plan.member_id)
            return self._response(plan, reservation, 100000 + plan.block_index + (1000 if plan.arm == "b" else 0))
        valid = self._orchestrate(run)
        mutations = {
            "two_a": lambda r: setattr(r.blocks[0].attempts[0].members[1], "arm", "a"),
            "wrong_position": lambda r: setattr(r.blocks[0].attempts[0].members[0], "order_position", 2),
            "wrong_seed": lambda r: setattr(r.blocks[0].attempts[0].members[0], "seed", 9),
            "wrong_block": lambda r: setattr(r.blocks[0].attempts[0].members[0], "block_index", 2),
            "wrong_attempt": lambda r: setattr(r.blocks[0].attempts[0].members[0], "attempt", 2),
            "wrong_item": lambda r: setattr(r.blocks[0].attempts[0].members[0], "candidate_item_id", SPEC.arm_b.item_id),
            "other_execution": lambda r: setattr(r.blocks[0].attempts[0].members[0], "comparison_execution_id", "other"),
            "one_member": lambda r: setattr(r.blocks[0].attempts[0], "members", r.blocks[0].attempts[0].members[:1]),
            "three_members": lambda r: setattr(r.blocks[0].attempts[0], "members", [*r.blocks[0].attempts[0].members, deepcopy(r.blocks[0].attempts[0].members[0])]),
            "duplicate_run": lambda r: setattr(r.blocks[1].attempts[0].members[0], "run_id", r.blocks[0].attempts[0].members[0].run_id),
            "simc_mismatch": lambda r: setattr(r.blocks[1].attempts[0].members[0], "observed_simc", SimulationCraftIdentity("other", "a81c39d", "c" * 64)),
            "artifact_invalid": lambda r: setattr(r.blocks[0].attempts[0].members[0], "artifacts", __import__('dpslab.comparison_models', fromlist=['RunArtifactSet']).RunArtifactSet(())),
        }
        for label, mutation in mutations.items():
            candidate = deepcopy(valid); mutation(candidate)
            with self.subTest(label=label), self.assertRaises(ComparisonAnalysisError):
                validate_analysis_preconditions(candidate, SPEC)

    def test_failed_member_retries_the_full_pair(self) -> None:
        calls: dict[tuple[int, int], int] = {}

        def run(plan, reservation):
            reservation.consume(comparison_execution_id=plan.comparison_execution_id, member_id=plan.member_id)
            calls[(plan.block_index, plan.attempt)] = calls.get((plan.block_index, plan.attempt), 0) + 1
            failed = plan.block_index == 1 and plan.attempt == 1 and plan.arm == "b"
            base = 100000 + plan.block_index * 17
            return self._response(plan, reservation, None if failed else base + (1000 if plan.arm == "b" else 0), valid=not failed)

        result = self._orchestrate(run)
        self.assertIn(result.status, {"completed", "inconclusive"})
        self.assertEqual(calls[(1, 1)], 2)
        self.assertEqual(calls[(1, 2)], 2)
        self.assertEqual(result.blocks[0].selected_attempt, 2)

    def test_two_failed_attempts_exhaust_block_and_skip_analysis(self) -> None:
        def run(plan, reservation):
            reservation.consume(comparison_execution_id=plan.comparison_execution_id, member_id=plan.member_id)
            valid = plan.arm == "a"
            return self._response(plan, reservation, 100000 if valid else None, valid=valid)

        result = self._orchestrate(run)
        self.assertEqual(result.status, "failed_protocol")
        self.assertEqual(result.blocks[0].status, "exhausted")
        self.assertEqual(result.analysis.status, "not_run")

    def test_duplicate_run_id_invalidates_pair(self) -> None:
        def run(plan, reservation):
            reservation.consume(comparison_execution_id=plan.comparison_execution_id, member_id=plan.member_id)
            return self._response(plan, reservation, 100000, run_id="duplicate")

        result = self._orchestrate(run)
        self.assertEqual(result.status, "failed_protocol")

    def test_insufficient_monotonic_pause_fails_protocol(self) -> None:
        broken = BrokenTime()
        def run(plan, reservation):
            reservation.consume(comparison_execution_id=plan.comparison_execution_id, member_id=plan.member_id)
            return self._response(plan, reservation, 100000)
        result = self._orchestrate(run, time=broken)
        self.assertEqual(result.status, "failed_protocol")
        self.assertIn("minimum_pause_not_met", [error.code for error in result.protocol_failures])

    def test_adapter_exception_is_converted_to_invalid_pair(self) -> None:
        def run(plan, reservation):
            raise RuntimeError("simulated")
        result = self._orchestrate(run)
        self.assertEqual(result.status, "failed_protocol")

    def test_planned_run_id_is_durable_before_invocation_and_adapter(self) -> None:
        observed = []
        def prepare(plan, reservation):
            document = __import__("json").loads(self.output.read_text(encoding="utf-8"))
            member = document["blocks"][plan.block_index - 1]["attempts"][-1]["members"][-1]
            observed.append((member["status"], member["reservation"]["planned_run_id"], member["invocation"]["status"]))
            return self._prepare(plan, reservation)
        def run(plan, reservation):
            document = __import__("json").loads(self.output.read_text(encoding="utf-8"))
            member = document["blocks"][plan.block_index - 1]["attempts"][-1]["members"][-1]
            self.assertEqual(member["status"], "running")
            self.assertEqual(member["invocation"]["status"], "built")
            reservation.consume(comparison_execution_id=plan.comparison_execution_id, member_id=plan.member_id)
            return self._response(plan, reservation, 100000 + plan.block_index)
        result = self._orchestrate(run, prepare=prepare)
        self.assertIn(result.status, {"completed", "inconclusive"})
        self.assertTrue(all(status == "planned" and run_id and invocation == "not_built" for status, run_id, invocation in observed))

    def test_preparation_failure_abandons_reservation(self) -> None:
        def prepare(plan, reservation):
            raise RuntimeError("before argv")
        def run(plan, reservation):
            self.fail("adapter must not run")
        result = self._orchestrate(run, prepare=prepare)
        self.assertEqual(result.status, "failed_protocol")
        members = result.blocks[0].attempts[0].members
        self.assertTrue(all(member.reservation.status == "abandoned" for member in members))
        self.assertTrue(all(member.invocation.status == "failed_before_start" for member in members))

    def test_injected_analysis_failure_is_failed_protocol_without_classification(self) -> None:
        def run(plan, reservation):
            reservation.consume(comparison_execution_id=plan.comparison_execution_id, member_id=plan.member_id)
            return self._response(plan, reservation, 100000 + plan.block_index)
        def broken(*args, **kwargs):
            raise RuntimeError("welch failed")
        result = self._orchestrate(run, analyzer=broken)
        self.assertEqual(result.status, "failed_protocol")
        self.assertIsNone(result.analysis.final_classification)

    def test_analysis_is_not_called_before_eight_valid_blocks(self) -> None:
        calls = []
        def run(plan, reservation):
            reservation.consume(comparison_execution_id=plan.comparison_execution_id, member_id=plan.member_id)
            valid = plan.arm == "a"
            return self._response(plan, reservation, 100000 if valid else None, valid=valid)
        def analyzer(*args, **kwargs):
            calls.append(True)
            self.fail("analysis must not run")
        result = self._orchestrate(run, analyzer=analyzer)
        self.assertEqual(result.status, "failed_protocol")
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
