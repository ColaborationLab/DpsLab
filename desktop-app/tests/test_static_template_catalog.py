import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from dpslab.knowledge_envelope import (
    CompatibilityContext,
    calculate_payload_sha256,
    canonical_json_bytes,
)
from dpslab.static_template_catalog import (
    ApprovalEvidence,
    StaticTemplateCatalogError,
    calculate_catalog_sha256,
    canonical_catalog_bytes,
    load_static_template_catalog,
    select_catalog_guidance,
    unsigned_catalog_bytes,
    validate_static_template_catalog,
)


ROOT = Path(__file__).parents[2]
CATALOG = ROOT / "knowledge/catalogs/static_template_catalog_synthetic_0_1.json"


def rehash(document):
    document["integrity"]["catalog_sha256"] = calculate_catalog_sha256(document)
    return document


class StaticTemplateCatalogTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.context = CompatibilityContext(
            "retail", 120500, 120500, 1, 71, 1, 80,
            "synthetic_single_target", datetime(2026, 8, 1, tzinfo=timezone.utc),
        )

    def assert_invalid(self, document, message):
        with self.assertRaisesRegex(StaticTemplateCatalogError, message):
            validate_static_template_catalog(document)

    def approved(self):
        document = copy.deepcopy(self.document)
        entry = document["entries"][0]
        entry["lifecycle_state"] = "approved"
        entry["source_coverage_complete"] = True
        entry["review"].update({
            "decision_id": "synthetic.approval.001", "reviewer_id": "synthetic.reviewer",
            "decided_at": "2026-07-31T12:00:00Z",
        })
        return rehash(document)

    def approval(self, document):
        entry = document["entries"][0]
        return ApprovalEvidence(
            document["identity"]["catalog_id"], document["identity"]["content_version"],
            entry["entry_id"], "synthetic.retail.damage.001", entry["envelope_sha256"],
            "approved", "synthetic.approval.001", "synthetic.reviewer",
            datetime(2026, 7, 31, 12, tzinfo=timezone.utc),
        )

    def test_fixture_is_canonical_valid_and_pending(self):
        loaded = load_static_template_catalog(CATALOG)
        self.assertEqual("pending_review", loaded["entries"][0]["lifecycle_state"])
        self.assertEqual(CATALOG.read_bytes(), canonical_catalog_bytes(loaded))

    def test_closed_root_entry_and_nested_fields(self):
        for target, key in ((self.document, "extra"), (self.document["entries"][0], "extra"), (self.document["entries"][0]["review"], "extra")):
            document = copy.deepcopy(self.document)
            if target is self.document:
                document[key] = True
            elif target is self.document["entries"][0]:
                document["entries"][0][key] = True
            else:
                document["entries"][0]["review"][key] = True
            self.assert_invalid(document, "fields_invalid")

    def test_hash_projection_omits_only_catalog_hash(self):
        baseline = unsigned_catalog_bytes(self.document)
        changed = copy.deepcopy(self.document)
        changed["integrity"]["catalog_sha256"] = "f" * 64
        self.assertEqual(baseline, unsigned_catalog_bytes(changed))
        changed["integrity"]["hash_algorithm"] = "sha512"
        self.assertNotEqual(baseline, unsigned_catalog_bytes(changed))

    def test_hash_including_hash_or_omitting_algorithm_is_rejected(self):
        included = copy.deepcopy(self.document)
        included["integrity"]["catalog_sha256"] = __import__("hashlib").sha256(canonical_catalog_bytes(included)).hexdigest()
        self.assert_invalid(included, "catalog_sha256_mismatch")
        omitted = copy.deepcopy(self.document)
        del omitted["integrity"]["hash_algorithm"]
        self.assert_invalid(omitted, "catalog_integrity_fields_invalid")

    def test_noncanonical_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(json.dumps(self.document, indent=2), encoding="utf-8")
            with self.assertRaisesRegex(StaticTemplateCatalogError, "catalog_bytes_noncanonical"):
                load_static_template_catalog(path)

    def test_path_is_confined_to_synthetic_fixture_root(self):
        for value, message in (("../fixture.json", "path_invalid"), ("C:\\fixture.json", "path_invalid"), ("knowledge/live/fixture.json", "outside_fixture_root"), ("knowledge/fixtures/x.toml", "path_invalid")):
            document = copy.deepcopy(self.document)
            document["entries"][0]["envelope_path"] = value
            self.assert_invalid(rehash(document), message)

    def test_duplicate_entry_id_is_rejected(self):
        document = copy.deepcopy(self.document)
        document["entries"].append(copy.deepcopy(document["entries"][0]))
        self.assert_invalid(rehash(document), "entry_id_duplicate")

    def test_overlapping_approved_dimensions_are_rejected(self):
        document = self.approved()
        duplicate = copy.deepcopy(document["entries"][0])
        duplicate["entry_id"] = "synthetic.damage.002"
        document["entries"].append(duplicate)
        self.assert_invalid(rehash(document), "approved_entry_overlap")

    def test_missing_self_and_cyclic_supersession_are_rejected(self):
        missing = copy.deepcopy(self.document)
        missing["entries"][0]["supersedes_entry_ids"] = ["missing.entry"]
        self.assert_invalid(rehash(missing), "supersession_invalid")
        self_ref = copy.deepcopy(self.document)
        self_ref["entries"][0]["supersedes_entry_ids"] = ["synthetic.damage.001"]
        self.assert_invalid(rehash(self_ref), "supersession_invalid")

    def test_all_lifecycle_states_have_closed_review_matrix(self):
        for state in ("draft", "pending_review"):
            document = copy.deepcopy(self.document)
            document["entries"][0]["lifecycle_state"] = state
            validate_static_template_catalog(rehash(document))
        for state in ("approved", "rejected", "deprecated", "withdrawn"):
            document = copy.deepcopy(self.document)
            entry = document["entries"][0]
            entry["lifecycle_state"] = state
            entry["review"].update({"decision_id": "decision.1", "reviewer_id": "reviewer.1", "decided_at": "2026-07-31T00:00:00Z"})
            if state == "rejected": entry["review"]["transition_reason"] = "rejected.reason"
            if state in {"deprecated", "withdrawn"}:
                entry["review"]["prior_approval_decision_id"] = "decision.0"
                entry["review"]["transition_reason"] = "state.changed"
            validate_static_template_catalog(rehash(document))

    def test_contradictory_review_states_are_rejected(self):
        pending = copy.deepcopy(self.document)
        pending["entries"][0]["review"]["decision_id"] = "decision.1"
        self.assert_invalid(rehash(pending), "review_state_contradiction")
        approved = self.approved()
        approved["entries"][0]["review"]["transition_reason"] = "not.allowed"
        self.assert_invalid(rehash(approved), "review_state_contradiction")

    def test_role_policy_must_match_role(self):
        document = copy.deepcopy(self.document)
        document["entries"][0]["role_policy"]["policy_id"] = "tank.safety_first.0_1"
        self.assert_invalid(rehash(document), "role_policy_mismatch")

    def test_pending_review_is_never_selectable(self):
        selected = select_catalog_guidance(self.document, ROOT, self.context, None)
        self.assertEqual(("guidance_unavailable", "no_eligible_entry"), (selected.status, selected.reason))

    def test_approved_entry_still_requires_external_evidence(self):
        document = self.approved()
        selected = select_catalog_guidance(document, ROOT, self.context, None)
        self.assertEqual("approval_missing", selected.reason)

    def test_matching_external_approval_allows_synthetic_guidance(self):
        document = self.approved()
        selected = select_catalog_guidance(document, ROOT, self.context, self.approval(document))
        self.assertEqual("guidance_available", selected.status)
        self.assertEqual("synthetic.damage.001", selected.entry_id)

    def test_mismatched_approval_fails_closed(self):
        document = self.approved()
        approval = self.approval(document)
        approval = ApprovalEvidence(**{**approval.__dict__, "catalog_content_version": "9.9.9"})
        self.assertEqual("approval_mismatch", select_catalog_guidance(document, ROOT, self.context, approval).reason)

    def test_external_approval_must_match_review_identity_and_utc_time(self):
        document = self.approved()
        approval = self.approval(document)
        for field, value in (
            ("decision_id", "other.decision"),
            ("reviewer_id", "other.reviewer"),
            ("decided_at", datetime(2026, 7, 31, 7, tzinfo=__import__("datetime").timezone(__import__("datetime").timedelta(hours=-5)))),
        ):
            changed = ApprovalEvidence(**{**approval.__dict__, field: value})
            self.assertEqual("approval_mismatch", select_catalog_guidance(document, ROOT, self.context, changed).reason)

    def test_incomplete_or_invalidated_source_coverage_fails_closed(self):
        for field, value in (("source_coverage_complete", False), ("invalidation_reasons", ["stale_source"])):
            document = self.approved()
            document["entries"][0][field] = value
            document = rehash(document)
            self.assertEqual("no_eligible_entry", select_catalog_guidance(document, ROOT, self.context, self.approval(document)).reason)

    def test_index_must_equal_envelope(self):
        document = copy.deepcopy(self.document)
        document["entries"][0]["index"]["class_id"] = 2
        document = rehash(document)
        with self.assertRaisesRegex(StaticTemplateCatalogError, "catalog_index_envelope_mismatch"):
            select_catalog_guidance(document, ROOT, self.context, None)

    def test_envelope_bytes_are_bound_by_sha256(self):
        document = copy.deepcopy(self.document)
        document["entries"][0]["envelope_sha256"] = "a" * 64
        document = rehash(document)
        with self.assertRaisesRegex(StaticTemplateCatalogError, "catalog_envelope_sha256_mismatch"):
            select_catalog_guidance(document, ROOT, self.context, None)

    def test_unknown_build_and_expiry_remain_fail_closed(self):
        document = self.approved()
        approval = self.approval(document)
        unknown = CompatibilityContext(**{**self.context.__dict__, "build": 999999})
        self.assertEqual("no_eligible_entry", select_catalog_guidance(document, ROOT, unknown, approval).reason)
        expired = CompatibilityContext(**{**self.context.__dict__, "observed_at": datetime(2027, 1, 1, tzinfo=timezone.utc)})
        self.assertEqual("no_eligible_entry", select_catalog_guidance(document, ROOT, expired, approval).reason)

    def test_tank_and_healer_require_dynamic_safety(self):
        source = json.loads((ROOT / "knowledge/fixtures/static_fallback_template_synthetic_0_1.json").read_text(encoding="utf-8"))
        for role in ("tank", "healer"):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                fixture = root / "knowledge/fixtures/static_fallback_template_synthetic_0_1.json"
                fixture.parent.mkdir(parents=True)
                envelope = copy.deepcopy(source)
                envelope["subject"]["role"] = role
                envelope["integrity"]["payload_sha256"] = calculate_payload_sha256(envelope)
                fixture.write_bytes(canonical_json_bytes(envelope))
                document = self.approved()
                entry = document["entries"][0]
                entry["index"]["role"] = role
                entry["role_policy"]["policy_id"] = f"{role}.safety_first.0_1"
                entry["role_policy"]["dynamic_safety_satisfied"] = False
                entry["envelope_sha256"] = __import__("hashlib").sha256(fixture.read_bytes()).hexdigest()
                document = rehash(document)
                self.assertEqual("no_eligible_entry", select_catalog_guidance(document, root, self.context, self.approval(document)).reason)

    def test_catalog_contains_no_database_or_network_state(self):
        text = CATALOG.read_text(encoding="utf-8").lower()
        for forbidden in ("database", "sqlite", "http://", "https://", "c:\\users\\", "d:\\proyectos\\"):
            self.assertNotIn(forbidden, text)

    def test_fixture_makes_no_live_balance_claim(self):
        text = CATALOG.read_text(encoding="utf-8").lower()
        for forbidden in ("best in slot", "stat weight", "rotation", "arms warrior"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
