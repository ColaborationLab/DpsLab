# Next Task — DpsLab

## Active implementation contract

Daniel authorized the closed local implementation of GitHub Automation 0.1.
This contract permits editing and local verification only. It does not permit
commit, push, tag, branch, pull request, remote changes, GitHub settings,
SimulationCraft, or Subblock 2.2.b2.

<!-- DPSLAB_TASK_CONTRACT_BEGIN -->
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
<!-- DPSLAB_TASK_CONTRACT_END -->

## Required output state

`dpslab_github_automation_0_1_implemented_pending_independent_audit`

The local audit artifact required by this intervention verifies process and
integrity evidence. It does not constitute the later independent technical
audit or authorize publication or the next task.

## Preserved project state

- Canonical formal baseline: `results/runs/20260715T072501.415324Z-95439dae`.
- Subblock 2.2.b1 remains approved (`block_2_2_b1_approved`).
- The A/B collar comparator has not executed a real comparison.
- The current functional-suite baseline is 208/208 passing tests.
- Subblock 2.2.b2 remains future, candidate, and unauthorized.
