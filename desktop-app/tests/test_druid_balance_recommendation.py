import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from dpslab.druid_balance_recommendation import run_druid_balance_recommendation
from dpslab.addon_live_analysis_transport import PREFIX, canonical_live_analysis_bytes
from dpslab.__main__ import _arguments
from dpslab.result_models import DpsResult, ExecutionResult, RunDiagnostics, RunIdentification, RunScenario, RunSummary, RunVariant, SummaryGeneration


def summary(dps):
    return RunSummary("0.3", RunIdentification("run", None, None, "Druid", "druid", "balance", 90), RunScenario(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None), RunVariant(None, None, None, None, None, None, None, None, None, None, None), DpsResult(dps, None, None, None, None, None, None, None), ExecutionResult("completed", None, None, None, 0), RunDiagnostics([], False, None, None, True), SummaryGeneration("completed", None))


def export_text():
    value = {"schema_version": "0.4", "observation_type": "live_manual_analysis_export", "compatibility": {"wow_product": "retail", "build": 69587, "interface_version": 120100}, "subject": {"class_id": 11, "specialization_id": 102, "role": "damage", "level": 90, "race_id": 4}, "analysis_context": {"talent_loadouts": {"active": {"config_id": 1, "talent_string": "ABCD"}, "comparison": {"config_id": 2, "talent_string": "EFGH"}}}, "equipment": {"equipped": [{"item_id": 100, "item_level": 250, "item_link": "item:100", "location": 1, "slot": "slot_1", "source": "equipped"}]}, "safety": {"contains_direct_identifiers": False, "executable": False, "no_automation": True}}
    return PREFIX + canonical_live_analysis_bytes(value).decode()


def export_text_three_loadouts():
    value = {"schema_version": "0.7", "observation_type": "live_manual_analysis_export", "compatibility": {"wow_product": "retail", "build": 69587, "interface_version": 120100}, "subject": {"class_id": 11, "specialization_id": 102, "role": "damage", "level": 90, "race_id": 4}, "analysis_context": {"talent_loadouts": [{"config_id": 1, "name": "Lunar", "talent_string": "ABCD"}, {"config_id": 2, "name": "Solar", "talent_string": "EFGH"}, {"config_id": 3, "name": "Eclipse", "talent_string": "IJKL"}]}, "equipment": {"equipped": [{"item_id": 100, "item_level": 250, "item_link": "item:100", "location": 1, "slot": "slot_1", "source": "equipped", "stats": {"Intellect": 100}}]}, "safety": {"contains_direct_identifiers": False, "executable": False, "no_automation": True}}
    return PREFIX + canonical_live_analysis_bytes(value).decode()


class DruidBalanceRecommendationTests(unittest.TestCase):
    def test_balance_command_opens_the_balance_workspace(self):
        self.assertEqual("balance", _arguments(["balance"]).command)

    def test_flow_writes_the_addon_result(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); addon = root / "DpsLab"; addon.mkdir()
            for name in ("DpsLab.toc", "DpsLab.lua", "simc.exe"):
                (addon / name if name != "simc.exe" else root / name).write_text("", encoding="utf-8")
            runs = iter((SimpleNamespace(artifacts=SimpleNamespace(run_dir=root / "a")), SimpleNamespace(artifacts=SimpleNamespace(run_dir=root / "b"))))
            result = run_druid_balance_recommendation(export_text(), root / "simc.exe", addon, root=root, runner=lambda *_a, **_k: next(runs), summary_loader=lambda run, **_k: summary(100 if run.name == "a" else 110))
            self.assertEqual(2, result.preferred_loadout)
            self.assertIn("Loadout 2", (addon / "DpsLabRealRecommendation.lua").read_text(encoding="utf-8"))

    def test_three_selected_loadouts_run_with_the_same_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); addon = root / "DpsLab"; addon.mkdir()
            for name in ("DpsLab.toc", "DpsLab.lua", "simc.exe"):
                (addon / name if name != "simc.exe" else root / name).write_text("", encoding="utf-8")
            runs = iter(tuple(SimpleNamespace(artifacts=SimpleNamespace(run_dir=root / name)) for name in ("a", "b", "c")))
            result = run_druid_balance_recommendation(export_text_three_loadouts(), root / "simc.exe", addon, root=root, selected_config_ids=(1, 2, 3), runner=lambda *_a, **_k: next(runs), summary_loader=lambda run, **_k: summary({"a": 100, "b": 110, "c": 120}[run.name]))
            self.assertEqual(((1, 100.0), (2, 110.0), (3, 120.0)), result.loadouts)
            self.assertEqual(3, result.preferred_loadout)
            self.assertIn("Usa Eclipse", (addon / "DpsLabRealRecommendation.lua").read_text(encoding="utf-8"))
