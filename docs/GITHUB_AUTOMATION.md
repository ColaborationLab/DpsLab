# GitHub Automation 0.1

## Operational status

GitHub Automation 0.1 is implemented, independently audited, published, and
operational. Commit `bf2db644bfebeb07246f8e967f39101a7aa3e77a` is synchronized
across local `main`, `origin/main`, and the live GitHub remote. The
post-publication run `29645964849` completed successfully in all three evidence
lanes. This operational status records evidence; it does not authorize a later
task, SimulationCraft, or Subblock 2.2.b2.

## Purpose and authority boundary

`.github/workflows/dpslab-ci.yml` supplies reproducible CI evidence for pull
requests to `main`, manual dispatches, and pushes to `main`. The push trigger is
post-publication auditing only. CI reports test outcomes; it does not approve a
change, consume or grant authorization, or start a later task.

The workflow never invokes `tools/quality_gate.py`, SimulationCraft, the DpsLab
runner, comparisons, or run creation. The local quality gate remains the
authoritative process for contractual implementation and independent audit.

## Security controls

- Every lane runs on GitHub-hosted `windows-latest` with Python `3.13.14`.
- Workflow permissions are globally limited to `contents: read`; all omitted
  permissions are `none` under GitHub Actions permission semantics.
- Third-party workflow actions are pinned to full commit SHAs and annotated
  with the verified release version.
- Checkout sets `persist-credentials: false`.
- No secrets, write tokens, environments, or self-hosted runners are used.
- `pull_request_target` is intentionally absent, so pull-request code never
  executes in a privileged base-repository context.

## Evidence lanes

1. **Policy and contract** runs the synthetic assertions in
   `tools/tests/test_github_automation.py` against the workflow and contract.
2. **Tools tests** runs the complete `tools/tests` module.
3. **Functional suite** runs all `desktop-app/tests` with `PYTHONPATH=src` in
   the same process environment. `comparison_models` is part of this lane and
   therefore fails closed: its failure fails the job rather than being skipped,
   tolerated, or rewritten as success.

Each lane uploads only its test log and a small JSON summary. Artifacts are
retained for seven days and contain no profiles, scenarios, variants, local
configuration, SimulationCraft output, run artifacts, or secrets.

## Compensating controls

Branch protection and rulesets are repository settings and are outside this
implementation's authority. Until an administrator configures them, CI cannot
prevent direct pushes or require checks before merge. The compensating controls
are procedural:

- review the pull-request run from the exact candidate commit;
- require all three lanes to pass before a human publication decision;
- record approval separately from CI and from publication;
- use the `push` run only to confirm the already-published `main` commit;
- compare the published commit SHA with the reviewed candidate;
- keep local quality-gate implementation and independent-audit evidence.

These controls improve traceability but do not technically enforce merge or
push policy. Absence of configured branch protection/rulesets must remain an
explicit governance limitation.
