import unittest
from unittest.mock import patch

from dpslab.patch_note_semantic_review_window import (
    REASONS,
    ROLES,
    SemanticReviewWindowError,
    build_synthetic_window_model,
    request_synthetic_decision,
    synthetic_demo,
)


class FakePort:
    def __init__(self, decision=None):
        self.decision = decision
        self.models = []

    def present(self, model):
        self.models.append(model)
        return self.decision


class SemanticReviewWindowTests(unittest.TestCase):
    def content(self):
        return memoryview(bytearray("Contenido sint\u00e9tico visible".encode())).toreadonly()

    def test_model_marks_synthetic_mode_prominently(self):
        model = build_synthetic_window_model("slot.path_01", self.content())
        self.assertIn("SINT\u00c9TICA", model.title.upper())
        self.assertIn("NO ES INFORMACI\u00d3N REAL", model.mode_label)

    def test_one_slot_and_content_are_present(self):
        model = build_synthetic_window_model("slot.path_02", self.content())
        self.assertEqual(model.slot_id, "slot.path_02")
        self.assertEqual(model.content, "Contenido sint\u00e9tico visible")

    def test_closed_choice_vocabularies(self):
        model = build_synthetic_window_model("slot.path_01", self.content())
        self.assertEqual(model.roles, ROLES)
        self.assertEqual(model.reasons, REASONS)

    def test_choices_start_empty_and_continue_requires_both(self):
        model = build_synthetic_window_model("slot.path_01", self.content())
        self.assertEqual(model.initial_role, "")
        self.assertEqual(model.initial_reason, "")
        self.assertTrue(model.continue_requires_explicit_choices)

    def test_cancel_returns_none(self):
        self.assertIsNone(request_synthetic_decision("slot.path_01", self.content(), port=FakePort()))

    def test_valid_decision_is_copied(self):
        decision = {"role": "unknown", "reason_code": "ambiguous_visual_structure"}
        result = request_synthetic_decision("slot.path_01", self.content(), port=FakePort(decision))
        self.assertEqual(result, decision)
        self.assertIsNot(result, decision)

    def test_port_receives_exactly_one_model(self):
        port = FakePort({"role": "rejected", "reason_code": "reviewer_rejected"})
        request_synthetic_decision("slot.path_03", self.content(), port=port)
        self.assertEqual(len(port.models), 1)

    def test_mutable_view_is_rejected(self):
        with self.assertRaisesRegex(SemanticReviewWindowError, "readonly"):
            build_synthetic_window_model("slot.path_01", memoryview(bytearray(b"synthetic")))

    def test_invalid_utf8_is_rejected(self):
        with self.assertRaisesRegex(SemanticReviewWindowError, "utf8"):
            build_synthetic_window_model("slot.path_01", memoryview(bytearray(b"\xff")).toreadonly())

    def test_empty_content_is_rejected(self):
        with self.assertRaisesRegex(SemanticReviewWindowError, "empty"):
            build_synthetic_window_model("slot.path_01", memoryview(bytearray()).toreadonly())

    def test_invalid_slot_is_rejected(self):
        with self.assertRaisesRegex(SemanticReviewWindowError, "slot_id"):
            build_synthetic_window_model("article_title", self.content())

    def test_extra_decision_field_is_rejected(self):
        decision = {"role": "unknown", "reason_code": "ambiguous_visual_structure", "text": "forbidden"}
        with self.assertRaisesRegex(SemanticReviewWindowError, "shape"):
            request_synthetic_decision("slot.path_01", self.content(), port=FakePort(decision))

    def test_unknown_role_is_rejected(self):
        decision = {"role": "ability", "reason_code": "direct_visual_confirmation"}
        with self.assertRaisesRegex(SemanticReviewWindowError, "value"):
            request_synthetic_decision("slot.path_01", self.content(), port=FakePort(decision))

    def test_unknown_reason_is_rejected(self):
        decision = {"role": "article_body", "reason_code": "inferred_from_length"}
        with self.assertRaisesRegex(SemanticReviewWindowError, "value"):
            request_synthetic_decision("slot.path_01", self.content(), port=FakePort(decision))

    def test_model_has_no_persistence_or_network_fields(self):
        names = set(build_synthetic_window_model("slot.path_01", self.content()).__dict__)
        self.assertTrue(names.isdisjoint({"url", "path", "log", "clipboard", "receipt"}))

    def test_demo_uses_fixed_synthetic_content_and_zeroizes(self):
        with patch(
            "dpslab.patch_note_semantic_review_window.request_synthetic_decision",
            return_value=None,
        ) as request:
            self.assertIsNone(synthetic_demo())
        slot_id, view = request.call_args.args[:2]
        self.assertEqual(slot_id, "slot.path_01")
        self.assertTrue(view.readonly)
        self.assertFalse(any(view))
