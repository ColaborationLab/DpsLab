import json
import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "desktop-app" / "requirements-ci-win-py313.lock"
PYPROJECT = ROOT / "desktop-app" / "pyproject.toml"
SBOM = ROOT / "security" / "sbom-runtime-win-py313.spdx.json"
WORKFLOW = ROOT / ".github" / "workflows" / "dpslab-ci.yml"
LINE = re.compile(r"^([a-z0-9-]+)==([^ ]+) --hash=sha256:([0-9a-f]{64})$")


class DependencySupplyChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lock_text = LOCK.read_text(encoding="utf-8")
        cls.entries = {}
        for line in cls.lock_text.splitlines():
            match = LINE.fullmatch(line)
            if match:
                cls.entries[match.group(1)] = (match.group(2), match.group(3))
        cls.sbom = json.loads(SBOM.read_text(encoding="utf-8"))

    def test_lock_is_binary_only_exact_hashed_and_closed(self) -> None:
        self.assertIn("--only-binary=:all:", self.lock_text)
        self.assertEqual(
            set(self.entries),
            {"cffi", "cryptography", "numpy", "pycparser", "scipy", "setuptools"},
        )
        requirement_lines = [line for line in self.lock_text.splitlines() if line and not line.startswith(("#", "--"))]
        self.assertEqual(len(requirement_lines), len(self.entries))
        self.assertEqual(list(self.entries), sorted(self.entries))

    def test_project_dependencies_and_build_backend_are_covered(self) -> None:
        project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
        self.assertEqual(project["build-system"]["requires"], ["setuptools==84.0.0"])
        for requirement in project["project"]["dependencies"]:
            name = re.match(r"[A-Za-z0-9-]+", requirement).group(0).lower()
            self.assertIn(name, self.entries)

    def test_vulnerable_cryptography_version_is_not_reintroduced(self) -> None:
        self.assertEqual(
            self.entries["cryptography"],
            (
                "50.0.1",
                "aed8db4f6d71c51efb89530e12d9464e7bf2923d46c3205dc794a2a93f8c0648",
            ),
        )

    def test_sbom_matches_every_locked_version_and_hash(self) -> None:
        packages = {item["name"]: item for item in self.sbom["packages"]}
        self.assertEqual(set(packages), {"dpslab", *self.entries})
        for name, (version, digest) in self.entries.items():
            package = packages[name]
            self.assertEqual(package["versionInfo"], version)
            self.assertEqual(package["checksums"], [{"algorithm": "SHA256", "checksumValue": digest}])
            self.assertEqual(package["licenseConcluded"], "NOASSERTION")

    def test_sbom_is_spdx_and_relationships_reference_known_packages(self) -> None:
        self.assertEqual(self.sbom["spdxVersion"], "SPDX-2.3")
        ids = {item["SPDXID"] for item in self.sbom["packages"]}
        self.assertEqual(self.sbom["documentDescribes"], ["SPDXRef-Package-DpsLab"])
        for relation in self.sbom["relationships"]:
            self.assertIn(relation["spdxElementId"], ids)
            self.assertIn(relation["relatedSpdxElement"], ids)

    def test_ci_installs_hash_locked_dependencies_without_resolution(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("pip install --require-hashes -r ./desktop-app/requirements-ci-win-py313.lock", workflow)
        self.assertIn("pip install --no-deps --no-build-isolation ./desktop-app", workflow)
        self.assertNotIn("pip install ./desktop-app", workflow)
        self.assertEqual(workflow.count("persist-credentials: false"), 3)


if __name__ == "__main__":
    unittest.main()
