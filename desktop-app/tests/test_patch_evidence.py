import copy
import json
from pathlib import Path
import unittest

from dpslab.patch_evidence import (PatchContext, PatchEvidenceError,
    calculate_evidence_sha256, canonical_patch_bytes, intake_patch_evidence,
    validate_patch_evidence)

ROOT = Path(__file__).parents[2]
FIXTURE = ROOT / "knowledge/snapshots/patch_evidence_synthetic_0_1.json"
ALLOWED = frozenset({"synthetic.role.damage", "synthetic.role.safety"})

def rehash(value):
    value["integrity"]["evidence_sha256"] = calculate_evidence_sha256(value)
    return value

class PatchEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.value = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.context = PatchContext("retail", 120500, 120500)

    def mutate(self, path, content):
        value = copy.deepcopy(self.value); target = value
        for part in path[:-1]: target = target[part]
        target[path[-1]] = content
        return rehash(value)

    def test_fixture_is_valid_and_canonical(self):
        self.assertEqual(FIXTURE.read_bytes(), canonical_patch_bytes(validate_patch_evidence(self.value)))
    def test_hash_projection_omits_only_hash(self):
        value = copy.deepcopy(self.value); value["integrity"]["evidence_sha256"] = "f" * 64
        self.assertEqual(calculate_evidence_sha256(self.value), calculate_evidence_sha256(value))
    def test_wrong_hash_rejected(self):
        value = copy.deepcopy(self.value); value["integrity"]["evidence_sha256"] = "f" * 64
        with self.assertRaisesRegex(PatchEvidenceError, "sha256_mismatch"): validate_patch_evidence(value)
    def test_root_is_closed(self):
        value = copy.deepcopy(self.value); value["extra"] = True
        with self.assertRaisesRegex(PatchEvidenceError, "fields_invalid"): validate_patch_evidence(value)
    def test_identity_is_closed(self):
        value = copy.deepcopy(self.value); value["identity"]["extra"] = True
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(value)
    def test_source_is_closed(self):
        value = copy.deepcopy(self.value); value["source"]["extra"] = True
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(value)
    def test_assertion_is_closed(self):
        value = copy.deepcopy(self.value); value["assertions"][0]["extra"] = True
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(value)
    def test_schema_version_rejected(self):
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(self.mutate(["schema_version"], "0.2"))
    def test_lifecycle_rejected(self):
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(self.mutate(["identity","lifecycle"], "future"))
    def test_timestamp_order_rejected(self):
        with self.assertRaisesRegex(PatchEvidenceError, "timestamp_order"): validate_patch_evidence(self.mutate(["source","captured_at"], "2026-07-31T11:00:00Z"))
    def test_media_type_rejected(self):
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(self.mutate(["source","media_type"], "html"))
    def test_acquisition_policy_rejected(self):
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(self.mutate(["source","acquisition_class"], "scrape"))
    def test_license_policy_rejected(self):
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(self.mutate(["source","license_class"], "unknown"))
    def test_authenticity_policy_rejected(self):
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(self.mutate(["source","authenticity_class"], "guessed"))
    def test_product_rejected(self):
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(self.mutate(["source","wow_product"], "classic"))
    def test_range_rejected(self):
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(self.mutate(["source","build_min"], 120501))
    def test_bool_range_rejected(self):
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(self.mutate(["source","build_min"], True))
    def test_self_supersession_rejected(self):
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(self.mutate(["source","supersedes_evidence_id"], "synthetic.patch.120500.1"))
    def test_duplicate_assertion_rejected(self):
        value = copy.deepcopy(self.value); value["assertions"].append(copy.deepcopy(value["assertions"][0]))
        with self.assertRaisesRegex(PatchEvidenceError, "duplicate"): validate_patch_evidence(rehash(value))
    def test_conflicting_assertions_rejected(self):
        value = copy.deepcopy(self.value); other = copy.deepcopy(value["assertions"][0]); other["assertion_id"] = "other"; value["assertions"].append(other)
        with self.assertRaisesRegex(PatchEvidenceError, "conflict"): validate_patch_evidence(rehash(value))
    def test_invalid_operation_rejected(self):
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(self.mutate(["assertions",0,"operation"], "approve"))
    def test_ineffective_change_rejected(self):
        with self.assertRaises(PatchEvidenceError): validate_patch_evidence(self.mutate(["assertions",0,"new_token"], "synthetic-coefficient-a"))
    def test_pending_review_is_only_positive_outcome(self):
        result = intake_patch_evidence(self.value, self.context, ALLOWED)
        self.assertEqual(("pending_review", 1), (result.status, len(result.candidate_ids)))
    def test_empty_assertions_are_no_relevant_change(self):
        result = intake_patch_evidence(self.mutate(["assertions"], []), self.context, ALLOWED)
        self.assertEqual("no_relevant_change", result.status)
    def test_historical_is_isolated(self):
        result = intake_patch_evidence(self.mutate(["identity","lifecycle"], "historical"), self.context, ALLOWED)
        self.assertEqual(("evidence_unavailable", "historical_only"), (result.status, result.reason))
    def test_build_mismatch_fails_closed(self):
        self.assertEqual("build_mismatch", intake_patch_evidence(self.value, PatchContext("retail", 120501, 120500), ALLOWED).reason)
    def test_ambiguous_assertion_fails_closed(self):
        result = intake_patch_evidence(self.mutate(["assertions",0,"certainty"], "ambiguous"), self.context, ALLOWED)
        self.assertEqual("ambiguous_assertion", result.reason)
    def test_unknown_family_fails_closed(self):
        result = intake_patch_evidence(self.mutate(["assertions",0,"parameter_family_id"], "synthetic.unknown"), self.context, ALLOWED)
        self.assertEqual("unknown_family", result.reason)
    def test_malformed_subject_list_is_sanitized(self):
        for content in ("not-a-list", [None]):
            with self.assertRaises(PatchEvidenceError):
                validate_patch_evidence(self.mutate(["assertions",0,"subject_tokens"], content))
    def test_invalid_context_types_fail_closed(self):
        for context in (PatchContext("retail", "120500", 120500), PatchContext("retail", -1, 120500), PatchContext("retail", 120500, None)):
            self.assertEqual("context_invalid", intake_patch_evidence(self.value, context, ALLOWED).reason)
    def test_unknown_invalidation_family_fails_closed(self):
        value = self.mutate(["assertions",0,"invalidation_families"], ["synthetic.unknown"])
        self.assertEqual("unknown_family", intake_patch_evidence(value, self.context, ALLOWED).reason)
    def test_invalidation_is_separate_from_candidate(self):
        value = self.mutate(["assertions",0,"invalidation_families"], ["synthetic.role.safety"])
        result = intake_patch_evidence(value, self.context, ALLOWED)
        self.assertEqual(("coverage_invalidated", (), ("synthetic.role.safety",)), (result.status, result.candidate_ids, result.invalidated_families))
    def test_fixture_contains_no_real_or_network_claims(self):
        text = FIXTURE.read_text().lower()
        for forbidden in ("http://", "https://", "battle.net", "wowhead", "warrior", "sqlite", "database"):
            self.assertNotIn(forbidden, text)

if __name__ == "__main__": unittest.main()
