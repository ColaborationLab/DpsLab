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
    "knowledge/fixtures/blizzard_patch_notes_synthetic_0_1.html",
)

CHECKOUT_SHA = "de0fac2e4500dabe0009e67214ff5f5447ce83dd"
SETUP_PYTHON_SHA = "a309ff8b426b58ec0e2a45f0f869d46889d02405"
UPLOAD_ARTIFACT_SHA = "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"

ACTIVE_BEGIN = "<!-- DPSLAB_TASK_CONTRACT_BEGIN -->"
ACTIVE_END = "<!-- DPSLAB_TASK_CONTRACT_END -->"
HISTORICAL_BEGIN = "<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->"
HISTORICAL_END = "<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->"
ACTIVE_PATTERN = re.compile(
    re.escape(ACTIVE_BEGIN) + r"\s*"
    r"```json\s*(\{.*?\})\s*```\s*"
    + re.escape(ACTIVE_END),
    re.DOTALL,
)
HISTORICAL_PATTERN = re.compile(
    re.escape(HISTORICAL_BEGIN) + r"\s*"
    r"```json\s*(\{.*?\})\s*```\s*"
    + re.escape(HISTORICAL_END),
    re.DOTALL,
)


def contract_documents(
    text: str,
    pattern: re.Pattern[str],
    begin: str,
    end: str,
    label: str,
) -> list[dict[str, object]]:
    begin_count = text.count(begin)
    end_count = text.count(end)
    if begin_count != end_count:
        raise AssertionError(f"{label} delimiter mismatch")
    matches = pattern.findall(text)
    if len(matches) != begin_count:
        raise AssertionError(f"{label} malformed block")
    return [json.loads(match) for match in matches]


def active_contract(text: str) -> dict[str, object] | None:
    matches = contract_documents(
        text, ACTIVE_PATTERN, ACTIVE_BEGIN, ACTIVE_END, "active"
    )
    if len(matches) > 1:
        raise AssertionError("more than one active contract")
    return matches[0] if matches else None


def historical_contracts(text: str) -> list[dict[str, object]]:
    return contract_documents(
        text,
        HISTORICAL_PATTERN,
        HISTORICAL_BEGIN,
        HISTORICAL_END,
        "historical",
    )


def assert_unique_authority(
    active: dict[str, object] | None,
    historical: list[dict[str, object]],
) -> None:
    contracts = ([active] if active is not None else []) + historical
    task_ids = [contract["task_id"] for contract in contracts]
    authorization_ids = [
        contract["authorization"]["authorization_id"]
        for contract in contracts
    ]
    if len(task_ids) != len(set(task_ids)):
        raise AssertionError("task identity replay")
    if len(authorization_ids) != len(set(authorization_ids)):
        raise AssertionError("authorization identity replay")


