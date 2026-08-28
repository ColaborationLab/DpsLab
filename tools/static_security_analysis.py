"""Fail-closed sanitizer for static-analysis and secret-scan evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class SecurityAnalysisError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SecurityAnalysisError("invalid_scanner_json") from exc
    if not isinstance(value, dict):
        raise SecurityAnalysisError("invalid_scanner_json")
    return value


def _count(value: Any, key: str) -> int:
    if not isinstance(value, list):
        raise SecurityAnalysisError("invalid_scanner_schema")
    if any(not isinstance(item, dict) for item in value):
        raise SecurityAnalysisError("invalid_scanner_schema")
    return len(value)


def summarize(bandit: dict[str, Any], gitleaks: list[dict[str, Any]]) -> dict[str, Any]:
    if set(bandit) != {"errors", "generated_at", "metrics", "results"}:
        raise SecurityAnalysisError("invalid_bandit_schema")
    if not isinstance(gitleaks, list):
        raise SecurityAnalysisError("invalid_gitleaks_schema")
    high = sum(1 for item in bandit["results"] if item.get("issue_severity") == "HIGH")
    return {
        "schema_version": "0.1",
        "status": "clean" if high == 0 and not gitleaks else "findings",
        "bandit": {"high_severity_count": high, "result_count": _count(bandit["results"], "results")},
        "gitleaks": {"finding_count": _count(gitleaks, "gitleaks")},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bandit", type=Path, required=True)
    parser.add_argument("--gitleaks", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        secret = json.loads(args.gitleaks.read_text(encoding="utf-8"))
        summary = summarize(_load(args.bandit), secret)
        args.output.write_text(json.dumps(summary, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError, SecurityAnalysisError) as exc:
        raise SystemExit(f"static_security_analysis_failed:{exc}") from exc
    return 0 if summary["status"] == "clean" else 1


if __name__ == "__main__":
    raise SystemExit(main())
