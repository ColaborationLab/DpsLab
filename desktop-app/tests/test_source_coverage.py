import copy
from datetime import datetime, timezone
import json
from pathlib import Path

from tests.strict_temporary_cleanup import strict_temporary_directory
import tempfile
import unittest

from dpslab.source_coverage import (
    CoverageContext, SourceCoverageError, assess_source_coverage,
    calculate_archive_sha256, calculate_manifest_sha256,
    canonical_coverage_bytes, compare_historical_captures,
    load_source_capture_archive, load_source_coverage_manifest,
    validate_source_capture_archive, validate_source_coverage_manifest,
)

ROOT = Path(__file__).parents[2]
MANIFEST = ROOT / "knowledge/manifests/source_coverage_synthetic_0_1.json"
ARCHIVE = ROOT / "knowledge/snapshots/source_capture_synthetic_0_1.json"

def rehash_manifest(value):
    value["integrity"]["manifest_sha256"] = calculate_manifest_sha256(value)
    return value

def rehash_archive(value):
    value["integrity"]["archive_sha256"] = calculate_archive_sha256(value)
    return value

class SourceCoverageTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.archive = json.loads(ARCHIVE.read_text(encoding="utf-8"))
        self.context = CoverageContext("retail", 120500, 120500, 1, 71, "damage", "synthetic_single_target", datetime(2026, 7, 31, tzinfo=timezone.utc))

    def test_fixtures_are_canonical_and_valid(self):
        self.assertEqual(MANIFEST.read_bytes(), canonical_coverage_bytes(load_source_coverage_manifest(MANIFEST)))
        self.assertEqual(ARCHIVE.read_bytes(), canonical_coverage_bytes(load_source_capture_archive(ARCHIVE)))

    def test_manifest_root_is_closed(self):
        value = copy.deepcopy(self.manifest); value["extra"] = True
        with self.assertRaisesRegex(SourceCoverageError, "fields_invalid"): validate_source_coverage_manifest(value)

    def test_archive_and_capture_are_closed(self):
        for nested in (False, True):
            value = copy.deepcopy(self.archive)
            (value["captures"][0] if nested else value)["extra"] = True
            with self.assertRaisesRegex(SourceCoverageError, "fields_invalid"): validate_source_capture_archive(value)

    def test_hash_projections_omit_only_hash(self):
        manifest = copy.deepcopy(self.manifest); manifest["integrity"]["manifest_sha256"] = "f" * 64
        archive = copy.deepcopy(self.archive); archive["integrity"]["archive_sha256"] = "f" * 64
        self.assertEqual(calculate_manifest_sha256(self.manifest), calculate_manifest_sha256(manifest))
        self.assertEqual(calculate_archive_sha256(self.archive), calculate_archive_sha256(archive))

    def test_wrong_manifest_hash_is_rejected(self):
        value = copy.deepcopy(self.manifest); value["integrity"]["manifest_sha256"] = "f" * 64
        with self.assertRaisesRegex(SourceCoverageError, "sha256_mismatch"): validate_source_coverage_manifest(value)

    def test_wrong_archive_hash_is_rejected(self):
        value = copy.deepcopy(self.archive); value["integrity"]["archive_sha256"] = "f" * 64
        with self.assertRaisesRegex(SourceCoverageError, "sha256_mismatch"): validate_source_capture_archive(value)

    def test_noncanonical_file_is_rejected(self):
        with strict_temporary_directory() as directory:
            path = directory / "manifest.json"; path.write_text(json.dumps(self.manifest, indent=2), encoding="utf-8")
            with self.assertRaisesRegex(SourceCoverageError, "bytes_noncanonical"): load_source_coverage_manifest(path)

    def test_duplicate_requirement_family_is_rejected(self):
        value = copy.deepcopy(self.manifest); value["requirements"].append(copy.deepcopy(value["requirements"][0]))
        with self.assertRaisesRegex(SourceCoverageError, "family_id_duplicate"): validate_source_coverage_manifest(rehash_manifest(value))

    def test_requirement_policy_is_closed(self):
        for field, content in (("acquisition_classes", ["guess"]), ("license_classes", ["unknown"]), ("role_scope", "support")):
            value = copy.deepcopy(self.manifest); value["requirements"][0][field] = content
            with self.assertRaises(SourceCoverageError): validate_source_coverage_manifest(rehash_manifest(value))

    def test_duplicate_capture_id_is_rejected(self):
        value = copy.deepcopy(self.archive); value["captures"].append(copy.deepcopy(value["captures"][0]))
        with self.assertRaisesRegex(SourceCoverageError, "capture_id_duplicate"): validate_source_capture_archive(rehash_archive(value))

    def test_duplicate_current_family_is_rejected(self):
        value = copy.deepcopy(self.archive); duplicate = copy.deepcopy(value["captures"][0]); duplicate["capture_id"] = "synthetic.other"; value["captures"].append(duplicate)
        with self.assertRaisesRegex(SourceCoverageError, "current_family_duplicate"): validate_source_capture_archive(rehash_archive(value))

    def test_invalid_supersession_is_rejected(self):
        for previous in ("missing.capture", "synthetic.mechanics.current"):
            value = copy.deepcopy(self.archive); value["captures"][0]["supersedes_capture_id"] = previous
            with self.assertRaisesRegex(SourceCoverageError, "supersession_invalid"): validate_source_capture_archive(rehash_archive(value))

    def test_complete_coverage_is_pending_review_only(self):
        result = assess_source_coverage(self.manifest, self.archive, self.context)
        self.assertEqual(("pending_review", None, 2), (result.status, result.reason, len(result.current_capture_ids)))

    def test_missing_family_fails_closed(self):
        archive = copy.deepcopy(self.archive); archive["captures"] = [x for x in archive["captures"] if x["family_id"] != "synthetic.role.damage"]
        self.assertEqual("missing_family", assess_source_coverage(self.manifest, rehash_archive(archive), self.context).reason)

    def test_historical_capture_does_not_fill_current_gap(self):
        archive = copy.deepcopy(self.archive)
        for item in archive["captures"]:
            if item["family_id"] == "synthetic.role.damage": item["lifecycle"] = "historical"
        self.assertEqual("missing_family", assess_source_coverage(self.manifest, rehash_archive(archive), self.context).reason)

    def test_stale_and_future_captures_fail_closed(self):
        for captured in ("2026-07-01T00:00:00Z", "2026-08-01T00:00:00Z"):
            archive = copy.deepcopy(self.archive); archive["captures"][0]["captured_at"] = captured
            self.assertEqual("stale", assess_source_coverage(self.manifest, rehash_archive(archive), self.context).reason)

    def test_invalidated_capture_fails_closed(self):
        archive = copy.deepcopy(self.archive); archive["captures"][0]["invalidation_reasons"] = ["synthetic.withdrawn"]
        self.assertEqual("invalidated", assess_source_coverage(self.manifest, rehash_archive(archive), self.context).reason)

    def test_unknown_build_never_guesses_newest(self):
        context = CoverageContext(**{**self.context.__dict__, "build": 999999})
        self.assertEqual("unknown_build", assess_source_coverage(self.manifest, self.archive, context).reason)

    def test_context_subject_mismatches_fail_closed(self):
        for field, content in (("class_id", 2), ("specialization_id", 72), ("role", "tank"), ("content_context", "synthetic.other")):
            context = CoverageContext(**{**self.context.__dict__, field: content})
            self.assertEqual("subject", assess_source_coverage(self.manifest, self.archive, context).reason)

    def test_source_identity_mismatch_fails_closed(self):
        archive = copy.deepcopy(self.archive); archive["captures"][0]["source_id"] = "synthetic.other"
        self.assertEqual("source_identity", assess_source_coverage(self.manifest, rehash_archive(archive), self.context).reason)

    def test_source_policy_mismatch_fails_closed(self):
        for field, content in (("acquisition_class", "manual"), ("license_class", "permitted_derived_use")):
            archive = copy.deepcopy(self.archive); archive["captures"][0][field] = content
            self.assertEqual("source_policy", assess_source_coverage(self.manifest, rehash_archive(archive), self.context).reason)

    def test_capture_build_and_subject_mismatch_fail_closed(self):
        archive = copy.deepcopy(self.archive); archive["captures"][0]["build_max"] = 120100
        self.assertEqual("capture_build", assess_source_coverage(self.manifest, rehash_archive(archive), self.context).reason)
        archive = copy.deepcopy(self.archive); archive["captures"][0]["class_id"] = 2
        self.assertEqual("capture_subject", assess_source_coverage(self.manifest, rehash_archive(archive), self.context).reason)

    def test_historical_comparison_is_explicit_and_labeled(self):
        result = compare_historical_captures(self.archive, "synthetic.mechanics.previous", "synthetic.mechanics.current")
        self.assertTrue(result.historical_only); self.assertNotEqual(result.left_revision, result.right_revision)

    def test_historical_comparison_rejects_invalid_pairs(self):
        pairs = (("synthetic.mechanics.current", "synthetic.mechanics.current"), ("missing", "synthetic.mechanics.current"), ("synthetic.mechanics.current", "synthetic.damage.current"))
        for left, right in pairs:
            with self.assertRaises(SourceCoverageError): compare_historical_captures(self.archive, left, right)

    def test_tank_safety_family_is_mandatory_when_declared(self):
        manifest = copy.deepcopy(self.manifest); manifest["subject"]["role"] = "tank"
        requirement = copy.deepcopy(manifest["requirements"][1]); requirement.update({"family_id":"synthetic.tank.safety","role_scope":"tank","source_id":"synthetic.tank.source"}); manifest["requirements"] = [manifest["requirements"][0], requirement]
        archive = copy.deepcopy(self.archive)
        for item in archive["captures"]: item["role"] = "tank"
        context = CoverageContext(**{**self.context.__dict__, "role":"tank"})
        self.assertEqual("missing_family", assess_source_coverage(rehash_manifest(manifest), rehash_archive(archive), context).reason)

    def test_naive_observation_time_is_rejected(self):
        context = CoverageContext(**{**self.context.__dict__, "observed_at": datetime(2026, 7, 31)})
        with self.assertRaisesRegex(SourceCoverageError, "observed_at_invalid"): assess_source_coverage(self.manifest, self.archive, context)

    def test_fixtures_have_no_network_database_or_real_claims(self):
        text = (MANIFEST.read_text() + ARCHIVE.read_text()).lower()
        for forbidden in ("http://", "https://", "sqlite", "database", "best in slot", "arms warrior", "c:\\users\\", "d:\\proyectos\\"):
            self.assertNotIn(forbidden, text)

if __name__ == "__main__":
    unittest.main()
