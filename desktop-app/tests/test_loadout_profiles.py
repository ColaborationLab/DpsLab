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

    def test_each_registered_specialization_builds_a_profile_with_its_role(self):
        for capability in CAPABILITIES:
            with self.subTest(class_id=capability.class_id, specialization_id=capability.specialization_id):
                profile = build_loadout_profiles(snapshot(capability.class_id, capability.specialization_id, capability.role)).loadouts[0].profile
                role = {"damage": "dps", "tank": "tank", "healer": "heal"}[capability.role]
                self.assertIn(f'{capability.class_token}="DpsLab_{capability.specialization_token}"', profile)
                self.assertIn(f"spec={capability.specialization_token}", profile)
                self.assertIn(f"role={role}", profile)
                self.assertIn("main_hand=,id=1,ilevel=100", profile)

    def test_simc_role_matches_the_exported_role(self):
        self.assertIn("role=tank", build_loadout_profiles(snapshot(1, 73, "tank"), (1,)).loadouts[0].profile)
        self.assertIn("role=heal", build_loadout_profiles(snapshot(5, 257, "healer"), (1,)).loadouts[0].profile)

    def test_retail_item_link_keeps_enchant_gems_and_bonus_ids(self):
        value = snapshot()
        item = value.equipped[0]
        from dataclasses import replace
        value = replace(value, equipped=(replace(item, item_link="|Hitem:277802:6241:10:20::::90:250::36:2:12827:6652:1:28:5381:::::|h[Test]|h"),))
        profile = build_loadout_profiles(value, (1,)).loadouts[0].profile
        self.assertIn("enchant_id=6241", profile)
        self.assertIn("gem_id=10/20", profile)
        self.assertIn("bonus_id=12827/6652", profile)

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
