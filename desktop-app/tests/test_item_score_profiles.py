from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from dpslab.addon_live_analysis_transport import LiveAnalysisItem, LiveAnalysisSnapshot, TalentLoadout, parse_live_analysis_export
from dpslab.item_score_profiles import (
    ItemScoreProfileError, ScoreWeights, create_character, effective_weights, remove_builds, rename_profile, store_imported_build,
    load_profiles, profile_details, profile_export, profile_simulation_id, save_profiles, score_replacement, store_simulation_results, store_weight, update_from_export,
    weights_from_simc_run,
)
from dpslab.loadout_recommendation import LoadoutRecommendationError, write_item_score_profiles


def snapshot() -> LiveAnalysisSnapshot:
    item = LiveAnalysisItem(1, 100, "item:1", 16, "slot_16", "equipped", None, (("CritRating", 10),))
    return LiveAnalysisSnapshot(1, 1, 11, 102, "damage", 80, 4, (item,), (), "a" * 64, multi_talent_loadouts=(TalentLoadout(1, "AA", "Eclipse"), TalentLoadout(2, "BB", "ST")))


def weight(source="personalized", build=1) -> ScoreWeights:
    return ScoreWeights(source, 11, 102, build, (("CritRating", 2.0),), "simc-test", "Patchwerk", "b" * 64)


