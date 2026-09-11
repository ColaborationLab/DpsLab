from __future__ import annotations

import unittest

from dpslab.addon_live_analysis_transport import PREFIX, canonical_live_analysis_bytes, parse_live_analysis_export
from dpslab.loadout_capabilities import CAPABILITIES, capability_for
from dpslab.loadout_profiles import LoadoutProfileError, build_loadout_profiles


def snapshot(class_id=8, specialization_id=63, role="damage", race_id=1):
    document = {"schema_version": "0.7", "observation_type": "live_manual_analysis_export", "compatibility": {"wow_product": "retail", "build": 1, "interface_version": 1}, "subject": {"class_id": class_id, "specialization_id": specialization_id, "role": role, "level": 80, "race_id": race_id}, "analysis_context": {"talent_loadouts": [{"config_id": 1, "name": "Fuego", "talent_string": "AA"}, {"config_id": 2, "name": "Hielo", "talent_string": "BB"}]}, "equipment": {"equipped": [{"item_id": 1, "item_level": 100, "item_link": "item:1", "location": 16, "slot": "slot_16", "source": "equipped", "stats": {}}]}, "safety": {"contains_direct_identifiers": False, "executable": False, "no_automation": True}}
    return parse_live_analysis_export(PREFIX + canonical_live_analysis_bytes(document).decode())


class LoadoutProfileTests(unittest.TestCase):
    def test_catalog_has_unique_class_spec_entries(self):
        self.assertEqual(39, len(CAPABILITIES))
        self.assertEqual(39, len({(item.class_id, item.specialization_id) for item in CAPABILITIES}))
        self.assertIsNotNone(capability_for(11, 102, "damage"))
        self.assertEqual("deathknight", capability_for(6, 251, "damage").class_token)
        self.assertEqual("demonhunter", capability_for(12, 577, "damage").class_token)
        self.assertIsNone(capability_for(11, 102, "healer"))

    def test_any_registered_class_builds_same_spec_profiles(self):
        profiles = build_loadout_profiles(snapshot())
        self.assertIn('mage="DpsLab_fire"', profiles.loadouts[0].profile)
        self.assertIn("spec=fire", profiles.loadouts[0].profile)
        self.assertIn("main_hand=,id=1,ilevel=100", profiles.loadouts[0].profile)

    def test_one_exported_loadout_is_a_valid_individual_simulation(self):
        document = {"schema_version": "0.7", "observation_type": "live_manual_analysis_export", "compatibility": {"wow_product": "retail", "build": 1, "interface_version": 1}, "subject": {"class_id": 8, "specialization_id": 63, "role": "damage", "level": 80, "race_id": 1}, "analysis_context": {"talent_loadouts": [{"config_id": 1, "name": "Fuego", "talent_string": "AA"}]}, "equipment": {"equipped": [{"item_id": 1, "item_level": 100, "item_link": "item:1", "location": 16, "slot": "slot_16", "source": "equipped", "stats": {}}]}, "safety": {"contains_direct_identifiers": False, "executable": False, "no_automation": True}}
        profiles = build_loadout_profiles(parse_live_analysis_export(PREFIX + canonical_live_analysis_bytes(document).decode()))
        self.assertEqual(("Fuego",), tuple(item.name for item in profiles.loadouts))

    def test_named_manual_import_is_retained_and_limited_with_selected_loadouts(self):
        profiles = build_loadout_profiles(snapshot(), (1, 2), (("Manual ágil", "CC"),))
        self.assertEqual(("Fuego", "Hielo", "Manual ágil"), tuple(item.name for item in profiles.loadouts))
        with self.assertRaisesRegex(LoadoutProfileError, "selection_invalid"):
            build_loadout_profiles(snapshot(), (1, 2), (("uno", "CC"), ("dos", "DD"), ("tres", "EE")))

    def test_unknown_api_specialization_fails_closed(self):
        with self.assertRaisesRegex(LoadoutProfileError, "specialization_unavailable"):
            build_loadout_profiles(snapshot(12, 999, "damage"))