def assert_closed_contract(test: unittest.TestCase, contract: dict[str, object]) -> None:
    test.assertRegex(contract["task_id"], r"^[a-z0-9][a-z0-9_]*$")
    test.assertRegex(contract["baseline_commit"], r"^[0-9a-f]{40}$")
    test.assertIn(
        contract["authorization"]["status"],
        {"design_only", "authorized_for_implementation"},
    )
    allowed = contract["scope"]["allowed_paths"]
    test.assertTrue(allowed)
    test.assertEqual(len(allowed), len(set(allowed)))
    test.assertIn("docs/NEXT_TASK.md", allowed)
    test.assertFalse(contract["scope"]["allow_deletions"])
    test.assertFalse(contract["scope"]["allow_renames"])


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
        self.assertEqual(self.workflow.count("runs-on: windows-latest"), 4)
        self.assertEqual(self.workflow.count("python-version: 3.13.14"), 4)
        for job in ("policy", "static-security", "tools-tests", "functional-suite"):
            self.assertRegex(self.workflow, rf"(?m)^  {re.escape(job)}:$")
        self.assertIn("PYTHONPATH: src", self.workflow)
        self.assertIn("python -m unittest discover -s tests -v", self.workflow)

    def test_functional_suite_installs_authoritative_project_first(self) -> None:
        functional = self.workflow.split("\n  functional-suite:\n", 1)[1]
        setup = functional.index(f"actions/setup-python@{SETUP_PYTHON_SHA}")
        locked = functional.index(
            "python -m pip install --require-hashes -r ./desktop-app/requirements-ci-win-py313.lock"
        )
        install = functional.index(
            "python -m pip install --no-deps --no-build-isolation ./desktop-app"
        )
        suite = functional.index("python -m unittest discover -s tests -v")
        self.assertLess(setup, locked)
        self.assertLess(locked, install)
        self.assertLess(install, suite)
        self.assertNotIn("python -m pip install ./desktop-app", self.workflow)

    def test_contractual_text_types_have_canonical_lf_git_attributes(self) -> None:
        self.assertEqual(
            GITATTRIBUTES.read_bytes(),
            b"*.simc text eol=lf\n"
            b"*.toml text eol=lf\n"
            b".gitattributes text eol=lf\n"
            b"*.json text eol=lf\n"
            b"*.html text eol=lf\n"
            b"*.lock text eol=lf\n",
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
            f"actions/checkout@{CHECKOUT_SHA}": 4,
            f"actions/setup-python@{SETUP_PYTHON_SHA}": 4,
            f"actions/upload-artifact@{UPLOAD_ARTIFACT_SHA}": 4,
        }
        for reference, count in expected.items():
            self.assertEqual(self.workflow.count(reference), count)
        self.assertNotRegex(self.workflow, r"uses:\s+actions/[^@\s]+@v\d")
        self.assertEqual(self.workflow.count("persist-credentials: false"), 4)

    def test_forbidden_capabilities_are_absent(self) -> None:
        lowered = self.workflow.lower()
        for forbidden in (
            "secrets.", "self-hosted", "quality_gate.py", "simulationcraft",
            "simc.exe", "results/runs", "results/comparisons",
        ):
            self.assertNotIn(forbidden, lowered)
        self.assertIn("gitleaks.exe", self.workflow)
        self.assertIn("--config .gitleaks.toml", self.workflow)

    def test_artifacts_are_minimal_and_retained_seven_days(self) -> None:
        self.assertEqual(self.workflow.count("retention-days: 7"), 4)
        self.assertEqual(self.workflow.count("if: ${{ always() }}"), 4)
        self.assertEqual(self.workflow.count(".log"), 6)
        self.assertEqual(self.workflow.count("summary.json"), 8)

    def test_contract_lifecycle_accepts_zero_or_one_active_contract(self) -> None:
        text = NEXT_TASK.read_text(encoding="utf-8")
        active = active_contract(text)
        self.assertIsNotNone(active)
        assert active is not None
        assert_closed_contract(self, active)

        without_active = ACTIVE_PATTERN.sub("", text)
        self.assertIsNone(active_contract(without_active))
        active_block = ACTIVE_PATTERN.search(text)
        assert active_block is not None
        with self.assertRaisesRegex(AssertionError, "more than one active"):
            active_contract(text + "\n" + active_block.group(0))
        for marker in (ACTIVE_BEGIN, ACTIVE_END):
            with self.assertRaisesRegex(AssertionError, "delimiter mismatch"):
                active_contract(text + "\n" + marker)

    def test_historical_contracts_are_non_authoritative_and_append_only(self) -> None:
        text = NEXT_TASK.read_text(encoding="utf-8")
        active = active_contract(text)
        historical = historical_contracts(text)
        self.assertGreaterEqual(len(historical), 2)
        assert_unique_authority(active, historical)
        task_ids = [contract["task_id"] for contract in historical]
        self.assertIn(
            "planned_member_transactional_commit_0_1",
            task_ids,
        )
        for contract in historical:
            self.assertEqual(
                contract["authorization"]["status"],
                "authorized_for_implementation",
            )
            assert_closed_contract(self, contract)
        for marker in (HISTORICAL_BEGIN, HISTORICAL_END):
            with self.assertRaisesRegex(AssertionError, "delimiter mismatch"):
                historical_contracts(text + "\n" + marker)

        assert active is not None
        for field in ("task_id", "authorization_id"):
            replay = json.loads(json.dumps(active))
            if field == "task_id":
                replay["task_id"] = historical[0]["task_id"]
            else:
                replay["authorization"]["authorization_id"] = (
                    historical[0]["authorization"]["authorization_id"]
                )
            with self.assertRaisesRegex(AssertionError, "identity replay"):
                assert_unique_authority(replay, historical)

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