class ItemScoreProfileTests(unittest.TestCase):
    def test_workspace_exports_scores_only_through_the_explicit_choice(self):
        source = (Path(__file__).resolve().parents[1] / "src" / "dpslab" / "loadout_ui.py").read_text(encoding="utf-8")
        automatic = source.split("def _save_character_scores", 1)[1].split("def _export_chosen_scores", 1)[0]
        self.assertNotIn("write_item_score_profiles", automatic)
        self.assertIn("def _export_chosen_scores", source)
        self.assertIn("loadout_score_selection_invalid", (Path(__file__).resolve().parents[1] / "src" / "dpslab" / "loadout_recommendation.py").read_text(encoding="utf-8"))

    def test_round_trip_keeps_two_same_named_characters_separate(self):
        first = update_from_export(create_character("Luna", "A", 11), snapshot())
        second = update_from_export(create_character("Luna", "B", 11), snapshot())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); save_profiles(root, (first, second))
            self.assertEqual((first, second), load_profiles(root))

    def test_profile_alias_is_saved_separately_from_detected_identity(self):
        character = rename_profile(update_from_export(create_character("Luna", "A", 11), snapshot()), "Equilibrio mítico")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); save_profiles(root, (character,))
            restored = load_profiles(root)[0]
        self.assertEqual(("Luna", "A", "Equilibrio mítico"), (restored.name, restored.realm, restored.profile_name))

    def test_export_update_preserves_weight_and_other_spec(self):
        character = store_weight(update_from_export(create_character("Luna", "A", 11), snapshot()), weight())
        previous = character.specs + ((105, ()),)
        updated = update_from_export(character.__class__(character.character_id, character.name, character.realm, character.class_id, previous, character.equipped), snapshot())
        self.assertEqual(weight(), effective_weights(updated, 102, 1))
        self.assertIn(105, dict(updated.specs))

    def test_imported_build_survives_export_update_and_can_be_removed(self):
        character = store_imported_build(update_from_export(create_character("Luna", "A", 11), snapshot()), 102, "M+", "CC")
        updated = update_from_export(character, snapshot())
        imported_id = next(build.build_id for build in dict(updated.specs)[102] if build.name == "M+")
        self.assertLess(imported_id, 0)
        cleared = remove_builds(updated, 102, (imported_id,))
        self.assertNotIn("M+", tuple(build.name for build in dict(cleared.specs)[102]))

    def test_export_update_keeps_more_than_four_real_loadouts(self):
        six = replace(snapshot(), multi_talent_loadouts=tuple(TalentLoadout(index, f"A{index}", f"Build {index}") for index in range(1, 7)))
        character = update_from_export(create_character("Luna", "A", 11), six)
        self.assertEqual(6, len(dict(character.specs)[102]))

    def test_saved_profile_recreates_a_simulation_input_with_its_equipment(self):
        character = store_imported_build(update_from_export(create_character("Luna", "A", 11), snapshot()), 102, "Externa", "CC")
        exported = parse_live_analysis_export(profile_export(character, 102))
        self.assertEqual((80, 4, 1, 2, profile_simulation_id(-1)), (exported.level, exported.race_id, exported.balance_talent_loadouts[0].config_id, exported.balance_talent_loadouts[1].config_id, exported.balance_talent_loadouts[2].config_id))
        self.assertEqual(character.equipped, exported.equipped)

    def test_personalized_then_same_spec_generic_then_unavailable(self):
        character = update_from_export(create_character("Luna", "A", 11), snapshot())
        generic = store_weight(character, weight("generic", 1)); self.assertEqual("generic", effective_weights(generic, 102, 1).source)
        personal = store_weight(generic, weight()); self.assertEqual("personalized", effective_weights(personal, 102, 1).source)
        self.assertIsNone(effective_weights(personal, 105, 1))

    def test_score_replaces_only_matching_slot_and_keeps_dual_slots_explicit(self):
        equipped = (LiveAnalysisItem(1, 1, "item:1", 11, "slot_11", "equipped", None, (("CritRating", 10),)), LiveAnalysisItem(2, 1, "item:2", 12, "slot_12", "equipped", None, (("CritRating", 20),)))
        candidate = (LiveAnalysisItem(3, 1, "item:3", 11, "slot_11", "bag", None, (("CritRating", 15),)),)
        score = score_replacement(weight(), equipped, candidate)
        self.assertEqual((20.0, 30.0, 10.0), (score.equipped, score.candidate, score.delta))
        with self.assertRaisesRegex(ItemScoreProfileError, "duplicate_slot"):
            score_replacement(weight(), equipped, candidate + candidate)

    def test_only_completed_simc_report_produces_weight_record(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary); (run / "simc.json").write_text(json.dumps({"sim": {"players": [{"scale_factors": {"Crit": 1.5}}]}}), encoding="utf-8")
            (run / "run_metadata.json").write_text(json.dumps({"simc_version": "1200"}), encoding="utf-8")
            self.assertEqual((("CritRating", 1.5),), weights_from_simc_run(run, source="generic", class_id=11, specialization_id=102, build_id=1, scenario="Patchwerk", reference_profile="x").values)
            (run / "run_metadata.json").unlink(); self.assertIsNone(weights_from_simc_run(run, source="generic", class_id=11, specialization_id=102, build_id=1, scenario="Patchwerk", reference_profile="x"))

    def test_selected_profiles_are_written_for_addon_with_source(self):
        character = store_weight(update_from_export(create_character("Luna", "A", 11), snapshot()), weight())
        with tempfile.TemporaryDirectory() as temporary:
            addon = Path(temporary) / "DpsLab"; addon.mkdir()
            for name in ("DpsLab.toc", "DpsLab.lua"): (addon / name).write_text("", encoding="utf-8")
            write_item_score_profiles(addon, character, ((102, 1),))
            output = (addon / "DpsLabRealRecommendation.lua").read_text(encoding="utf-8")
            self.assertIn('schema_version = "0.5"', output)
            self.assertIn('source = "personalized"', output)
            self.assertIn("Eclipse", output)
            self.assertIn('character = { name = "Luna", realm = "A", class_id = 11 }', output)

    def test_score_export_requires_a_real_chosen_build(self):
        character = store_weight(update_from_export(create_character("Luna", "A", 11), snapshot()), weight())
        with tempfile.TemporaryDirectory() as temporary:
            addon = Path(temporary) / "DpsLab"; addon.mkdir()
            for name in ("DpsLab.toc", "DpsLab.lua"): (addon / name).write_text("", encoding="utf-8")
            with self.assertRaisesRegex(LoadoutRecommendationError, "selection_invalid"):
                write_item_score_profiles(addon, character, ())

    def test_saved_profile_browses_build_simulations_and_weight_source_after_reload(self):
        character = store_weight(update_from_export(create_character("Luna", "A", 11), snapshot()), weight())
        character = store_simulation_results(character, 102, ((1, 123.0),), (weight(),), ((1, 0.08),), ((1, "run-123"),))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); save_profiles(root, (character,)); restored = load_profiles(root)[0]
            self.assertIn("  Eclipse: 123 DPS · error 0.08%; pesos: personalized", profile_details(restored))
            record = dict(restored.specs)[102][0].simulations[0]
            self.assertEqual((0.08, "run-123"), (record.relative_error_percent, record.run_id))
