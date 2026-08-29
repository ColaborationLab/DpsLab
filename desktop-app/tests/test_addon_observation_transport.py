import copy
import json
import unittest

from dpslab.addon_observation_transport import (
    AddonObservationTransportError,
    MAX_PAYLOAD_BYTES,
    canonical_observation_bytes,
    parse_synthetic_saved_variable,
)


def document():
    value = {
        "schema_version": "0.1",
        "identity": {"observation_id": "synthetic.observation.001", "captured_at": "2026-08-29T00:00:00Z"},
        "producer": {"producer_id": "dpslab.addon.synthetic", "producer_version": "0.1.0"},
        "compatibility": {"wow_product": "retail", "build": 120000, "interface_version": 120000},
        "subject": {"synthetic": True, "class_token": "synthetic_class", "specialization_token": "synthetic_specialization", "role": "damage"},
        "observation": {"state": "synthetic_fixture", "sample_window_seconds": 0, "event_count": 0, "byte_count": 1, "signals": {"damage_events": 0, "incoming_damage_events": 0, "healing_events": 0}},
        "safety": {"synthetic": True, "contains_personal_data": False, "executable": False, "actionable": False, "no_automation": True},
    }
    for _ in range(4):
        value["observation"]["byte_count"] = len(canonical_observation_bytes(value))
    return value


def transport(value=None, *, settle_byte_count=True):
    value = value or document()
    if settle_byte_count:
        for _ in range(4):
            value["observation"]["byte_count"] = len(canonical_observation_bytes(value))
    payload = canonical_observation_bytes(value)
    return b'DpsLabObservationExport = "' + payload.hex().encode("ascii") + b'"\n'


class AddonObservationTransportTests(unittest.TestCase):
    def assert_invalid(self, raw, reason):
        with self.assertRaisesRegex(AddonObservationTransportError, reason):
            parse_synthetic_saved_variable(raw)

    def test_valid_transport_returns_immutable_summary(self):
        result = parse_synthetic_saved_variable(transport())
        self.assertEqual(("synthetic.observation.001", "damage", 0, 0, 0), (result.observation_id, result.role, result.damage_events, result.incoming_damage_events, result.healing_events))

    def test_assignment_grammar_rejects_code_extra_variables_and_uppercase_hex(self):
        valid = transport()
        self.assert_invalid(b"loadstring('x')\n" + valid, "assignment_invalid")
        self.assert_invalid(valid + b"Other = 1\n", "assignment_invalid")
        self.assert_invalid(valid.upper(), "assignment_invalid")

    def test_transport_requires_bytes_and_rejects_excess_before_decode(self):
        self.assert_invalid("text", "bytes_required")
        self.assert_invalid(b"x" * (2 * MAX_PAYLOAD_BYTES + 65), "transport_too_large")

    def test_non_utf8_invalid_json_and_duplicate_keys_fail_closed(self):
        self.assert_invalid(b'DpsLabObservationExport = "ff"\n', "json_invalid")
        raw = b'{"schema_version":"0.1","schema_version":"0.1"}\n'
        self.assert_invalid(b'DpsLabObservationExport = "' + raw.hex().encode() + b'"\n', "duplicate_json_key")

    def test_noncanonical_json_is_rejected(self):
        value = document()
        for _ in range(4):
            raw = (json.dumps(value, indent=2) + "\n").encode()
            value["observation"]["byte_count"] = len(raw)
        raw = (json.dumps(value, indent=2) + "\n").encode()
        self.assert_invalid(b'DpsLabObservationExport = "' + raw.hex().encode() + b'"\n', "json_noncanonical")

    def test_unknown_fields_and_non_synthetic_subject_are_rejected(self):
        value = document(); value["unknown"] = True
        self.assert_invalid(transport(value), "root_fields_invalid")
        value = document(); value["subject"]["synthetic"] = False
        self.assert_invalid(transport(value), "subject_not_synthetic")

    def test_boolean_integer_and_invalid_role_are_rejected(self):
        value = document(); value["compatibility"]["build"] = True
        self.assert_invalid(transport(value), "build_invalid")
        value = document(); value["subject"]["role"] = "support"
        self.assert_invalid(transport(value), "role_invalid")

    def test_signal_total_and_declared_byte_count_are_bound(self):
        value = document(); value["observation"]["signals"]["damage_events"] = 1
        self.assert_invalid(transport(value), "event_count_mismatch")
        value = document(); value["observation"]["byte_count"] = 1
        self.assert_invalid(transport(value, settle_byte_count=False), "byte_count_mismatch")

    def test_unsafe_state_is_rejected_without_partial_result(self):
        for field, unsafe in (("contains_personal_data", True), ("executable", True), ("actionable", True), ("no_automation", False)):
            value = document(); value["safety"][field] = unsafe
            self.assert_invalid(transport(value), "safety_invalid")

    def test_parser_source_contains_no_execution_or_filesystem_surface(self):
        import inspect
        import dpslab.addon_observation_transport as module
        source = inspect.getsource(module).lower()
        for forbidden in ("eval(", "exec(", "subprocess", "open(", "read_text", "read_bytes", "pathlib", "socket", "http"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
