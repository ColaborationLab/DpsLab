from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from unittest.mock import patch

from dpslab.run_identity import (
    RunIdentityError,
    RunIdentityPlan,
    build_current_run_id,
    select_run_identity,
    validate_run_identity_plan,
)


EXECUTION = "execution"
MEMBER = "execution:block-1:attempt-1:a"
ROOT = "results/runs"
RUN_ONE = "20260716T120000.123456Z-abcdef12"
RUN_TWO = "20260716T120000.123457Z-1234abcd"


class RunIdentityTests(unittest.TestCase):
    @staticmethod
    def _select(source, **changes):
        arguments = {
            "comparison_execution_id": EXECUTION,
            "member_id": MEMBER,
            "block_index": 1,
            "attempt": 1,
            "arm": "a",
            "runs_root_portable": ROOT,
            "run_id_source": source,
        }
        arguments.update(changes)
        return select_run_identity(**arguments)

    def test_current_run_id_convention_is_preserved_purely(self) -> None:
        timestamp = datetime(2026, 7, 16, 12, 0, 0, 123456, tzinfo=timezone.utc)
        self.assertEqual(build_current_run_id(timestamp, "ABCDEF123456"), RUN_ONE)
        plan = self._select(lambda: RUN_ONE)
        self.assertEqual(plan.run_id, RUN_ONE)
        self.assertEqual(plan.portable_path, f"{ROOT}/{RUN_ONE}")

    def test_plan_is_frozen_ephemeral_and_not_a_reservation(self) -> None:
        plan = self._select(lambda: RUN_ONE)
        self.assertEqual(
            set(plan.__dataclass_fields__),
            {
                "comparison_execution_id",
                "member_id",
                "block_index",
                "attempt",
                "arm",
                "run_id",
                "portable_path",
            },
        )
        self.assertFalse(hasattr(plan, "status"))
        self.assertFalse(hasattr(plan, "reservation"))
        self.assertFalse(hasattr(plan, "token"))
        with self.assertRaises(FrozenInstanceError):
            plan.run_id = RUN_TWO  # type: ignore[misc]

    def test_same_inputs_and_source_are_idempotent_without_cleanup(self) -> None:
        first = self._select(lambda: RUN_ONE)
        second = self._select(lambda: RUN_ONE)
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertNotIn("reserved", repr(first))
        self.assertNotIn("consumed", repr(first))
        self.assertNotIn("abandoned", repr(first))

    def test_different_source_value_produces_a_different_plan(self) -> None:
        first = self._select(lambda: RUN_ONE)
        second = self._select(lambda: RUN_TWO)
        self.assertNotEqual(first, second)
        self.assertNotEqual(first.portable_path, second.portable_path)

    def test_collision_collections_retry_with_the_existing_limit_policy(self) -> None:
        values = iter((RUN_ONE, RUN_TWO))
        plan = self._select(
            lambda: next(values),
            occupied_run_ids=frozenset({RUN_ONE}),
        )
        self.assertEqual(plan.run_id, RUN_TWO)

        values = iter((RUN_ONE, RUN_TWO))
        plan = self._select(
            lambda: next(values),
            occupied_portable_paths=frozenset({f"{ROOT}/{RUN_ONE}"}),
        )
        self.assertEqual(plan.run_id, RUN_TWO)

        calls = []
        with self.assertRaisesRegex(RunIdentityError, "max_attempts"):
            self._select(
                lambda: calls.append(RUN_ONE) or RUN_ONE,
                occupied_run_ids=frozenset({RUN_ONE}),
                max_attempts=3,
            )
        self.assertEqual(calls, [RUN_ONE, RUN_ONE, RUN_ONE])

    def test_known_plan_is_idempotent_for_same_owner_and_conflicts_for_another(self) -> None:
        known = self._select(lambda: RUN_ONE)
        repeated = self._select(lambda: RUN_ONE, known_plans=(known,))
        self.assertEqual(repeated, known)

        other = replace(
            known,
            comparison_execution_id="other",
            member_id="other:block-1:attempt-1:a",
        )
        with self.assertRaisesRegex(RunIdentityError, "max_attempts"):
            self._select(lambda: RUN_ONE, known_plans=(other,), max_attempts=1)

    def test_logical_ownership_must_match_the_current_member_convention(self) -> None:
        cases = {
            "execution": {"comparison_execution_id": ""},
            "member": {"member_id": ""},
            "arm": {"arm": "c"},
            "block_low": {"block_index": 0},
            "block_high": {"block_index": 9},
            "attempt_low": {"attempt": 0},
            "attempt_high": {"attempt": 3},
            "wrong_member": {"member_id": "execution:block-1:attempt-1:b"},
            "changed_execution": {"comparison_execution_id": "other"},
            "changed_block": {"block_index": 2},
            "changed_attempt": {"attempt": 2},
        }
        for label, changes in cases.items():
            with self.subTest(case=label), self.assertRaises(RunIdentityError):
                self._select(lambda: RUN_ONE, **changes)

    def test_run_id_and_source_validation_use_the_existing_character_rule(self) -> None:
        invalid = ("", "contains space", "a/b", "a\\b", "C:drive", "../escape")
        for value in invalid:
            with self.subTest(run_id=value), self.assertRaises(RunIdentityError):
                self._select(lambda value=value: value)
        with self.assertRaises(RunIdentityError):
            self._select(lambda: RUN_ONE, run_id_source=None)
        with self.assertRaises(RunIdentityError):
            self._select(lambda: RUN_ONE, max_attempts=0)

    def test_portable_root_and_path_validation_matrix(self) -> None:
        invalid_roots = (
            "",
            "/results/runs",
            "C:/results/runs",
            "../results/runs",
            "results/../runs",
            "results\\runs",
            "results//runs",
        )
        for root in invalid_roots:
            with self.subTest(root=root), self.assertRaises(RunIdentityError):
                self._select(lambda: RUN_ONE, runs_root_portable=root)

        valid = self._select(lambda: RUN_ONE)
        invalid_plans = (
            replace(valid, portable_path=f"{ROOT}/{RUN_TWO}"),
            replace(valid, portable_path=f"/{ROOT}/{RUN_ONE}"),
            replace(valid, portable_path=f"C:/{ROOT}/{RUN_ONE}"),
            replace(valid, portable_path=f"{ROOT}/../{RUN_ONE}"),
            replace(valid, run_id="bad/id"),
        )
        for plan in invalid_plans:
            with self.subTest(plan=plan), self.assertRaises(RunIdentityError):
                validate_run_identity_plan(plan, runs_root_portable=ROOT)

    def test_supplied_collections_are_not_mutated(self) -> None:
        occupied_ids = frozenset({"occupied"})
        occupied_paths = frozenset({f"{ROOT}/occupied"})
        known: tuple[RunIdentityPlan, ...] = ()
        self._select(
            lambda: RUN_ONE,
            occupied_run_ids=occupied_ids,
            occupied_portable_paths=occupied_paths,
            known_plans=known,
        )
        self.assertEqual(occupied_ids, frozenset({"occupied"}))
        self.assertEqual(occupied_paths, frozenset({f"{ROOT}/occupied"}))
        self.assertEqual(known, ())

    def test_selector_has_no_filesystem_store_runner_or_reservation_effects(self) -> None:
        patches = (
            patch("pathlib.Path.exists", side_effect=AssertionError("exists")),
            patch("pathlib.Path.mkdir", side_effect=AssertionError("mkdir")),
            patch("pathlib.Path.open", side_effect=AssertionError("open")),
            patch("tempfile.NamedTemporaryFile", side_effect=AssertionError("tempfile")),
            patch("os.link", side_effect=AssertionError("link")),
            patch("os.replace", side_effect=AssertionError("replace")),
            patch("os.remove", side_effect=AssertionError("remove")),
            patch("pathlib.Path.unlink", side_effect=AssertionError("unlink")),
            patch("dpslab.runner.reserve_run", side_effect=AssertionError("reserve_run")),
            patch(
                "dpslab.comparison_result_io.ComparisonResultStore.commit",
                side_effect=AssertionError("commit"),
            ),
            patch(
                "dpslab.comparison_result_io.ComparisonResultStore.create",
                side_effect=AssertionError("create"),
            ),
        )
        entered = []
        try:
            for item in patches:
                entered.append(item)
                item.start()
            plan = self._select(lambda: RUN_ONE)
        finally:
            for item in reversed(entered):
                item.stop()
        self.assertEqual(plan.portable_path, f"{ROOT}/{RUN_ONE}")

    def test_build_current_run_id_rejects_invalid_explicit_components(self) -> None:
        naive = datetime(2026, 7, 16, 12, 0, 0)
        with self.assertRaises(RunIdentityError):
            build_current_run_id(naive, "abcdef12")
        for value in ("", "abc", "not-hex!!"):
            with self.subTest(uuid_hex=value), self.assertRaises(RunIdentityError):
                build_current_run_id(
                    datetime(2026, 7, 16, 12, 0, 0, tzinfo=timezone.utc),
                    value,
                )


if __name__ == "__main__":
    unittest.main()
