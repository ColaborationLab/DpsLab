# Next Task — DpsLab

## Active implementation authorization — Comparison readiness bridge 0.1

Daniel authorized autonomous continuation on 2026-07-28. This block connects
the independently audited SimulationCraft identity probe to the frozen
comparison preflight through an injectable, fail-closed readiness boundary.
Tests use only simulated collaborators; this authorization does not permit a
real SimulationCraft invocation, run reservation, comparison, or result.

<!-- DPSLAB_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "comparison_readiness_bridge_0_1",
  "title": "Injectable fail-closed comparison readiness bridge",
  "baseline_commit": "ddcf0a4df87925484a17a8fa7c7761e42c511907",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "comparison_readiness_bridge_0_1-20260728-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-28T01:39:47-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/comparison_readiness.py",
      "desktop-app/tests/test_comparison_readiness.py",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/comparison_readiness_bridge_0_1/implementation.json",
      ".dpslab/quality-gates/comparison_readiness_bridge_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/src/dpslab/__main__.py",
      "desktop-app/src/dpslab/comparison_preflight.py",
      "desktop-app/src/dpslab/simc_identity.py",
      "desktop-app/src/dpslab/comparator.py",
      "desktop-app/src/dpslab/comparison_adapter.py",
      "desktop-app/src/dpslab/comparison_models.py",
      "desktop-app/src/dpslab/comparison_result_io.py",
      "desktop-app/src/dpslab/config.py",
      "desktop-app/src/dpslab/runner.py",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "comparisons/**",
      "results/**",
      "config/**",
      "flasil.simc",
      "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_comparison_readiness.py",
        "-v"
      ],
      "environment": {
        "PYTHONPATH": "src",
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v"
      ],
      "environment": {
        "PYTHONPATH": "src",
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "baseline_test_count": 240,
    "minimum_test_count": 246
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "comparisons/flasil_neck_50228_vs_249368_v1.toml": "68282327263d4f75797181521419f11aa54fdecf16f1634c0b3b1b2ac6fdbe4c",
    "desktop-app/src/dpslab/comparison_preflight.py": "1282997a6190845876283f66ba13d92cd14bb6d79b57f62443608b0111e931a2",
    "desktop-app/src/dpslab/simc_identity.py": "e243695b6802fd4a3bc2d9a273646d2da2d42a4e075c1445c8c8a03d6ec82c26",
    "desktop-app/src/dpslab/config.py": "a933de29661b8d06b6d6f1d1d89b2dc7d74e17c0b87d2d584891824c67c6b53b",
    "desktop-app/src/dpslab/comparison_spec.py": "2974dc8cbe8480dbe9667ffe61b2758bc5edb95bc997f49af4c45f7cf8f238d4",
    "desktop-app/src/dpslab/comparison_adapter.py": "0b65f3339e49217d716d7bc637d3fecf4e821ff68503ee850e61e67fbd0d887e",
    "desktop-app/src/dpslab/comparator.py": "f9d222229a13deb5f46164038f83d45af45ee634c2262313ce881a70ce5ade32",
    "desktop-app/src/dpslab/runner.py": "92dc7712a5fa2001e816f4dc7025e1af6c81b67b2c98b9fd5f52c3301abacc93"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "exactly the three authorized versioned paths in the delta",
    "the bridge composes identity capture and frozen preflight without duplicating either implementation",
    "identity and preflight collaborators are injectable and all tests use simulated collaborators",
    "the bridge validates isolated probe metadata, portable argv, executable source, complete identity, comparison identity, and software identity",
    "dependency failures cross the public boundary as static sanitized errors",
    "no run directory, reservation, comparison result, or durable artifact is created",
    "focused tests, at least 246 functional tests, and tools tests pass",
    "protected hashes remain intact",
    "no real SimulationCraft, comparison, commit, push, or remote mutation occurs during implementation"
  ],
  "express_exclusions": [
    "real SimulationCraft invocation",
    "real comparison or run artifact creation",
    "reservation, planning, orchestration, persistence, or CLI wiring",
    "profiles, scenarios, variants, comparison specs, results, and local config",
    "workflow, quality gate, tools, or GitHub settings changes",
    "authorization of comparison execution or any later block"
  ]
}
```
<!-- DPSLAB_TASK_CONTRACT_END -->

## Completed implementation authorization — SimulationCraft identity probe 0.1

Daniel authorized `simulationcraft_identity_probe_0_1` on 2026-07-28. This
block adds an isolated, fail-closed identity probe for the configured
SimulationCraft executable. Implementation tests use only simulated processes.
The audited implementation was published in
`ddcf0a4df87925484a17a8fa7c7761e42c511907`, and GitHub Actions run
`30334998069` passed all three lanes. The authorization is consumed and does
not permit a real invocation.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "simulationcraft_identity_probe_0_1",
  "title": "Isolated fail-closed SimulationCraft identity probe",
  "baseline_commit": "751ec113fcfdb0f922b853b554fdeabd8b83b064",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "simulationcraft_identity_probe_0_1-20260728-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-28T00:55:57-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/simc_identity.py",
      "desktop-app/tests/test_simc_identity.py",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/simulationcraft_identity_probe_0_1/implementation.json",
      ".dpslab/quality-gates/simulationcraft_identity_probe_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/src/dpslab/__main__.py",
      "desktop-app/src/dpslab/comparison_preflight.py",
      "desktop-app/src/dpslab/comparator.py",
      "desktop-app/src/dpslab/comparison_adapter.py",
      "desktop-app/src/dpslab/comparison_models.py",
      "desktop-app/src/dpslab/comparison_result_io.py",
      "desktop-app/src/dpslab/config.py",
      "desktop-app/src/dpslab/runner.py",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "comparisons/**",
      "results/**",
      "config/**",
      "flasil.simc",
      "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_s?mc_identity.py",
        "-v"
      ],
      "environment": {
        "PYTHONPATH": "src",
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v"
      ],
      "environment": {
        "PYTHONPATH": "src",
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "baseline_test_count": 230,
    "minimum_test_count": 240
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "comparisons/flasil_neck_50228_vs_249368_v1.toml": "68282327263d4f75797181521419f11aa54fdecf16f1634c0b3b1b2ac6fdbe4c",
    "desktop-app/src/dpslab/comparison_spec.py": "2974dc8cbe8480dbe9667ffe61b2758bc5edb95bc997f49af4c45f7cf8f238d4",
    "desktop-app/src/dpslab/comparison_adapter.py": "0b65f3339e49217d716d7bc637d3fecf4e821ff68503ee850e61e67fbd0d887e",
    "desktop-app/src/dpslab/comparator.py": "f9d222229a13deb5f46164038f83d45af45ee634c2262313ce881a70ce5ade32",
    "desktop-app/src/dpslab/runner.py": "92dc7712a5fa2001e816f4dc7025e1af6c81b67b2c98b9fd5f52c3301abacc93",
    "desktop-app/src/dpslab/comparison_preflight.py": "1282997a6190845876283f66ba13d92cd14bb6d79b57f62443608b0111e931a2"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "exactly the three authorized versioned paths in the delta",
    "implementation exposes an explicit identity probe but tests start no real process",
    "the only permitted future command is the absolute executable plus display_build=2",
    "process invocation uses an argument list, shell false, closed stdin, timeout, and an isolated environment",
    "the configured executable path must already be absolute before resolution",
    "personal environment values and credentials do not cross the process boundary",
    "personal executable paths are absent from raised errors and their exception chains",
    "temporary HOME, USERPROFILE, TEMP, TMP, and working directory are removed after the probe",
    "version, branch, revision, executable source, and executable SHA-256 are captured",
    "version, branch, and revision must come from one unique correlated line in one stream with exactly one build clause",
    "combined output is bounded incrementally, the process is stopped above 64 KiB, and failure to confirm termination fails closed",
    "missing, ambiguous, oversized, nonzero, timed out, or mutating probes fail closed",
    "no run directory, reservation, comparison, or durable result is created",
    "focused tests, at least 240 functional tests, and tools tests pass",
    "protected hashes remain intact",
    "no real SimulationCraft, comparison, commit, push, or remote mutation"
  ],
  "express_exclusions": [
    "real SimulationCraft invocation",
    "real comparison or run artifact creation",
    "preflight, reservation, planning, orchestration, result persistence, or CLI wiring",
    "profiles, scenarios, variants, comparison specs, results, and local config",
    "workflow, quality gate, tools, or GitHub settings changes",
    "commits, pushes, tags, branches, pull requests, and remote changes",
    "authorization of a probe execution, comparison execution, or any later block"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

## Completed implementation authorization — Comparison execution preflight 0.1

Daniel authorized `comparison_execution_preflight_0_1` on 2026-07-28. This
block adds a read-only, fail-closed boundary that proves the frozen comparison
inputs and environment are coherent before any process, reservation, durable
result, or run artifact can be created.

Implementation, independent audit, controlled publication, and canonical CI
verification are complete:

- commit: `751ec113fcfdb0f922b853b554fdeabd8b83b064`;
- GitHub Actions run: `30332372100`;
- Policy and contract, Tools tests, and Functional suite: success.

The authorization is consumed. The preserved JSON below is historical evidence
only and cannot authorize another mutation.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "comparison_execution_preflight_0_1",
  "title": "Read-only fail-closed comparison execution preflight",
  "baseline_commit": "6c1ce6c34aab341e3ab26c5ec007c2cc54dc994b",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "comparison_execution_preflight_0_1-20260728-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-28T00:19:50-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/comparison_preflight.py",
      "desktop-app/tests/test_comparison_preflight.py",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/comparison_execution_preflight_0_1/implementation.json",
      ".dpslab/quality-gates/comparison_execution_preflight_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/src/dpslab/__main__.py",
      "desktop-app/src/dpslab/comparator.py",
      "desktop-app/src/dpslab/comparison_adapter.py",
      "desktop-app/src/dpslab/comparison_models.py",
      "desktop-app/src/dpslab/comparison_result_io.py",
      "desktop-app/src/dpslab/comparison_spec.py",
      "desktop-app/src/dpslab/runner.py",
      "desktop-app/tests/test_comparator.py",
      "desktop-app/tests/test_comparison_adapter.py",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "comparisons/**",
      "results/**",
      "config/**",
      "flasil.simc",
      "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": [
        "python",
        "-m",
        "unittest",
        "tests.test_comparison_preflight",
        "-v"
      ],
      "environment": {
        "PYTHONPATH": "src",
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v"
      ],
      "environment": {
        "PYTHONPATH": "src",
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "baseline_test_count": 220,
    "minimum_test_count": 230
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "comparisons/flasil_neck_50228_vs_249368_v1.toml": "68282327263d4f75797181521419f11aa54fdecf16f1634c0b3b1b2ac6fdbe4c",
    "desktop-app/src/dpslab/comparison_spec.py": "2974dc8cbe8480dbe9667ffe61b2758bc5edb95bc997f49af4c45f7cf8f238d4",
    "desktop-app/src/dpslab/comparison_adapter.py": "0b65f3339e49217d716d7bc637d3fecf4e821ff68503ee850e61e67fbd0d887e",
    "desktop-app/src/dpslab/comparator.py": "f9d222229a13deb5f46164038f83d45af45ee634c2262313ce881a70ce5ade32",
    "desktop-app/src/dpslab/runner.py": "92dc7712a5fa2001e816f4dc7025e1af6c81b67b2c98b9fd5f52c3301abacc93"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "exactly the three authorized versioned paths in the delta",
    "preflight accepts an explicit environment record and starts no process",
    "frozen spec and all referenced assets are rehashed at the preflight boundary",
    "spec and scenario objects must equal authoritative reloads from their verified bytes",
    "authoritative scenario equality includes its source precision while execution precision remains frozen by the comparison spec",
    "scenario, parameters, runs root, and executable source fail closed",
    "complete SimulationCraft version, revision, and executable hash must match",
    "CPython, SciPy, and clean DpsLab source identity are verified",
    "runtime versions and mutually exclusive source identities use strict canonical forms",
    "source-tree identity is recomputed from a sorted unique portable inventory",
    "no reservation, comparison_result, run directory, or artifact is created",
    "focused tests, at least 230 functional tests, and tools tests pass",
    "protected hashes remain intact",
    "no SimulationCraft, real comparison, commit, push, or remote mutation"
  ],
  "express_exclusions": [
    "SimulationCraft invocation or identity probe",
    "real comparison or run artifact creation",
    "reservation, planning, orchestration, result persistence, or CLI wiring",
    "profiles, scenarios, variants, comparison specs, results, and local config",
    "workflow, quality gate, tools, or GitHub settings changes",
    "commits, pushes, tags, branches, pull requests, and remote changes",
    "authorization of a comparison execution or any later block"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

## Completed implementation authorization — SimulationCraft revision capture 0.1

Daniel authorized `simulationcraft_revision_capture_0_1` on 2026-07-28. This
prerequisite captures the root `git_revision` emitted in an already generated
SimulationCraft JSON report so the typed comparison adapter can validate the
frozen expected revision. It does not invoke SimulationCraft or authorize a
comparison.

Implementation, independent audit, controlled publication, and canonical CI
verification are complete:

- commit: `6c1ce6c34aab341e3ab26c5ec007c2cc54dc994b`;
- GitHub Actions run: `30331030751`;
- Policy and contract, Tools tests, and Functional suite: success.

The authorization is consumed. The preserved JSON below is historical evidence
only and cannot authorize another mutation.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "simulationcraft_revision_capture_0_1",
  "title": "Capture SimulationCraft git revision from generated JSON",
  "baseline_commit": "0de971c34ff372efcfb841a19a5f5670b9a7b4f0",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "simulationcraft_revision_capture_0_1-20260728-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-28T00:03:21-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/runner.py",
      "desktop-app/tests/test_runner.py",
      "docs/NEXT_TASK.md",
      "tools/tests/test_github_automation.py"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/simulationcraft_revision_capture_0_1/implementation.json",
      ".dpslab/quality-gates/simulationcraft_revision_capture_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/src/dpslab/__main__.py",
      "desktop-app/src/dpslab/comparator.py",
      "desktop-app/src/dpslab/comparison_adapter.py",
      "desktop-app/src/dpslab/comparison_models.py",
      "desktop-app/src/dpslab/comparison_result_io.py",
      "desktop-app/src/dpslab/planned_member.py",
      "desktop-app/tests/test_comparator.py",
      "desktop-app/tests/test_comparison_adapter.py",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "comparisons/**",
      "results/**",
      "config/**",
      "flasil.simc",
      "tools/quality_gate.py",
      "tools/tests/test_quality_gate.py"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": [
        "python",
        "-m",
        "unittest",
        "tests.test_runner",
        "-v"
      ],
      "environment": {
        "PYTHONPATH": "src",
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v"
      ],
      "environment": {
        "PYTHONPATH": "src",
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "baseline_test_count": 219,
    "minimum_test_count": 220
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "comparisons/flasil_neck_50228_vs_249368_v1.toml": "68282327263d4f75797181521419f11aa54fdecf16f1634c0b3b1b2ac6fdbe4c",
    "desktop-app/src/dpslab/comparison_adapter.py": "0b65f3339e49217d716d7bc637d3fecf4e821ff68503ee850e61e67fbd0d887e",
    "desktop-app/src/dpslab/comparator.py": "f9d222229a13deb5f46164038f83d45af45ee634c2262313ce881a70ce5ade32"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "exactly the four authorized versioned paths in the delta",
    "root git_revision is persisted as simc_revision in metadata",
    "only a nonempty root string is accepted and surrounding whitespace is removed",
    "missing, blank, non-string, or nested revision remains null without inference",
    "existing simc_version extraction and runner behavior remain compatible",
    "contract lifecycle validation remains task-agnostic and rotatable",
    "focused runner tests, at least 220 functional tests, and tools tests pass",
    "protected hashes remain intact",
    "no SimulationCraft, comparison, commit, push, or remote mutation"
  ],
  "express_exclusions": [
    "SimulationCraft invocation or identity probe",
    "real comparison or run artifact creation",
    "comparison orchestration, adapter, models, result persistence, or CLI wiring",
    "profiles, scenarios, variants, comparison specs, results, and local config",
    "workflow, quality gate, or GitHub settings changes",
    "commits, pushes, tags, branches, pull requests, and remote changes",
    "authorization of comparison_execution_preflight_0_1 or any later block"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

## Completed implementation authorization — Contract lifecycle 0.2

Daniel authorized `contract_lifecycle_rotatability_0_2` on 2026-07-27. This
prerequisite restores machine-checked rotation between a legitimate active
contract and an append-only historical record without granting any functional
or execution authority.

Implementation, independent audit, controlled publication, and canonical CI
verification are complete:

- commit: `0de971c34ff372efcfb841a19a5f5670b9a7b4f0`;
- GitHub Actions run: `30330280480`;
- Policy and contract, Tools tests, and Functional suite: success.

The authorization is consumed. The preserved JSON below is historical evidence
only and cannot authorize another mutation.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "contract_lifecycle_rotatability_0_2",
  "title": "Rotatable active and historical task-contract lifecycle",
  "baseline_commit": "7f8b5bf131f0bf82a757f9c5f47290ead4e99592",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "contract_lifecycle_rotatability_0_2-20260727-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-27T23:45:55-05:00"
  },
  "scope": {
    "allowed_paths": [
      "docs/NEXT_TASK.md",
      "docs/GITHUB_AUTOMATION.md",
      "tools/tests/test_github_automation.py"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/contract_lifecycle_rotatability_0_2/implementation.json",
      ".dpslab/quality-gates/contract_lifecycle_rotatability_0_2/audit.json"
    ],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/**",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "comparisons/**",
      "results/**",
      "config/**",
      "flasil.simc",
      "tools/quality_gate.py",
      "tools/tests/test_quality_gate.py"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": ".",
      "argv": [
        "python",
        "-m",
        "unittest",
        "tools.tests.test_github_automation",
        "-v"
      ],
      "environment": {
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "full": {
      "working_directory": ".",
      "argv": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tools/tests",
        "-v"
      ],
      "environment": {
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "baseline_test_count": 51,
    "minimum_test_count": 52
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "tools/quality_gate.py": "c13fed03827c5e81cec9304f2dd0a01a69925f4b7ee8a5107a34480ea5fc6bbd",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "exactly the three authorized versioned paths in the delta",
    "zero or one active contract is accepted by the CI lifecycle parser",
    "more than one active contract fails closed",
    "orphaned, unbalanced, or malformed active and historical delimiters fail closed",
    "an active contract retains strict closed-scope validation",
    "two or more historical contracts are accepted without an exact-count ceiling",
    "task and authorization identities are unique across the active and historical union",
    "a consumed historical identity cannot be replayed as active authority",
    "historical contracts are never interpreted as active authority",
    "quality_gate.py remains unchanged and fails closed when no active delimiters exist",
    "focused and complete tools tests pass with at least 52 tests",
    "protected hashes remain intact",
    "no SimulationCraft, comparison, functional code, commit, push, or remote mutation"
  ],
  "express_exclusions": [
    "changes to quality_gate.py or its tests",
    "workflow or GitHub settings changes",
    "desktop application and comparison implementation",
    "SimulationCraft invocation or real comparison",
    "profiles, scenarios, variants, comparisons, results, and local config",
    "commits, pushes, tags, branches, pull requests, and remote changes",
    "authorization of simulationcraft_revision_capture_0_1 or any later block"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

## Completed implementation authorization — Subblock 2.2.b2

Daniel explicitly authorized continuation of Subblock 2.2.b2 and subsequently
authorized the one additional CI-contract compatibility path on 2026-07-27.
The completed task is `planned_member_transactional_commit_0_1`.

The task is limited to durable, transactional persistence of the already
approved pure planned-member candidate. It accepts the existing single-writer
file model; it does not claim multiprocess compare-and-swap or locking.

The authorization has been consumed. Implementation, independent audit,
controlled commit and publication, and canonical CI verification are complete:

- commit: `d8bc2406b6b9ea2acc46bf16e5b4811d01573243`;
- GitHub Actions run: `30328581221`;
- focused tests: 26/26;
- related modules: 73/73;
- functional suite: 219/219;
- tools tests: 51/51;
- Policy and contract, Tools tests, and Functional suite: success.

The machine-readable contract below preserves the authorization exactly as it
existed during implementation. Its `authorized_for_implementation` value is
historical evidence and does not authorize another edit, rerun, commit, push,
real comparison, SimulationCraft invocation, or later block.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "planned_member_transactional_commit_0_1",
  "title": "Subblock 2.2.b2 transactional planned-member commit",
  "baseline_commit": "6da6d075cf934edfc1ea6a07bed7464cbfbfbf4a",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "planned_member_transactional_commit_0_1-20260727-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-27T22:56:42-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/comparison_result_io.py",
      "desktop-app/tests/test_planned_member.py",
      "docs/NEXT_TASK.md",
      "tools/tests/test_github_automation.py"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/planned_member_transactional_commit_0_1/implementation.json",
      ".dpslab/quality-gates/planned_member_transactional_commit_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/src/dpslab/planned_member.py",
      "desktop-app/src/dpslab/comparator.py",
      "desktop-app/src/dpslab/comparison_models.py",
      "desktop-app/src/dpslab/comparison_transitions.py",
      "desktop-app/src/dpslab/runner.py",
      "desktop-app/src/dpslab/comparison_adapter.py",
      "desktop-app/tests/test_comparator.py",
      "desktop-app/tests/test_comparison_models.py",
      "desktop-app/tests/test_comparison_member_transactions.py",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "comparisons/**",
      "results/**",
      "config/**",
      "flasil.simc",
      "tools/quality_gate.py",
      "tools/tests/test_quality_gate.py"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": [
        "python",
        "-m",
        "unittest",
        "tests.test_planned_member",
        "-v"
      ],
      "environment": {
        "PYTHONPATH": "src",
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v"
      ],
      "environment": {
        "PYTHONPATH": "src",
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "baseline_test_count": 213,
    "minimum_test_count": 219
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/planned_member.py": "8e9aac859576abefc3f810f152e93f2541880d673825d1cfa1474f04b1e6a2b2",
    "desktop-app/tests/test_comparison_models.py": "420989a5f9d56a15ac3c67e3375420f7cc0f441001a62a0434b5edc7b33c92d0"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "exactly the four authorized versioned paths in the delta",
    "no deletions or renames",
    "durable state must exist and equal previous before candidate construction",
    "new planned member persists through the existing atomic commit boundary",
    "exact idempotence confirms durable state without any physical write",
    "durable updated_at advances strictly and all pure 2.2.b1 invariants remain fail-closed",
    "reservation_token plaintext never enters JSON, physical operations, or errors",
    "physical failures preserve previous bytes and remove temporary files",
    "full suite reports at least 219 tests and tools tests remain green",
    "protected hashes remain intact",
    "no SimulationCraft, real comparison, commit, push, or remote mutation"
  ],
  "express_exclusions": [
    "multiprocess locking or compare-and-swap",
    "changes to planned_member.py or the comparator orchestrator",
    "runner, adapter, SimulationCraft, profiles, scenarios, variants, comparisons, results, and config",
    "GitHub workflow or settings changes",
    "commits, pushes, tags, branches, pull requests, and remote changes",
    "Subblock 2.2.b3 and real experiment execution"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

## Completed implementation authorization

Daniel authorized autonomous continuation on 2026-07-27. The closed task is
`comparison_timestamp_monotonicity_0_1`, based on the independently
reviewed Python 3.12 diagnosis.

This authorization has been consumed. The implementation, independent audit,
controlled commit and push, and canonical CI verification are complete:

- commit: `b19fb6eae2a44240467cc8684adfd2733e09f0bb`;
- GitHub Actions run: `30326263409`;
- Policy and contract: success;
- Tools tests: success;
- Functional suite on Python 3.13.14: success;
- local Python 3.12.13 verification: 213/213 passing tests.

The closed scope below is retained as historical evidence and does not
authorize further mutation.

Allowed versioned paths:

- `desktop-app/src/dpslab/comparison_models.py`
- `desktop-app/src/dpslab/comparison_result_io.py`
- `desktop-app/tests/test_comparison_models.py`
- `docs/NEXT_TASK.md`

Required behavior:

- sample the wall clock once per new event;
- make the durable logical timestamp strictly later than the previous
  `updated_at`, advancing by one microsecond when the wall-clock sample is
  equal or earlier;
- assign the same logical timestamp to `StateEvent.occurred_at` and
  `ComparisonResult.updated_at`, and reuse it for transition-specific
  `started_at` or `finished_at`;
- reject malformed, timezone-naive, or out-of-range historical timestamps as
  `ComparisonResultError` before mutating status or events;
- enforce the same invariants again at the durable commit boundary, including
  exact event/updated/transition-side timestamp equality and strict progress
  from the confirmed state;
- preserve fail-closed validation, durable ISO-8601 UTC timestamps, historical
  schema compatibility, and all protected assets;
- verify deterministic equal, earlier, and normally later clock cases;
- run the focused module, full functional suite, tools tests, independent
  audit, controlled commit, push, and canonical CI verification.

This authorization excludes SimulationCraft, Subblock 2.2.b2, profiles,
scenarios, variants, comparisons, results, GitHub settings, workflow changes,
and every other production or test path.

## Latest consumed implementation contract

Daniel authorized the closed local implementation of GitHub Automation 0.1.
The contract below is retained verbatim as historical and machine-readable
evidence. Its implementation authorization has been consumed: it does not
authorize additional edits, reruns, commits, pushes, remote changes, GitHub
settings, SimulationCraft, Subblock 2.2.b2, or a later task.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "dpslab_github_automation_0_1",
  "title": "GitHub Automation 0.1",
  "baseline_commit": "6bff15c2d6b03c96a65ed520ca4f800161d53d2c",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "dpslab_github_automation_0_1-20260718-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-18T04:04:32-05:00"
  },
  "scope": {
    "allowed_paths": [
      ".github/workflows/dpslab-ci.yml",
      "docs/GITHUB_AUTOMATION.md",
      "docs/NEXT_TASK.md",
      "tools/tests/test_github_automation.py"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/dpslab_github_automation_0_1/implementation.json",
      ".dpslab/quality-gates/dpslab_github_automation_0_1/audit.json"
    ],
    "forbidden_paths": [
      "desktop-app/src/**",
      "desktop-app/tests/**",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "comparisons/**",
      "results/**",
      "config/**",
      "flasil.simc",
      "tools/quality_gate.py",
      "tools/tests/test_quality_gate.py"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": ".",
      "argv": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tools/tests",
        "-v"
      ],
      "environment": {
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v"
      ],
      "environment": {
        "PYTHONPATH": "src",
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "baseline_test_count": 208,
    "minimum_test_count": 208
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/planned_member.py": "8e9aac859576abefc3f810f152e93f2541880d673825d1cfa1474f04b1e6a2b2",
    "desktop-app/tests/test_planned_member.py": "5d68029c3e21d98695d5f5c9d83fd14cfa72ae6634fa3c7b8c6f879f616a9d89",
    "desktop-app/tests/test_comparison_models.py": "c2ab1edf521a430899d6770e131fae664c816735c5930140427c4627d18e82fd"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "exactly the four authorized versioned paths in the delta",
    "no deletions or renames",
    "workflow uses windows-latest and exact Python 3.13.14",
    "three evidence lanes pass and comparison_models fails closed",
    "full suite reports at least 208 tests",
    "protected hashes remain intact",
    "implementation.json and audit.json are generated locally and ignored by Git",
    "no SimulationCraft, runs, comparisons, authority decisions, commits, or remotes"
  ],
  "express_exclusions": [
    "production code",
    "tests outside tools/tests/test_github_automation.py",
    "quality_gate.py and its existing tests",
    "profiles, scenarios, variants, comparisons, results, config, and flasil.simc",
    "GitHub settings, branch protection, and rulesets",
    "commits, pushes, tags, branches, pull requests, and remote changes",
    "SimulationCraft",
    "Subblock 2.2.b2"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

## Completed output state

`dpslab_github_automation_0_1_completed_and_operational`

The implementation, independent audit, controlled publication, and live
post-publication verification are complete. Commit
`bf2db644bfebeb07246f8e967f39101a7aa3e77a` is the synchronized local and
remote `main`. GitHub Actions run `29645964849` completed successfully in all
three lanes: Policy and contract, Tools tests, and Functional suite. CI
evidence does not authorize the next task.

## Preserved project state

- Canonical formal baseline: `results/runs/20260715T072501.415324Z-95439dae`.
- Subblock 2.2.b1 remains approved (`block_2_2_b1_approved`).
- The A/B collar comparator has not executed a real comparison.
- The current functional-suite baseline is 219/219 passing tests.
- The Python 3.12 `updated_at` observation is closed by
  `comparison_timestamp_monotonicity_0_1`: logical timestamps now advance
  strictly, durable boundaries enforce the invariant, and local Python 3.12.13
  verification passed 213/213 tests.
- The former `comparison_models` test incident is closed by the deterministic
  test-only correction published in
  `6bff15c2d6b03c96a65ed520ca4f800161d53d2c`.
- GitHub Automation 0.1 is implemented, independently audited, published, and
  operational (`dpslab_github_automation_0_1_completed_and_operational`).
- Subblock 2.2.b2 is implemented, independently audited, published, and
  verified by canonical CI in
  `d8bc2406b6b9ea2acc46bf16e5b4811d01573243`.
- `planned_member_transactional_commit_0_1` is consumed; no implementation
  contract is active and no real comparison is authorized.
