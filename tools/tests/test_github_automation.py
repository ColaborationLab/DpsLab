"""Synthetic contract tests for GitHub Automation 0.1."""

from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "dpslab-ci.yml"
NEXT_TASK = ROOT / "docs" / "NEXT_TASK.md"
DOCUMENTATION = ROOT / "docs" / "GITHUB_AUTOMATION.md"
GITATTRIBUTES = ROOT / ".gitattributes"

CANONICAL_LF_PATHS = (
    ".gitattributes",
    "profiles/flasil.simc",
    "variants/flasil_soul_shards_0_v1.toml",
    "scenarios/st_lightmovement_300s_v1.toml",
    "comparisons/flasil_neck_50228_vs_249368_v1.toml",
    "comparisons/evidence/flasil_neck_50228_vs_249368_v1/evidence_manifest.json",
)

CHECKOUT_SHA = "de0fac2e4500dabe0009e67214ff5f5447ce83dd"
SETUP_PYTHON_SHA = "a309ff8b426b58ec0e2a45f0f869d46889d02405"
UPLOAD_ARTIFACT_SHA = "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"


def contract() -> dict[str, object]:
    text = NEXT_TASK.read_text(encoding="utf-8")
    match = re.search(
        r"<!-- DPSLAB_TASK_CONTRACT_BEGIN -->\s*```json\s*(\{.*?\})\s*```\s*"
        r"<!-- DPSLAB_TASK_CONTRACT_END -->",
        text,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("active contract is missing")
    return json.loads(match.group(1))


class GitHubAutomationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_exact_triggers_and_no_pull_request_target(self) -> None:
        self.assertRegex(self.workflow, r"(?m)^  pull_request:$")
        self.assertRegex(self.workflow, r"(?m)^  workflow_dispatch:$")
        self.assertRegex(self.workflow, r"(?m)^  push:$")
        self.assertEqual(self.workflow.count("      - main"), 2)
        self.assertNotIn("pull_request_target", self.workflow)

    def test_global_permissions_are_read_only(self) -> None:
        self.assertRegex(
            self.workflow,
            r"(?m)^permissions:\n  contents: read\n\ndefaults:",
        )
        self.assertNotRegex(self.workflow, r"(?m)^[ \t]+permissions:")

    def test_host_python_and_lanes_are_exact(self) -> None:
        self.assertEqual(self.workflow.count("runs-on: windows-latest"), 3)
        self.assertEqual(self.workflow.count("python-version: 3.13.14"), 3)
        for job in ("policy", "tools-tests", "functional-suite"):
            self.assertRegex(self.workflow, rf"(?m)^  {re.escape(job)}:$")
        self.assertIn("PYTHONPATH: src", self.workflow)
        self.assertIn("python -m unittest discover -s tests -v", self.workflow)

    def test_functional_suite_installs_authoritative_project_first(self) -> None:
        functional = self.workflow.split("\n  functional-suite:\n", 1)[1]
        setup = functional.index(f"actions/setup-python@{SETUP_PYTHON_SHA}")
        install = functional.index("python -m pip install ./desktop-app")
        suite = functional.index("python -m unittest discover -s tests -v")
        self.assertLess(setup, install)
        self.assertLess(install, suite)
        self.assertEqual(self.workflow.count("python -m pip install ./desktop-app"), 1)

    def test_contractual_text_types_have_canonical_lf_git_attributes(self) -> None:
        self.assertEqual(
            GITATTRIBUTES.read_bytes(),
            b"*.simc text eol=lf\n"
            b"*.toml text eol=lf\n"
            b".gitattributes text eol=lf\n"
            b"*.json text eol=lf\n",
        )

        eol = subprocess.run(
            ["git", "ls-files", "--eol", "--", *CANONICAL_LF_PATHS],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            shell=False,
            check=False,
        )
        self.assertEqual(eol.returncode, 0, eol.stderr)
        eol_by_path = {
            line.split("\t", 1)[1]: line.split("\t", 1)[0].split()
            for line in eol.stdout.splitlines()
        }
        self.assertEqual(set(eol_by_path), set(CANONICAL_LF_PATHS))
        for path in CANONICAL_LF_PATHS:
            self.assertEqual(eol_by_path[path][0], "i/lf")
            self.assertEqual(eol_by_path[path][2:], ["attr/text", "eol=lf"])

        attributes = subprocess.run(
            ["git", "check-attr", "eol", "--", *CANONICAL_LF_PATHS],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            shell=False,
            check=False,
        )
        self.assertEqual(attributes.returncode, 0, attributes.stderr)
        self.assertEqual(
            attributes.stdout.splitlines(),
            [f"{path}: eol: lf" for path in CANONICAL_LF_PATHS],
        )

    def test_actions_are_pinned_and_checkout_drops_credentials(self) -> None:
        expected = {
            f"actions/checkout@{CHECKOUT_SHA}": 3,
            f"actions/setup-python@{SETUP_PYTHON_SHA}": 3,
            f"actions/upload-artifact@{UPLOAD_ARTIFACT_SHA}": 3,
        }
        for reference, count in expected.items():
            self.assertEqual(self.workflow.count(reference), count)
        self.assertNotRegex(self.workflow, r"uses:\s+actions/[^@\s]+@v\d")
        self.assertEqual(self.workflow.count("persist-credentials: false"), 3)

    def test_forbidden_capabilities_are_absent(self) -> None:
        lowered = self.workflow.lower()
        for forbidden in (
            "secrets.", "self-hosted", "quality_gate.py", "simulationcraft",
            "simc.exe", "results/runs", "results/comparisons",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_artifacts_are_minimal_and_retained_seven_days(self) -> None:
        self.assertEqual(self.workflow.count("retention-days: 7"), 3)
        self.assertEqual(self.workflow.count("if: ${{ always() }}"), 3)
        self.assertEqual(self.workflow.count(".log"), 6)
        self.assertEqual(self.workflow.count("summary.json"), 6)

    def test_active_contract_is_rotatable_and_has_closed_scope(self) -> None:
        active = contract()
        self.assertRegex(active["task_id"], r"^[a-z0-9][a-z0-9_]*$")
        self.assertRegex(active["baseline_commit"], r"^[0-9a-f]{40}$")
        self.assertIn(
            active["authorization"]["status"],
            {"design_only", "authorized_for_implementation"},
        )
        allowed = active["scope"]["allowed_paths"]
        self.assertTrue(allowed)
        self.assertEqual(len(allowed), len(set(allowed)))
        self.assertIn("docs/NEXT_TASK.md", allowed)
        self.assertFalse(active["scope"]["allow_deletions"])
        self.assertFalse(active["scope"]["allow_renames"])

    def test_documentation_preserves_authority_boundary(self) -> None:
        documentation = DOCUMENTATION.read_text(encoding="utf-8")
        for phrase in (
            "does not approve a\nchange",
            "never invokes `tools/quality_gate.py`",
            "seven days",
            "Branch protection and rulesets",
        ):
            self.assertIn(phrase, documentation)


if __name__ == "__main__":
    unittest.main()
