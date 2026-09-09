"""Run one real Balance comparison and write its bounded addon result."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from .druid_balance_profiles import build_druid_balance_profiles
from .druid_restoration_recommendation import (
    DruidRestorationRecommendation,
    DruidRestorationRecommendationError,
    Runner,
    SummaryLoader,
    run_druid_recommendation,
)

DruidBalanceRecommendation = DruidRestorationRecommendation
DruidBalanceRecommendationError = DruidRestorationRecommendationError


def run_druid_balance_recommendation(
    export_text: str,
    simc_exe: Path,
    addon_directory: Path,
    *,
    root: Path,
    runner: Runner | Callable = None,
    summary_loader: SummaryLoader | Callable = None,
) -> DruidBalanceRecommendation:
    options = {"root": root, "profile_builder": build_druid_balance_profiles}
    if runner is not None:
        options["runner"] = runner
    if summary_loader is not None:
        options["summary_loader"] = summary_loader
    return run_druid_recommendation(export_text, simc_exe, addon_directory, **options)
