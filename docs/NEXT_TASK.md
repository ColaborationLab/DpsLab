# Next Task — DpsLab

## Active implementation authorization

Daniel explicitly authorized continuation of Subblock 2.2.b2 and subsequently
authorized the one additional CI-contract compatibility path on 2026-07-27.
The active task is `planned_member_transactional_commit_0_1`.

The task is limited to durable, transactional persistence of the already
approved pure planned-member candidate. It accepts the existing single-writer
file model; it does not claim multiprocess compare-and-swap or locking.

<!-- DPSLAB_TASK_CONTRACT_BEGIN -->
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
<!-- DPSLAB_TASK_CONTRACT_END -->

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
- The current functional-suite baseline is 208/208 passing tests.
- The Python 3.12 `updated_at` observation is closed by
  `comparison_timestamp_monotonicity_0_1`: logical timestamps now advance
  strictly, durable boundaries enforce the invariant, and local Python 3.12.13
  verification passed 213/213 tests.
- The former `comparison_models` test incident is closed by the deterministic
  test-only correction published in
  `6bff15c2d6b03c96a65ed520ca4f800161d53d2c`.
- GitHub Automation 0.1 is implemented, independently audited, published, and
  operational (`dpslab_github_automation_0_1_completed_and_operational`).
- Subblock 2.2.b2 is now the active, narrowly authorized transactional
  persistence task; it does not authorize execution of a real comparison.
- `planned_member_transactional_commit_0_1` is the only active implementation
  contract.
