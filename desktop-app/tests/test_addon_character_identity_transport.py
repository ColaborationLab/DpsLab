import copy
from dataclasses import FrozenInstanceError
import json
import unittest

from dpslab.addon_character_identity_transport import (
    CharacterIdentityTransportError,
    canonical_character_identity_bytes,
    parse_character_identity_saved_variable,
)


def document():
    return {
        "capture": {"captured_at": 1_788_079_200, "mode": "manual_command"},
        "compatibility": {"build": 120500, "interface_version": 120500, "wow_product": "retail"},
        "observation_type": "character_identity_snapshot",
        "safety": {
            "actionable": False,
            "contains_character_data": True,
            "contains_direct_identifiers": False,
            "executable": False,
            "no_automation": True,
        },
        "schema_version": "0.1",
        "subject": {"class_id": 2, "level": 90, "race_id": 1, "role": "damage", "specialization_id": 70},
    }


def transport(value):
    return b'DpsLabObservationExport = "' + canonical_character_identity_bytes(value).hex().encode("ascii") + b'"\n'


class CharacterIdentityTransportTests(unittest.TestCase):
    def assert_invalid(self, raw, reason):
        with self.assertRaisesRegex(CharacterIdentityTransportError, f"^{reason}$"):
            parse_character_identity_saved_variable(raw)

    def test_valid_snapshot_is_immutable_and_contains_only_closed_values(self):
        value = parse_character_identity_saved_variable(transport(document()))
        self.assertEqual((120500, 120500, 2, 70, "damage", 90, 1, 1_788_079_200), tuple(value.__dict__.values()))
        with self.assertRaises(FrozenInstanceError):
            value.level = 91

    def test_all_three_normalized_roles_are_supported(self):
        for role in ("damage", "tank", "healer"):
            with self.subTest(role=role):
                value = document(); value["subject"]["role"] = role
                self.assertEqual(role, parse_character_identity_saved_variable(transport(value)).role)

    def test_unknown_missing_and_direct_identifier_fields_are_rejected(self):
        for mutation in ("unknown", "missing", "direct"):
            with self.subTest(mutation=mutation):
                value = document()
                if mutation == "unknown": value["extra"] = 1
                elif mutation == "missing": del value["capture"]
                else: value["subject"]["character_name"] = "forbidden"
                self.assert_invalid(transport(value), "character_identity_root_fields_invalid" if mutation != "direct" else "character_identity_subject_fields_invalid")

    def test_booleans_are_not_integers(self):
        for section, field in (("compatibility", "build"), ("subject", "class_id"), ("capture", "captured_at")):
            with self.subTest(field=field):
                value = document(); value[section][field] = True
                self.assert_invalid(transport(value), f"character_identity_{field}_invalid")

    def test_integer_bounds_fail_closed(self):
        cases = (("compatibility", "build", 0), ("compatibility", "interface_version", 10_000_000), ("subject", "class_id", 0), ("subject", "specialization_id", 100_001), ("subject", "level", 0), ("subject", "race_id", 1001), ("capture", "captured_at", 0))
        for section, field, invalid in cases:
            with self.subTest(field=field):
                value = document(); value[section][field] = invalid
                self.assert_invalid(transport(value), f"character_identity_{field}_invalid")

    def test_schema_type_product_role_mode_and_safety_are_exact(self):
        cases = (
            ("schema_version", None, "0.2", "character_identity_schema_incompatible"),
            ("observation_type", None, "synthetic_observation", "character_identity_type_unsupported"),
            ("compatibility", "wow_product", "classic", "character_identity_product_unsupported"),
            ("subject", "role", "support", "character_identity_role_invalid"),
            ("capture", "mode", "automatic", "character_identity_capture_mode_invalid"),
            ("safety", "actionable", True, "character_identity_safety_invalid"),
        )
        for section, field, invalid, reason in cases:
            with self.subTest(reason=reason):
                value = document()
                if field is None: value[section] = invalid
                else: value[section][field] = invalid
                self.assert_invalid(transport(value), reason)

    def test_synthetic_schema_is_not_reinterpreted(self):
        value = {"schema_version": "0.1", "observation_type": "synthetic", "compatibility": {}, "subject": {}, "capture": {}, "safety": {}}
        self.assert_invalid(transport(value), "character_identity_type_unsupported")

    def test_duplicate_keys_noncanonical_json_and_nonfinite_numbers_are_rejected(self):
        canonical = canonical_character_identity_bytes(document())
        duplicate = canonical.replace(b'{"capture":', b'{"schema_version":"0.1","capture":', 1)
        self.assert_invalid(b'DpsLabObservationExport = "' + duplicate.hex().encode() + b'"\n', "character_identity_duplicate_json_key")
        noncanonical = json.dumps(document(), indent=2).encode() + b"\n"
        self.assert_invalid(b'DpsLabObservationExport = "' + noncanonical.hex().encode() + b'"\n', "character_identity_json_noncanonical")
        nonfinite = canonical.replace(b'"captured_at":1788079200', b'"captured_at":NaN')
        self.assert_invalid(b'DpsLabObservationExport = "' + nonfinite.hex().encode() + b'"\n', "character_identity_nonfinite_number")

    def test_transport_is_exact_lowercase_even_hex_and_bounded(self):
        valid = transport(document())
        self.assert_invalid(valid.upper(), "character_identity_assignment_invalid")
        self.assert_invalid(b'DpsLabObservationExport = "0"\n', "character_identity_assignment_invalid")
        self.assert_invalid(b'prefix' + valid, "character_identity_assignment_invalid")
        self.assert_invalid(b'DpsLabObservationExport = "' + b"00" * 5000 + b'"\n', "character_identity_transport_too_large")

    def test_non_bytes_invalid_utf8_json_and_scalar_roots_are_rejected(self):
        self.assert_invalid("text", "character_identity_transport_bytes_required")
        self.assert_invalid(b'DpsLabObservationExport = "ff"\n', "character_identity_json_invalid")
        raw = b"not-json\n"
        self.assert_invalid(b'DpsLabObservationExport = "' + raw.hex().encode() + b'"\n', "character_identity_json_invalid")
        raw = b"[]\n"
        self.assert_invalid(b'DpsLabObservationExport = "' + raw.hex().encode() + b'"\n', "character_identity_root_invalid")


if __name__ == "__main__":
    unittest.main()
