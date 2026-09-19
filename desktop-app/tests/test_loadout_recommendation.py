from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from dpslab.addon_live_analysis_transport import PREFIX, canonical_live_analysis_bytes
from dpslab.item_score_profiles import ScoreWeights
from dpslab.loadout_recommendation import decode_weight_transfer, encode_weight_transfer, run_loadout_recommendation
from dpslab.result_models import DpsResult, ExecutionResult, RunDiagnostics, RunIdentification, RunScenario, RunSummary, RunVariant, SummaryGeneration


def export_text():
    value = {"schema_version": "0.7", "observation_type": "live_manual_analysis_export", "compatibility": {"wow_product": "retail", "build": 1, "interface_version": 1}, "subject": {"class_id": 1, "specialization_id": 72, "role": "damage", "level": 80, "race_id": 1}, "analysis_context": {"talent_loadouts": [{"config_id": 1, "name": "Furia", "talent_string": "AA"}, {"config_id": 2, "name": "Armas", "talent_string": "BB"}]}, "equipment": {"equipped": [{"item_id": 1, "item_level": 100, "item_link": "item:1", "location": 16, "slot": "slot_16", "source": "equipped", "stats": {}}]}, "safety": {"contains_direct_identifiers": False, "executable": False, "no_automation": True}}
    return PREFIX + canonical_live_analysis_bytes(value).decode()


def summary(value: float):
    return RunSummary("0.3", RunIdentification("run", None, None, "Warrior", "warrior", "fury", 80), RunScenario(*([None] * 18)), RunVariant(*([None] * 11)), DpsResult(value, *([None] * 7)), ExecutionResult("completed", None, None, None, 0), RunDiagnostics([], False, None, None, True), SummaryGeneration("completed", None))


class LoadoutRecommendationTests(unittest.TestCase):
    def test_manual_weight_transfer_round_trip(self):
        weight = ScoreWeights("personalized", 1, 72, 5, (("CritRating", 1.25), ("HasteRating", 2.5)), "simc", "Patchwerk", "a" * 64)
        name, imported = decode_weight_transfer(encode_weight_transfer(weight, "Furia rápida"), class_id=1, build_id=9)
        self.assertEqual("Furia rápida", name)
        self.assertEqual(("manual", 1, 72, 9, weight.values), (imported.source, imported.class_id, imported.specialization_id, imported.build_id, imported.values))

    def test_two_non_druid_loadouts_use_one_metric_and_write_context(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); addon = root / "DpsLab"; addon.mkdir()
            for name in ("DpsLab.toc", "DpsLab.lua"): (addon / name).write_text("", encoding="utf-8")
            executable = root / "simc.exe"; executable.write_bytes(b"synthetic")
            runs = iter((SimpleNamespace(artifacts=SimpleNamespace(run_dir=root / "one")), SimpleNamespace(artifacts=SimpleNamespace(run_dir=root / "two"))))
            configs = []
            def runner(_profile, config, **_kwargs):
                configs.append(config); return next(runs)
            result = run_loadout_recommendation(export_text(), executable, addon, root=root, runner=runner, summary_loader=lambda directory, **_kwargs: summary(100 if directory.name == "one" else 120))
            self.assertEqual((1, 72, "damage", "DPS"), (result.class_id, result.specialization_id, result.role, result.metric))
            self.assertTrue(all(config.target_error == 0.1 and config.iterations == 1_000_000 and config.runs_dir == root / "weight-runs" for config in configs))
            self.assertEqual(((1, "one"), (2, "two")), result.run_ids)
            rendered = (addon / "DpsLabRealRecommendation.lua").read_text(encoding="utf-8")
            self.assertIn('schema_version = "0.3"', rendered)
            self.assertIn("specialization_id = 72", rendered)
