# Canonical Comparison Result — Flasil Neck V1

## Identity

- Comparison: `flasil_neck_50228_vs_249368_v1`
- Execution: `cmp-3120334d365b4ba2922cdbb25afe0d7f`
- Status: `completed`
- Created: `2026-07-28T15:10:31.437760Z`
- Started: `2026-07-28T15:10:31.457334Z`
- Finished: `2026-07-28T15:29:13.042376Z`
- Result SHA-256:
  `5e9e18257fb9fb306584d9c0603767b4cdd166cb9a94a9d2cfa6a75407b701c5`
- Code commit:
  `7f06e5c12acc1e586a81891f8a1bf16c960eaeb3`
- Independent verdict: `comparison_real_execution_audit_approved`

The full result remains local at
`results/comparisons/cmp-3120334d365b4ba2922cdbb25afe0d7f/comparison_result.json`.
`results/runs/` and `results/comparisons/` remain intentionally excluded from
Git.

## Frozen inputs

- Arm A: Barbed Ymirheim Choker, item `50228`
- Arm B: Eternal Voidsong Chain, item `249368`
- Base profile SHA-256:
  `f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738`
- Arm B effective-profile SHA-256:
  `8274f6706b603b167380167735b7a1a714498c36ad2bcf0da4c621275297f388`
- Scenario SHA-256:
  `93187338a61d1cfc330f5262abb0b9183acb727d310099eca7917138207c09aa`
- Comparison specification SHA-256:
  `68282327263d4f75797181521419f11aa54fdecf16f1634c0b3b1b2ac6fdbe4c`
- SimulationCraft: `1205-01`, revision `a81c39d`
- Executable SHA-256:
  `710c71129f779376ed17dbcd92f67aa325056e19e27fa8b2b0182fb05db8c7ee`

## Protocol and integrity

- Eight of eight blocks valid.
- Sixteen of sixteen members valid, all on attempt 1.
- No retries, duplicate run IDs, errors, or warnings.
- 5,000 iterations, two threads, timeout 900 seconds.
- Alternating orders `AB`, `BA`; all frozen seeds verified.
- Minimum within-pair pause: `30.000062787` seconds.
- Minimum between-block pause: `60.000187594` seconds.
- All 96 referenced run artifacts independently rehashed successfully.
- Every effective profile changed only the `neck` line.
- The two historical runs and the canonical baseline retained their hashes.

## Statistical result

Primary Welch delta:

- Estimate: `0.9687020358080112 %`
- 95 % CI: `[0.925919404270558, 1.0114846673454643]`
- Classification: `winner_b`

Paired sensitivity:

- Estimate: `0.9687189054410156 %`
- 95 % CI: `[0.9195884609043131, 1.0178493499777181]`
- Classification: `winner_b`

There was no classification disagreement. For this frozen character, profile,
scenario, software revision, and item pair, Arm B produced the higher simulated
DPS. This result is not a universal recommendation for other characters,
specializations, equipment sets, patches, or scenarios.

## Run IDs

1. `20260728T151031.502124Z-94a826bf`
2. `20260728T151131.886279Z-a7255c68`
3. `20260728T151302.641431Z-b7729b12`
4. `20260728T151400.661347Z-94f2b836`
5. `20260728T151529.138098Z-f8f07895`
6. `20260728T151627.763234Z-5c3673e6`
7. `20260728T151757.905009Z-3e1e6342`
8. `20260728T151855.779965Z-904a47a6`
9. `20260728T152022.940739Z-f9db8432`
10. `20260728T152120.282486Z-6526be25`
11. `20260728T152251.113039Z-cfd6ccd4`
12. `20260728T152351.291659Z-e9923a3c`
13. `20260728T152519.180425Z-3369951d`
14. `20260728T152617.205440Z-e1517f72`
15. `20260728T152746.932830Z-5a348b1e`
16. `20260728T152844.364012Z-c525f180`

## External backup

The comparison result and all 16 run directories were copied to an external
backup identified as
`DpsLab_comparison_cmp-3120334d365b4ba2922cdbb25afe0d7f_20260728`.

Verification covered 97 files and 33,813,799 bytes, with zero missing,
additional, or different hashes.
