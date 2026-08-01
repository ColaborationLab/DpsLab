# Next Task — DpsLab

## Consumed design authorization — Comparison result productization 0.1

The completed collar experiment is evidence for one frozen case, not a
multiclass recommendation engine. The next task is limited to designing how an
audited comparison result may inform templates, user guidance, and later
product work without overgeneralizing its scope.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "comparison_result_productization_design_0_1",
  "title": "Design the governed transition from one audited result to product guidance",
  "baseline_commit": "7f06e5c12acc1e586a81891f8a1bf16c960eaeb3",
  "authorization": {
    "status": "design_only",
    "authorization_id": "comparison_result_productization_design_0_1-20260728-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-28T10:34:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/**",
      "tools/**",
      "comparisons/**",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "results/**",
      "config/**",
      "flasil.simc"
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
    "baseline_test_count": 267,
    "minimum_test_count": 267
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "scenarios/st_lightmovement_300s_v1.toml": "93187338a61d1cfc330f5262abb0b9183acb727d310099eca7917138207c09aa",
    "comparisons/flasil_neck_50228_vs_249368_v1.toml": "68282327263d4f75797181521419f11aa54fdecf16f1634c0b3b1b2ac6fdbe4c",
    "comparisons/simulationcraft_identity_manifest_0_1.json": "0a305a5991de0d3c1c4aafbb1756351b6643366a663f532877d6e137b69542eb"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "design keeps the result scoped to the frozen character and scenario",
    "future templates distinguish static fallback data from measured evidence",
    "no implementation, simulation, comparison, or recommendation is authorized",
    "the next implementation decision remains human and contract-bound"
  ],
  "express_exclusions": [
    "implementation or code changes",
    "SimulationCraft invocation or comparison execution",
    "new runs, results, baselines, or frozen input changes",
    "universal recommendation claims",
    "commits, pushes, releases, marketing, or distribution changes"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

## Design output — governed productization boundary

### Product objective

DpsLab must help a player improve damage across WoW characters while
accounting for class, specialization, race, talents, equipment, encounter
conditions, game build, and evidence age. The addon and desktop application
are complementary parts of one solution:

- the addon observes game-exposed state, presents guidance, and exchanges
  versioned packages;
- the desktop application validates character data, executes or imports
  analytical evidence, maintains provenance, and prepares signed content;
- neither component automates gameplay or silently converts one character's
  simulation into a general rule.

### Three evidence tiers

Every recommendation candidate must declare exactly one evidence tier.

1. `static_fallback_template`
   - Ships with the addon and works without the desktop application.
   - May contain conservative starting priorities for a specific WoW product,
     build range, class, specialization, race applicability, level range, and
     supported content context.
   - Must label unknown or unsupported variables and must never claim to be a
     personalized simulation.
2. `imported_analytical_evidence`
   - Produced by an approved DpsLab desktop workflow or imported through a
     compatible, verified package.
   - Must bind character identity, frozen inputs, scenario, software versions,
     result hashes, statistical method, confidence interval, and expiry
     policy.
   - The audited collar result belongs here and remains scoped to Flasil,
     SimulationCraft `1205-01` revision `a81c39d`, the frozen profile and
     scenario, and the two compared items.
3. `character_observation`
   - Derived only from values exposed by the WoW API and the player's saved
     local data.
   - May explain mismatches between current state and an applicable template
     or imported package.
   - Missing API data is `unknown` or `not_available`; it is not inferred.

A future presentation layer may combine these tiers for explanation, but it
must retain each tier's separate provenance and may not raise confidence by
aggregation.

### Canonical recommendation envelope

The future cross-component schema should use an immutable envelope with these
families:

- `identity`: package ID, schema version, content version, channel, created
  time, publisher key ID;
- `compatibility`: WoW product, branch, expansion/season, interface number,
  build minimum/maximum, locale independence, addon minimum/maximum, desktop
  minimum/maximum;
- `subject`: class, specialization, optional race applicability, level range,
  role, content context, and optional character-bound fingerprint;
- `guidance`: ordered and typed statements, prerequisites, mutually exclusive
  alternatives, explanatory text keys, and explicit unsupported variables;
- `evidence`: tier, source IDs, hashes, method, sample/run counts, uncertainty,
  limitations, and age;
- `safety`: no-automation declaration, required warnings, degradation policy,
  and invalidation reasons;
- `integrity`: canonical payload hash, signature algorithm, signature, and
  signing-key lineage.

The addon must consume only a closed subset of this envelope. Desktop-only
fields may be ignored only when the schema explicitly marks them optional and
the remaining addon subset is still valid.

### Applicability and fail-closed selection

Selection must evaluate, in order:

1. package authenticity and byte integrity;
2. schema compatibility;
3. exact WoW product and build range;
4. class and specialization;
5. level and content context;
6. race only when the guidance declares a race-sensitive dependency;
7. required equipment, talents, or character fingerprint;
8. evidence expiry and invalidation rules.

An unknown build must not silently select the newest known package. The addon
may fall back from personalized analytical evidence to a compatible static
template, but the UI must show the downgrade, provenance, age, and reason.
When no compatible template exists, the correct result is
`guidance_unavailable`, not a best-effort recommendation.

### Initial-template policy

Initial templates are curated knowledge artifacts, not simulator output. A
template may provide:

- a conservative starter priority;
- baseline stat-orientation language with no fabricated exact weights;
- supported talent/loadout prerequisites;
- equipment or mechanic checks that can be evaluated from exposed API data;
- explicit branches for known contexts;
- links or identifiers for deeper desktop analysis.

A template must not embed copied proprietary simulator logic, undocumented
third-party data, universal BiS claims, or exact numerical weights without a
versioned source and review. Race-specific templates should exist only when a
real applicability difference is documented; otherwise race remains a
compatibility dimension with shared guidance.

### Desktop and update architecture

Binary releases, knowledge packages, schemas, and metadata are independently
versioned components. The update client should:

1. fetch a small signed channel manifest;
2. verify publisher key, signature, hashes, compatibility, and rollback floor;
3. stage the complete candidate set outside the active location;
4. validate the candidate as a compatible set;
5. activate it atomically;
6. retain the last known-good compatible set for rollback.

`stable` and `beta` remain separate channels. Patch-note ingestion may create
`pending_review` candidates and invalidate affected knowledge, but patch notes
alone never publish guidance. Human or separately authorized machine review
must map source changes to canonical entities, applicability, tests, and a
signed release.

Offline operation uses the last verified compatible package and displays its
age. Manual import uses the same signature, integrity, compatibility, and
rollback checks as network updates. Telemetry, if ever authorized, is
off-by-default, revocable, minimized, and separated from update eligibility.

### Addon boundary

The addon may:

- read permitted WoW API state;
- display static or imported guidance with provenance;
- record local observations in SavedVariables;
- export/import explicitly initiated payloads;
- notify the player that verified knowledge is stale or unavailable.

The addon may not:

- run a simulator;
- control movement, targeting, combat actions, or input;
- infer inaccessible state;
- download or execute arbitrary code;
- hide evidence age, applicability failures, or a fallback downgrade.

### Repository and release boundary

The current design does not decide repository topology. If the addon later
uses a separate repository, schemas must still have one authoritative source
and generated copies must carry source commit and content hash. DpsLab and UPL
remain separate projects: only domain-neutral patterns may be reused, never
data, credentials, releases, or implied authority.

### Candidate work packages

The following packages are candidates only and are not authorized:

1. `knowledge_envelope_schema_0_1`
   - closed JSON schema, canonical serialization, compatibility evaluator, and
     signature-independent hash model;
2. `static_template_catalog_0_1`
   - one synthetic specialization fixture plus review states, without claims
     about live class balance;
3. `addon_guidance_reader_0_1`
   - pure Lua reader/validator against synthetic packages, no WoW automation;
4. `desktop_knowledge_packager_0_1`
   - local packaging, staging, compatibility checks, and rollback primitives;
5. `patch_evidence_intake_0_1`
   - patch-source snapshots and `pending_review` candidate generation only;
6. `signed_update_channel_0_1`
   - key policy, manifest format, stable/beta separation, and recovery design;
7. `specialization_template_program_0_1`
   - governed research and review workflow for expanding class/spec coverage.

### Recommended next contract

The smallest useful implementation candidate is
`knowledge_envelope_schema_0_1`. It should begin with synthetic fixtures and
pure validation only. It must not include live recommendations, class balance
claims, signing credentials, network updates, addon UI, SimulationCraft, or
automatic patch-note publication.

Before implementation authorization, human review must decide:

1. whether the canonical envelope belongs initially in the current DpsLab
   repository;
2. whether the first implementation covers only
   `static_fallback_template` or also the structural fields for imported
   analytical evidence;
3. the initial supported WoW product (`Retail` only is recommended);
4. whether signing remains an interface placeholder until a separate key
   management decision (recommended);
5. the exact implementation allowlist and protected paths.

Design verdict: `comparison_result_productization_design_ready_for_human_review`.

## Completed implementation authorization — Knowledge envelope schema 0.1

Daniel approved the closed contract on 2026-07-29. The implementation was
audited, committed as `ee1822aed19f4aa46507f0e09d7b735ae36491ce`, published
to `main`, and verified by GitHub Actions run `30622148623` on 2026-07-31.
That run completed successfully in all three lanes. The authorization below is
consumed historical evidence and cannot authorize another edit, test run,
commit, push, SimulationCraft invocation, addon change, UI, network operation,
real key, or live recommendation.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "knowledge_envelope_schema_0_1",
  "title": "Closed Retail knowledge envelope schema and pure validator",
  "baseline_commit": "0c11f0971c703e740b1d2b4237e685e0cc861f08",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "knowledge_envelope_schema_0_1-20260729-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-29T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/knowledge_envelope.py",
      "desktop-app/tests/test_knowledge_envelope.py",
      "knowledge/schemas/knowledge_envelope_0_1.json",
      "knowledge/fixtures/static_fallback_template_synthetic_0_1.json",
      "docs/KNOWLEDGE_ENVELOPE.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/knowledge_envelope_schema_0_1/implementation.json",
      ".dpslab/quality-gates/knowledge_envelope_schema_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/src/dpslab/__main__.py",
      "desktop-app/src/dpslab/comparison_*.py",
      "desktop-app/src/dpslab/runner.py",
      "desktop-app/tests/test_comparison_*.py",
      "desktop-app/tests/test_runner.py",
      "tools/**",
      "addons/**",
      "comparisons/**",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "results/**",
      "config/**",
      "flasil.simc",
      "AGENTS.md",
      "docs/PROJECT_BRIEF.md",
      "docs/ROADMAP.md"
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
        "test_knowledge_envelope.py",
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
    "baseline_test_count": 267,
    "minimum_test_count": 281
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "scenarios/st_lightmovement_300s_v1.toml": "93187338a61d1cfc330f5262abb0b9183acb727d310099eca7917138207c09aa",
    "comparisons/flasil_neck_50228_vs_249368_v1.toml": "68282327263d4f75797181521419f11aa54fdecf16f1634c0b3b1b2ac6fdbe4c",
    "comparisons/simulationcraft_identity_manifest_0_1.json": "0a305a5991de0d3c1c4aafbb1756351b6643366a663f532877d6e137b69542eb",
    "docs/COMPARISON_RESULT_FLASIL_NECK_V1.md": "9b8fd4b512e680149e219ab8834563019339bfcdf6b9ef3805ff62594507c229"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "exactly the six authorized versioned paths in the delta",
    "Retail is the only accepted WoW product in schema 0.1",
    "the envelope structurally supports static_fallback_template and imported_analytical_evidence while the only fixture is synthetic static fallback data",
    "character_observation is reserved as an evidence tier but no observation ingestion is implemented",
    "closed root and nested object families reject unknown fields",
    "canonical JSON bytes use UTF-8, sorted keys, compact separators, and exactly one trailing LF",
    "payload_sha256 covers canonical UTF-8 bytes of the envelope after omitting exactly integrity.payload_sha256 and integrity.signature while retaining integrity.signature_algorithm and integrity.publisher_key_id",
    "focused tests reject hashes calculated by including either omitted integrity field and reject projections that omit signature_algorithm or publisher_key_id",
    "signature fields are validated placeholders only and no cryptographic signing or key storage is implemented",
    "compatibility rejects unknown products, reversed or malformed build ranges, incompatible class or specialization, and expired evidence",
    "an unknown or out-of-range build produces guidance_unavailable and never selects newest",
    "race applicability is optional and defaults to shared guidance rather than generating race-specific claims",
    "guidance statements are typed, ordered, prerequisite-bound, and cannot contain executable code",
    "synthetic fixture contains no live balance claim, proprietary simulator logic, personal path, credential, or real character fingerprint",
    "at least 14 focused tests, at least 281 total functional tests, and all tools tests pass",
    "protected hashes remain intact and simulationcraft_invoked remains false"
  ],
  "express_exclusions": [
    "live class, specialization, race, talent, stat-weight, or best-in-slot recommendations",
    "addon code, Lua, UI, SavedVariables, or WoW API access",
    "desktop UI, networking, downloads, updater activation, rollback execution, or release channels",
    "real signatures, key generation, key storage, certificates, secrets, or trust-store changes",
    "patch-note fetching, parsing, mapping, or publication",
    "telemetry, analytics, accounts, donations, marketing, distribution, or releases",
    "SimulationCraft invocation, comparisons, runs, results, baselines, profiles, scenarios, or variants",
    "new dependencies, pyproject changes, CLI integration, GitHub workflow changes, commits, pushes, tags, branches, or settings"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Closure evidence:

- implementation audit: `knowledge_envelope_schema_0_1_audit_approved`;
- commit audit: `knowledge_envelope_schema_0_1_commit_audit_approved`;
- published commit: `ee1822aed19f4aa46507f0e09d7b735ae36491ce`;
- GitHub Actions: run `30622148623`, success, three lanes;
- focal tests: 25; functional tests: 292; tools tests: 52;
- final state: `knowledge_envelope_schema_0_1_published_ci_passed`.

## Completed implementation authorization — Static template catalog 0.1

Daniel approved the completed design and authorized only the closed synthetic
catalog implementation below. It does not authorize real class or balance
data, live recommendations, SimulationCraft, addon or UI work, networking,
packaging, signing, commit, publication, or a later block.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "static_template_catalog_0_1",
  "title": "Implement a governed synthetic static fallback template catalog",
  "baseline_commit": "020239c4a3138b68a2c9983b3a443f660f60b878",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "static_template_catalog_0_1-implementation-20260731-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-31T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/static_template_catalog.py",
      "desktop-app/tests/test_static_template_catalog.py",
      "knowledge/schemas/static_template_catalog_0_1.json",
      "knowledge/catalogs/static_template_catalog_synthetic_0_1.json",
      "docs/STATIC_TEMPLATE_CATALOG.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/src/dpslab/knowledge_envelope.py",
      "desktop-app/tests/test_knowledge_envelope.py",
      "knowledge/schemas/knowledge_envelope_0_1.json",
      "knowledge/fixtures/static_fallback_template_synthetic_0_1.json",
      "tools/**",
      "addons/**",
      "comparisons/**",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "results/**",
      "config/**",
      "flasil.simc",
      "AGENTS.md",
      "docs/KNOWLEDGE_ENVELOPE.md",
      "docs/PROJECT_BRIEF.md",
      "docs/ROADMAP.md"
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
        "tests.test_static_template_catalog",
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
    "baseline_test_count": 292,
    "minimum_test_count": 312
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "scenarios/st_lightmovement_300s_v1.toml": "93187338a61d1cfc330f5262abb0b9183acb727d310099eca7917138207c09aa",
    "comparisons/flasil_neck_50228_vs_249368_v1.toml": "68282327263d4f75797181521419f11aa54fdecf16f1634c0b3b1b2ac6fdbe4c",
    "comparisons/simulationcraft_identity_manifest_0_1.json": "0a305a5991de0d3c1c4aafbb1756351b6643366a663f532877d6e137b69542eb",
    "docs/COMPARISON_RESULT_FLASIL_NECK_V1.md": "9b8fd4b512e680149e219ab8834563019339bfcdf6b9ef3805ff62594507c229"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "define catalog identity, versioning, lifecycle, review states, provenance, compatibility, invalidation, and rollback boundaries",
    "exclude databases and simulation-history stores from the canonical architecture",
    "define current-only activation with stale knowledge failing closed",
    "define role-aware objective priority for damage, tank, and healer specializations",
    "use only synthetic examples and one synthetic specialization fixture proposal",
    "preserve the knowledge envelope 0.1 schema as the authoritative item format",
    "separate catalog metadata from envelope payloads and from future distribution manifests",
    "define draft, pending_review, approved, rejected, deprecated, and withdrawn states without treating technical validity as approval",
    "require explicit human approval before any template becomes eligible for a future release",
    "keep unknown or incompatible knowledge fail-closed as guidance_unavailable",
    "implement exactly the six authorized paths with no new dependency or generated state",
    "make no live class balance, stat weight, talent, race, equipment, best-in-slot, or rotation claim",
    "pass at least 20 focused catalog tests, at least 312 functional tests, and all tools tests",
    "leave commit, publication, real data, and every later block unauthorized"
  ],
  "express_exclusions": [
    "files outside the six-path implementation allowlist or new dependencies",
    "databases, warehouses, simulation-history services, retrospective recommendation stores, or server-side catalog state",
    "real World of Warcraft data, patch-note ingestion, web research, or live recommendations",
    "SimulationCraft invocation, comparison execution, runs, results, baselines, profiles, scenarios, or variants",
    "addon code, Lua, UI, SavedVariables, WoW API access, desktop UI, or packaging",
    "network access, downloads, update channels, signing, keys, secrets, releases, or distribution",
    "commits, pushes, tags, branches, pull requests, GitHub settings, workflow changes, or later blocks"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict:
`static_template_catalog_0_1_implementation_authorized`.

### Local implementation and procedural audit result

Implementation remained limited to the six authorized versioned paths. The
catalog fixture is canonical, synthetic, `pending_review`, incomplete by
design, and therefore unavailable for guidance. No approval was inferred.

- focused catalog tests: 24/24 passed;
- functional suite: 316/316 passed, exit code 0;
- tools suite: 52/52 passed, exit code 0;
- all six protected hashes matched the contract;
- no SimulationCraft, comparison, real data, database, addon, UI, network,
  commit, push, or later block was used;
- audit separation is procedural and declared, not cryptographic identity
  separation.

Local verdict: `static_template_catalog_0_1_audit_passed_ready_for_approval`.
The implementation authorization is now consumed for further edits or test
runs. A commit requires a separate explicit human decision.

Publication closure:

- commit: `18315a99297d75d47da8e9dff082e3d4d3c6b2fe`;
- GitHub Actions run: `30631876146`;
- Policy and contract, Tools tests, and Functional suite: success;
- final state: `static_template_catalog_0_1_published_ci_passed`.

### Design output — catalog boundary

The catalog is a governed index of knowledge envelopes. It does not duplicate
the envelope schema, contain executable behavior, or decide distribution. Each
catalog entry points to one immutable canonical envelope by repository-relative
path and SHA-256. Catalog validity proves structure and integrity only; it does
not prove that guidance is correct or approved.

The catalog and its entries use independent identities and versions:

- `catalog_id` identifies the catalog lineage;
- `catalog_version` identifies this catalog schema (`0.1`);
- `content_version` advances when membership or governance metadata changes;
- `entry_id` identifies one catalog membership record;
- `package_id` remains owned by the referenced knowledge envelope;
- `envelope_sha256` covers the complete canonical envelope bytes, while the
  envelope's own `payload_sha256` retains its existing projection semantics.

Catalog order is non-semantic. Selection may never depend on array position or
filesystem discovery order.

### Closed catalog families

The initial catalog document should contain exactly these root families:

- `catalog_version`;
- `identity`: catalog ID, content version, channel, and creation time;
- `entries`: a non-empty list of closed membership records;
- `integrity`: exactly `catalog_sha256` and `hash_algorithm`.

`hash_algorithm` is exactly `sha256`. `catalog_sha256` covers the canonical
UTF-8 catalog bytes after omitting exactly `integrity.catalog_sha256`; the
`integrity` object and its `hash_algorithm` member remain present in the hashed
projection. No other root, nested, review, lifecycle, or entry field may be
omitted. Focused tests must reject a hash that includes `catalog_sha256` and a
projection that omits `hash_algorithm` or any additional field.

Each entry should contain exactly:

- `entry_id`;
- `envelope_path` and `envelope_sha256`;
- copied indexing keys: WoW product, build and interface bounds, class,
  specialization, optional race applicability, level bounds, role, and content
  contexts;
- `lifecycle_state`;
- `review`: decision ID, reviewer ID, decision time, and review notes tokens;
- `supersedes_entry_ids`;
- `invalidation_reasons`.

Copied indexing keys are search accelerators, not a second authority. They must
equal the referenced envelope exactly. Any mismatch invalidates the catalog.

### Lifecycle and human authority

The lifecycle is closed to these states:

1. `draft`: incomplete work product; never selectable;
2. `pending_review`: structurally complete and awaiting human review; never
   selectable;
3. `approved`: explicitly approved by a recorded human decision; potentially
   selectable only after all compatibility and integrity checks pass;
4. `rejected`: reviewed and refused; never selectable;
5. `deprecated`: formerly approved but superseded or approaching retirement;
   never selected for a new context in version 0.1;
6. `withdrawn`: invalidated after approval; never selectable.

Technical validation cannot create or infer `approved`. Review fields embedded
in the catalog are descriptive and untrusted for authority purposes. An
`approved` entry becomes eligible only when the caller injects separately
verified external approval evidence from a future trusted authority provider.
That evidence must bind exactly:

- `catalog_id` and catalog `content_version`;
- `entry_id`, referenced envelope `package_id`, and `envelope_sha256`;
- decision `approved`, a non-empty decision ID, an authorized reviewer ID, and
  a UTC decision timestamp.

Every bound value must equal the validated catalog and envelope. Missing,
untrusted, stale, mismatched, rejected, or differently scoped approval evidence
returns `guidance_unavailable`. Version 0.1 accepts approval evidence only as an
injected immutable value; it does not read accounts, files, networks, keys, or
approval services. The synthetic fixture remains `pending_review`, so the first
implementation needs only the fail-closed interface and negative evidence
tests, not real approval evidence.

The materialized `review` family is closed to `decision_id`, `reviewer_id`,
`decided_at`, `notes`, `prior_approval_decision_id`, and
`transition_reason`. Its exact state matrix is:

| State | Final decision fields | Prior approval | Transition reason |
| --- | --- | --- | --- |
| `draft` | all null | null | null |
| `pending_review` | all null | null | null |
| `approved` | decision ID, reviewer ID, UTC time required | null | null |
| `rejected` | decision ID, reviewer ID, UTC time required | null | required |
| `deprecated` | new decision ID, reviewer ID, UTC time required | required | required |
| `withdrawn` | new decision ID, reviewer ID, UTC time required | required | required |

Here “final decision fields” means exactly `decision_id`, `reviewer_id`, and
`decided_at`. `notes` is always a list of unique tokens and may be empty.
Required strings are non-empty tokens. No other null/non-null combination is
valid. `prior_approval_decision_id` is a reference only; external evidence must
also prove that prior approval before a deprecated or withdrawn record is
accepted as coherent.

State transitions are append-only governance events in future work. Version
0.1 validates only the materialized current state and does not implement an
event log, database, or approval UI.

### Eligibility and collision rules

A catalog entry is eligible only when all of the following are true:

1. the catalog and referenced envelope are canonical and hash-valid;
2. the entry is `approved` by explicit human evidence;
3. copied indexing keys equal the referenced envelope;
4. the envelope tier is `static_fallback_template`;
5. product, build, interface, class, specialization, level, content context,
   optional race, expiry, and safety constraints all match;
6. no catalog or entry invalidation applies.

All other cases produce `guidance_unavailable`. The catalog must reject:

- duplicate `entry_id` or duplicate referenced `package_id`;
- missing, absolute, traversing, or non-JSON envelope paths;
- envelope paths outside `knowledge/fixtures/` in the first implementation;
- overlapping `approved` entries for the same selection dimensions;
- supersession references that are missing, self-referential, cyclic, or point
  to a different subject/compatibility lineage;
- any entry whose state or review evidence is contradictory.

Version 0.1 has no automatic tie-breaker. Newest version, widest build range,
array order, or channel must never silently resolve an ambiguity.

### Current activation and historical evidence policy

DpsLab does not require a database, data warehouse, or opaque retrospective
recommendation store as a canonical product layer. Canonical knowledge remains
a versioned set of immutable envelope and evidence files plus a single active
catalog. Local indexes, if a future reader needs them for speed, must be fully
reconstructible from those files and disposable.

Only currently applicable knowledge may become eligible for guidance. A
catalog build must therefore bind every entry to explicit Retail build and
interface ranges, evidence expiry, source capture time, and source revision.
When any required source is unknown, stale, superseded, contradictory, or
outside its supported range, the affected entry becomes ineligible and the
result is `guidance_unavailable`.

“Current” never means “latest file found.” It means that all mandatory source
families declared for that specialization and context have been captured,
validated, reconciled, reviewed, and approved for the same supported game
range. The system must not claim complete coverage when a mandatory source is
missing. Historical evidence is retained when useful for audit, regression
analysis, explicit before/after comparison, explanation of changes, rollback,
or recovery. It may be queried only through an explicitly historical analysis
mode that labels the compared builds and provenance. Historical evidence never
silently becomes current guidance and is never extrapolated into a new patch.

### Source coverage and freshness

A later `catalog_candidate_pipeline_0_1` should maintain a versioned source
coverage manifest, not a database. For each specialization and supported
context it must declare the source families needed to evaluate DPS-affecting
parameters, including as applicable:

- game build and interface metadata;
- class, specialization, role, spell, aura, resource, cooldown, and mechanic
  definitions;
- talents and loadout constraints;
- equipment, item effects, set effects, embellishments, trinkets, weapons, and
  stat rules;
- race applicability when a documented performance dependency exists;
- encounter or content-context constraints;
- corrections, hotfixes, and authoritative patch changes;
- DpsLab review decisions and explicit limitations.

Each source family needs an authoritative source identifier, captured revision
or timestamp, content hash, license/use classification, freshness rule,
applicability range, and last successful review. Automated capture may create
only `pending_review` candidates and stale/invalidation alerts. It cannot infer
approval, publish content, or silently fill missing parameters. Manual imports
enter the same quarantine and validation path.

The project goal is complete declared coverage of every parameter family that
materially affects supported DPS guidance. Because external information can be
late, incomplete, or contradictory, completeness is measured against the
coverage manifest and exposed honestly; it is never asserted as an
unverifiable universal guarantee.

### Role-aware optimization hierarchy

The product objective is not identical for every specialization. Every future
template must declare one role policy matching the envelope's `subject.role`.
Role policy changes applicability and priority, but never authorizes gameplay
automation.

1. `damage`
   - Primary objective: improve expected damage for the supported context.
   - Hard constraints: character safety, encounter obligations, target rules,
     resource legality, and declared unsupported variables.
   - Guidance must not trade required mechanics or survival for theoretical
     damage that cannot be executed safely.
2. `tank`
   - Primary objective: remain alive and satisfy mitigation, active-defense,
     threat, positioning, and encounter obligations.
   - Secondary objective: improve damage only inside the survivability and
     mitigation budget validated for the supported context.
   - When incoming damage, mitigation state, healer support, or encounter risk
     is unknown, the catalog must not recommend a damage-first alternative.
3. `healer`
   - Primary objective: maintain required ally survival, healing coverage,
     dispels, emergency capacity, and encounter obligations.
   - Secondary objective: improve damage during safe healing windows.
   - Damage abilities that directly produce healing or required resources may
     participate in the healing plan, but their priority is evaluated by their
     healing contribution first and damage contribution second.
   - When ally risk, healing demand, or resource safety is unknown, damage
     guidance must degrade or become unavailable rather than compete with
     required healing.

The catalog 0.1 implementation may validate the existing closed `role` field,
role-policy identity, and governance consistency using synthetic data. It does
not yet have enough live observation inputs to calculate incoming damage,
mitigation budgets, ally health, healing demand, or safe damage windows. Those
runtime inputs belong to separately designed addon/desktop observation
contracts. Until then, no static template may claim that a dynamic tank or
healer safety condition has been satisfied.

Before any real template program begins, human review must define per-role and
per-context mandatory source families, safety constraints, unavailable-state
behavior, and validation evidence. A later schema revision is required if
these constraints cannot be represented without overloading generic guidance
tokens; catalog implementation must not silently extend knowledge envelope
0.1.

### Synthetic specialization proposal

The sole proposed catalog fixture references the existing synthetic envelope
`static_fallback_template_synthetic_0_1.json`. Its copied subject remains the
synthetic class/spec tuple already present in that fixture, and its state is
`pending_review`. Names and guidance tokens remain explicitly synthetic. It is
not an Arms Warrior recommendation merely because the numeric fixture IDs
coincide with real game identifiers, and no user-facing class label may be
derived from them in this block.

The fixture must contain no real balance data, stat weights, talents,
equipment, rotations, proprietary simulator logic, personal paths, character
fingerprints, credentials, or claims of game-patch currency.

### Separation from packaging and distribution

This catalog is repository-local versioned content. It does not define:

- update manifests, signatures, keys, downloads, channels, or rollback files;
- addon serialization or Lua consumption;
- desktop packaging or installation;
- patch-note intake or automatic invalidation;
- recommendation presentation or localization text.

Those remain separate future contracts. A later packager may consume an
approved catalog, but it must not mutate lifecycle state or reinterpret human
approval.

### Proposed implementation allowlist

A future implementation contract should be limited to exactly:

1. `desktop-app/src/dpslab/static_template_catalog.py`;
2. `desktop-app/tests/test_static_template_catalog.py`;
3. `knowledge/schemas/static_template_catalog_0_1.json`;
4. `knowledge/catalogs/static_template_catalog_synthetic_0_1.json`;
5. `docs/STATIC_TEMPLATE_CATALOG.md`;
6. `docs/NEXT_TASK.md`.

The existing envelope schema, validator, fixture, CI workflow, comparison
assets, profiles, scenarios, results, addon paths, and project governance
documents remain protected and read-only.

The future focused suite should contain at least 20 tests covering canonical
bytes, catalog hash projection, closed fields, path confinement, duplicate
identities, copied-key equality, every lifecycle state, contradictory review
evidence, collision rejection, supersession failures, expiry, and fail-closed
selection. It must additionally reject database or remote-state dependencies,
stale or incomplete source coverage, role-policy mismatch, damage-first tank
guidance without satisfied synthetic safety constraints, and healer damage
guidance without satisfied synthetic healing constraints. The functional floor
must be at least the then-current 292 tests, and all tools tests must pass.
SimulationCraft must remain uninvoked.

Implementation-contract proposal verdict:
`static_template_catalog_0_1_design_ready_for_human_review`.

## Consumed design authorization — Current knowledge candidate pipeline 0.1

This contract authorizes documentation-only design for determining whether the
source coverage required by a specialization and context is current, complete,
and reviewable. It does not authorize source capture, web access, real WoW
data, catalog mutation, approval, publication, or implementation.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "catalog_candidate_pipeline_design_0_1",
  "title": "Design current activation, historical evidence, and pending-review candidates",
  "baseline_commit": "18315a99297d75d47da8e9dff082e3d4d3c6b2fe",
  "authorization": {
    "status": "design_only",
    "authorization_id": "catalog_candidate_pipeline_design_0_1-20260731-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-31T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/**",
      "knowledge/**",
      "tools/**",
      "addons/**",
      "comparisons/**",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "results/**",
      "config/**",
      "flasil.simc",
      "AGENTS.md",
      "docs/STATIC_TEMPLATE_CATALOG.md",
      "docs/KNOWLEDGE_ENVELOPE.md",
      "docs/PROJECT_BRIEF.md",
      "docs/ROADMAP.md"
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
    "baseline_test_count": 316,
    "minimum_test_count": 316
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/static_template_catalog.py": "47654521f1b80173c64eb1887502c5dabd4ecdaa14f1d9c1e872ba546e8b4307",
    "knowledge/schemas/static_template_catalog_0_1.json": "826f974ca2a2165544795063ee4231644ac6d9579666416f4d4d427cee583d71",
    "knowledge/catalogs/static_template_catalog_synthetic_0_1.json": "9f0dbf2066444ec0753980ffb074a0ba081d9e5a7327079ef8503dcd838dfba0",
    "knowledge/fixtures/static_fallback_template_synthetic_0_1.json": "0aa67412ee12876998a9ae2bb49c5698463aaac332a2c17ce6169dcf9125d8aa"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "design a versioned source coverage manifest rather than a database",
    "define mandatory source families by role and supported content context",
    "bind every capture to source identity, revision, time, hash, license classification, applicability, and freshness policy",
    "treat automated and manual intake identically as quarantined pending_review candidates",
    "make missing, stale, conflicting, incomplete, or unsupported coverage fail closed",
    "preserve human approval as an external authority that automation cannot infer",
    "define current-only activation without selecting the newest file by guess",
    "retain content-addressed historical evidence for explicit audit, comparison, regression, rollback, and recovery uses",
    "keep historical analysis clearly labeled and unable to become current guidance implicitly",
    "produce a closed synthetic implementation proposal and leave it unauthorized",
    "use no real game data, source download, network access, or live recommendation"
  ],
  "express_exclusions": [
    "implementation, schemas, fixtures, code, tests, dependencies, or generated artifacts",
    "databases, warehouses, retrospective recommendation stores, or remote catalog state",
    "web research, patch-note retrieval, APIs, downloads, scraping, or network access",
    "real classes, specializations, races, stats, talents, equipment, rotations, or balance claims",
    "catalog or envelope mutation, approval, signing, packaging, release, or distribution",
    "SimulationCraft, comparisons, runs, results, baselines, profiles, scenarios, or variants",
    "addon, Lua, WoW API access, desktop UI, commits, pushes, or later blocks"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict:
`catalog_candidate_pipeline_design_0_1_authorized`.

Design publication closure:

- commit: `ce33cf0f5016fc38371f8ece3e4cb3bbe4f48c48`;
- GitHub Actions run: `30632412176`;
- Policy and contract, Tools tests, and Functional suite: success;
- final state: `catalog_candidate_pipeline_design_0_1_published_ci_passed`.

### Design output — current activation and historical evidence boundary

The candidate pipeline is a deterministic quarantine and coverage-checking
boundary. It does not fetch sources, decide truth, approve guidance, or publish
a catalog. Its output is only a synthetic candidate report whose maximum
lifecycle state is `pending_review`. The initial implementation uses immutable
files; a future storage optimization is allowed only if it preserves identical
content hashes, provenance, exportability, and fail-closed behavior.

#### Versioned source coverage manifest

Each supported specialization and content context must declare a closed list of
mandatory source families. A family declaration contains:

- `family_id` and schema version;
- supported Retail build and interface ranges;
- applicable class, specialization, role, race dependency, level, and context;
- authoritative source owner and stable source identifier;
- capture method classification: manual, first-party API, signed artifact, or
  reviewed document snapshot;
- license/use classification and permitted derived use;
- required revision identifier, capture time, content SHA-256, and media type;
- freshness maximum age and explicit invalidation triggers;
- required reviewer capability and evidence requirements.

The manifest is immutable and repository-versioned. It declares what complete
coverage means; it does not contain live guidance. One active manifest is
selected explicitly by compatibility and human release policy, never by
filename order or modification time.

#### Historical evidence archive

Validated source captures are content-addressed and append-only. Superseded
captures may be retained with their source identity, revision, captured time,
hash, license classification, applicability range, invalidation reason, and
successor reference. Retention enables:

- auditing why guidance changed;
- comparing mechanics or parameters between named game builds;
- detecting regressions in parsers, mappings, and candidate generation;
- reproducing a prior release decision;
- rollback and disaster recovery;
- evaluating whether a previously observed rule remains stable.

Historical access is an explicit analytical operation. Every result labels the
source builds, capture ages, hashes, and limitations. It cannot feed the active
catalog, fill missing current coverage, or produce recommendations unless the
same evidence is separately revalidated and approved for the current build.
Retention policy may compact redundant raw bytes later, but canonical metadata,
hashes, decisions, and required reproducibility evidence must remain portable.

#### Quarantine model

Every captured source enters the same quarantine regardless of whether capture
was automated or manual. Validation proceeds in this order:

1. source identity and allowed acquisition classification;
2. exact bytes, media type, and SHA-256;
3. captured revision and UTC time;
4. license/use compatibility;
5. Retail build, interface, subject, role, and context applicability;
6. freshness and invalidation policy;
7. completeness against all mandatory families;
8. contradiction detection across sources covering the same fact family;
9. deterministic candidate construction.

Failure at any stage produces a static reason code and no candidate. A valid
result produces only `pending_review`; it cannot modify the current catalog or
an envelope. Raw source bytes, personal paths, credentials, tokens, and private
account information are never embedded in candidate metadata.

#### Currentness and invalidation

`current` means every mandatory family is present, hash-valid, license-usable,
applicable to the exact supported build range, within its declared freshness
window, mutually coherent, and reviewed for that same range. Any missing,
unknown, stale, superseded, withdrawn, or contradictory family makes coverage
incomplete.

Patch notes or hotfix notices may later invalidate affected families and create
review alerts. They cannot generate new guidance or reapprove an old template.
An unknown game build returns `coverage_unavailable`; it never falls back to
the numerically newest known build.

#### Role-aware mandatory families

All roles require game-build metadata, specialization mechanics, talents,
equipment effects, stat rules, encounter constraints, corrections, and review
decisions. Additional mandatory families are role-specific:

- damage: target model, resource constraints, damage windows, and required
  encounter obligations;
- tank: incoming-damage model, mitigation and active-defense rules, threat,
  positioning obligations, and explicit survival constraints;
- healer: ally-risk model, healing coverage, dispels, emergency capacity,
  resource safety, and the healing contribution of damaging abilities.

Missing tank or healer safety families prevents damage-oriented candidates.
Static coverage cannot claim that a dynamic safety condition is satisfied.

#### Automation boundary

A future capture adapter may be scheduled to notice source revisions, but each
adapter must be separately authorized for one named source family and must
store only a content-addressed snapshot plus sanitized metadata. Network
credentials, rate limits, robots/licensing terms, and redistribution rights are
source-specific decisions and are outside this block.

Automation may create alerts and `pending_review` candidates. Only a verified
human authority may approve a candidate, build a knowledge envelope, add it to
the catalog, sign a release, or distribute it. Approval remains bound to exact
hashes and supported ranges.

#### Proposed synthetic implementation

The smallest implementation should validate a synthetic coverage manifest and
produce a pure coverage assessment from injected synthetic current and prior
capture records. It should use exactly these seven versioned paths:

1. `desktop-app/src/dpslab/source_coverage.py`;
2. `desktop-app/tests/test_source_coverage.py`;
3. `knowledge/schemas/source_coverage_manifest_0_1.json`;
4. `knowledge/manifests/source_coverage_synthetic_0_1.json`;
5. `knowledge/snapshots/source_capture_synthetic_0_1.json`;
6. `docs/SOURCE_COVERAGE.md`;
7. `docs/NEXT_TASK.md`.

The first fixture should describe a synthetic damage specialization and remain
incomplete or `pending_review`. At least 24 focused tests should cover closed
fields, canonical bytes, hashes, duplicate families, current versus historical
capture isolation, explicit historical comparison labeling, build and subject
compatibility, missing coverage, expiry, contradictions, license rejection,
unknown builds, role-policy completeness, deterministic ordering, sanitized
errors, and the prohibition on approval or catalog mutation. The functional
floor is 340 tests and all tools tests must pass.

It must not include source fetching, URL handling, HTTP libraries, real patch
notes, real WoW identifiers or balance data, databases, catalog writes,
SimulationCraft, addon/UI behavior, credentials, signing, or publication.

Design verdict:
`catalog_candidate_pipeline_design_0_1_ready_for_implementation_contract`.

## Completed implementation authorization — Source coverage manifest 0.1

Daniel's expanded technical authorization permits this closed synthetic
implementation. It validates current coverage and explicitly labeled
historical evidence without fetching sources or using real WoW data.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "source_coverage_manifest_0_1",
  "title": "Implement synthetic current coverage and historical evidence validation",
  "baseline_commit": "ce33cf0f5016fc38371f8ece3e4cb3bbe4f48c48",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "source_coverage_manifest_0_1-20260731-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-31T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/source_coverage.py",
      "desktop-app/tests/test_source_coverage.py",
      "knowledge/schemas/source_coverage_manifest_0_1.json",
      "knowledge/manifests/source_coverage_synthetic_0_1.json",
      "knowledge/snapshots/source_capture_synthetic_0_1.json",
      "docs/SOURCE_COVERAGE.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/src/dpslab/knowledge_envelope.py",
      "desktop-app/src/dpslab/static_template_catalog.py",
      "desktop-app/tests/test_knowledge_envelope.py",
      "desktop-app/tests/test_static_template_catalog.py",
      "knowledge/schemas/knowledge_envelope_0_1.json",
      "knowledge/schemas/static_template_catalog_0_1.json",
      "knowledge/fixtures/**",
      "knowledge/catalogs/**",
      "tools/**",
      "addons/**",
      "comparisons/**",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "results/**",
      "config/**",
      "flasil.simc",
      "AGENTS.md"
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
        "tests.test_source_coverage",
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
    "baseline_test_count": 316,
    "minimum_test_count": 340
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/static_template_catalog.py": "47654521f1b80173c64eb1887502c5dabd4ecdaa14f1d9c1e872ba546e8b4307",
    "knowledge/schemas/static_template_catalog_0_1.json": "826f974ca2a2165544795063ee4231644ac6d9579666416f4d4d427cee583d71",
    "knowledge/catalogs/static_template_catalog_synthetic_0_1.json": "9f0dbf2066444ec0753980ffb074a0ba081d9e5a7327079ef8503dcd838dfba0",
    "knowledge/fixtures/static_fallback_template_synthetic_0_1.json": "0aa67412ee12876998a9ae2bb49c5698463aaac332a2c17ce6169dcf9125d8aa"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "implement exactly the seven authorized versioned paths without new dependencies",
    "validate canonical manifest and capture archive bytes with closed SHA-256 projections",
    "assess current coverage only from compatible nonhistorical captures",
    "retain historical captures for explicit labeled comparison without filling current gaps",
    "reject missing, duplicate, stale, invalidated, contradictory, license-incompatible, or unknown-build evidence",
    "enforce role-specific mandatory source families and fail closed for missing tank or healer safety coverage",
    "produce at most pending_review and never infer approval or mutate a catalog",
    "use only synthetic identifiers and content",
    "pass at least 24 focused tests, at least 340 functional tests, and all tools tests",
    "preserve all protected hashes and avoid SimulationCraft, network access, databases, commits during implementation, and later blocks"
  ],
  "express_exclusions": [
    "source fetching, URLs, HTTP clients, APIs, scraping, downloads, or network access",
    "real patch notes, classes, specializations, races, stats, talents, equipment, rotations, or balance data",
    "databases, warehouses, remote catalog state, credentials, secrets, or personal paths",
    "catalog or envelope writes, approval, signing, packaging, release, or distribution",
    "SimulationCraft, comparisons, runs, results, baselines, addon, Lua, WoW API access, or UI",
    "changes outside the seven-path allowlist, commits during implementation, pushes, or later blocks"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict:
`source_coverage_manifest_0_1_implementation_authorized`.

### Local implementation and procedural audit result

The implementation remained within the seven authorized paths. The synthetic
manifest and capture archive are canonical and hash-bound. Current coverage
uses only fresh compatible `current` captures, while retained captures are
available only through explicitly labeled historical comparison.

- focused source-coverage tests: 27/27 passed;
- functional suite: 343/343 passed, exit code 0;
- tools suite: 52/52 passed, exit code 0;
- all protected hashes remained unchanged;
- no source retrieval, real data, database, SimulationCraft, catalog mutation,
  addon, UI, network, signing, packaging, or later block was used;
- audit separation is procedural and declared, not cryptographic identity
  separation.

Local verdict: `source_coverage_manifest_0_1_audit_passed_ready_for_approval`.
The implementation authorization is consumed for further edits and test runs;
technical closure may proceed under Daniel's expanded authorization.

Publication closure:

- commit: `61fb6359cd22193b9fc1a8278ff6289b88d018eb`;
- GitHub Actions run: `30633565923`;
- Policy and contract, Tools tests, and Functional suite: success;
- final state: `source_coverage_manifest_0_1_published_ci_passed`.

## Consumed design contract — Patch evidence intake 0.1

This contract authorizes documentation-only design for converting injected
patch and hotfix evidence into sanitized, reviewable change candidates. It does
not authorize network access, source retrieval, real patch data, implementation,
catalog mutation, approval, or publication.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "patch_evidence_intake_design_0_1",
  "title": "Design governed patch and hotfix evidence intake",
  "baseline_commit": "61fb6359cd22193b9fc1a8278ff6289b88d018eb",
  "authorization": {
    "status": "design_only",
    "authorization_id": "patch_evidence_intake_design_0_1-20260731-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-31T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/**",
      "knowledge/**",
      "tools/**",
      "addons/**",
      "comparisons/**",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "results/**",
      "config/**",
      "flasil.simc",
      "AGENTS.md",
      "docs/SOURCE_COVERAGE.md",
      "docs/STATIC_TEMPLATE_CATALOG.md",
      "docs/PROJECT_BRIEF.md",
      "docs/ROADMAP.md"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": ".",
      "argv": ["python", "-m", "unittest", "tools.tests.test_github_automation", "-v"],
      "environment": {"PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 343,
    "minimum_test_count": 343
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/source_coverage.py": "85bfddadfd8fc5d6704d8bba9df223db27e6123a09e835629d3b8765afab63a7",
    "knowledge/schemas/source_coverage_manifest_0_1.json": "99bac38dbc4bbdeda035b722df427a6c0aa441e58759ddbb73712745616528e6",
    "knowledge/manifests/source_coverage_synthetic_0_1.json": "519a165dc7bbb4a663a8086076fc35e2b249d1720df8aafdd77019e29623e573",
    "knowledge/snapshots/source_capture_synthetic_0_1.json": "34439c8b4e541d03225eac97d20ec9526f1de8c4035f64b3be867de12dc9f07f"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "define a source-neutral injected evidence record with canonical bytes and hashes",
    "separate source capture from semantic interpretation and from approval",
    "map changes only to canonical parameter-family identifiers and explicit supported ranges",
    "retain superseded evidence for labeled historical comparison and rollback",
    "produce only pending_review change candidates and invalidation alerts",
    "reject ambiguous, duplicate, unsigned where required, stale, unsupported, or license-incompatible evidence",
    "define source-specific adapters as later separately authorized boundaries",
    "preserve current guidance until an exact replacement is reviewed and approved",
    "produce a closed synthetic implementation proposal and leave it unauthorized"
  ],
  "express_exclusions": [
    "implementation, code, schemas, fixtures, tests, dependencies, or generated artifacts",
    "URLs, HTTP clients, APIs, scraping, downloads, browsers, or network access",
    "real patch notes, hotfixes, game data, balance data, or live recommendations",
    "automatic semantic inference, approval, catalog mutation, signing, packaging, release, or distribution",
    "databases, credentials, secrets, SimulationCraft, addon, UI, commits, pushes, or later blocks"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict:
`patch_evidence_intake_design_0_1_authorized`.

### Design output — patch evidence quarantine

The intake boundary receives evidence records as injected immutable values. It
does not connect to a website, API, launcher, game client, or account. A future
source adapter is responsible only for obtaining exact bytes under a separately
approved source-specific policy; this core validates and classifies the injected
record without trusting its prose.

#### Three separated layers

1. `source_capture`
   - exact source identity, revision, publication and capture times, media type,
     content hash, acquisition class, license classification, authenticity
     evidence, and supported product/build range;
2. `change_assertion`
   - source-provided subject identifiers, operation kind, old/new tokens when
     explicitly present, citations into the captured bytes, and uncertainty;
3. `review_candidate`
   - canonical parameter-family mapping, affected coverage families, possible
     invalidations, required reviewers, and static limitations.

No layer may infer human approval. Free-form patch prose is evidence, not an
executable instruction and not authoritative structured data merely because it
came from an official-looking source.

#### Source policy

Each adapter must declare one stable source owner and source family. Its policy
defines permitted acquisition, authenticity requirements, rate/usage limits,
license and redistribution treatment, locale normalization, revision identity,
and failure behavior. Redirected ownership, missing revisions, mutable bytes
under the same revision, or an incompatible license fails closed.

Official first-party sources are preferred for facts they publish. Community
or analytical sources may later supplement gaps only with distinct provenance,
license review, and lower authority; they never overwrite first-party facts.
Conflicts remain explicit review blockers.

#### Candidate and invalidation behavior

Intake may emit either:

- `no_relevant_change`, with the inspected source hash and supported mapping
  version;
- `pending_review`, containing one or more deterministic change candidates;
- `coverage_invalidated`, identifying current coverage families that can no
  longer be treated as current;
- `evidence_unavailable`, with a static sanitized reason.

An invalidation alert may immediately prevent affected guidance from being
treated as current, but it cannot create replacement guidance. The last known
good package remains available only when its compatibility and invalidation
rules still allow it; otherwise the user sees `guidance_unavailable`.

#### Historical retention

Captured source evidence and candidate decisions are content-addressed and
append-only. Superseded records remain usable for explicit build-to-build
comparison, parser regression, audit, rollback, and explanation. Historical
assertions cannot fill missing current coverage or be remapped silently after a
mapping-schema change.

#### Proposed synthetic implementation

The first implementation should parse no prose and perform no network access.
It should validate injected synthetic structured assertions and generate pure
candidate or invalidation results in exactly these seven paths:

1. `desktop-app/src/dpslab/patch_evidence.py`;
2. `desktop-app/tests/test_patch_evidence.py`;
3. `knowledge/schemas/patch_evidence_record_0_1.json`;
4. `knowledge/schemas/patch_change_candidate_0_1.json`;
5. `knowledge/snapshots/patch_evidence_synthetic_0_1.json`;
6. `docs/PATCH_EVIDENCE.md`;
7. `docs/NEXT_TASK.md`.

At least 28 focused tests should cover canonical hashing, closed fields, source
identity, authenticity classification, license policy, build applicability,
duplicate and conflicting assertions, deterministic ordering, invalidation,
historical isolation, sanitized errors, and the impossibility of approval or
catalog mutation. The functional floor is 371 tests and all tools tests pass.

Design verdict:
`patch_evidence_intake_design_0_1_ready_for_implementation_contract`.

Design publication closure:

- commit: `3d0b783fb6364eaadb66b3e7aa24f5437e68ab75`;
- local and live remote `main`: synchronized;
- GitHub Actions lookup through the expired local API session returned 404,
  so canonical CI evidence remains an explicit publication observation rather
  than an inferred success.

## Completed implementation contract — Patch evidence intake 0.1

Daniel's expanded technical authorization permits this closed synthetic
implementation. It does not authorize live acquisition, real patch data,
catalog mutation, recommendation approval, or network activity.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "patch_evidence_intake_0_1",
  "title": "Pure fail-closed intake of injected patch evidence",
  "baseline_commit": "3d0b783fb6364eaadb66b3e7aa24f5437e68ab75",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "patch_evidence_intake_0_1-20260731-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-31T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/patch_evidence.py",
      "desktop-app/tests/test_patch_evidence.py",
      "knowledge/schemas/patch_evidence_record_0_1.json",
      "knowledge/schemas/patch_change_candidate_0_1.json",
      "knowledge/snapshots/patch_evidence_synthetic_0_1.json",
      "docs/PATCH_EVIDENCE.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/patch_evidence_intake_0_1/implementation.json",
      ".dpslab/quality-gates/patch_evidence_intake_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "profiles/**", "scenarios/**", "variants/**",
      "comparisons/**", "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_patch_evidence", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 343,
    "minimum_test_count": 371
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "knowledge/schemas/source_coverage_manifest_0_1.json": "99bac38dbc4bbdeda035b722df427a6c0aa441e58759ddbb73712745616528e6",
    "knowledge/manifests/source_coverage_synthetic_0_1.json": "519a165dc7bbb4a663a8086076fc35e2b249d1720df8aafdd77019e29623e573",
    "knowledge/snapshots/source_capture_synthetic_0_1.json": "34439c8b4e541d03225eac97d20ec9526f1de8c4035f64b3be867de12dc9f07f"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "exactly seven allowlisted paths and no deletion or rename",
    "closed canonical evidence with deterministic SHA-256",
    "only review, invalidation, no-change, or unavailable outcomes",
    "historical evidence cannot generate a current candidate",
    "ambiguous, incompatible, conflicting, or unknown evidence fails closed",
    "at least 28 focused tests, 371 functional tests, and all tools tests pass",
    "protected hashes remain intact"
  ],
  "express_exclusions": [
    "network acquisition, scraping, prose parsing, or real patch data",
    "database, catalog mutation, recommendation approval, signing, or release",
    "SimulationCraft, comparisons, addon, UI, commit, or push"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `patch_evidence_intake_0_1_authorized`.

### Publication closure

- audited commit: `4290a3174c3951c15d9f2c3bdb17daf4e6e14753`;
- GitHub Actions run: `30634764223`;
- Policy and contract, Tools tests, and Functional suite: success;
- local `main`, `origin/main`, and the live remote were synchronized;
- final state: `patch_evidence_intake_0_1_published_ci_passed`.

The implementation authorization is consumed. The retained contract is
historical evidence and cannot authorize another mutation, real data
acquisition, catalog update, recommendation approval, or release.

## Consumed design contract — First-party patch source adapter 0.1

This design-only block specifies how official, current patch and hotfix
material may be acquired and converted into the already implemented evidence
quarantine. It does not fetch a source, store real content, infer balance
changes from prose, or update a catalog.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "first_party_patch_source_adapter_design_0_1",
  "title": "Design controlled acquisition of current first-party patch evidence",
  "baseline_commit": "4290a3174c3951c15d9f2c3bdb17daf4e6e14753",
  "authorization": {
    "status": "design_only",
    "authorization_id": "first_party_patch_source_adapter_design_0_1-20260731-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-31T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": ["docs/NEXT_TASK.md"],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": ".",
      "argv": ["python", "-m", "unittest", "tools.tests.test_github_automation", "-v"],
      "environment": {"PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 376,
    "minimum_test_count": 376
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/patch_evidence.py": "d2f3562e44b2ff92f6319305136887f97465e5b42c1d154f5a547e1de09b9fcf",
    "knowledge/snapshots/patch_evidence_synthetic_0_1.json": "f3d58b536a853975e92d9359a5e3a8104bb1fa460431d7dbf9a294655cfc56a4"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "first-party sources are preferred and source identities are allowlisted",
    "acquisition and semantic interpretation remain separate boundaries",
    "cache validators and content hashes prevent silent duplicate processing",
    "new evidence enters quarantine as pending_review or evidence_unavailable",
    "historical captures remain labeled and cannot become current implicitly",
    "outages, redirects, unknown builds, and changed formats fail closed",
    "no real source access or catalog mutation occurs"
  ],
  "express_exclusions": [
    "network calls, scraping, real patch notes, credentials, or telemetry",
    "automatic prose interpretation or recommendation approval",
    "catalog mutation, signing, release, addon, UI, SimulationCraft, commit, or push"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict: `first_party_patch_source_adapter_design_0_1_authorized`.

### Design output — acquisition before interpretation

The adapter boundary is divided into four explicit stages:

1. `source_registry` contains allowlisted first-party source identities,
   expected media families, permitted redirect hosts, WoW product, locale
   handling, and review ownership. A URL discovered outside this registry is
   not followed automatically.
2. `transport_capture` accepts an injected transport response and records the
   final source identity, retrieval time, response media type, cache validator,
   byte count, and SHA-256. Network implementation is deferred; tests use
   synthetic response objects.
3. `format_adapter` converts one recognized, versioned source format into
   structured assertions. It cannot approve meaning, invent missing build
   ranges, or convert unstructured prose by guesswork. An unknown layout is
   `evidence_unavailable` and alerts review.
4. `patch_evidence` validates the resulting record and emits only the existing
   quarantine outcomes. Catalog publication remains a separate human-reviewed
   transaction.

Freshness is defined by source revision, content hash, declared game build,
and capture time—not merely by retrieval time. Conditional retrieval may use
an injected ETag or Last-Modified value, but a `not_modified` response reuses
only a previously verified byte hash. Redirects, authentication challenges,
HTML error pages, oversized bodies, partial transfers, and media-type changes
fail closed without replacing the last known-good capture.

The current layer and historical layer remain separate. A newly verified
capture may supersede a prior capture only through an explicit lineage link.
The prior bytes and facts remain content-addressed for build comparison,
regression analysis, audit, and rollback; they cannot satisfy current coverage
after supersession.

The smallest implementation candidate is
`first_party_patch_source_adapter_0_1`, limited to pure validation of a
synthetic source registry, injected transport metadata and bytes, deterministic
capture hashing, duplicate detection, redirect policy, size/media limits, and
handoff to `patch_evidence`. It should not include an HTTP client, real URLs,
real patch content, HTML parsing, catalog updates, or recommendation logic.

Proposed closed implementation paths:

- `desktop-app/src/dpslab/patch_source_adapter.py`;
- `desktop-app/tests/test_patch_source_adapter.py`;
- `knowledge/schemas/patch_source_registry_0_1.json`;
- `knowledge/registries/patch_source_registry_synthetic_0_1.json`;
- `docs/PATCH_SOURCE_ADAPTER.md`;
- `docs/NEXT_TASK.md`.

Design verdict:
`first_party_patch_source_adapter_design_0_1_ready_for_implementation_contract`.

Design publication closure:

- commit: `093756ca7b0944dc22a907cff91a3df43e5feac5`;
- GitHub Actions run: `30635526891`;
- Policy and contract, Tools tests, and Functional suite: success;
- final state: `first_party_patch_source_adapter_design_0_1_published_ci_passed`.

## Completed implementation contract — First-party patch source adapter 0.1

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "first_party_patch_source_adapter_0_1",
  "title": "Pure synthetic source registry and injected transport capture",
  "baseline_commit": "093756ca7b0944dc22a907cff91a3df43e5feac5",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "first_party_patch_source_adapter_0_1-20260731-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-31T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/patch_source_adapter.py",
      "desktop-app/tests/test_patch_source_adapter.py",
      "knowledge/schemas/patch_source_registry_0_1.json",
      "knowledge/registries/patch_source_registry_synthetic_0_1.json",
      "docs/PATCH_SOURCE_ADAPTER.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/first_party_patch_source_adapter_0_1/implementation.json",
      ".dpslab/quality-gates/first_party_patch_source_adapter_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "profiles/**", "scenarios/**", "variants/**",
      "comparisons/**", "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_patch_source_adapter", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 376,
    "minimum_test_count": 406
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/patch_evidence.py": "d2f3562e44b2ff92f6319305136887f97465e5b42c1d154f5a547e1de09b9fcf",
    "knowledge/snapshots/patch_evidence_synthetic_0_1.json": "f3d58b536a853975e92d9359a5e3a8104bb1fa460431d7dbf9a294655cfc56a4"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "exactly six allowlisted paths and no deletion or rename",
    "closed canonical registry with deterministic SHA-256",
    "only injected response objects and synthetic source identities",
    "redirect, status, completeness, media and size policies fail closed",
    "not-modified reuse requires previously verified validators and hash",
    "duplicates are deterministic and do not replace known-good evidence",
    "handoff can produce only patch_evidence quarantine outcomes",
    "at least 30 focused tests, 406 functional tests, and all tools tests pass",
    "protected hashes remain intact and SimulationCraft is not invoked"
  ],
  "express_exclusions": [
    "HTTP client, DNS, browser, scraping, real URL, or real patch content",
    "HTML or natural-language interpretation",
    "catalog mutation, approval, signing, release, addon, UI, SimulationCraft"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict:
`first_party_patch_source_adapter_0_1_authorized`.

### Publication closure

- audited commit: `b3c4995c7944dcacf7f05f6811760c6c0a13590b`;
- GitHub Actions run: `30636187755`;
- Policy and contract, Tools tests, and Functional suite: success;
- local `main`, `origin/main`, and live remote synchronized;
- final state: `first_party_patch_source_adapter_0_1_published_ci_passed`.

The implementation authorization is consumed and retained only as historical
evidence.

## Consumed design contract — Structured patch format adapter 0.1

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "structured_patch_format_adapter_design_0_1",
  "title": "Design deterministic conversion of recognized structured patch fields",
  "baseline_commit": "b3c4995c7944dcacf7f05f6811760c6c0a13590b",
  "authorization": {
    "status": "design_only",
    "authorization_id": "structured_patch_format_adapter_design_0_1-20260731-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-31T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": ["docs/NEXT_TASK.md"],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": ".",
      "argv": ["python", "-m", "unittest", "tools.tests.test_github_automation", "-v"],
      "environment": {"PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 414,
    "minimum_test_count": 414
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/patch_source_adapter.py": "14c826d7f1b40467602949c2958f71b0343fac72c9561eb2625bd0bfa494bbee",
    "knowledge/registries/patch_source_registry_synthetic_0_1.json": "7c91df0ab7eda6846f85e3d1c27dc867213d6e791ce51cc5c493af6470fab3f0"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "input format is closed, versioned, canonical, and synthetic",
    "only explicitly mapped parameter families and operations are accepted",
    "unstructured prose and unknown fields fail closed",
    "build, source, citation, and subject lineage are preserved",
    "output is a valid patch_evidence record with pending-review semantics",
    "no catalog mutation, recommendation, network, or real data occurs"
  ],
  "express_exclusions": [
    "HTML, Markdown, natural-language or heuristic parsing",
    "real sources, URLs, credentials, network, or telemetry",
    "catalog mutation, approval, release, addon, UI, or SimulationCraft"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict:
`structured_patch_format_adapter_design_0_1_authorized`.

### Design output — closed structured conversion

The first format adapter accepts only one synthetic JSON dialect with an exact
schema version. Its root binds source evidence ID, source revision, Retail
build/interface range, publication and capture timestamps, lifecycle, and a
list of typed change records. It does not accept free-form descriptions.

Each change record must carry an external change ID, an allowlisted semantic
kind, canonical subject tokens, a closed operation, old/new typed tokens,
source-local citation, certainty, and explicit invalidation families. A
versioned mapping table converts semantic kinds to canonical parameter-family
IDs. The mapping is data supplied by the caller and cannot be expanded from
the input document.

Conversion is deterministic: source order is irrelevant, assertion IDs and
candidate order are canonical, duplicate IDs and duplicate semantic targets
are rejected, and the generated evidence record receives the existing
canonical SHA-256. Unknown kinds, unsupported operations, missing build ranges,
ambiguous certainty, and ineffective changes fail closed before handoff.

The adapter may produce a structurally valid `patch_evidence` record but cannot
change its lifecycle, approve it, select a template, or write a catalog. The
existing `patch_evidence` validator remains authoritative for quarantine.

Proposed implementation paths:

- `desktop-app/src/dpslab/patch_format_adapter.py`;
- `desktop-app/tests/test_patch_format_adapter.py`;
- `knowledge/schemas/structured_patch_input_0_1.json`;
- `knowledge/snapshots/structured_patch_input_synthetic_0_1.json`;
- `docs/PATCH_FORMAT_ADAPTER.md`;
- `docs/NEXT_TASK.md`.

Design verdict:
`structured_patch_format_adapter_design_0_1_ready_for_implementation_contract`.

Design publication closure:

- commit: `fa1adde903b2c47425067b34c76cfbfe31a87315`;
- GitHub Actions run: `30638015330`;
- Policy and contract, Tools tests, and Functional suite: success.

## Completed implementation contract — Structured patch format adapter 0.1

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "structured_patch_format_adapter_0_1",
  "title": "Pure conversion of synthetic structured patch input to quarantine evidence",
  "baseline_commit": "fa1adde903b2c47425067b34c76cfbfe31a87315",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "structured_patch_format_adapter_0_1-20260731-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-31T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/patch_format_adapter.py",
      "desktop-app/tests/test_patch_format_adapter.py",
      "knowledge/schemas/structured_patch_input_0_1.json",
      "knowledge/snapshots/structured_patch_input_synthetic_0_1.json",
      "docs/PATCH_FORMAT_ADAPTER.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/structured_patch_format_adapter_0_1/implementation.json",
      ".dpslab/quality-gates/structured_patch_format_adapter_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "profiles/**", "scenarios/**", "variants/**",
      "comparisons/**", "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_patch_format_adapter", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 414,
    "minimum_test_count": 444
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/patch_source_adapter.py": "14c826d7f1b40467602949c2958f71b0343fac72c9561eb2625bd0bfa494bbee",
    "knowledge/registries/patch_source_registry_synthetic_0_1.json": "7c91df0ab7eda6846f85e3d1c27dc867213d6e791ce51cc5c493af6470fab3f0"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "exactly six allowlisted paths and no deletion or rename",
    "closed canonical input with deterministic SHA-256",
    "caller-supplied closed semantic mapping controls all output families",
    "unknown, ambiguous, duplicate, conflicting, or ineffective changes fail closed",
    "output validates under patch_evidence and remains pending review",
    "at least 30 focused tests, 444 functional tests, and all tools tests pass",
    "protected hashes remain intact and SimulationCraft is not invoked"
  ],
  "express_exclusions": [
    "HTML, Markdown, prose, heuristic, AI, or natural-language parsing",
    "real source content, network, URL, credential, or telemetry",
    "catalog mutation, approval, release, addon, UI, or SimulationCraft"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict:
`structured_patch_format_adapter_0_1_authorized`.

### Publication closure

- audited commit: `784bf682fa8b2765263f35db0b0e0159c07757e2`;
- GitHub Actions run: `30638676119`;
- Policy and contract, Tools tests, and Functional suite: success;
- local `main`, `origin/main`, and live remote synchronized;
- final state: `structured_patch_format_adapter_0_1_published_ci_passed`.

The implementation authorization is consumed and retained only as historical
evidence.

## Consumed design contract — Catalog change proposal 0.1

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "catalog_change_proposal_design_0_1",
  "title": "Design reviewable proposals from quarantined evidence without catalog mutation",
  "baseline_commit": "784bf682fa8b2765263f35db0b0e0159c07757e2",
  "authorization": {
    "status": "design_only",
    "authorization_id": "catalog_change_proposal_design_0_1-20260731-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-31T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": ["docs/NEXT_TASK.md"],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": ".",
      "argv": ["python", "-m", "unittest", "tools.tests.test_github_automation", "-v"],
      "environment": {"PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 453,
    "minimum_test_count": 453
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/patch_format_adapter.py": "701a8e1732fdfcbf998056c76ae305bbc5b1ff851865ab191f3bcd1fc8d454a6",
    "knowledge/snapshots/structured_patch_input_synthetic_0_1.json": "f53eb1ec777cf72c4c0468a746768dbb20a386600e8c4f53ef344c0338706270"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "only validated current pending-review evidence may enter proposal construction",
    "proposal binds exact catalog and evidence hashes plus build and subject",
    "operations are explicit additions, replacements, removals, or invalidations",
    "role safety policy is preserved for tanks and healers",
    "proposal cannot represent approval, publication, or direct catalog mutation",
    "conflicts, stale inputs, unknown families, and historical evidence fail closed"
  ],
  "express_exclusions": [
    "catalog writes, approvals, signing, publication, or automatic recommendations",
    "real sources, network, credentials, telemetry, addon, UI, or SimulationCraft",
    "live class balance claims or specialization content"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict: `catalog_change_proposal_design_0_1_authorized`.

### Design output — immutable proposal, separate approval

The proposal builder receives three already validated inputs: one current
`patch_evidence` record whose intake result is `pending_review` or
`coverage_invalidated`, one exact catalog snapshot, and one closed policy
mapping from parameter families to permitted catalog fields. It never opens or
writes a catalog path.

Every proposal binds the evidence SHA-256, catalog SHA-256, source revision,
Retail build/interface range, subject tokens, role, content contexts, creation
time, and expiry. Each proposed operation includes before and after tokens,
the originating assertion and citation, limitations, and an explicit review
state fixed initially to `pending_review`.

The builder rejects historical evidence, ambiguous assertions, catalog hash
mismatches, unknown parameter families, overlapping operations, ineffective
replacements, missing citations, unsupported build ranges, and expired source
evidence. An invalidation creates a proposal to suspend affected guidance; it
does not silently delete or replace content.

Role safety is non-negotiable. A tank proposal may adjust damage guidance only
while preserving declared survival constraints and required damage-intake
context. A healer proposal may adjust damage guidance only while preserving
healing-coverage constraints and ally-health context. Missing safety evidence
produces `proposal_unavailable`, never a damage-only fallback.

The output is content-addressed and can be reviewed, rejected, superseded, or
expired. A later approval transaction must bind the exact proposal hash and
reviewer identity; even then, catalog application and publication remain
separate transactions.

Proposed implementation paths:

- `desktop-app/src/dpslab/catalog_change_proposal.py`;
- `desktop-app/tests/test_catalog_change_proposal.py`;
- `knowledge/schemas/catalog_change_proposal_0_1.json`;
- `knowledge/proposals/catalog_change_proposal_synthetic_0_1.json`;
- `docs/CATALOG_CHANGE_PROPOSAL.md`;
- `docs/NEXT_TASK.md`.

Design verdict: `catalog_change_proposal_design_0_1_ready_for_implementation_contract`.

Design publication closure:

- commit: `6b433aa7229f0584cae3e8135aa500231a8fc19c`;
- GitHub Actions run: `30684540522`;
- Policy and contract, Tools tests, and Functional suite: success.

## Completed implementation contract — Catalog change proposal 0.1

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "catalog_change_proposal_0_1",
  "title": "Pure content-addressed catalog proposal builder",
  "baseline_commit": "6b433aa7229f0584cae3e8135aa500231a8fc19c",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "catalog_change_proposal_0_1-20260731-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-31T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/catalog_change_proposal.py",
      "desktop-app/tests/test_catalog_change_proposal.py",
      "knowledge/schemas/catalog_change_proposal_0_1.json",
      "knowledge/proposals/catalog_change_proposal_synthetic_0_1.json",
      "docs/CATALOG_CHANGE_PROPOSAL.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/catalog_change_proposal_0_1/implementation.json",
      ".dpslab/quality-gates/catalog_change_proposal_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "profiles/**", "scenarios/**", "variants/**",
      "comparisons/**", "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_catalog_change_proposal", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 453,
    "minimum_test_count": 483
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/patch_format_adapter.py": "701a8e1732fdfcbf998056c76ae305bbc5b1ff851865ab191f3bcd1fc8d454a6",
    "knowledge/snapshots/structured_patch_input_synthetic_0_1.json": "f53eb1ec777cf72c4c0468a746768dbb20a386600e8c4f53ef344c0338706270"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "exactly six allowlisted paths and no deletion or rename",
    "proposal binds validated catalog and evidence hashes",
    "proposal status is fixed to pending_review and has no approval fields",
    "historical, ambiguous, stale, conflicting, or unknown evidence fails closed",
    "tank and healer damage proposals require matching safety-family evidence",
    "no catalog path is opened or written",
    "at least 30 focused tests, 483 functional tests, and all tools tests pass",
    "protected hashes remain intact and SimulationCraft is not invoked"
  ],
  "express_exclusions": [
    "catalog mutation, approval, signing, release, or recommendation selection",
    "real content, network, credentials, telemetry, addon, UI, or SimulationCraft"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `catalog_change_proposal_0_1_authorized`.

### Publication closure

- audited commit: `bcae8e36ff7ccc9184e4f244a36543b9af1c7598`;
- GitHub Actions run: `30684833738`;
- Policy and contract, Tools tests, and Functional suite: success;
- local `main`, `origin/main`, and live remote synchronized;
- final state: `catalog_change_proposal_0_1_published_ci_passed`.

The implementation authorization is consumed and retained only as historical
evidence.

## Consumed design contract — Proposal review decision 0.1

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "proposal_review_decision_design_0_1",
  "title": "Design exact human review decisions bound to proposal hashes",
  "baseline_commit": "bcae8e36ff7ccc9184e4f244a36543b9af1c7598",
  "authorization": {
    "status": "design_only",
    "authorization_id": "proposal_review_decision_design_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": ["docs/NEXT_TASK.md"],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": ".",
      "argv": ["python", "-m", "unittest", "tools.tests.test_github_automation", "-v"],
      "environment": {"PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 490,
    "minimum_test_count": 490
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/catalog_change_proposal.py": "824f06db37caca9191e0add6e48eb6c2e4603169088d515f228facc8ac6ec20a",
    "knowledge/proposals/catalog_change_proposal_synthetic_0_1.json": "bfbe624d2b37572f9512447acaf6be0ebe6c97ebf590bc74339b732c29f11c39"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "decision binds exact proposal ID, proposal SHA-256, catalog SHA-256, and evidence SHA-256",
    "reviewer identity, authority reference, UTC time, decision, and reason codes are mandatory",
    "approval is rejected after proposal expiry or before proposal creation",
    "a decision cannot alter proposal operations, bindings, subject, or expiry",
    "approval does not authorize or perform catalog application or publication",
    "conflicting or replayed decisions fail closed"
  ],
  "express_exclusions": [
    "catalog mutation, application, signing keys, publication, or recommendation selection",
    "real content, network, credentials, telemetry, addon, UI, or SimulationCraft"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict: `proposal_review_decision_design_0_1_authorized`.

### Design output — decision evidence, not mutation authority

A review decision is a separate immutable document. It binds the exact
proposal ID and SHA-256, the proposal's catalog and evidence hashes, reviewer
ID, authority reference, decision time, decision (`approved` or `rejected`),
closed reason codes, limitations acknowledged, and its own canonical SHA-256.

Approval is valid only when the decision time is UTC, is not earlier than the
proposal creation time, and is not later than its expiry. The proposal must
still validate byte-for-byte and remain `pending_review`. Rejection follows the
same binding rules and cannot be converted to approval by editing the decision;
a new decision document with a distinct ID is required and conflicts remain
fail-closed.

Replay protection is expressed through a caller-supplied set of consumed
decision IDs and proposal hashes. The pure validator reports
`decision_eligible`, `decision_rejected`, or `decision_unavailable`; it never
stores consumption state. Durable single-use recording belongs to the later
application transaction.

Even `decision_eligible` does not mutate the catalog. A future application
block must revalidate proposal, decision, current catalog hash, expiry, and
single-use status at one durable boundary, produce a candidate catalog copy,
and require a separate publication step.

Proposed implementation paths:

- `desktop-app/src/dpslab/proposal_review.py`;
- `desktop-app/tests/test_proposal_review.py`;
- `knowledge/schemas/proposal_review_decision_0_1.json`;
- `knowledge/reviews/proposal_review_decision_synthetic_0_1.json`;
- `docs/PROPOSAL_REVIEW.md`;
- `docs/NEXT_TASK.md`.

Design verdict: `proposal_review_decision_design_0_1_ready_for_implementation_contract`.

Design publication closure:

- commit: `231263caa904e4b3af3e3b0ad5035b145aa00e91`;
- GitHub Actions run: `30684980499`;
- Policy and contract, Tools tests, and Functional suite: success.

## Completed implementation contract — Proposal review decision 0.1

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "proposal_review_decision_0_1",
  "title": "Pure hash-bound proposal review decision validation",
  "baseline_commit": "231263caa904e4b3af3e3b0ad5035b145aa00e91",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "proposal_review_decision_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/proposal_review.py",
      "desktop-app/tests/test_proposal_review.py",
      "knowledge/schemas/proposal_review_decision_0_1.json",
      "knowledge/reviews/proposal_review_decision_synthetic_0_1.json",
      "docs/PROPOSAL_REVIEW.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/proposal_review_decision_0_1/implementation.json",
      ".dpslab/quality-gates/proposal_review_decision_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "profiles/**", "scenarios/**", "variants/**",
      "comparisons/**", "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_proposal_review", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 490,
    "minimum_test_count": 520
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/catalog_change_proposal.py": "824f06db37caca9191e0add6e48eb6c2e4603169088d515f228facc8ac6ec20a",
    "knowledge/proposals/catalog_change_proposal_synthetic_0_1.json": "bfbe624d2b37572f9512447acaf6be0ebe6c97ebf590bc74339b732c29f11c39"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "exactly six allowlisted paths and no deletion or rename",
    "decision binds exact proposal, catalog, and evidence hashes",
    "reviewer, authority, UTC time, outcome, reasons, and limitations are mandatory",
    "decisions outside the proposal validity window fail closed",
    "consumed decision IDs or proposal hashes cannot be replayed",
    "decision validation never mutates catalog or proposal",
    "at least 30 focused tests, 520 functional tests, and all tools tests pass",
    "protected hashes remain intact and SimulationCraft is not invoked"
  ],
  "express_exclusions": [
    "catalog application, mutation, signing keys, publication, or recommendation selection",
    "real content, network, credentials, telemetry, addon, UI, or SimulationCraft"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `proposal_review_decision_0_1_authorized`.

### Publication closure

- audited commit: `83d6eb56dd3913a016e852e1136f9a59beef82bd`;
- GitHub Actions run: `30685261169`;
- Policy and contract, Tools tests, and Functional suite: success;
- local `main`, `origin/main`, and live remote synchronized;
- final state: `proposal_review_decision_0_1_published_ci_passed`.

The implementation authorization is consumed and retained only as historical
evidence.

## Consumed design contract — Candidate knowledge-set application 0.1

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "candidate_knowledge_set_application_design_0_1",
  "title": "Design pure application to a candidate envelope and catalog set",
  "baseline_commit": "83d6eb56dd3913a016e852e1136f9a59beef82bd",
  "authorization": {
    "status": "design_only",
    "authorization_id": "candidate_knowledge_set_application_design_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": ["docs/NEXT_TASK.md"],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": ".",
      "argv": ["python", "-m", "unittest", "tools.tests.test_github_automation", "-v"],
      "environment": {"PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 522,
    "minimum_test_count": 522
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/proposal_review.py": "5c261e5972bc313f3395ea55904c65423a1dbd31d4c72757bd57efc3f3ff56bd",
    "knowledge/reviews/proposal_review_decision_synthetic_0_1.json": "e795b08346e5b051b63456ba763ab3115bc2f68f6f46640e9c4687d14a1f7c52"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "design corrects the catalog-only assumption without changing product architecture",
    "candidate set contains an envelope, catalog, and single-use receipt bound together",
    "physical field mapping is closed and external to proposal evidence",
    "source envelope, source catalog, proposal, and decision remain unchanged",
    "candidate envelope and catalog validate independently and cross-reference exact hashes",
    "output remains unpublished, unsigned, and in pending-review state"
  ],
  "express_exclusions": [
    "filesystem writes, atomic replacement, durable consumption, signing, or publication",
    "real guidance, live data, network, credentials, addon, UI, or SimulationCraft"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict: `candidate_knowledge_set_application_design_0_1_authorized`.

### Design output — candidate set, not catalog-only mutation

Structural review confirmed that `static_template_catalog` is an index whose
entries reference immutable knowledge envelopes. Guidance statements and
evidence metadata live in the envelope, not in the catalog. Therefore a
proposal targeting guidance cannot be correctly applied by editing only the
catalog. The application unit must be a candidate knowledge set.

The pure application boundary receives exact validated values for source
envelope, source catalog, proposal, eligible review decision, and a closed
physical mapping policy. The policy maps proposal `catalog_field` tokens to
specific permitted envelope transformations. Unknown fields or transformations
fail closed; proposal data cannot invent a physical path.

Application creates three new values in memory:

1. a candidate envelope with a new package ID and content version, updated
   guidance/evidence fields, complete provenance, null signature, and a new
   payload SHA-256;
2. a candidate catalog with a new content version and pending-review entry
   pointing to the candidate envelope's future portable path and byte hash;
3. a consumption receipt binding source hashes, proposal hash, decision hash,
   candidate hashes, decision ID, and application time.

The source entry remains preserved as historical evidence. The candidate entry
may declare `supersedes_entry_ids`, but its lifecycle is `pending_review`, its
review fields are empty, source coverage is false until separately verified,
and it cannot be selected as guidance. The source entry is not deprecated or
withdrawn during pure candidate construction.

Tank and healer safety constraints are revalidated at both proposal and
candidate-envelope boundaries. Physical mapping may update only allowlisted
synthetic guidance statement tokens and provenance fields in 0.1; it cannot
change subject, role, compatibility, automation safety, signatures, or channel.

Durable application is explicitly deferred. A later transactional block must
confirm current on-disk hashes, write envelope and catalog through atomic
replacement under the declared single-writer model, and atomically record the
receipt. Publication and signature remain later separate steps.

Proposed implementation paths:

- `desktop-app/src/dpslab/candidate_knowledge_set.py`;
- `desktop-app/tests/test_candidate_knowledge_set.py`;
- `knowledge/schemas/candidate_knowledge_set_receipt_0_1.json`;
- `knowledge/candidates/candidate_knowledge_set_synthetic_0_1.json`;
- `docs/CANDIDATE_KNOWLEDGE_SET.md`;
- `docs/NEXT_TASK.md`.

Design verdict:
`candidate_knowledge_set_application_design_0_1_ready_for_implementation_contract`.

Design publication closure:

- commit: `5d8dfa9cee05f45f435f4524f9c94484c1613a63`;
- GitHub Actions run: `30685645926`;
- Policy and contract, Tools tests, and Functional suite: success.

## Completed implementation contract — Candidate knowledge-set application 0.1

The authorization below is consumed. The pure candidate constructor was
implemented, audited, committed, published, and verified without making the
candidate selectable or durable:

- commit: `76f155c1dff63954dc60549f42724c571a89634a`;
- focused tests: 34/34;
- full functional suite: 556/556;
- GitHub Actions run: `30686106447`;
- Policy and contract, Tools tests, and Functional suite: success.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "candidate_knowledge_set_application_0_1",
  "title": "Pure synthetic candidate envelope, catalog, and receipt construction",
  "baseline_commit": "5d8dfa9cee05f45f435f4524f9c94484c1613a63",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "candidate_knowledge_set_application_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/candidate_knowledge_set.py",
      "desktop-app/tests/test_candidate_knowledge_set.py",
      "knowledge/schemas/candidate_knowledge_set_receipt_0_1.json",
      "knowledge/candidates/candidate_knowledge_set_synthetic_0_1.json",
      "docs/CANDIDATE_KNOWLEDGE_SET.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/candidate_knowledge_set_application_0_1/implementation.json",
      ".dpslab/quality-gates/candidate_knowledge_set_application_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "profiles/**", "scenarios/**", "variants/**",
      "comparisons/**", "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_candidate_knowledge_set", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 522,
    "minimum_test_count": 552
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/proposal_review.py": "5c261e5972bc313f3395ea55904c65423a1dbd31d4c72757bd57efc3f3ff56bd",
    "knowledge/reviews/proposal_review_decision_synthetic_0_1.json": "e795b08346e5b051b63456ba763ab3115bc2f68f6f46640e9c4687d14a1f7c52"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "exactly six allowlisted paths and no deletion or rename",
    "pure construction returns envelope, catalog, and receipt without filesystem access",
    "closed physical mapping controls every permitted transformation",
    "source values remain byte-equivalent and candidate values validate independently",
    "candidate catalog keeps source entry and adds pending-review successor",
    "receipt binds source, proposal, decision, and candidate hashes",
    "at least 30 focused tests, 552 functional tests, and all tools tests pass",
    "protected hashes remain intact and SimulationCraft is not invoked"
  ],
  "express_exclusions": [
    "filesystem writes, durable consumption, atomic replacement, signing, or publication",
    "real guidance, live data, network, credentials, addon, UI, or SimulationCraft"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Closure verdict: `candidate_knowledge_set_application_0_1_published_ci_passed`.

## Design-only contract — Candidate knowledge-set persistence 0.1

The next boundary may make an already validated synthetic candidate set
durable, but must not approve, sign, publish, or select it. Directly replacing
an envelope, catalog, and receipt as three independent files is not an atomic
transaction: a process interruption could expose a mixed generation. The
design therefore uses immutable generation directories plus one small atomic
commit marker as the only visibility boundary.

The writer operates under the existing single-writer model. It must re-read
and revalidate the source envelope, source catalog, proposal, decision, and
candidate set immediately before staging; compare every bound byte hash; reject
symlinks, path escapes, an existing generation ID, or prior consumption of the
decision/proposal; and write only beneath a caller-provided confined store
root. Staged files use canonical bytes, are flushed before visibility, and are
re-read and rehashed before the commit marker is atomically installed.

The committed generation contains immutable candidate envelope, candidate
catalog, receipt, and a closed manifest binding their relative paths and
hashes. The receipt records durable single-use consumption only inside the
committed generation. A reader trusts a generation solely when the atomic
marker and manifest agree. Abandoned staging remains invisible and may be
reported for later controlled cleanup; the transaction must not silently
delete evidence. Exact replay returns the already committed generation without
rewriting it; any divergent replay fails closed.

This block does not alter the repository's current catalog, does not activate
guidance, and does not create a history warehouse. It establishes only the
crash-consistent handoff required for a later, separate human review and
publication decision.

Proposed implementation paths:

- `desktop-app/src/dpslab/candidate_knowledge_store.py`;
- `desktop-app/tests/test_candidate_knowledge_store.py`;
- `knowledge/schemas/candidate_knowledge_set_commit_0_1.json`;
- `docs/CANDIDATE_KNOWLEDGE_SET.md`;
- `docs/NEXT_TASK.md`.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "candidate_knowledge_set_persistence_0_1",
  "title": "Crash-consistent synthetic candidate knowledge-set persistence",
  "baseline_commit": "d1037abc0440a6c7003c04b2fd412d279db4efc7",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "candidate_knowledge_set_persistence_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/candidate_knowledge_store.py",
      "desktop-app/tests/test_candidate_knowledge_store.py",
      "knowledge/schemas/candidate_knowledge_set_commit_0_1.json",
      "docs/CANDIDATE_KNOWLEDGE_SET.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/candidate_knowledge_set_persistence_0_1/implementation.json",
      ".dpslab/quality-gates/candidate_knowledge_set_persistence_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "knowledge/catalogs/**", "knowledge/fixtures/**",
      "knowledge/candidates/**", "knowledge/proposals/**", "knowledge/reviews/**",
      "profiles/**", "scenarios/**", "variants/**",
      "comparisons/**", "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_candidate_knowledge_store", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 556,
    "minimum_test_count": 580
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/candidate_knowledge_set.py": "eb12d5f812bbb592df185e9ca7e21fb0a9d858317789265a059421278de7e628",
    "knowledge/candidates/candidate_knowledge_set_synthetic_0_1.json": "3c97b650a2654eb666dbb0693f474ddee8ab94b29c0e5bc10838ab473309aa1a"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "one atomic marker is the sole visibility boundary for an immutable generation",
    "all source and candidate bindings are revalidated immediately before staging",
    "durable single-use consumption becomes visible only with the committed generation",
    "exact replay is idempotent and divergent replay fails closed",
    "staging failures preserve the prior visible generation and expose no partial candidate",
    "no approval, signature, publication, selection, network, real data, or SimulationCraft"
  ],
  "express_exclusions": [
    "multi-writer or distributed locking guarantees",
    "active catalog replacement, addon or UI consumption, signing, or publication"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Closure verdict: `candidate_knowledge_set_persistence_0_1_published_ci_passed`.

Implementation closure:

- commit: `3feafc7137beaa9ab1c006a33bc283e47f52f1ea`;
- focused tests: 28/28, with one Windows symlink capability skip;
- full functional suite: 584/584;
- GitHub Actions run: `30697245606`;
- Policy and contract, Tools tests, and Functional suite: success.

## Design-only contract — Candidate knowledge-set review 0.1

The next boundary is an explicit human review of one exact durable candidate
generation. It receives the canonical visibility marker, commit manifest,
candidate envelope, candidate catalog, receipt, source evidence, and reviewer
context. It must bind their byte hashes and reject any mismatch, stale source,
incomplete source coverage, unsupported build, missing human attestation, or
role-safety gap.

The decision record is immutable and closed. It may conclude `approved` or
`rejected`, but approval means only that the exact candidate generation is
eligible for a later publication transaction. It does not modify the candidate
files, current marker, repository catalog, addon payload, or desktop guidance.
Publication, signing keys, distribution, and activation remain separate future
contracts.

Tank review must affirm survival-first constraints under incoming damage.
Healer review must affirm ally-healing priority and safe damage opportunities.
Damage-specialization review must still preserve no-automation and contextual
applicability. Every role fails closed when current patch/build evidence or
source coverage is missing.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "candidate_knowledge_set_review_0_1",
  "title": "Human review record for one exact durable candidate generation",
  "baseline_commit": "caf45e41ae8e9abc30fc7fdd920fe2da0e4d857d",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "candidate_knowledge_set_review_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/candidate_knowledge_review.py",
      "desktop-app/tests/test_candidate_knowledge_review.py",
      "knowledge/schemas/candidate_knowledge_review_decision_0_1.json",
      "knowledge/reviews/candidate_knowledge_review_decision_synthetic_0_1.json",
      "docs/CANDIDATE_KNOWLEDGE_SET.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/candidate_knowledge_set_review_0_1/implementation.json",
      ".dpslab/quality-gates/candidate_knowledge_set_review_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "tools/**", "knowledge/catalogs/**", "knowledge/fixtures/**",
      "knowledge/candidates/**", "knowledge/proposals/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_candidate_knowledge_review", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 584,
    "minimum_test_count": 610
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/candidate_knowledge_store.py": "8af1c763e652dbe3127eaa3cf61cdd81df11dd4cb13fad5ee476c9497cb1b19f",
    "knowledge/candidates/candidate_knowledge_set_synthetic_0_1.json": "3c97b650a2654eb666dbb0693f474ddee8ab94b29c0e5bc10838ab473309aa1a"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "review decision binds the exact marker, commit, envelope, catalog, receipt, and source hashes",
    "freshness, applicability, source coverage, and role safety are explicit fail-closed inputs",
    "approved and rejected are immutable review outcomes, never self-declared by the candidate",
    "approval only establishes eligibility for a later separately authorized publication",
    "no candidate mutation, activation, signing, distribution, real guidance, network, or SimulationCraft"
  ],
  "express_exclusions": [
    "automatic approval, catalog activation, signing, addon packaging, or publication"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Closure verdict: `candidate_knowledge_set_review_0_1_published_ci_passed`.

Implementation closure:

- commit: `c290af6f089fcb823daf5ffee86edca22eae1b49`;
- focused tests: 31/31;
- full functional suite: 615/615;
- GitHub Actions run: `30697867678`;
- Policy and contract, Tools tests, and Functional suite: success.

## Design-only contract — Candidate knowledge release bundle 0.1

The next boundary constructs, in memory, a release-candidate bundle from one
exact durable generation and one eligible human review decision. The bundle
must bind all prior hashes, carry only current and applicable synthetic
guidance, and contain a candidate envelope, candidate catalog transition, human
review, and closed release manifest. It remains an internal release candidate:
construction is not signing, publication, distribution, or activation.

Promotion logic is explicit. The reviewed pending entry may become `approved`
only in the release-candidate copy; review identity and time must be copied from
the bound decision, source coverage becomes complete only from the approved
assessment, and role safety must remain satisfied. The prior source entry is
preserved. Deprecation or withdrawal of that source requires a later distinct
decision and is not inferred from supersession.

The manifest must declare target channel, supported build/interface bounds,
content version, review decision hash, candidate commit hash, and byte hashes
for every bundle member. It must remain unsigned with an explicit
`signature_pending` state. A later signing/publication transaction must bind the
exact manifest hash and use separately managed credentials.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "candidate_knowledge_release_bundle_0_1",
  "title": "Pure reviewed candidate release-bundle construction",
  "baseline_commit": "bace9039795fb63b17549a4a961a0f2e53d21e50",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "candidate_knowledge_release_bundle_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/candidate_release_bundle.py",
      "desktop-app/tests/test_candidate_release_bundle.py",
      "knowledge/schemas/candidate_release_manifest_0_1.json",
      "knowledge/releases/candidate_knowledge_release_bundle_synthetic_0_1.json",
      "docs/CANDIDATE_KNOWLEDGE_SET.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/candidate_knowledge_release_bundle_0_1/implementation.json",
      ".dpslab/quality-gates/candidate_knowledge_release_bundle_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "tools/**", "knowledge/catalogs/**", "knowledge/fixtures/**",
      "knowledge/candidates/**", "knowledge/proposals/**", "knowledge/reviews/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_candidate_release_bundle", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 615,
    "minimum_test_count": 645
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/candidate_knowledge_review.py": "43bfd9a066a23ff99b8be526127c79db2b797ca105dd4866316c3c258e98b826",
    "knowledge/reviews/candidate_knowledge_review_decision_synthetic_0_1.json": "2851131b250879862f7bb9ae6e0044f73608cb4d10a08228363d74c88bfaa2f7"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "bundle binds the exact durable generation and eligible human review decision",
    "promotion occurs only in an immutable release-candidate copy",
    "source entry remains preserved and is not automatically deprecated or withdrawn",
    "manifest binds every member hash, compatibility range, channel, and content version",
    "bundle remains signature_pending and cannot be selected or distributed"
  ],
  "express_exclusions": [
    "credentials, cryptographic signing, active catalog replacement, addon packaging, distribution, or publication"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Closure verdict: `candidate_knowledge_release_bundle_0_1_published_ci_passed`.

Implementation closure:

- commit: `d5469b381bfbed838b3283ba455b79275ec264bc`;
- focused tests: 32/32;
- full functional suite: 647/647;
- GitHub Actions run: `30698418367`;
- Policy and contract, Tools tests, and Functional suite: success.

## Design-only contract — Release signing policy 0.1

The recommended release-signing boundary uses Ed25519 over the exact canonical
release-manifest bytes. The private key must never enter Git, source fixtures,
test artifacts, logs, addon files, desktop configuration, or GitHub Actions
artifacts. Only a versioned public-key registry, key identifiers, validity
windows, rotation relationships, and revocation records may be committed.

Signing is an explicit operator action over one manifest already validated as
`signature_pending`. The signer returns a detached signature and key ID; it
cannot modify bundle members. Verification recomputes every member hash,
validates the manifest, resolves exactly one currently trusted public key, and
fails closed on unknown, expired, revoked, ambiguous, or algorithm-mismatched
keys. A valid signature changes only release eligibility; publication remains a
separate transaction.

Tests may use deterministic synthetic keys clearly marked non-production.
Production key generation and storage require a later human choice among an
OS-protected local key, hardware-backed key, or managed signing service. CI may
verify signatures with public keys but must never receive the production
private key during this phase.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "release_signing_policy_0_1",
  "title": "Ed25519 release signing, trust registry, rotation, and revocation design",
  "baseline_commit": "d6932d1397d9250a8cef339ecb75e1f7e40ada68",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "release_signing_policy_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/pyproject.toml",
      "desktop-app/src/dpslab/release_signing.py",
      "desktop-app/tests/test_release_signing.py",
      "knowledge/schemas/release_trust_registry_0_1.json",
      "knowledge/trust/release_trust_registry_synthetic_0_1.json",
      "docs/CANDIDATE_KNOWLEDGE_SET.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/release_signing_policy_0_1/implementation.json",
      ".dpslab/quality-gates/release_signing_policy_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "tools/**", "knowledge/catalogs/**", "knowledge/fixtures/**",
      "knowledge/candidates/**", "knowledge/proposals/**", "knowledge/reviews/**",
      "knowledge/releases/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_release_signing", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 647,
    "minimum_test_count": 675
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/candidate_release_bundle.py": "906f06f86db80f3d328284da47b0e459902250155081d5037de321f233939bde",
    "knowledge/releases/candidate_knowledge_release_bundle_synthetic_0_1.json": "f3ab281dfb8d2a17d13ff254e988b131a2ca026a72e0132526670d95a3b774a3"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "Ed25519 signature covers exact canonical release-manifest bytes",
    "private key is external to repository, artifacts, logs, addon, and desktop configuration",
    "public-key registry supports validity windows, rotation, and fail-closed revocation",
    "CI verifies only with public keys and synthetic tests never resemble production credentials",
    "valid signature grants eligibility only and cannot publish or activate a release"
  ],
  "express_exclusions": [
    "production key generation, production secret storage, production signing, publication, or distribution"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Published outcome: commit `af4eb398a522a9e07b8d708ceb11a4bb905a9db6`
is synchronized with `origin/main`. GitHub Actions run `30699358693` completed
successfully across policy, tools, and functional lanes. The gate recorded 30
focused tests and 677 global tests with one existing skip.

Closure verdict: `release_signing_policy_0_1_published_ci_approved`.

The authorization above is consumed by the published commit and is retained
verbatim only as historical evidence.

The implementation contains only a synthetic public trust fixture and a test
private key constructed in memory. Production key generation remains blocked
until Daniel chooses and separately authorizes a custody model. The recommended
initial option is a Windows OS-protected local Ed25519 key with an encrypted
offline recovery copy; hardware-backed or managed signing remains a future
upgrade when operational scale justifies it.

## Active design task — Production release-key custody 0.1

This task may compare custody choices and prepare an operational recovery and
rotation plan. It may not generate, import, store, expose, or use a production
private key.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "production_release_key_custody_design_0_1",
  "title": "Design production Ed25519 key custody, recovery, and rotation",
  "baseline_commit": "af4eb398a522a9e07b8d708ceb11a4bb905a9db6",
  "authorization": {
    "status": "design_only",
    "authorization_id": "production_release_key_custody_design_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": ["docs/NEXT_TASK.md"],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "acceptance_criteria": [
    "compare Windows OS-protected, hardware-backed, and managed custody",
    "define backup, recovery, rotation, revocation, and operator boundaries",
    "recommend one initial model with explicit migration triggers",
    "keep all production key operations subject to later human authorization"
  ],
  "express_exclusions": [
    "production or test key generation",
    "secret import, storage, export, signing, or recovery execution",
    "release publication, activation, or distribution",
    "code, CI, addon, desktop, SimulationCraft, commit, or push implementation"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict: `production_release_key_custody_design_0_1_ready`.

### Custody design decision

Three models were evaluated for the first production signing key:

| Model | Initial fit | Main strength | Main limitation |
| --- | --- | --- | --- |
| Windows user-scoped OS protection | Recommended | Low operating cost and no plaintext key at rest | Signing is tied to one controlled Windows operator profile |
| Hardware-backed key | Later upgrade | Strong isolation and explicit physical presence | Added cost, device support, backup, and replacement complexity |
| Managed signing service | Scale upgrade | Central policy, audit, and multi-operator automation | Recurring cost, network dependency, and expanded service trust |

Decision: start with one Ed25519 key encrypted at rest through Windows
user-scoped OS protection. The desktop application may request a signature
through a narrow local adapter, but it must never log, return, serialize, or
place the decrypted private key in project configuration. CI and the addon
receive only the public registry and detached signatures.

### Operator and transaction boundaries

- Daniel is the initial key owner and the only person who may authorize key
  creation, recovery, rotation, revocation, or a production signature.
- Generation and recovery are separate, attended operations. Neither may run
  from CI, an addon, a background updater, or a general development command.
- Every signing request must display the exact manifest SHA-256, channel,
  content version, build range, and public key identifier before confirmation.
- A successful signature grants release eligibility only. Publication and
  activation remain distinct, audited transactions.
- The protected key container, recovery copy, public registry, and release
  artifacts must use separate locations and permissions.

### Backup and recovery

The first key requires one encrypted offline recovery copy on user-controlled
removable storage, plus a second separately stored record containing only the
public key identifier, fingerprint, creation date, and recovery procedure. The
recovery copy must never enter Git, cloud synchronization, chat, CI artifacts,
logs, or the addon package.

Recovery is fail-closed: restore into a controlled Windows profile, derive the
public key, and require an exact fingerprint match with the trusted registry
before any signing operation. A mismatch triggers revocation review rather
than registry replacement.

### Rotation and revocation

- Planned rotation: annually, or 30 days before the key validity window ends,
  whichever occurs first.
- Immediate revocation: suspected disclosure, lost recovery media, Windows
  profile compromise, unexplained signature, fingerprint mismatch, or loss of
  exclusive operator control.
- Rotation creates a new key identifier and a registry entry linked through
  `rotated_from_key_id`; it never overwrites the prior public entry.
- Revocation records UTC time and reason. Previously signed releases remain
  historical evidence, but no new release may validate through a revoked key.
- Emergency response order: stop signing, preserve evidence, revoke publicly,
  generate a replacement through a separately authorized ceremony, then
  republish the trust registry before resuming releases.

### Migration triggers

Move to hardware-backed custody when releases become revenue-bearing, a second
trusted operator is required, or compromise impact materially increases. Move
to a managed signing service only when unattended release automation or a
multi-operator approval policy becomes necessary. Neither migration is implied
by this design.

Design verdict: `production_release_key_custody_design_0_1_complete`.

## Active design task — Windows production signing adapter 0.1

The next task is limited to specifying a closed implementation contract for a
Windows user-scoped signing adapter and an attended key ceremony. It cannot
create, import, recover, or use a production key.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "windows_production_signing_adapter_design_0_1",
  "title": "Design the Windows-protected production signing adapter and attended ceremony",
  "baseline_commit": "d26546f8e410257bce7c6315e42dc069ac2e6e90",
  "authorization": {
    "status": "design_only",
    "authorization_id": "windows_production_signing_adapter_design_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": ["docs/NEXT_TASK.md"],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "acceptance_criteria": [
    "define a narrow signer interface with no private-key return path",
    "define Windows user-scoped protection and explicit filesystem boundaries",
    "define attended generation, backup, recovery, rotation, and revocation ceremonies",
    "define tests using synthetic keys and simulated OS-protection calls only",
    "separate adapter implementation from production key creation and signing"
  ],
  "express_exclusions": [
    "production key generation, import, recovery, storage, or signing",
    "real secret or recovery-media access",
    "release publication, activation, or distribution",
    "code, CI, addon, desktop, SimulationCraft, commit, or push implementation"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict: `windows_production_signing_adapter_design_0_1_ready`.

### Adapter design output

The adapter has three closed layers. `WindowsDataProtector` is the only layer
allowed to call Windows DPAPI and must use current-user scope with user
interface disabled; machine-wide scope is forbidden. `ProtectedKeyContainer`
stores only versioned metadata, the public-key fingerprint, and DPAPI-protected
ciphertext. `WindowsReleaseSigner` accepts canonical manifest bytes and returns
only a 64-byte detached Ed25519 signature.

No public API returns decrypted key bytes. Unprotected bytes remain local to
one signing call and are discarded immediately afterward; Python cannot
guarantee perfect memory zeroization, so the design does not claim it. The
container path is outside the repository under the current user's local
application-data directory. Repository paths, arbitrary caller-selected paths,
machine scope, UI prompts, network calls, logs, and environment-variable
secrets fail closed.

The attended ceremony remains a separate future operation. It must verify that
an encrypted offline recovery copy exists before the first production key is
accepted. This is required because Windows user-scoped DPAPI normally binds
recovery to the same credentials and machine, and administrative password
reset can make protected material unavailable.

Design verdict: `windows_production_signing_adapter_design_0_1_complete`.

## Active implementation — Windows protected signing adapter 0.1

This implementation may add the adapter and synthetic tests. Tests must inject
a simulated protector and deterministic synthetic Ed25519 keys. They may test
the Windows-call wrapper structurally but may not invoke DPAPI with real secret
material or write outside temporary test directories.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "windows_protected_signing_adapter_0_1",
  "title": "Implement a Windows user-scoped release signer with synthetic verification",
  "baseline_commit": "df24c3ca83fdea6b037ca75fb8cb76e33b42aac2",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "windows_protected_signing_adapter_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/windows_key_protection.py",
      "desktop-app/src/dpslab/windows_release_signer.py",
      "desktop-app/tests/test_windows_key_protection.py",
      "desktop-app/tests/test_windows_release_signer.py",
      "docs/RELEASE_KEY_CUSTODY.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/windows_protected_signing_adapter_0_1/implementation.json",
      ".dpslab/quality-gates/windows_protected_signing_adapter_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "desktop-app/pyproject.toml", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_windows_key_protection", "tests.test_windows_release_signer", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 677,
    "minimum_test_count": 701
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/release_signing.py": "50b38b6875b317b58bba1b0b32dc9beceb1dec89c4b92e12a06770e4e58c8604",
    "knowledge/trust/release_trust_registry_synthetic_0_1.json": "99819f2111d78852df8e4627033c9070b441fae10f8f0f536320b3cb8283989b"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "machine-wide DPAPI scope and UI prompts are impossible through the adapter",
    "protected containers are closed, versioned, fingerprint-bound, and path-confined",
    "the signer returns only a detached signature over exact caller bytes",
    "private material is neither logged nor returned by public APIs",
    "tests use deterministic synthetic keys and simulated protection only"
  ],
  "express_exclusions": [
    "production key generation, import, recovery, backup, or signing",
    "real DPAPI invocation with secret material",
    "release publication, activation, or distribution",
    "CI changes, addon, SimulationCraft, commit or push of production artifacts"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `windows_protected_signing_adapter_0_1_authorized_for_synthetic_implementation`.

Published outcome: commit `10ba0a8d0de26a78626efde48ea3600340acb7d1`
is synchronized with `origin/main`. GitHub Actions run `30700240783` completed
successfully across policy, tools, and functional lanes. The quality gate
recorded 26 focused tests and 703 global tests with one existing skip.

Closure verdict: `windows_protected_signing_adapter_0_1_published_ci_approved`.
The implementation authorization is consumed and retained verbatim above as
historical evidence. No production key or real protected container exists.

## Active design task — Production key ceremony 0.1

This task may prepare an exact attended checklist and recovery evidence format.
It may not execute any ceremony step or generate any key.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "production_release_key_ceremony_design_0_1",
  "title": "Design the attended production release-key ceremony and recovery evidence",
  "baseline_commit": "10ba0a8d0de26a78626efde48ea3600340acb7d1",
  "authorization": {
    "status": "design_only",
    "authorization_id": "production_release_key_ceremony_design_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": ["docs/NEXT_TASK.md", "docs/RELEASE_KEY_CUSTODY.md"],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "acceptance_criteria": [
    "define attended preconditions, confirmations, evidence, and abort conditions",
    "define encrypted offline recovery-copy verification without exposing secret material",
    "define initial validity, fingerprint, registry, rotation, and revocation records",
    "identify the exact point requiring Daniel's explicit authorization and presence"
  ],
  "express_exclusions": [
    "key generation, DPAPI protection, backup creation, recovery, or signing",
    "secret, removable-media, or production-container access",
    "release publication, activation, or distribution",
    "code, CI, addon, SimulationCraft, commit, or push implementation"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict: `production_release_key_ceremony_design_0_1_ready`.

Design outcome: the four checkpoints, recovery verification, non-secret
evidence record, and fail-closed abort conditions are canonicalized in
`docs/RELEASE_KEY_CUSTODY.md`. Key identifier
`dpslab.release.ed25519.001` and a one-year validity window remain proposals
until Daniel confirms them during the future attended transaction.

Design verdict: `production_release_key_ceremony_design_0_1_complete`.

## Active design task — Ceremony dry-run tooling 0.1

The next task may design a machine-checkable ceremony plan and synthetic dry
run. It may not generate or protect any real key.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "release_key_ceremony_dry_run_design_0_1",
  "title": "Design a fail-closed production key ceremony plan and synthetic dry run",
  "baseline_commit": "c1bb1c54ebb5923e79b003f3520e1f04672635e4",
  "authorization": {
    "status": "design_only",
    "authorization_id": "release_key_ceremony_dry_run_design_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": ["docs/NEXT_TASK.md", "docs/RELEASE_KEY_CUSTODY.md"],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "acceptance_criteria": [
    "define a closed plan schema with four independently confirmed checkpoints",
    "validate resolved paths, repository state, identity, time, and collision preconditions",
    "produce only non-secret synthetic evidence during dry runs",
    "make production mode structurally unavailable in the dry-run implementation"
  ],
  "express_exclusions": [
    "key generation, protection, recovery, backup, registry mutation, or signing",
    "real filesystem destinations, removable media, DPAPI, or secrets",
    "release publication, activation, or distribution",
    "code, CI, addon, SimulationCraft, commit, or push implementation"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict: `release_key_ceremony_dry_run_design_0_1_ready`.

Design output: the dry run is a pure evaluator over a closed plan,
observations, and four explicit checkpoint confirmations. Version 0.1 accepts
only `synthetic_dry_run`, `synthetic://` destinations, placeholder media
identifiers, and non-secret hashes. It performs no filesystem, DPAPI, key,
registry, signing, network, or publication operation.

Design verdict: `release_key_ceremony_dry_run_design_0_1_complete`.

## Active implementation — Ceremony synthetic dry run 0.1

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "release_key_ceremony_dry_run_0_1",
  "title": "Implement the pure synthetic release-key ceremony evaluator",
  "baseline_commit": "40faa9e2370f3cb47d7f0449ecca5f225b729e98",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "release_key_ceremony_dry_run_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/release_key_ceremony.py",
      "desktop-app/tests/test_release_key_ceremony.py",
      "knowledge/schemas/release_key_ceremony_plan_0_1.json",
      "docs/RELEASE_KEY_CUSTODY.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/release_key_ceremony_dry_run_0_1/implementation.json",
      ".dpslab/quality-gates/release_key_ceremony_dry_run_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "desktop-app/pyproject.toml", "knowledge/trust/**",
      "knowledge/releases/**", "tools/**", "profiles/**", "scenarios/**",
      "variants/**", "comparisons/**", "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_release_key_ceremony", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 703,
    "minimum_test_count": 727
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/windows_key_protection.py": "27d1bfdce76df7c06666e98aaaa2456cd23e17b06eaccee98f7bb440080ef67b",
    "desktop-app/src/dpslab/windows_release_signer.py": "066b26990b40afb2ac79afe11c320af686f22031a088450ac46ed56bfa406070"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "closed plan, observation, confirmation, and evidence structures",
    "exactly four ordered and independently confirmed checkpoints",
    "only synthetic URI destinations and non-secret placeholder identities",
    "fail-closed result with one stable abort reason and no partial authorization",
    "pure evaluation with no filesystem, DPAPI, key, registry, signing, or network effect"
  ],
  "express_exclusions": [
    "production mode or production key material",
    "filesystem, removable-media, DPAPI, registry, signing, or network operations",
    "release publication, activation, or distribution",
    "CI changes, addon, SimulationCraft, production commit or secret artifact"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `release_key_ceremony_dry_run_0_1_authorized_for_synthetic_implementation`.

Published outcome: commit `7b9a00a1e5bdde54e7f408a358d76b3a54e6e2db`
is synchronized with `origin/main`. GitHub Actions run `30701094461` completed
successfully across policy, tools, and functional lanes. The quality gate
recorded 24 focused tests and 727 global tests with one existing skip.

An in-memory acceptance dry run returned `synthetic_dry_run_ready`; all four
checkpoints were true, plan SHA-256 was
`60627176d5670b964b908d8192cb4219ba92f8d576a2cbb37188ead9a9fb1d18`,
and evidence SHA-256 was
`73eec3b207c6877e644a5a5a28863693e878b9e6e80afddb0095d786af4c24ec`.
No evidence file, key, DPAPI blob, registry entry, or production artifact was
created.

Closure verdict: `release_key_ceremony_dry_run_0_1_published_ci_approved`.

## Active design task — Production ceremony execution preflight 0.1

This task may inspect only non-secret readiness state and prepare the exact
attended prompt. It may not generate or protect a key, select destinations for
Daniel, or access removable media.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "production_key_ceremony_execution_preflight_0_1",
  "title": "Prepare the non-secret preflight for the first attended production key ceremony",
  "baseline_commit": "7b9a00a1e5bdde54e7f408a358d76b3a54e6e2db",
  "authorization": {
    "status": "design_only",
    "authorization_id": "production_key_ceremony_execution_preflight_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": ["docs/NEXT_TASK.md", "docs/RELEASE_KEY_CUSTODY.md"],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "acceptance_criteria": [
    "identify the exact non-secret repository and environment checks",
    "prepare a human-readable confirmation containing proposed key identity and validity",
    "request Daniel to select three destinations without exposing passphrases or contents",
    "stop before any key, DPAPI, media, registry, signing, or publication operation"
  ],
  "express_exclusions": [
    "key generation, protection, backup, recovery, registry mutation, or signing",
    "secret collection or removable-media writes",
    "release publication, activation, or distribution",
    "code, CI, addon, SimulationCraft, commit, or push implementation"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict: `production_key_ceremony_execution_preflight_0_1_ready`.

Preflight outcome:

- repository HEAD and `origin/main` matched at
  `b8a4aaf7ec15d79cc02c73642485c7237a45cc1e` with no versioned delta;
- the default user-local root resolved to
  `C:\Users\dpcs9\AppData\Local`;
- the effective process identity was `DANIELPC\CodexSandboxOffline`, which is
  not Daniel's interactive operator identity;
- removable-volume enumeration was denied in this context;
- no key, DPAPI call, destination write, media access, or secret collection
  occurred.

Verdict: `production_key_ceremony_execution_preflight_0_1_blocked_wrong_operator_context`.

## Active design task — Native ceremony handoff 0.1

This task may prepare a visible native-session launcher and human checklist.
It may not launch the production ceremony, collect a passphrase, or generate a
key without Daniel present and explicitly confirming the native identity and
destinations.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "native_production_key_ceremony_handoff_design_0_1",
  "title": "Design the visible native-session handoff for the production key ceremony",
  "baseline_commit": "b8a4aaf7ec15d79cc02c73642485c7237a45cc1e",
  "authorization": {
    "status": "design_only",
    "authorization_id": "native_production_key_ceremony_handoff_design_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": ["docs/NEXT_TASK.md", "docs/RELEASE_KEY_CUSTODY.md"],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "acceptance_criteria": [
    "require a visible terminal in Daniel's interactive Windows session",
    "display and confirm the effective identity before all other checks",
    "collect only destination selections before the final generation checkpoint",
    "keep passphrase entry local and invisible to Codex, logs, and chat",
    "define a hard stop before the first irreversible secret operation"
  ],
  "express_exclusions": [
    "starting the ceremony or generating, protecting, backing up, recovering, or signing with a key",
    "passphrase, clipboard, removable-media content, or secret access",
    "release publication, activation, or distribution",
    "code, CI, addon, SimulationCraft, commit, or push implementation"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design-entry verdict: `native_production_key_ceremony_handoff_design_0_1_ready`.

Native read-only outcome:

- an unrestricted read-only check ran as `DANIELPC\dpcs9`, the intended
  interactive operator identity;
- `F:` was visible as healthy NTFS storage labeled `Black 3Tb`, with
  approximately 576 GB free; Windows reports it as `Fixed` even though Daniel
  attests that it is external and under his control;
- no second external volume was visible during the check;
- no key, DPAPI, file write, media write, registry change, or secret input
  occurred.

Design verdict: `native_production_key_ceremony_handoff_design_0_1_complete_second_media_not_connected`.

## Active implementation — Production ceremony executor 0.1

This block may implement and test the attended executor with synthetic
protectors, temporary paths, and injected passphrases. It may not execute the
production ceremony or access `F:` or any removable medium.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "production_release_key_ceremony_executor_0_1",
  "title": "Implement the attended production key ceremony executor without executing it",
  "baseline_commit": "2aaafc8f7b22e66b9d3b521c183fbc3a5bfa3d69",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "production_release_key_ceremony_executor_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/release_key_ceremony_executor.py",
      "desktop-app/tests/test_release_key_ceremony_executor.py",
      "knowledge/schemas/release_key_ceremony_evidence_0_1.json",
      "docs/RELEASE_KEY_CUSTODY.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/production_release_key_ceremony_executor_0_1/implementation.json",
      ".dpslab/quality-gates/production_release_key_ceremony_executor_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "desktop-app/pyproject.toml", "knowledge/trust/**",
      "knowledge/releases/**", "tools/**", "profiles/**", "scenarios/**",
      "variants/**", "comparisons/**", "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_release_key_ceremony_executor", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 727,
    "minimum_test_count": 755
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/release_key_ceremony.py": "dc66f8109174a516fab600838cc86f021a4bb2e424199bde76b7088fe982c080",
    "desktop-app/src/dpslab/windows_key_protection.py": "27d1bfdce76df7c06666e98aaaa2456cd23e17b06eaccee98f7bb440080ef67b",
    "desktop-app/src/dpslab/windows_release_signer.py": "066b26990b40afb2ac79afe11c320af686f22031a088450ac46ed56bfa406070"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "four explicit checkpoint tokens are single-use, ordered, and bound to the exact plan",
    "key generation, protection, recovery encryption, verification, and evidence writes are injected boundaries",
    "all three destinations are resolved, distinct, absent, and outside repositories before generation",
    "recovery verification derives and matches the public fingerprint before registry eligibility",
    "evidence excludes private bytes, passphrases, DPAPI ciphertext, and recovery ciphertext",
    "tests use synthetic keys, protectors, passphrases, and temporary directories only"
  ],
  "express_exclusions": [
    "production ceremony execution or real key generation",
    "access to F:, removable media, DPAPI, operator passphrase, or native prompts",
    "trust-registry mutation, release signing, publication, activation, or distribution",
    "CI changes, addon, SimulationCraft, production artifact commit or push"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `production_release_key_ceremony_executor_0_1_authorized_for_synthetic_implementation_only`.

Human destination decision: Daniel selected
`F:\DpsLab Release Key Recovery` for the encrypted recovery artifact. The
directory was created and verified empty. The protected container remains on
`C:` under current-user local application data; the public non-secret record
remains governed on `D:` and GitHub. No key or artifact was created.

Published outcome: commit `1694437db4403d57128fdc782962400a1510c425`
is synchronized with `origin/main`. GitHub Actions run `30703402102` completed
successfully. The quality gate recorded 28 focused tests and 755 global tests
with one existing skip. The authorization above is consumed.

Closure verdict: `production_release_key_ceremony_executor_0_1_published_ci_approved`.

## Active implementation — Recovery encryption and artifact transaction 0.1

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "release_key_recovery_transaction_0_1",
  "title": "Implement passphrase recovery encryption and compensating new-artifact transaction",
  "baseline_commit": "1694437db4403d57128fdc782962400a1510c425",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "release_key_recovery_transaction_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/release_key_recovery.py",
      "desktop-app/src/dpslab/new_artifact_transaction.py",
      "desktop-app/tests/test_release_key_recovery.py",
      "desktop-app/tests/test_new_artifact_transaction.py",
      "knowledge/schemas/release_key_recovery_bundle_0_1.json",
      "docs/RELEASE_KEY_CUSTODY.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/release_key_recovery_transaction_0_1/implementation.json",
      ".dpslab/quality-gates/release_key_recovery_transaction_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "desktop-app/pyproject.toml", "knowledge/trust/**",
      "knowledge/releases/**", "tools/**", "profiles/**", "scenarios/**",
      "variants/**", "comparisons/**", "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_release_key_recovery", "tests.test_new_artifact_transaction", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 755,
    "minimum_test_count": 785
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/release_key_ceremony_executor.py": "04dd2e4edf50edb82364d80c86615a129ae89ade36582e95ecdd84dc4bb1984b",
    "desktop-app/src/dpslab/windows_key_protection.py": "27d1bfdce76df7c06666e98aaaa2456cd23e17b06eaccee98f7bb440080ef67b"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "Scrypt-derived AES-256-GCM recovery bundle binds key identity and public fingerprint",
    "wrong passphrase, tampering, malformed parameters, and fingerprint mismatch fail closed",
    "passphrase is supplied transiently and never returned, logged, serialized, or stored",
    "new-artifact transaction refuses existing targets, stages beside each target, fsyncs, and rolls back its own outputs on failure",
    "cross-volume behavior is documented as compensating rollback, not impossible atomicity",
    "tests use synthetic key bytes, passphrases, and temporary directories only"
  ],
  "express_exclusions": [
    "production ceremony, real passphrase, key, DPAPI, F: write, or removable-media access",
    "trust-registry mutation, release signing, publication, activation, or distribution",
    "CI changes, addon, SimulationCraft, production artifact commit or push"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `release_key_recovery_transaction_0_1_authorized_for_synthetic_implementation_only`.

Published outcome: commit `411c422dff947c4bf63d874bee8724b579f11672`
is synchronized with `origin/main`; GitHub Actions run `30703694495` completed
successfully. The quality gate recorded 30 focused tests and 785 global tests
with one existing skip. The authorization above is consumed.

Closure verdict: `release_key_recovery_transaction_0_1_published_ci_approved`.

## Active implementation — Native attended ceremony launcher 0.1

<!-- DPSLAB_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "native_release_key_ceremony_launcher_0_1",
  "title": "Implement the native attended production key ceremony launcher without running it",
  "baseline_commit": "fcb8776de0a8240978b1666f18c241363ef4ce8e",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "native_release_key_ceremony_launcher_0_1-20260801-daniel-ux-correction",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/release_key_ceremony_cli.py",
      "desktop-app/tests/test_release_key_ceremony_cli.py",
      "docs/RELEASE_KEY_CUSTODY.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/native_release_key_ceremony_launcher_0_1/implementation.json",
      ".dpslab/quality-gates/native_release_key_ceremony_launcher_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "desktop-app/pyproject.toml", "knowledge/**", "tools/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_release_key_ceremony_cli", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 785,
    "minimum_test_count": 805
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/release_key_ceremony_executor.py": "04dd2e4edf50edb82364d80c86615a129ae89ade36582e95ecdd84dc4bb1984b",
    "desktop-app/src/dpslab/release_key_recovery.py": "3e07388cb4062dad53da0322c8dddbbb1521b1655a10048a2568d52f76ceeeb0",
    "desktop-app/src/dpslab/new_artifact_transaction.py": "ecdd9a6061b99d82252aea1ebad5e0e123a98ac7a30d60a47902bd1dbf14ff8a",
    "desktop-app/src/dpslab/windows_key_protection.py": "27d1bfdce76df7c06666e98aaaa2456cd23e17b06eaccee98f7bb440080ef67b"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "launcher displays exact identity, key, validity, plan hash, and three destinations",
    "four exact plan-bound confirmation phrases are entered in order",
    "passphrase is read twice through hidden local input and never echoed or returned",
    "native DPAPI, recovery encryption, verification, and transaction are wired only after final confirmation",
    "surrogate identity, path drift, existing output, password mismatch, or noninteractive input aborts before generation",
    "tests inject all I/O, secret, key, protector, and transaction boundaries"
  ],
  "express_exclusions": [
    "running the production ceremony or creating any real key artifact",
    "real passphrase, DPAPI invocation, C:/D:/F: writes, registry mutation, or signing",
    "release publication, activation, distribution, CI changes, addon, or SimulationCraft"
  ]
}
```
<!-- DPSLAB_TASK_CONTRACT_END -->

Implementation-entry verdict: `native_release_key_ceremony_launcher_0_1_authorized_for_simulated_testing_only`.

Usability correction: after two safe pre-generation aborts, Daniel authorized
continuation. The launcher may ignore surrounding whitespace in checkpoint
phrases and convert expected operator-input errors into concise safe-cancel
messages. This does not relax phrase content or any security checkpoint.

## Completed implementation authorization — Comparison execution bridge CI fix 0.1

Daniel authorized autonomous continuation on 2026-07-28. GitHub Actions run
`30370837485` demonstrated one Windows-only test defect: the runner exposes its
temporary directory through an 8.3 alias while the bridge deliberately resolves
the root before orchestration. This correction may align only that assertion
with the production path-normalization contract.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "comparison_execution_bridge_ci_fix_0_1",
  "title": "Portable Windows assertion for the comparison execution bridge",
  "baseline_commit": "d8ef26c8ed92d9528f861e5f24891a58251d285d",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "comparison_execution_bridge_ci_fix_0_1-20260728-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-28T12:30:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/tests/test_comparison_execution.py",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/comparison_execution_bridge_ci_fix_0_1/implementation.json",
      ".dpslab/quality-gates/comparison_execution_bridge_ci_fix_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/src/**",
      "comparisons/**",
      "profiles/**",
      "scenarios/**",
      "variants/**",
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
        "test_comparison_execution.py",
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
    "baseline_test_count": 267,
    "minimum_test_count": 267
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "scenarios/st_lightmovement_300s_v1.toml": "93187338a61d1cfc330f5262abb0b9183acb727d310099eca7917138207c09aa",
    "comparisons/flasil_neck_50228_vs_249368_v1.toml": "68282327263d4f75797181521419f11aa54fdecf16f1634c0b3b1b2ac6fdbe4c",
    "comparisons/simulationcraft_identity_manifest_0_1.json": "0a305a5991de0d3c1c4aafbb1756351b6643366a663f532877d6e137b69542eb",
    "desktop-app/src/dpslab/comparison_execution.py": "bedfd9109c64ef33849337cf6f60639b30d2de3e6bd84eaf977e72572ca74084"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "exactly the two authorized versioned paths in the delta",
    "the test compares the output path against the resolved temporary root",
    "no production behavior or expectation is relaxed",
    "the focused test, at least 267 functional tests, and all tools tests pass",
    "protected hashes remain intact",
    "simulationcraft_invoked remains false"
  ],
  "express_exclusions": [
    "production code",
    "workflow or tools changes",
    "real SimulationCraft invocation",
    "real comparison, run, or result creation",
    "changes to frozen specifications, evidence, profiles, or scenarios"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

The correction was independently audited, committed as
`7f06e5c12acc1e586a81891f8a1bf16c960eaeb3`, published to `main`, and
verified by GitHub Actions run `30371755873` in all three lanes. Its
implementation authorization is consumed.

## Completed operational comparison — frozen collar A/B 0.1

Daniel's explicit authorization to cross the execution boundary was consumed
on 2026-07-28 by exactly one `comparison-execute` invocation. Execution
`cmp-3120334d365b4ba2922cdbb25afe0d7f` completed all eight blocks without a
retry. Independent audit returned `comparison_real_execution_audit_approved`.
The result manifest is `docs/COMPARISON_RESULT_FLASIL_NECK_V1.md`.

No implementation contract is active. A later task must not repeat this
comparison, change the frozen inputs, promote the winning item into a general
recommendation, or begin another product block without a new closed contract.

## Completed implementation authorization — Comparison execution bridge 0.1

Daniel authorized autonomous continuation on 2026-07-28. This block implements
only the closed bridge between the already-audited readiness boundary and the
simulated comparison protocol. Implementation and tests must not invoke
SimulationCraft or create repository runs.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "comparison_execution_bridge_0_1",
  "title": "Closed operational bridge for the frozen A/B comparison",
  "baseline_commit": "7fe6bf1ad7f9ea49b2e09e1b0d460738bba29a6d",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "comparison_execution_bridge_0_1-20260728-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-28T10:15:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/comparison_execution.py",
      "desktop-app/src/dpslab/comparison_adapter.py",
      "desktop-app/src/dpslab/comparator.py",
      "desktop-app/src/dpslab/__main__.py",
      "desktop-app/tests/test_comparison_execution.py",
      "desktop-app/tests/test_comparison_adapter.py",
      "desktop-app/tests/test_comparator.py",
      "desktop-app/tests/test_comparison_cli.py",
      "desktop-app/tests/test_comparison_member_transactions.py",
      "desktop-app/tests/test_comparison_models.py",
      "desktop-app/tests/test_planned_member.py",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/comparison_execution_bridge_0_1/implementation.json",
      ".dpslab/quality-gates/comparison_execution_bridge_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**",
      "comparisons/**",
      "profiles/**",
      "scenarios/**",
      "variants/**",
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
        "test_comparison_*.py",
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
    "baseline_test_count": 255,
    "minimum_test_count": 267
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "scenarios/st_lightmovement_300s_v1.toml": "93187338a61d1cfc330f5262abb0b9183acb727d310099eca7917138207c09aa",
    "comparisons/flasil_neck_50228_vs_249368_v1.toml": "68282327263d4f75797181521419f11aa54fdecf16f1634c0b3b1b2ac6fdbe4c",
    "comparisons/simulationcraft_identity_manifest_0_1.json": "0a305a5991de0d3c1c4aafbb1756351b6643366a663f532877d6e137b69542eb"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "exactly the twelve authorized versioned paths in the delta",
    "readiness software identity is injected without recapture",
    "all preconditions pass before exclusive output creation",
    "the bridge delegates exactly once to comparator orchestration",
    "profiles preserve every byte outside the single neck line",
    "explicit_cli is accepted only with exact SimulationCraft identity",
    "CLI errors are static and contain no personal paths",
    "at least 267 functional tests and all tools tests pass",
    "protected hashes remain intact",
    "simulationcraft_invoked remains false during implementation"
  ],
  "express_exclusions": [
    "real SimulationCraft invocation",
    "real comparison, run, or result creation",
    "changes to frozen specifications, evidence, profiles, or scenarios",
    "workflow, tools, GitHub settings, tags, or baselines",
    "authorization of the later real execution block"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

## Completed implementation authorization — SimulationCraft identity manifest 0.1

Daniel explicitly authorized `simulationcraft_identity_manifest_0_1` on
2026-07-28 after three controlled probes demonstrated that
`display_build=2` reports version `1205-01` but omits branch and revision.
This block records Daniel's trust-on-first-use attestation for one exact
executable SHA-256 and permits a fail-closed manifest fallback. It does not
authorize another SimulationCraft invocation, comparison, run, or result.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "simulationcraft_identity_manifest_0_1",
  "title": "Fail-closed attested SimulationCraft identity manifest",
  "baseline_commit": "ee396a01bc5c48ea8babb3522821fd1624a3c516",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "simulationcraft_identity_manifest_0_1-20260728-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-28T02:20:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "comparisons/simulationcraft_identity_manifest_0_1.json",
      "desktop-app/src/dpslab/simc_identity.py",
      "desktop-app/tests/test_simc_identity.py",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/simulationcraft_identity_manifest_0_1/implementation.json",
      ".dpslab/quality-gates/simulationcraft_identity_manifest_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/src/dpslab/__main__.py",
      "desktop-app/src/dpslab/comparison_readiness.py",
      "desktop-app/src/dpslab/comparison_preflight.py",
      "desktop-app/src/dpslab/comparison_environment.py",
      "desktop-app/src/dpslab/comparison_spec.py",
      "desktop-app/src/dpslab/config.py",
      "desktop-app/src/dpslab/runner.py",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "comparisons/flasil_neck_50228_vs_249368_v1.toml",
      "comparisons/evidence/**",
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
        "test_*identity.py",
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
    "baseline_test_count": 252,
    "minimum_test_count": 255
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "scenarios/st_lightmovement_300s_v1.toml": "93187338a61d1cfc330f5262abb0b9183acb727d310099eca7917138207c09aa",
    "comparisons/flasil_neck_50228_vs_249368_v1.toml": "68282327263d4f75797181521419f11aa54fdecf16f1634c0b3b1b2ac6fdbe4c",
    "desktop-app/src/dpslab/__main__.py": "82bd59e19029f4435362977f7f38ed3391b6ad5f93f17072c8c69e25491e99a4",
    "desktop-app/src/dpslab/comparison_readiness.py": "e2a4ce520b88d9df7ba1dda96ff99e5af4c25bdb91c67411931a480f7cf14ab2",
    "desktop-app/src/dpslab/comparison_preflight.py": "1282997a6190845876283f66ba13d92cd14bb6d79b57f62443608b0111e931a2",
    "desktop-app/src/dpslab/comparison_spec.py": "2974dc8cbe8480dbe9667ffe61b2758bc5edb95bc997f49af4c45f7cf8f238d4",
    "desktop-app/src/dpslab/config.py": "a933de29661b8d06b6d6f1d1d89b2dc7d74e17c0b87d2d584891824c67c6b53b"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "exactly the four authorized versioned paths in the delta",
    "the manifest is closed, versioned, portable, and records explicit trust-on-first-use authority",
    "the exact attested executable hash maps uniquely to version 1205-01, branch midnight, revision a81c39d",
    "complete process output remains authoritative without manifest repair",
    "manifest fallback is allowed only for one unambiguous observed version with no git build marker",
    "unknown hashes, duplicates, malformed manifests, version conflicts, and ambiguous output fail closed",
    "no binary string-table extraction or historical-output inference is implemented",
    "focused tests, at least 255 functional tests, and tools tests pass",
    "protected hashes remain intact",
    "no real SimulationCraft, comparison, commit, push, or remote mutation occurs during implementation"
  ],
  "express_exclusions": [
    "real SimulationCraft invocation or readiness probe",
    "real comparison, run reservation, or result creation",
    "binary string-table inspection or heuristic identity extraction",
    "profiles, scenarios, variants, frozen comparison spec, evidence, results, and local config",
    "CLI, readiness bridge, preflight, runner, workflow, tools, or GitHub settings changes",
    "authorization of comparison execution or any later block"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

## Completed implementation authorization — Comparison readiness CLI 0.1

Daniel authorized autonomous continuation on 2026-07-28. This block exposes
the audited readiness bridge through a narrow command-line entry point that
reports only portable, non-sensitive readiness evidence. Tests inject every
collaborator and forbid process creation. The audited implementation was
published in `ee396a01bc5c48ea8babb3522821fd1624a3c516`, and GitHub Actions run
`30337561035` passed all three lanes. The implementation authorization is
consumed and does not authorize invoking SimulationCraft.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "comparison_readiness_cli_0_1",
  "title": "Portable comparison readiness CLI",
  "baseline_commit": "a66e96a1001ff2fbc37e565a14305ee0c053fbb2",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "comparison_readiness_cli_0_1-20260728-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-28T02:01:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/__main__.py",
      "desktop-app/tests/test_comparison_cli.py",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/comparison_readiness_cli_0_1/implementation.json",
      ".dpslab/quality-gates/comparison_readiness_cli_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/src/dpslab/comparison_readiness.py",
      "desktop-app/src/dpslab/comparison_preflight.py",
      "desktop-app/src/dpslab/simc_identity.py",
      "desktop-app/src/dpslab/comparison_environment.py",
      "desktop-app/src/dpslab/comparison_spec.py",
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
        "test_comparison_cli.py",
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
    "baseline_test_count": 247,
    "minimum_test_count": 251
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "comparisons/flasil_neck_50228_vs_249368_v1.toml": "68282327263d4f75797181521419f11aa54fdecf16f1634c0b3b1b2ac6fdbe4c",
    "desktop-app/src/dpslab/comparison_readiness.py": "e2a4ce520b88d9df7ba1dda96ff99e5af4c25bdb91c67411931a480f7cf14ab2",
    "desktop-app/src/dpslab/comparison_preflight.py": "1282997a6190845876283f66ba13d92cd14bb6d79b57f62443608b0111e931a2",
    "desktop-app/src/dpslab/simc_identity.py": "e243695b6802fd4a3bc2d9a273646d2da2d42a4e075c1445c8c8a03d6ec82c26",
    "desktop-app/src/dpslab/comparison_environment.py": "8ce3ec80c2f88430f6ee97a2b55f91a50175e785a8adaa456f0102c78b6ed94e",
    "desktop-app/src/dpslab/comparison_spec.py": "2974dc8cbe8480dbe9667ffe61b2758bc5edb95bc997f49af4c45f7cf8f238d4",
    "desktop-app/src/dpslab/config.py": "a933de29661b8d06b6d6f1d1d89b2dc7d74e17c0b87d2d584891824c67c6b53b"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "exactly the three authorized versioned paths in the delta",
    "one comparison-ready command composes frozen spec, scenario, exact protocol config, software identity, and the audited readiness bridge",
    "the command emits deterministic JSON containing only portable readiness evidence and no personal paths",
    "dependency failures use the existing CLI error channel and nonzero exit status",
    "all focused tests inject collaborators and fail if any process starts",
    "focused tests, at least 251 functional tests, and tools tests pass",
    "protected hashes remain intact",
    "no real SimulationCraft, comparison, commit, push, or remote mutation occurs during implementation"
  ],
  "express_exclusions": [
    "real SimulationCraft invocation or readiness probe",
    "real comparison, run reservation, or result creation",
    "comparison orchestration, persistence, or retry scheduling",
    "profiles, scenarios, variants, comparison specs, results, and local config",
    "workflow, quality gate, tools, or GitHub settings changes",
    "authorization of comparison execution or any later block"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

## Completed implementation authorization — Comparison readiness bridge 0.1

Daniel authorized autonomous continuation on 2026-07-28. This block connects
the independently audited SimulationCraft identity probe to the frozen
comparison preflight through an injectable, fail-closed readiness boundary.
Tests use only simulated collaborators. The audited implementation was
published in `a66e96a1001ff2fbc37e565a14305ee0c053fbb2`, and GitHub Actions run
`30336527406` passed all three lanes. The authorization is consumed and does
not permit a real SimulationCraft invocation, run reservation, comparison, or
result.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
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
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

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
