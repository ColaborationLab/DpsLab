import copy
from datetime import datetime, timezone, tzinfo
import json
from pathlib import Path
import tempfile
import unittest

from dpslab.knowledge_envelope import (
    CompatibilityContext,
    KnowledgeEnvelopeError,
    calculate_payload_sha256,
    canonical_json_bytes,
    load_knowledge_envelope,
    select_guidance,
    unsigned_payload_bytes,
    validate_knowledge_envelope,
)


FIXTURE = (
    Path(__file__).parents[2]
    / "knowledge"
    / "fixtures"
    / "static_fallback_template_synthetic_0_1.json"
)


def rehash(document):
    document["integrity"]["payload_sha256"] = calculate_payload_sha256(document)
    return document


class KnowledgeEnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.context = CompatibilityContext(
            wow_product="retail",
            build=120500,
            interface=120500,
            class_id=1,
            specialization_id=71,
            race_id=1,
            level=80,
            content_context="synthetic_single_target",
            observed_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        )

    def assert_invalid(self, document, message):
        with self.assertRaisesRegex(KnowledgeEnvelopeError, message):
            validate_knowledge_envelope(document)

    def test_fixture_is_canonical_and_valid(self):
        loaded = load_knowledge_envelope(FIXTURE)
        self.assertEqual(self.document, loaded)
        self.assertEqual(FIXTURE.read_bytes(), canonical_json_bytes(loaded))

    def test_fixture_payload_hash_is_reproducible(self):
        self.assertEqual(
            self.document["integrity"]["payload_sha256"],
            calculate_payload_sha256(self.document),
        )

    def test_unknown_root_and_nested_fields_are_rejected(self):
        root = copy.deepcopy(self.document)
        root["unknown"] = True
        self.assert_invalid(root, "knowledge_root_fields_invalid")
        nested = copy.deepcopy(self.document)
        nested["subject"]["unknown"] = True
        self.assert_invalid(nested, "knowledge_subject_fields_invalid")

    def test_only_retail_and_ordered_ranges_are_accepted(self):
        product = copy.deepcopy(self.document)
        product["compatibility"]["wow_product"] = "classic"
        self.assert_invalid(rehash(product), "knowledge_wow_product_unsupported")
        ranges = copy.deepcopy(self.document)
        ranges["compatibility"]["build_min"] = 121000
        self.assert_invalid(rehash(ranges), "knowledge_compatibility_range_invalid")

    def test_static_tier_cannot_claim_analytical_evidence(self):
        document = copy.deepcopy(self.document)
        document["evidence"]["method"] = "synthetic_method"
        self.assert_invalid(rehash(document), "knowledge_static_evidence_overclaimed")

    def test_imported_evidence_requires_complete_provenance(self):
        document = copy.deepcopy(self.document)
        document["evidence"]["tier"] = "imported_analytical_evidence"
        self.assert_invalid(rehash(document), "knowledge_imported_evidence_incomplete")
        document["evidence"].update(
            {
                "method": "synthetic_import",
                "run_count": 10,
                "confidence_interval_percent": [95, 95],
                "source_hashes": {"synthetic_source": "a" * 64},
            }
        )
        validate_knowledge_envelope(rehash(document))
        document["evidence"]["source_ids"] = []
        self.assert_invalid(rehash(document), "knowledge_imported_evidence_incomplete")

    def test_character_observation_tier_is_structurally_reserved(self):
        document = copy.deepcopy(self.document)
        document["evidence"]["tier"] = "character_observation"
        validate_knowledge_envelope(rehash(document))
        selection = select_guidance(rehash(document), self.context)
        self.assertEqual(
            ("guidance_unavailable", "evidence_tier_reserved", ()),
            tuple(selection.__dict__.values()),
        )

    def test_noncanonical_file_bytes_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "envelope.json"
            path.write_text(json.dumps(self.document, indent=2), encoding="utf-8")
            with self.assertRaisesRegex(
                KnowledgeEnvelopeError, "knowledge_envelope_bytes_noncanonical"
            ):
                load_knowledge_envelope(path)

    def test_hash_projection_omits_only_hash_and_signature(self):
        baseline = unsigned_payload_bytes(self.document)
        omitted = copy.deepcopy(self.document)
        omitted["integrity"]["payload_sha256"] = "f" * 64
        omitted["integrity"]["signature"] = "ignored-by-projection"
        self.assertEqual(baseline, unsigned_payload_bytes(omitted))
        retained = copy.deepcopy(self.document)
        retained["integrity"]["publisher_key_id"] = "placeholder.local.002"
        self.assertNotEqual(baseline, unsigned_payload_bytes(retained))
        retained = copy.deepcopy(self.document)
        retained["integrity"]["signature_algorithm"] = "future-algorithm"
        self.assertNotEqual(baseline, unsigned_payload_bytes(retained))

    def test_hash_that_includes_hash_field_is_rejected(self):
        document = copy.deepcopy(self.document)
        document["integrity"]["payload_sha256"] = (
            __import__("hashlib").sha256(canonical_json_bytes(document)).hexdigest()
        )
        self.assert_invalid(document, "knowledge_payload_sha256_mismatch")

    def test_hash_that_includes_signature_field_is_rejected(self):
        document = copy.deepcopy(self.document)
        projection = copy.deepcopy(document)
        del projection["integrity"]["payload_sha256"]
        document["integrity"]["payload_sha256"] = (
            __import__("hashlib").sha256(canonical_json_bytes(projection)).hexdigest()
        )
        self.assert_invalid(document, "knowledge_payload_sha256_mismatch")

    def test_compatible_context_returns_guidance(self):
        selection = select_guidance(self.document, self.context)
        self.assertEqual("guidance_available", selection.status)
        self.assertEqual(2, len(selection.statements))

    def test_unknown_build_fails_closed_without_newest_fallback(self):
        context = copy.copy(self.context)
        context = CompatibilityContext(**{**context.__dict__, "build": 999999})
        selection = select_guidance(self.document, context)
        self.assertEqual(("guidance_unavailable", "build", ()), tuple(selection.__dict__.values()))

    def test_subject_mismatches_fail_closed(self):
        for field, value, reason in (
            ("class_id", 2, "class"),
            ("specialization_id", 72, "specialization"),
            ("level", 79, "level"),
            ("content_context", "unknown_context", "content_context"),
        ):
            context = CompatibilityContext(**{**self.context.__dict__, field: value})
            self.assertEqual(reason, select_guidance(self.document, context).reason)

    def test_null_races_are_shared_but_explicit_races_are_closed(self):
        self.assertEqual(
            "guidance_available", select_guidance(self.document, self.context).status
        )
        document = copy.deepcopy(self.document)
        document["subject"]["race_ids"] = [2]
        selection = select_guidance(rehash(document), self.context)
        self.assertEqual("race", selection.reason)

    def test_expired_evidence_fails_closed(self):
        context = CompatibilityContext(
            **{
                **self.context.__dict__,
                "observed_at": datetime(2027, 1, 1, tzinfo=timezone.utc),
            }
        )
        self.assertEqual("expired", select_guidance(self.document, context).reason)

    def test_naive_observation_time_is_rejected(self):
        context = CompatibilityContext(
            **{
                **self.context.__dict__,
                "observed_at": datetime(2026, 8, 1),
            }
        )
        with self.assertRaisesRegex(
            KnowledgeEnvelopeError, "knowledge_observed_at_invalid"
        ):
            select_guidance(self.document, context)

    def test_timezone_with_no_effective_offset_is_rejected(self):
        class NoOffset(tzinfo):
            def utcoffset(self, value):
                return None

        context = CompatibilityContext(
            **{
                **self.context.__dict__,
                "observed_at": datetime(2026, 8, 1, tzinfo=NoOffset()),
            }
        )
        with self.assertRaisesRegex(
            KnowledgeEnvelopeError, "knowledge_observed_at_invalid"
        ):
            select_guidance(self.document, context)

    def test_timezone_offset_failure_is_normalized_to_static_error(self):
        class InvalidOffset(tzinfo):
            def utcoffset(self, value):
                raise OverflowError("synthetic out of range")

        context = CompatibilityContext(
            **{
                **self.context.__dict__,
                "observed_at": datetime(2026, 8, 1, tzinfo=InvalidOffset()),
            }
        )
        with self.assertRaisesRegex(
            KnowledgeEnvelopeError, "knowledge_observed_at_invalid"
        ):
            select_guidance(self.document, context)

    def test_external_context_rejects_boolean_and_invalid_scalars(self):
        for field, value, message in (
            ("class_id", True, "knowledge_context_class_id_invalid"),
            ("build", 0, "knowledge_context_build_invalid"),
            ("race_id", False, "knowledge_context_race_id_invalid"),
            (
                "content_context",
                "arbitrary prose",
                "knowledge_context_content_context_invalid",
            ),
        ):
            context = CompatibilityContext(**{**self.context.__dict__, field: value})
            with self.assertRaisesRegex(KnowledgeEnvelopeError, message):
                select_guidance(self.document, context)

    def test_character_bound_evidence_requires_exact_fingerprint(self):
        fingerprint = "b" * 64
        document = copy.deepcopy(self.document)
        document["subject"]["character_fingerprint"] = fingerprint
        document = rehash(document)
        self.assertEqual(
            "character_fingerprint",
            select_guidance(document, self.context).reason,
        )
        context = CompatibilityContext(
            **{**self.context.__dict__, "character_fingerprint": fingerprint}
        )
        self.assertEqual("guidance_available", select_guidance(document, context).status)

    def test_context_fingerprint_shape_is_validated(self):
        context = CompatibilityContext(
            **{**self.context.__dict__, "character_fingerprint": "not-a-hash"}
        )
        with self.assertRaisesRegex(
            KnowledgeEnvelopeError, "knowledge_context_character_fingerprint_invalid"
        ):
            select_guidance(self.document, context)

    def test_statement_contract_is_closed_and_ordered(self):
        document = copy.deepcopy(self.document)
        document["guidance"]["statements"][0]["order"] = 2
        self.assert_invalid(rehash(document), "knowledge_statement_order_invalid")
        document = copy.deepcopy(self.document)
        document["guidance"]["statements"][0]["text_key"] = "arbitrary prose"
        self.assert_invalid(rehash(document), "knowledge_statement_text_key_invalid")

    def test_safety_and_placeholder_signing_fail_closed(self):
        safety = copy.deepcopy(self.document)
        safety["safety"]["no_automation"] = False
        self.assert_invalid(rehash(safety), "knowledge_no_automation_required")
        signature = copy.deepcopy(self.document)
        signature["integrity"]["signature"] = "not-a-real-signature"
        self.assert_invalid(rehash(signature), "knowledge_signature_must_be_null")

    def test_fixture_is_synthetic_and_contains_no_personal_paths(self):
        text = FIXTURE.read_text(encoding="utf-8").lower()
        self.assertIn("synthetic_fixture_only", text)
        for forbidden in ("c:\\users\\", "d:\\proyectos\\", "best rotation"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
