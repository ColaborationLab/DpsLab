from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from dpslab.druid_restoration_recommendation import (
    DruidRestorationRecommendationError,
    compare_druid_restoration_runs,
    run_druid_restoration_recommendation,
    write_addon_recommendation,
)
from dpslab.result_models import (
    DpsResult, ExecutionResult, RunDiagnostics, RunIdentification, RunScenario,
    RunSummary, RunVariant, SummaryGeneration,
)


def summary(dps: float) -> RunSummary:
    return RunSummary(
        "0.3", RunIdentification("run", None, None, "Druid", "druid", "restoration", 90),
        RunScenario(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
        RunVariant(None, None, None, None, None, None, None, None, None, None, None),
        DpsResult(dps, None, None, None, None, None, None, None),
        ExecutionResult("completed", None, None, None, 0),
        RunDiagnostics([], False, None, None, True), SummaryGeneration("completed", None),
    )


class DruidRestorationRecommendationTests(unittest.TestCase):
    def test_higher_comparison_is_a_concrete_recommendation(self) -> None:
        result = compare_druid_restoration_runs(summary(100.0), summary(110.0))
        self.assertEqual(result.preferred_loadout, "comparison")
        self.assertIn("segundo loadout", result.message)

    def test_tied_result_makes_no_claim(self) -> None:
        with self.assertRaisesRegex(DruidRestorationRecommendationError, "tied"):
            compare_druid_restoration_runs(summary(100.0), summary(100.0))

    def test_writes_only_the_dedicated_addon_data_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            addon = Path(temporary) / "DpsLab"
            addon.mkdir()
            (addon / "DpsLab.toc").write_text("", encoding="utf-8")
            (addon / "DpsLab.lua").write_text("", encoding="utf-8")
            written = write_addon_recommendation(addon, compare_druid_restoration_runs(summary(100), summary(110)))
            self.assertEqual(written, addon / "DpsLabRealRecommendation.lua")
            self.assertIn('state = "ready"', written.read_text(encoding="utf-8"))

    @patch("dpslab.druid_restoration_recommendation.build_druid_restoration_profiles")
    @patch("dpslab.druid_restoration_recommendation.parse_live_analysis_export")
    def test_flow_runs_twice_then_writes_addon_result(self, parsed, built) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            addon = root / "DpsLab"
            addon.mkdir()
            (addon / "DpsLab.toc").write_text("", encoding="utf-8")
            (addon / "DpsLab.lua").write_text("", encoding="utf-8")
            executable = root / "simc.exe"
            executable.write_text("", encoding="utf-8")
            parsed.return_value = object()
            built.return_value = SimpleNamespace(active_profile='druid="A"\n', comparison_profile='druid="B"\n')
            runs = iter((SimpleNamespace(artifacts=SimpleNamespace(run_dir=root / "a")), SimpleNamespace(artifacts=SimpleNamespace(run_dir=root / "b"))))
            summaries = iter((summary(100.0), summary(110.0)))
            result = run_druid_restoration_recommendation(
                "DPSLAB-LIVE-ANALYSIS-0.1\n{}\n", executable, addon, root=root,
                runner=lambda *_args, **_kwargs: next(runs),
                summary_loader=lambda *_args, **_kwargs: next(summaries),
            )
            self.assertEqual(result.preferred_loadout, "comparison")
            self.assertTrue((addon / "DpsLabRealRecommendation.lua").is_file())
