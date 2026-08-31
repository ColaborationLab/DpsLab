from dataclasses import FrozenInstanceError
import json
import unittest

from dpslab.addon_specialization_registry_transport import (
    SpecializationRegistryTransportError,
    canonical_specialization_registry_bytes,
    parse_specialization_registry_saved_variable,
)


def document():
    return {
        "capture": {"captured_at": 1_788_079_200, "mode": "manual_command"},
        "compatibility": {
            "build": 120500,
            "interface_version": 120500,
            "wow_product": "retail",
        },
        "observation_type": "class_specialization_registry_snapshot",
        "safety": {
            "actionable": False,
            "contains_character_data": True,
            "contains_direct_identifiers": False,
            "executable": False,
            "no_automation": True,
        },
        "schema_version": "0.1",
        "specializations": [
            {"role": "damage", "specialization_id": 81001},
            {"role": "damage", "specialization_id": 81002},
            {"role": "tank", "specialization_id": 81003},
            {"role": "healer", "specialization_id": 81004},
        ],
        "subject": {"class_id": 801},
    }


def transport(value=None):
    value = document() if value is None else value
    return (
        b'DpsLabObservationExport = "'
        + canonical_specialization_registry_bytes(value).hex().encode("ascii")
        + b'"\n'
    )


class SpecializationRegistryTransportTests(unittest.TestCase):
    def assert_invalid(self, raw, reason):
        with self.assertRaisesRegex(SpecializationRegistryTransportError, f"^{reason}$"):
            parse_specialization_registry_saved_variable(raw)

    def test_valid_registry_is_immutable_closed_and_nonactionable(self):
        value = parse_specialization_registry_saved_variable(transport())
        self.assertEqual((120500, 120500, 801, 1_788_079_200), (
            value.build, value.interface_version, value.class_id, value.captured_at
        ))
        self.assertEqual(
            ((81001, "damage"), (81002, "damage"), (81003, "tank"), (81004, "healer")),
            tuple((item.specialization_id, item.role) for item in value.specializations),
        )
        with self.assertRaises(FrozenInstanceError):
            value.class_id = 1

    def test_exact_four_unique_entries_and_role_shape_are_required(self):
        for mutation, reason in (
            ("short", "specialization_registry_shape_invalid"),
            ("duplicate", "specialization_registry_specialization_duplicate"),
            ("role", "specialization_registry_role_shape_invalid"),
            ("unknown", "specialization_registry_role_invalid"),
        ):
            with self.subTest(mutation=mutation):
                value = document()
                if mutation == "short":
                    value["specializations"].pop()
                elif mutation == "duplicate":
                    value["specializations"][1]["specialization_id"] = 81001
                elif mutation == "role":
                    value["specializations"][1]["role"] = "tank"
                else:
                    value["specializations"][0]["role"] = "support"
                self.assert_invalid(transport(value), reason)

    def test_unknown_missing_and_entry_fields_are_rejected(self):
        for mutation, reason in (
            ("root_unknown", "specialization_registry_root_fields_invalid"),
            ("root_missing", "specialization_registry_root_fields_invalid"),
            ("entry_unknown", "specialization_registry_entry_fields_invalid"),
        ):
            with self.subTest(mutation=mutation):
                value = document()
                if mutation == "root_unknown":
                    value["extra"] = 1
                elif mutation == "root_missing":
                    del value["capture"]
                else:
                    value["specializations"][0]["name"] = "forbidden"
                self.assert_invalid(transport(value), reason)

    def test_schema_product_type_capture_and_safety_are_exact(self):
        cases = (
            ("schema_version", None, "0.2", "specialization_registry_schema_incompatible"),
            ("observation_type", None, "future", "specialization_registry_type_unsupported"),
            ("compatibility", "wow_product", "classic", "specialization_registry_product_unsupported"),
            ("capture", "mode", "automatic", "specialization_registry_capture_mode_invalid"),
            ("safety", "actionable", True, "specialization_registry_safety_invalid"),
        )
        for section, field, invalid, reason in cases:
            with self.subTest(reason=reason):
                value = document()
                if field is None:
                    value[section] = invalid
                else:
                    value[section][field] = invalid
                self.assert_invalid(transport(value), reason)

    def test_booleans_are_not_integers_and_bounds_fail_closed(self):
        for section, field, invalid, reason in (
            ("compatibility", "build", True, "specialization_registry_build_invalid"),
            ("subject", "class_id", 0, "specialization_registry_class_id_invalid"),
            ("capture", "captured_at", True, "specialization_registry_captured_at_invalid"),
        ):
            with self.subTest(field=field):
                value = document()
                value[section][field] = invalid
                self.assert_invalid(transport(value), reason)
        value = document()
        value["specializations"][0]["specialization_id"] = 100001
        self.assert_invalid(transport(value), "specialization_registry_specialization_id_invalid")

    def test_transport_is_exact_lowercase_even_hex_and_bounded(self):
        valid = transport()
        self.assert_invalid(valid.upper(), "specialization_registry_assignment_invalid")
        self.assert_invalid(b'DpsLabObservationExport = "0"\n', "specialization_registry_assignment_invalid")
        self.assert_invalid(
            b'DpsLabObservationExport = "' + b"00" * 5000 + b'"\n',
            "specialization_registry_transport_too_large",
        )

    def test_duplicate_keys_noncanonical_and_invalid_json_are_rejected(self):
        canonical = canonical_specialization_registry_bytes(document())
        duplicate = canonical.replace(b'{"capture":', b'{"schema_version":"0.1","capture":', 1)
        self.assert_invalid(
            b'DpsLabObservationExport = "' + duplicate.hex().encode() + b'"\n',
            "specialization_registry_duplicate_json_key",
        )
        noncanonical = json.dumps(document(), indent=2).encode() + b"\n"
        self.assert_invalid(
            b'DpsLabObservationExport = "' + noncanonical.hex().encode() + b'"\n',
            "specialization_registry_json_noncanonical",
        )
        self.assert_invalid(b'DpsLabObservationExport = "ff"\n', "specialization_registry_json_invalid")

    def test_names_and_direct_identifiers_have_no_accepted_field(self):
        value = document()
        value["subject"]["character_name"] = "forbidden"
        self.assert_invalid(transport(value), "specialization_registry_subject_fields_invalid")


if __name__ == "__main__":
    unittest.main()
