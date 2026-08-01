import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dpslab.candidate_knowledge_set import calculate_receipt_sha256
from dpslab.candidate_knowledge_store import (
    CandidateKnowledgeStoreError,
    calculate_commit_sha256,
    commit_candidate_knowledge_set,
    read_current_candidate_generation,
    validate_candidate_commit,
)
from dpslab.proposal_review import calculate_decision_sha256
from dpslab.knowledge_envelope import canonical_json_bytes


ROOT = Path(__file__).parents[2]
FILES = {
    "source_envelope": "knowledge/fixtures/static_fallback_template_synthetic_0_1.json",
    "source_catalog": "knowledge/catalogs/static_template_catalog_synthetic_0_1.json",
    "proposal": "knowledge/proposals/catalog_change_proposal_synthetic_0_1.json",
    "decision": "knowledge/reviews/proposal_review_decision_synthetic_0_1.json",
    "candidate_set": "knowledge/candidates/candidate_knowledge_set_synthetic_0_1.json",
}


def load(name):
    return json.loads((ROOT / FILES[name]).read_text(encoding="utf-8"))


class CandidateKnowledgeStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Path(self.temp.name) / "store"
        self.values = {name: load(name) for name in FILES}
        self.time = datetime(2026, 8, 1, 6, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.temp.cleanup()

    def commit(self, **changes):
        values = {**self.values, **changes}
        return commit_candidate_knowledge_set(
            self.store,
            source_envelope=values["source_envelope"],
            source_catalog=values["source_catalog"],
            proposal=values["proposal"],
            decision=values["decision"],
            candidate_set=values["candidate_set"],
            generation_id=values.get("generation_id", "candidate.synthetic.001"),
            committed_at=values.get("committed_at", self.time),
        )

    def test_commit_creates_visible_generation(self):
        result = self.commit()
        self.assertFalse(result.idempotent)
        self.assertTrue((result.generation_path / "commit.json").is_file())
        self.assertTrue((self.store / "current.json").is_file())

    def test_read_round_trips_candidate_set(self):
        self.commit()
        current = read_current_candidate_generation(self.store)
        for key in ("candidate_envelope", "candidate_catalog", "receipt"):
            self.assertEqual(self.values["candidate_set"][key], current[key])

    def test_commit_is_pending_and_durable(self):
        self.commit()
        commit = read_current_candidate_generation(self.store)["commit"]
        self.assertEqual("candidate_pending_review", commit["identity"]["status"])
        self.assertTrue(commit["consumption"]["durably_recorded"])

    def test_exact_replay_is_idempotent(self):
        first = self.commit()
        before = (first.generation_path / "commit.json").stat().st_mtime_ns
        marker_before = (self.store / "current.json").stat().st_mtime_ns
        second = self.commit()
        self.assertTrue(second.idempotent)
        self.assertEqual(before, (second.generation_path / "commit.json").stat().st_mtime_ns)
        self.assertEqual(marker_before, (self.store / "current.json").stat().st_mtime_ns)

    def test_divergent_generation_replay_fails(self):
        self.commit()
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "consumption_replay"):
            self.commit(generation_id="candidate.synthetic.002")

    def test_divergent_timestamp_replay_fails(self):
        self.commit()
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "consumption_replay"):
            self.commit(committed_at=datetime(2026, 8, 1, 6, 1, tzinfo=timezone.utc))

    def test_naive_commit_time_fails_before_store_creation(self):
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "committed_at_invalid"):
            self.commit(committed_at=datetime(2026, 8, 1, 6, 0))
        self.assertFalse(self.store.exists())

    def test_invalid_generation_id_fails(self):
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "generation_id_invalid"):
            self.commit(generation_id="../escape")

    def test_windows_unsafe_generation_id_fails(self):
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "generation_id_invalid"):
            self.commit(generation_id="candidate:unsafe")

    def test_source_envelope_binding_fails_closed(self):
        value = copy.deepcopy(self.values["source_envelope"])
        value["guidance"]["statements"][0]["text_key"] = "synthetic.changed"
        with self.assertRaises(CandidateKnowledgeStoreError):
            self.commit(source_envelope=value)

    def test_source_catalog_binding_fails_closed(self):
        value = copy.deepcopy(self.values["candidate_set"])
        value["receipt"]["source_bindings"]["source_catalog_sha256"] = "f" * 64
        value["receipt"]["integrity"]["receipt_sha256"] = calculate_receipt_sha256(value["receipt"])
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "source_binding_mismatch"):
            self.commit(candidate_set=value)

    def test_decision_binding_fails_closed(self):
        value = copy.deepcopy(self.values["decision"])
        value["identity"]["reviewer_id"] = "synthetic.reviewer.2"
        value["integrity"]["decision_sha256"] = calculate_decision_sha256(value)
        with self.assertRaises(CandidateKnowledgeStoreError):
            self.commit(decision=value)

    def test_candidate_envelope_binding_fails_closed(self):
        value = copy.deepcopy(self.values["candidate_set"])
        value["candidate_envelope"]["guidance"]["statements"][0]["text_key"] = "synthetic.changed"
        with self.assertRaises(CandidateKnowledgeStoreError):
            self.commit(candidate_set=value)

    def test_candidate_set_root_is_closed(self):
        value = copy.deepcopy(self.values["candidate_set"])
        value["extra"] = True
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "candidate_set_fields_invalid"):
            self.commit(candidate_set=value)

    def test_store_root_symlink_is_rejected(self):
        target = Path(self.temp.name) / "target"
        target.mkdir()
        try:
            self.store.symlink_to(target, target_is_directory=True)
        except OSError:
            self.skipTest("directory symlink unavailable")
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "store_root_invalid"):
            self.commit()

    def test_generation_layout_file_is_rejected(self):
        (self.store / "generations").mkdir(parents=True)
        (self.store / "staging").mkdir()
        (self.store / "generations" / "unexpected").write_text("x")
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "generation_layout_invalid"):
            self.commit()

    def test_corrupt_existing_commit_fails_closed(self):
        self.commit()
        path = self.store / "generations" / "candidate.synthetic.001" / "commit.json"
        path.write_text("{}\n", encoding="utf-8")
        with self.assertRaises(CandidateKnowledgeStoreError):
            self.commit(generation_id="candidate.synthetic.002")

    def test_marker_mismatch_fails_closed(self):
        self.commit()
        marker = json.loads((self.store / "current.json").read_text())
        marker["commit_sha256"] = "f" * 64
        (self.store / "current.json").write_bytes(canonical_json_bytes(marker))
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "marker_commit_mismatch"):
            read_current_candidate_generation(self.store)

    def test_noncanonical_marker_fails_closed(self):
        self.commit()
        marker = json.loads((self.store / "current.json").read_text())
        (self.store / "current.json").write_text(json.dumps(marker, indent=2) + "\n")
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "noncanonical"):
            read_current_candidate_generation(self.store)

    def test_missing_marker_fails_closed(self):
        self.store.mkdir()
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "durable_file_invalid"):
            read_current_candidate_generation(self.store)

    def test_read_does_not_create_missing_store(self):
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "store_root_invalid"):
            read_current_candidate_generation(self.store)
        self.assertFalse(self.store.exists())

    def test_commit_hash_projection_is_stable(self):
        self.commit()
        value = read_current_candidate_generation(self.store)["commit"]
        changed = copy.deepcopy(value)
        changed["integrity"]["commit_sha256"] = "f" * 64
        self.assertEqual(calculate_commit_sha256(value), calculate_commit_sha256(changed))

    def test_commit_validator_rejects_extra_field(self):
        self.commit()
        value = read_current_candidate_generation(self.store)["commit"]
        value["extra"] = True
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "commit_fields_invalid"):
            validate_candidate_commit(value)

    def test_commit_validator_rejects_false_consumption(self):
        self.commit()
        value = read_current_candidate_generation(self.store)["commit"]
        value["consumption"]["durably_recorded"] = False
        value["integrity"]["commit_sha256"] = calculate_commit_sha256(value)
        with self.assertRaisesRegex(CandidateKnowledgeStoreError, "consumption_not_durable"):
            validate_candidate_commit(value)

    def test_atomic_marker_failure_leaves_generation_invisible(self):
        real_replace = __import__("os").replace
        def fail_marker(source, target):
            if Path(target).name == "current.json":
                raise OSError("synthetic marker failure")
            return real_replace(source, target)
        with patch("dpslab.candidate_knowledge_store.os.replace", side_effect=fail_marker):
            with self.assertRaisesRegex(OSError, "synthetic marker failure"):
                self.commit()
        self.assertFalse((self.store / "current.json").exists())
        self.assertTrue((self.store / "generations" / "candidate.synthetic.001").is_dir())

    def test_retry_after_marker_failure_recovers_exact_generation(self):
        real_replace = __import__("os").replace
        failed = False
        def fail_once(source, target):
            nonlocal failed
            if Path(target).name == "current.json" and not failed:
                failed = True
                raise OSError("synthetic marker failure")
            return real_replace(source, target)
        with patch("dpslab.candidate_knowledge_store.os.replace", side_effect=fail_once):
            with self.assertRaises(OSError):
                self.commit()
        result = self.commit()
        self.assertTrue(result.idempotent)
        self.assertEqual("candidate.synthetic.001", read_current_candidate_generation(self.store)["commit"]["identity"]["generation_id"])

    def test_input_values_are_not_mutated(self):
        before = copy.deepcopy(self.values)
        self.commit()
        self.assertEqual(before, self.values)

    def test_no_approval_or_signature_is_introduced(self):
        self.commit()
        current = read_current_candidate_generation(self.store)
        self.assertIsNone(current["candidate_envelope"]["integrity"]["signature"])
        self.assertEqual("pending_review", current["candidate_catalog"]["entries"][-1]["lifecycle_state"])


if __name__ == "__main__":
    unittest.main()
