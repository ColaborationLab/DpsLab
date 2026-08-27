import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "security" / "security_baseline_0_1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "dpslab-ci.yml"
PYPROJECT = ROOT / "desktop-app" / "pyproject.toml"


class SecurityBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = json.loads(POLICY.read_text(encoding="utf-8"))

    def test_policy_is_closed_and_versioned(self) -> None:
        self.assertEqual(
            set(self.policy),
            {
                "schema_version",
                "policy_id",
                "principles",
                "trust_boundaries",
                "secret_forbidden_locations",
                "external_beta_required_gates",
                "unsafe_patterns",
            },
        )
        self.assertEqual(self.policy["schema_version"], "0.1")
        self.assertEqual(self.policy["policy_id"], "dpslab.security-baseline.0.1")

    def test_control_lists_are_nonempty_sorted_and_unique(self) -> None:
        for name, value in self.policy.items():
            if name in {"schema_version", "policy_id"}:
                continue
            self.assertIsInstance(value, list)
            self.assertTrue(value)
            self.assertEqual(value, sorted(value))
            self.assertEqual(len(value), len(set(value)))

    def test_core_boundaries_and_beta_gates_cannot_disappear(self) -> None:
        self.assertGreaterEqual(
            set(self.policy["trust_boundaries"]),
            {"addon_runtime", "github_ci", "release_keys", "update_channel"},
        )
        self.assertGreaterEqual(
            set(self.policy["external_beta_required_gates"]),
            {
                "dependency_audit",
                "independent_security_review",
                "secret_scanning",
                "signed_update_verification",
                "static_analysis",
            },
        )

    def test_ci_retains_least_privilege_controls(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertEqual(workflow.count("persist-credentials: false"), 3)
        self.assertNotIn("pull_request_target:", workflow)
        self.assertNotIn("secrets.", workflow)

    def test_dependency_ranges_have_upper_bounds(self) -> None:
        project = PYPROJECT.read_text(encoding="utf-8")
        dependency_line = next(
            line for line in project.splitlines() if line.startswith("dependencies =")
        )
        self.assertIn("scipy>=1.11.0,<2.0.0", dependency_line)
        self.assertIn("cryptography>=49.0.0,<50.0.0", dependency_line)


if __name__ == "__main__":
    unittest.main()
