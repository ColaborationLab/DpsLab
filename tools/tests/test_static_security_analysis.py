import json
import unittest
from pathlib import Path

from tools.static_security_analysis import SecurityAnalysisError, summarize


ROOT = Path(__file__).resolve().parents[2]


class StaticSecurityAnalysisTests(unittest.TestCase):
    def test_policies_and_empty_exception_registry_are_closed(self) -> None:
        static = json.loads((ROOT / "security/static_analysis_policy_0_1.json").read_text(encoding="utf-8"))
        secret = json.loads((ROOT / "security/secret_scan_policy_0_1.json").read_text(encoding="utf-8"))
        registry = json.loads((ROOT / "security/secret_scan_exceptions_0_1.json").read_text(encoding="utf-8"))
        self.assertEqual(static["scanner"], {"name": "bandit", "version": "1.9.4", "severity_gate": "HIGH"})
        self.assertEqual(secret["scanner"]["version"], "8.30.0")
        self.assertEqual(len(secret["scanner"]["windows_x64_zip_sha256"]), 64)
        self.assertEqual(registry, {"schema_version": "0.1", "registry_id": "dpslab.secret-scan-exceptions.0.1", "exceptions": []})

    def test_clean_summary_exposes_counts_only(self) -> None:
        result = summarize({"errors": [], "generated_at": "x", "metrics": {}, "results": []}, [])
        self.assertEqual(result, {"schema_version": "0.1", "status": "clean", "bandit": {"high_severity_count": 0, "result_count": 0}, "gitleaks": {"finding_count": 0}})

    def test_high_or_secret_finding_fails_closed(self) -> None:
        bandit = {"errors": [], "generated_at": "x", "metrics": {}, "results": [{"issue_severity": "HIGH", "issue_text": "never emit"}]}
        self.assertEqual(summarize(bandit, [{"Secret": "never emit"}])["status"], "findings")

    def test_rejects_open_or_malformed_bandit_document(self) -> None:
        with self.assertRaisesRegex(SecurityAnalysisError, "invalid_bandit_schema"):
            summarize({"results": [], "errors": [], "metrics": {}, "generated_at": "x", "path": "forbidden"}, [])

    def test_rejects_malformed_gitleaks_document(self) -> None:
        with self.assertRaisesRegex(SecurityAnalysisError, "invalid_gitleaks_schema"):
            summarize({"errors": [], "generated_at": "x", "metrics": {}, "results": []}, {})


if __name__ == "__main__":
    unittest.main()
