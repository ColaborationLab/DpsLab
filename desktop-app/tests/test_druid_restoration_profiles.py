import unittest

from dpslab.addon_live_analysis_transport import (
    PREFIX,
    canonical_live_analysis_bytes,
    parse_live_analysis_export,
)
from dpslab.druid_restoration_profiles import (
    DruidRestorationProfileError,
    build_druid_restoration_profiles,
    profile_sha256,
)


def export_document():
    return {
        "schema_version": "0.4",
        "observation_type": "live_manual_analysis_export",
        "compatibility": {"wow_product": "retail", "build": 69587, "interface_version": 120100},
        "subject": {"class_id": 11, "specialization_id": 105, "role": "healer", "level": 90, "race_id": 4},
        "analysis_context": {"talent_loadouts": {
            "active": {"config_id": 1, "talent_string": "ABCD"},
            "comparison": {"config_id": 2, "talent_string": "EFGH"},
        }},
        "equipment": {"equipped": [
            {"item_id": 100, "item_level": 250, "item_link": "item:100", "location": 1, "slot": "slot_1", "source": "equipped"},
            {"item_id": 200, "item_level": 260, "item_link": "item:200", "location": 16, "slot": "slot_16", "source": "equipped"},
        ]},
        "safety": {"contains_direct_identifiers": False, "executable": False, "no_automation": True},
    }


def snapshot(value=None):
    document = value or export_document()
    return parse_live_analysis_export(PREFIX + canonical_live_analysis_bytes(document).decode())


class DruidRestorationProfileTests(unittest.TestCase):
    def test_real_loadouts_become_two_profiles_with_shared_equipment(self):
        pair = build_druid_restoration_profiles(snapshot())
        self.assertIn("spec=restoration", pair.active_profile)
        self.assertIn("talents=ABCD", pair.active_profile)
        self.assertIn("talents=EFGH", pair.comparison_profile)
        self.assertIn("head=,id=100,ilevel=250", pair.active_profile)
        self.assertIn("main_hand=,id=200,ilevel=260", pair.comparison_profile)
        self.assertNotEqual(profile_sha256(pair.active_profile), profile_sha256(pair.comparison_profile))

    def test_other_specialization_is_not_silently_mapped(self):
        value = export_document()
        value["subject"]["specialization_id"] = 102
        with self.assertRaisesRegex(DruidRestorationProfileError, "restoration_required"):
            build_druid_restoration_profiles(snapshot(value))

    def test_unsupported_race_is_rejected(self):
        value = export_document()
        value["subject"]["race_id"] = 1
        with self.assertRaisesRegex(DruidRestorationProfileError, "race_unavailable"):
            build_druid_restoration_profiles(snapshot(value))
