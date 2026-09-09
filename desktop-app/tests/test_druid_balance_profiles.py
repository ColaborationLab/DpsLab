import unittest

from dpslab.addon_live_analysis_transport import PREFIX, canonical_live_analysis_bytes, parse_live_analysis_export
from dpslab.druid_balance_profiles import DruidBalanceProfileError, build_druid_balance_profiles


def snapshot(specification_id=102, role="damage"):
    document = {
        "schema_version": "0.4", "observation_type": "live_manual_analysis_export",
        "compatibility": {"wow_product": "retail", "build": 69587, "interface_version": 120100},
        "subject": {"class_id": 11, "specialization_id": specification_id, "role": role, "level": 90, "race_id": 4},
        "analysis_context": {"talent_loadouts": {
            "active": {"config_id": 1, "talent_string": "ABCD"},
            "comparison": {"config_id": 2, "talent_string": "EFGH"},
        }},
        "equipment": {"equipped": [{"item_id": 100, "item_level": 250, "item_link": "item:100", "location": 1, "slot": "slot_1", "source": "equipped"}]},
        "safety": {"contains_direct_identifiers": False, "executable": False, "no_automation": True},
    }
    return parse_live_analysis_export(PREFIX + canonical_live_analysis_bytes(document).decode())


class DruidBalanceProfileTests(unittest.TestCase):
    def test_real_balance_loadouts_become_two_balance_profiles(self):
        pair = build_druid_balance_profiles(snapshot())
        self.assertIn("spec=balance", pair.active_profile)
        self.assertIn("talents=ABCD", pair.active_profile)
        self.assertIn("talents=EFGH", pair.comparison_profile)

    def test_other_specialization_is_rejected(self):
        with self.assertRaisesRegex(DruidBalanceProfileError, "balance_required"):
            build_druid_balance_profiles(snapshot(105, "healer"))
