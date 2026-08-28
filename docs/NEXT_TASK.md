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

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
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
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

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

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "native_release_key_ceremony_launcher_0_1",
  "title": "Implement the native attended production key ceremony launcher without running it",
  "baseline_commit": "22c2ba3bbf1f039d345c1dde82ba647f537eaf59",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "native_release_key_ceremony_launcher_0_1-20260801-daniel-passphrase-retry",
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
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `native_release_key_ceremony_launcher_0_1_authorized_for_simulated_testing_only`.

Usability correction: after two safe pre-generation aborts, Daniel authorized
continuation. The launcher may ignore surrounding whitespace in checkpoint
phrases and convert expected operator-input errors into concise safe-cancel
messages. This does not relax phrase content or any security checkpoint.

Masked-input correction: after a safe `passphrase_mismatch` abort, Daniel
requested visible length feedback on his local computer. The launcher may show
one `*` per entered character and support Backspace while never echoing the
actual character. The two full secret values must still match exactly.

Retry correction: Daniel requested direct password retry without repeating the
four ceremony checkpoints. The launcher may allow at most three local attempts
for mismatch or insufficient length, still before key generation. Exhaustion
aborts safely; messages reveal neither password value.

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

## Active implementation — Production release trust registry 0.1

The attended ceremony created and internally verified one production Ed25519
key. This task may publish only its public identity and non-secret ceremony
binding. It may not read plaintext private material, decrypt the recovery
copy, sign a release, or activate distribution.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "production_release_trust_registry_0_1",
  "title": "Register the first production release public key",
  "baseline_commit": "8aec71d05212caf8590ae39e2391c19af9510bb2",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "production_release_trust_registry_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T10:31:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "knowledge/trust/release_trust_registry_0_1.json",
      "desktop-app/tests/test_production_release_trust_registry.py",
      "docs/RELEASE_KEY_CUSTODY.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/production_release_trust_registry_0_1/implementation.json",
      ".dpslab/quality-gates/production_release_trust_registry_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**",
      "desktop-app/src/**",
      "knowledge/releases/**",
      "knowledge/trust/release_trust_registry_synthetic_0_1.json",
      "knowledge/schemas/**",
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
      "argv": ["python", "-m", "unittest", "tests.test_production_release_trust_registry", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 814,
    "minimum_test_count": 819
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/release_signing.py": "50b38b6875b317b58bba1b0b32dc9beceb1dec89c4b92e12a06770e4e58c8604",
    "knowledge/schemas/release_trust_registry_0_1.json": "e0c5538a58dcb733a315690b30c868d9324f5030455a2a583c1c6da582a60e11"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "exactly the four authorized versioned paths in the delta",
    "the production registry validates canonically and its content hash matches",
    "the sole public key decodes to exactly 32 bytes and its SHA-256 matches the ceremony evidence",
    "key identity and validity exactly match the verified ceremony evidence",
    "the registry contains no private, protected-container, recovery, passphrase, or personal-path material",
    "focused tests, full functional suite, tools tests, and protected hashes pass",
    "no release signing, activation, distribution, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "private-key access or DPAPI unprotection",
    "recovery decryption or passphrase handling",
    "release signing, publication, activation, or distribution",
    "production code, schemas, workflows, GitHub settings, addon, UI, and SimulationCraft",
    "commits, pushes, tags, branches, pull requests, and remote changes"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `production_release_trust_registry_0_1_authorized_for_implementation`.

## Production release trust registry 0.1 — approved implementation

The four-path implementation was reviewed against the verified non-secret
ceremony evidence. The production registry contains only the public Ed25519
key and its time-bounded trust metadata. Its canonical registry hash is
`4948b246303c99c7f7ead0f550baef75bd095ae375aa82e431caf96162c880d8`;
the decoded public key fingerprint is
`dbcca6f6baf6ceb5e883971ad8727de2a7a858e1669a86d8bcc04d49ba9a4af3`.

Focused tests passed 5/5, the functional suite passed 819/819 with one
pre-existing skip, and tools tests passed 52/52. The declared and procedural
audit recorded no findings. The implementation authorization is consumed by
this approved delta; publication and CI verification remain pending. This
approval does not authorize release signing, activation, distribution,
private-key access, recovery decryption, SimulationCraft, or a later block.

Approval verdict: `production_release_trust_registry_0_1_approved_pending_commit`.

## Production release trust registry 0.1 — publication closure

Commit `33405fab73704dbaaa079cafbd712012458a198c` published the exact audited
four-path delta to `main`. Local `HEAD`, `origin/main`, and the live remote
branch matched that commit. GitHub Actions run `30706440486` passed Policy and
contract, Tools tests, and Functional suite. The production public registry is
therefore published and CI-verified. This state makes the key discoverable for
future separately authorized signing operations; it does not sign, publish,
activate, or distribute any release.

Closure verdict: `production_release_trust_registry_0_1_published_ci_approved`.

## Active documentation task — Production trust registry closure 0.1

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "production_release_trust_registry_closure_0_1",
  "title": "Record publication and CI closure of the production public trust registry",
  "baseline_commit": "33405fab73704dbaaa079cafbd712012458a198c",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "production_release_trust_registry_closure_0_1-20260801-daniel-expanded",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T10:42:00-05:00"
  },
  "scope": {
    "allowed_paths": ["docs/NEXT_TASK.md"],
    "generated_paths": [
      ".dpslab/quality-gates/production_release_trust_registry_closure_0_1/implementation.json",
      ".dpslab/quality-gates/production_release_trust_registry_closure_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "profiles/**",
      "scenarios/**", "variants/**", "comparisons/**", "results/**",
      "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": ".",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tools/tests", "-v"],
      "environment": {"PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": ".",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tools/tests", "-v"],
      "environment": {"PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 52,
    "minimum_test_count": 52
  },
  "protected_files": {
    "knowledge/trust/release_trust_registry_0_1.json": "26b5da31d34fa1f5c1115438aee7ebe75b71b25f8c44706a6c91164ea2064f0c",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5",
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "docs/NEXT_TASK.md is the only versioned path in the delta",
    "the exact commit and GitHub Actions run are recorded",
    "published and CI-verified do not imply release signing or activation",
    "tools tests and protected hashes pass",
    "no code, registry, secret, release, SimulationCraft, commit, or push beyond this closure"
  ],
  "express_exclusions": [
    "all code, tests, workflows, registries, schemas, profiles, and results",
    "private-key access, recovery decryption, release signing, activation, and distribution",
    "SimulationCraft and real comparisons",
    "tags, branches, pull requests, settings, and unrelated remote changes"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Closure-document verdict: `production_release_trust_registry_closure_0_1_approved_pending_commit`.

## Active design task — First production release candidate readiness 0.1

The production public key is published and CI-verified, but no production
knowledge release candidate exists. The repository contains only
`candidate_knowledge_release_bundle_synthetic_0_1.json`, whose identifiers,
evidence limitations, source claims, review authority, and publisher identity
are explicitly synthetic. It is test evidence and must never be relabeled or
signed as a production release.

The next implementation block must introduce a fail-closed production
readiness boundary before any private-key operation. It must accept only an
exact durable candidate generation with current source coverage, an exact
human review decision, role-specific safety, current build/interface bounds,
an unsigned canonical manifest, and the published production key identity.
Synthetic, placeholder, expired, incomplete, stale, ambiguous, or already
signed input must be rejected before a signer can be constructed.

Recommended decisions:

1. The first candidate remains internal and unpublished until its exact
   content and compatibility bounds receive human review; `stable` is not
   inferred from a synthetic fixture.
2. Production readiness must be a pure read-only assessment with no DPAPI,
   signing, filesystem mutation, network, activation, or distribution effect.
3. Currentness is proven from governed source captures and explicit UTC/build
   applicability, never from filename, newest-known fallback, or chat history.
4. Damage, tank, and healer guidance retain their distinct safety policies;
   incomplete role coverage is reported explicitly and never filled by a
   generic DPS template.
5. Candidate construction, human approval, attended signing, signature
   verification, publication decision, and distribution remain separate
   transactions.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "production_release_candidate_readiness_0_1",
  "title": "Design the fail-closed readiness boundary for the first production release candidate",
  "baseline_commit": "8289aa40c7736f3f9bd05d00dac9710ab571fea2",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "production_release_candidate_readiness_0_1-20260801-daniel-continue",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T10:48:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/production_release_readiness.py",
      "desktop-app/tests/test_production_release_readiness.py",
      "docs/CANDIDATE_KNOWLEDGE_SET.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/production_release_candidate_readiness_0_1/implementation.json",
      ".dpslab/quality-gates/production_release_candidate_readiness_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "desktop-app/src/dpslab/windows_release_signer.py",
      "desktop-app/src/dpslab/windows_key_protection.py", "knowledge/releases/**",
      "knowledge/trust/**", "knowledge/catalogs/**", "knowledge/fixtures/**",
      "profiles/**", "scenarios/**", "variants/**", "comparisons/**",
      "results/**", "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_production_release_readiness", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 819,
    "minimum_test_count": 827
  },
  "protected_files": {
    "knowledge/trust/release_trust_registry_0_1.json": "26b5da31d34fa1f5c1115438aee7ebe75b71b25f8c44706a6c91164ea2064f0c",
    "knowledge/releases/candidate_knowledge_release_bundle_synthetic_0_1.json": "f3ab281dfb8d2a17d13ff254e988b131a2ca026a72e0132526670d95a3b774a3",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5",
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "a pure typed assessment returns ready or explicit fail-closed reasons",
    "synthetic and placeholder material is rejected before signer construction",
    "current source coverage, exact human review, role safety, compatibility, expiry, and production key identity are required",
    "already signed or noncanonical input is rejected",
    "tests use synthetic in-memory mutations and no production private material",
    "no signing, DPAPI, recovery, publication, activation, distribution, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "changes outside the four authorized implementation paths",
    "creation or modification of any real knowledge candidate",
    "private-key access, signing, recovery decryption, activation, and distribution",
    "network capture, live recommendations, addon, UI, SimulationCraft, and real comparisons",
    "commits and pushes except a separately audited publication of this design document"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Design verdict: `production_release_candidate_readiness_0_1_design_ready`.

Current release verdict: `additional_evidence_required_no_production_candidate`.

Implementation-entry verdict: `production_release_candidate_readiness_0_1_authorized_for_implementation`.

## Production release candidate readiness 0.1 — implemented

The pure readiness boundary now rejects invalid candidate or registry input,
synthetic and placeholder material, stale evidence, mismatched channel,
build/interface drift, review drift, publisher-key mismatch, and a missing or
out-of-window production trust key. Success returns only eligibility for a
later attended signing review.

Focused tests passed 8/8 and the functional suite passed 827/827 with one
pre-existing skip. One initial full-suite attempt encountered the known
Windows temporary-directory cleanup error (`WinError 145`); the diagnostic
run identified that environmental cause and the single formal repetition
passed. No signer was constructed and no DPAPI, private key, recovery,
signature, release, network, or SimulationCraft operation occurred.

Implementation verdict: `production_release_candidate_readiness_0_1_implemented_pending_final_audit`.

## Active design task — Official source acquisition 0.1

The first production candidate requires current first-party evidence. The
official World of Warcraft Content Update Notes index is the canonical change
discovery surface, while the Battle.net World of Warcraft Game Data APIs are
the preferred structured first-party data surface where an applicable endpoint
exists. Neither surface is itself a recommendation source: captured changes
remain quarantined until structured extraction, source coverage, role safety,
and human review all pass.

The desktop application must not transform live patch notes into immediate
user guidance. The maintenance pipeline detects official-source changes,
prepares and reviews a candidate knowledge package, signs its exact manifest
through an attended operation, and publishes it separately. Desktop clients
then verify and consume signed DpsLab packages. This preserves automatic
updates without distributing Blizzard API secrets or allowing unreviewed
network content to alter recommendations.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "official_source_acquisition_0_1",
  "title": "Design first-party source discovery and quarantined acquisition",
  "baseline_commit": "1d9665052146ba6dd7ee97b56e512dd5a78dbb51",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "official_source_acquisition_0_1-20260801-daniel-expanded-design",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T11:58:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "docs/OFFICIAL_SOURCE_ACQUISITION.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/official_source_acquisition_0_1/implementation.json",
      ".dpslab/quality-gates/official_source_acquisition_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "profiles/**",
      "scenarios/**", "variants/**", "comparisons/**", "results/**",
      "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": ".",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tools/tests", "-v"],
      "environment": {"PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": ".",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tools/tests", "-v"],
      "environment": {"PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 52,
    "minimum_test_count": 52
  },
  "protected_files": {
    "desktop-app/src/dpslab/patch_source_adapter.py": "14c826d7f1b40467602949c2958f71b0343fac72c9561eb2625bd0bfa494bbee",
    "desktop-app/src/dpslab/source_coverage.py": "85bfddadfd8fc5d6704d8bba9df223db27e6123a09e835629d3b8765afab63a7",
    "knowledge/trust/release_trust_registry_0_1.json": "26b5da31d34fa1f5c1115438aee7ebe75b71b25f8c44706a6c91164ea2064f0c",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "only first-party Blizzard sources are authoritative for automatic discovery",
    "official patch notes and Game Data APIs have separate discovery and structured-data roles",
    "network responses enter quarantine and never become recommendations directly",
    "desktop automatic updates consume only reviewed signed DpsLab packages",
    "OAuth credentials and API secrets are never embedded in addon, desktop binaries, catalogs, logs, or repository",
    "source snapshots are content-addressed and prior captures remain historical-only",
    "no network implementation, live capture, secret, signing, publication, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "implementation under this design-only authorization",
    "live HTTP requests or storage of Blizzard page contents",
    "credentials, OAuth registration, scraping, parsing, recommendations, or real catalogs",
    "signing, release activation, distribution, addon, UI, SimulationCraft, and comparisons",
    "commits and pushes except separate publication of this design document"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Design verdict: `official_source_acquisition_0_1_design_ready`.

## Active implementation — Official request planning 0.1

This implementation is limited to constructing inert HTTPS request plans for
an injected transport. It cannot open sockets, resolve DNS, follow redirects,
read credentials, persist responses, parse patch facts, or approve evidence.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "official_source_request_planning_0_1",
  "title": "Implement pure fail-closed official-source request planning",
  "baseline_commit": "2355fedcd58779a14b9a29d87c694840048b1c57",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "official_source_request_planning_0_1-20260801-daniel-continue",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T12:05:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/official_source_request.py",
      "desktop-app/tests/test_official_source_request.py",
      "docs/OFFICIAL_SOURCE_ACQUISITION.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/official_source_request_planning_0_1/implementation.json",
      ".dpslab/quality-gates/official_source_request_planning_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "desktop-app/src/dpslab/patch_source_adapter.py",
      "desktop-app/src/dpslab/source_coverage.py", "knowledge/**", "profiles/**",
      "scenarios/**", "variants/**", "comparisons/**", "results/**",
      "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_official_source_request", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 827,
    "minimum_test_count": 837
  },
  "protected_files": {
    "desktop-app/src/dpslab/patch_source_adapter.py": "14c826d7f1b40467602949c2958f71b0343fac72c9561eb2625bd0bfa494bbee",
    "desktop-app/src/dpslab/source_coverage.py": "85bfddadfd8fc5d6704d8bba9df223db27e6123a09e835629d3b8765afab63a7",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5",
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "plans are immutable inert values with GET, exact HTTPS URL, bounded headers, redirect hosts, media types, and maximum bytes",
    "patch-note discovery is confined to the exact Blizzard host and en-us path",
    "Game Data API plans are confined to the official API host, /data/wow paths, namespace, and en_US locale",
    "credentials are represented only as an external requirement and never accepted as input or emitted as a header",
    "userinfo, fragments, traversal, control characters, arbitrary query keys, and non-HTTPS URLs fail closed",
    "conditional validators are sanitized and bounded",
    "no network, DNS, credential, persistence, parsing, approval, signing, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "HTTP transport and live requests",
    "OAuth token acquisition, client identifiers, secrets, or Authorization headers",
    "response persistence, HTML parsing, fact extraction, catalogs, and recommendations",
    "signing, release activation, distribution, addon, UI, SimulationCraft, and comparisons",
    "changes outside the four authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `official_source_request_planning_0_1_authorized_for_implementation`.

## Official request planning 0.1 — implemented

The planner now creates immutable inert plans for the exact content-update
notes endpoint and bounded Game Data API paths. It rejects unsafe paths,
namespaces, locales, validators, credentials, redirects, and query expansion.
Focused tests passed 10/10 and the functional suite passed 837/837 with one
pre-existing skip. No network or credential operation occurred.

Implementation verdict: `official_source_request_planning_0_1_implemented_pending_final_audit`.

## Active implementation — Injected official-source transport 0.1

The transport boundary executes no built-in networking. It accepts an injected
sender, validates the complete response against the immutable request plan,
and returns only a quarantined `InjectedResponse`. Credentialed API plans stop
before sender invocation in this block.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "official_source_injected_transport_0_1",
  "title": "Implement simulated and injected official-source transport validation",
  "baseline_commit": "ee6de2ba34ea673389e845bc09c5163e09c24596",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "official_source_injected_transport_0_1-20260801-daniel-continue",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T14:02:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/official_source_transport.py",
      "desktop-app/tests/test_official_source_transport.py",
      "docs/OFFICIAL_SOURCE_ACQUISITION.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/official_source_injected_transport_0_1/implementation.json",
      ".dpslab/quality-gates/official_source_injected_transport_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "desktop-app/src/dpslab/official_source_request.py",
      "desktop-app/src/dpslab/patch_source_adapter.py", "knowledge/**", "profiles/**",
      "scenarios/**", "variants/**", "comparisons/**", "results/**",
      "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_official_source_transport", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 837,
    "minimum_test_count": 847
  },
  "protected_files": {
    "desktop-app/src/dpslab/official_source_request.py": "4a62f047d71316872198b85c99ff16182d9f543cae36dd41c4535b405ddd2501",
    "desktop-app/src/dpslab/patch_source_adapter.py": "14c826d7f1b40467602949c2958f71b0343fac72c9561eb2625bd0bfa494bbee",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5",
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "the sender is injected and tests use simulated responses only",
    "credentialed plans stop as credential_required before sender invocation",
    "only status 200 and structurally valid 304 responses reach quarantine",
    "final HTTPS host and path remain confined to the original plan and explicit redirect policy",
    "media type, byte count, completeness, timeout, ETag, and Last-Modified fail closed",
    "transport exceptions become typed unavailable outcomes without exception text or secrets",
    "successful output is an InjectedResponse pending the existing capture and review boundaries",
    "no built-in HTTP client, DNS, live network, OAuth, credential, persistence, parsing, approval, signing, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "urllib, requests, sockets, or any other built-in transport implementation",
    "live requests and first production capture",
    "OAuth, bearer tokens, client identifiers, secrets, or Authorization headers",
    "response storage, parsing, fact extraction, catalogs, and recommendations",
    "changes outside the four authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `official_source_injected_transport_0_1_authorized_for_implementation`.

## Injected official-source transport 0.1 — implemented

The injected boundary now validates simulated responses and returns only
quarantined evidence. Credentialed plans stop before sender invocation.
Focused tests passed 10/10 and the functional suite passed 847/847 with one
pre-existing skip. No live network, credential, persistence, or parsing
operation occurred.

Implementation verdict: `official_source_injected_transport_0_1_implemented_pending_final_audit`.

## Active implementation — Public HTTPS client 0.1

This block adds a concrete standard-library HTTPS client for credential-free
plans only. It denies redirects before following them, reads one bounded
response into memory, and delegates all semantic acceptance to the injected
transport validator. Tests inject a fake opener; no live request belongs to
the implementation task.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "official_public_https_client_0_1",
  "title": "Implement bounded credential-free HTTPS retrieval for official public sources",
  "baseline_commit": "ce9029b7830697bdb6080cb688878ca60064d61c",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "official_public_https_client_0_1-20260801-daniel-continue",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T14:15:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/official_source_http.py",
      "desktop-app/tests/test_official_source_http.py",
      "docs/OFFICIAL_SOURCE_ACQUISITION.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/official_public_https_client_0_1/implementation.json",
      ".dpslab/quality-gates/official_public_https_client_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "desktop-app/src/dpslab/official_source_request.py",
      "desktop-app/src/dpslab/official_source_transport.py", "knowledge/**", "profiles/**",
      "scenarios/**", "variants/**", "comparisons/**", "results/**",
      "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "tests.test_official_source_http", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 847,
    "minimum_test_count": 857
  },
  "protected_files": {
    "desktop-app/src/dpslab/official_source_request.py": "4a62f047d71316872198b85c99ff16182d9f543cae36dd41c4535b405ddd2501",
    "desktop-app/src/dpslab/official_source_transport.py": "9276c80830341ac3a00b1306822592ae3c221c56db26bf0e857ed9c06b47b221",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5",
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "only OfficialRequestPlan values with credential_mode none are sent",
    "the request uses GET, the exact plan URL and headers, and a bounded timeout",
    "redirects are denied before a second request is made",
    "response reads are bounded to max_bytes plus one and oversized content fails closed",
    "Content-Length disagreement, malformed length, transport exceptions, and HTTP errors are sanitized",
    "the concrete client delegates final URL, media, status, completeness, and validator checks to official_source_transport",
    "tests inject fake openers and prove zero live network dependency",
    "no live request, OAuth, credential, persistence, parsing, approval, signing, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "first live official-source request",
    "authenticated Game Data API transport",
    "OAuth, tokens, client identifiers, secrets, or Authorization headers",
    "response persistence, parsing, fact extraction, catalogs, and recommendations",
    "changes outside the four authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `official_public_https_client_0_1_authorized_for_implementation`.

## Active implementation — Official HTML source registry 0.1

The first live public diagnostic returned a complete HTML response from the
exact Blizzard Content Update Notes endpoint. This block may add HTML to the
closed media-type vocabulary and register only that exact first-party source.
It does not repeat the request or store the observed response.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "official_html_source_registry_0_1",
  "title": "Register Blizzard Content Update Notes as an explicit HTML source",
  "baseline_commit": "aec1a4031f7422057c29007c70006db5b9d6c15c",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "official_html_source_registry_0_1-20260801-daniel-approved-adjustment",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T14:28:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/patch_source_adapter.py",
      "desktop-app/tests/test_patch_source_adapter.py",
      "knowledge/sources/official_patch_source_registry_0_1.json",
      "docs/OFFICIAL_SOURCE_ACQUISITION.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/official_html_source_registry_0_1/implementation.json",
      ".dpslab/quality-gates/official_html_source_registry_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "desktop-app/src/dpslab/official_source_http.py",
      "desktop-app/src/dpslab/official_source_request.py",
      "desktop-app/src/dpslab/official_source_transport.py", "knowledge/snapshots/**",
      "knowledge/catalogs/**", "knowledge/fixtures/**", "profiles/**", "scenarios/**",
      "variants/**", "comparisons/**", "results/**", "config/**", "flasil.simc", "tools/**"
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
    "baseline_test_count": 857,
    "minimum_test_count": 860
  },
  "protected_files": {
    "desktop-app/src/dpslab/official_source_http.py": "423a28a8db7fdbffbe9d46a28ca652ba756d318752b6902f4286edf280c7b1a9",
    "desktop-app/src/dpslab/official_source_request.py": "4a62f047d71316872198b85c99ff16182d9f543cae36dd41c4535b405ddd2501",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5",
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "text/html is accepted only when explicitly listed by a validated source",
    "the canonical production registry contains exactly the Blizzard Content Update Notes source",
    "the exact host, no redirects, en_us_canonical locale, one-megabyte bound, and maintainer review remain closed",
    "the registry is canonical and its SHA-256 projection validates",
    "HTML supplied to a JSON-only source still fails closed",
    "a valid official-shaped HTML response remains captured_pending_review only",
    "no live request, response storage, parsing, recommendation, credential, signing, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "repeat of the live diagnostic or persistence of its bytes",
    "HTML parsing, fact extraction, source approval, catalog generation, and recommendations",
    "authenticated APIs, OAuth, tokens, secrets, signing, activation, and distribution",
    "changes outside the five authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `official_html_source_registry_0_1_authorized_for_implementation`.

## Implementation result — Official HTML source registry 0.1

The authorized implementation changed only the five allowlisted paths. It
extended the closed adapter vocabulary with `text/html`, added one canonical
registry entry for Blizzard Content Update Notes, and preserved per-source
media enforcement and `captured_pending_review` quarantine semantics.

The focused adapter module passed 41/41 tests. The complete functional suite
passed 860/860 tests with one existing skip and exit code 0. Protected hashes
matched the contract, SimulationCraft was not invoked, and no live request or
response persistence occurred. The procedural independent audit recorded no
findings and status `audit_recorded_not_automatically_approved`.

Daniel's approval of the adjustment and instruction to continue consumes the
implementation authorization for further edits. Publication of the exact
audited delta remains a separate traceable operation and does not approve the
source content, parsing, recommendations, or another network request.

Implementation verdict: `official_html_source_registry_0_1_approved_for_commit`.

## Active design task — Secondary source policy 0.1

Community and analytical sources can help discover omissions, explain
mechanics, and corroborate facts that Blizzard does not expose in a structured
surface. They remain lower-authority evidence and cannot silently replace,
override, or approve first-party facts. No named site is allowlisted by this
design.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "secondary_source_policy_0_1",
  "title": "Design governed use of community and analytical WoW sources",
  "baseline_commit": "1f3f6e230f236e32b51220a24e9d89320ac008a0",
  "authorization": {
    "status": "design_only",
    "authorization_id": "secondary_source_policy_0_1-20260801-daniel-continue",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T14:31:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "docs/SECONDARY_SOURCE_POLICY.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [],
    "forbidden_paths": [
      ".github/**", "desktop-app/**", "knowledge/**", "profiles/**",
      "scenarios/**", "variants/**", "comparisons/**", "results/**",
      "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": ".",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tools/tests", "-v"],
      "environment": {"PYTHONDONTWRITEBYTECODE": "1"}
    },
    "full": {
      "working_directory": ".",
      "argv": ["python", "-m", "unittest", "discover", "-s", "tools/tests", "-v"],
      "environment": {"PYTHONDONTWRITEBYTECODE": "1"}
    },
    "baseline_test_count": 52,
    "minimum_test_count": 52
  },
  "protected_files": {
    "desktop-app/src/dpslab/patch_source_adapter.py": "985feae6cdb28080d73922ae4b28bda711aef86b4b1984b78444dd60d4b26802",
    "desktop-app/src/dpslab/source_coverage.py": "85bfddadfd8fc5d6704d8bba9df223db27e6123a09e835629d3b8765afab63a7",
    "knowledge/trust/release_trust_registry_0_1.json": "26b5da31d34fa1f5c1115438aee7ebe75b71b25f8c44706a6c91164ea2064f0c",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "first-party Blizzard evidence always retains higher authority for facts it publishes",
    "secondary sources are used only for discovery, corroboration, explanation, or explicit first-party coverage gaps",
    "every candidate source requires separate identity, ownership, license and terms review, freshness, applicability, and acquisition policy",
    "conflicts with first-party evidence or between secondary sources remain explicit review blockers",
    "absence of first-party structured data never converts one community assertion into an approved fact",
    "stored evidence is minimized and content bodies are not retained or redistributed without explicit permission",
    "no site allowlisting, network access, scraping, parsing, real capture, recommendation, commit, or push"
  ],
  "express_exclusions": [
    "approval or allowlisting of Wowhead or any other named site",
    "legal conclusion about licenses, terms of use, robots policy, or redistribution rights",
    "HTTP clients, browser automation, scraping, APIs, downloads, credentials, or persistence",
    "catalog mutation, recommendations, signing, distribution, addon, UI, SimulationCraft, and comparisons",
    "implementation outside the two documentary paths"
  ]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design verdict: `secondary_source_policy_0_1_design_ready`.

## Active design task — Official source capture receipt 0.1

Two controlled memory-only requests returned the same 274005-byte SHA-256 for
the exact Blizzard Content Update Notes endpoint. The published client,
transport, and registry now produce `captured_pending_review`. This block
designs a content-free receipt so freshness and change detection can be audited
without storing or redistributing the page body.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "official_source_capture_receipt_0_1",
  "title": "Implement canonical metadata-only receipts for quarantined official captures",
  "baseline_commit": "ff7f8b6f63cae46292278d821b42fbe269f2cfc4",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "official_source_capture_receipt_0_1-20260801-daniel-continue-implementation",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T14:38:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/official_source_receipt.py",
      "desktop-app/tests/test_official_source_receipt.py",
      "knowledge/schemas/official_source_capture_receipt_0_1.json",
      "knowledge/snapshots/official_source_capture_receipt_synthetic_0_1.json",
      "docs/OFFICIAL_SOURCE_ACQUISITION.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/official_source_capture_receipt_0_1/implementation.json",
      ".dpslab/quality-gates/official_source_capture_receipt_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "profiles/**", "scenarios/**",
      "variants/**", "comparisons/**", "results/**", "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "tests.test_official_source_receipt", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "full": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "baseline_test_count": 860,
    "minimum_test_count": 872
  },
  "protected_files": {
    "desktop-app/src/dpslab/official_source_http.py": "423a28a8db7fdbffbe9d46a28ca652ba756d318752b6902f4286edf280c7b1a9",
    "desktop-app/src/dpslab/patch_source_adapter.py": "985feae6cdb28080d73922ae4b28bda711aef86b4b1984b78444dd60d4b26802",
    "knowledge/sources/official_patch_source_registry_0_1.json": "665ac715a7ba66b51e5a21886a14177cf39164d9422dd10f441161a147439d7e",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "receipt contains source identity, capture time, status, final host, media type, byte count, content SHA-256, completeness, and sanitized validators",
    "receipt contains no response body, extracted prose, cookies, credentials, personal path, or recommendation",
    "canonical hashing binds the receipt and duplicate hashes remain explicit",
    "receipt status cannot exceed captured_pending_review",
    "implementation uses synthetic fixtures and injected clocks only",
    "no additional live request, persistence, parser, catalog change, recommendation, commit, or push"
  ],
  "express_exclusions": [
    "storage or redistribution of Blizzard page contents",
    "HTML parsing, semantic extraction, facts, coverage approval, and recommendations",
    "secondary-source acquisition, authenticated APIs, credentials, signing, distribution, addon, UI, SimulationCraft, and comparisons",
    "changes outside the six authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `official_source_capture_receipt_0_1_authorized_for_implementation`.

## Active implementation — Official receipt change detection 0.1

This block compares canonical metadata-only receipts. It retains only the
minimum receipt metadata needed for audit and classifies a source as first
seen, unchanged, or changed pending review. Historical metadata cannot satisfy
current source coverage and no content body is accepted.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "official_source_receipt_change_detection_0_1",
  "title": "Classify changes across canonical official-source receipts",
  "baseline_commit": "66f31c4084f5747b3cbe1ae1de50227ab8e9d4ce",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "official_source_receipt_change_detection_0_1-20260801-daniel-continue",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T15:18:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/official_source_change.py",
      "desktop-app/tests/test_official_source_change.py",
      "docs/OFFICIAL_SOURCE_ACQUISITION.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/official_source_receipt_change_detection_0_1/implementation.json",
      ".dpslab/quality-gates/official_source_receipt_change_detection_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "knowledge/**", "profiles/**", "scenarios/**", "variants/**",
      "comparisons/**", "results/**", "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "tests.test_official_source_change", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "full": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "baseline_test_count": 872,
    "minimum_test_count": 884
  },
  "protected_files": {
    "desktop-app/src/dpslab/official_source_receipt.py": "cae5e9a03780b8e3b13bb9be44ef3a2eab6c0d5ef99562ac9e3b1a4206fe9186",
    "desktop-app/src/dpslab/official_source_http.py": "423a28a8db7fdbffbe9d46a28ca652ba756d318752b6902f4286edf280c7b1a9",
    "knowledge/sources/official_patch_source_registry_0_1.json": "665ac715a7ba66b51e5a21886a14177cf39164d9422dd10f441161a147439d7e",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "first receipt is first_seen_pending_review",
    "equal source and content hashes are unchanged",
    "a different content hash is changed_pending_review",
    "source, host, or media mismatch fails closed",
    "receipt IDs are unique and capture times strictly increase",
    "history is immutable metadata only and cannot establish current coverage",
    "no network, response body, parser, catalog mutation, recommendation, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "database or unbounded historical warehouse",
    "real receipt persistence and scheduled acquisition",
    "HTML storage, parsing, facts, approval, signing, distribution, addon, or UI",
    "changes outside the four authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `official_source_receipt_change_detection_0_1_authorized_for_implementation`.

## Active implementation — Official source schedule policy 0.1

This block decides when a public official source check is due. It is a pure
policy boundary with an injected UTC clock; it neither sleeps nor performs,
schedules, or retries network operations.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "official_source_schedule_policy_0_1",
  "title": "Implement bounded scheduling and backoff policy for official-source checks",
  "baseline_commit": "099a001465a6cd0016d2101761c851cf0120a541",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "official_source_schedule_policy_0_1-20260801-daniel-forward",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T15:24:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/official_source_schedule.py",
      "desktop-app/tests/test_official_source_schedule.py",
      "docs/OFFICIAL_SOURCE_ACQUISITION.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/official_source_schedule_policy_0_1/implementation.json",
      ".dpslab/quality-gates/official_source_schedule_policy_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "knowledge/**", "profiles/**", "scenarios/**", "variants/**",
      "comparisons/**", "results/**", "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "tests.test_official_source_schedule", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "full": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "baseline_test_count": 884,
    "minimum_test_count": 896
  },
  "protected_files": {
    "desktop-app/src/dpslab/official_source_change.py": "d07f1a1c8d59264122bf9e20fa9a70ffd4503c5854dea8d2aec98410eed33982",
    "desktop-app/src/dpslab/official_source_receipt.py": "cae5e9a03780b8e3b13bb9be44ef3a2eab6c0d5ef99562ac9e3b1a4206fe9186",
    "desktop-app/src/dpslab/official_source_http.py": "423a28a8db7fdbffbe9d46a28ca652ba756d318752b6902f4286edf280c7b1a9",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "no prior receipt is due for an initial check",
    "a fresh receipt is not_due and returns its exact next due time",
    "elapsed interval or expired freshness is due",
    "failures use bounded exponential backoff and never loop or sleep",
    "naive clocks, clock regression, booleans as integers, and invalid policy ranges fail closed",
    "receipt validation remains mandatory",
    "no network, scheduler registration, persistence, parser, recommendation, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "Windows Task Scheduler, cron, background service, or automatic retry",
    "real request, credential, receipt persistence, content parsing, and catalog mutation",
    "signing, distribution, addon, UI, SimulationCraft, and comparisons",
    "changes outside the four authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `official_source_schedule_policy_0_1_authorized_for_implementation`.

## Active implementation — Official source cycle coordinator 0.1

The coordinator composes the published pure boundaries into one injected,
single-attempt transaction. It cannot create a network client, persist state,
retry, parse content, or approve a source.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "official_source_cycle_coordinator_0_1",
  "title": "Coordinate one scheduled official-source capture transaction with injected transport",
  "baseline_commit": "42ec1954a5b2409cc55022085e92d828682a3d2b",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "official_source_cycle_coordinator_0_1-20260801-daniel-all-necessary",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T15:31:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/official_source_cycle.py",
      "desktop-app/tests/test_official_source_cycle.py",
      "docs/OFFICIAL_SOURCE_ACQUISITION.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/official_source_cycle_coordinator_0_1/implementation.json",
      ".dpslab/quality-gates/official_source_cycle_coordinator_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "knowledge/**", "profiles/**", "scenarios/**", "variants/**",
      "comparisons/**", "results/**", "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "tests.test_official_source_cycle", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "full": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "baseline_test_count": 896,
    "minimum_test_count": 910
  },
  "protected_files": {
    "desktop-app/src/dpslab/official_source_schedule.py": "30beb7e09c14d0c2f4c50927f31fd22971c5c15c6720d6b51dc22fb8ce79f982",
    "desktop-app/src/dpslab/official_source_change.py": "d07f1a1c8d59264122bf9e20fa9a70ffd4503c5854dea8d2aec98410eed33982",
    "desktop-app/src/dpslab/official_source_receipt.py": "cae5e9a03780b8e3b13bb9be44ef3a2eab6c0d5ef99562ac9e3b1a4206fe9186",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "not_due and backoff decisions never invoke the injected fetcher",
    "a due cycle performs at most one injected fetch",
    "conditional validators are taken only from a validated previous receipt",
    "transport and capture failures produce sanitized evidence_unavailable without a receipt",
    "successful 200 and 304 outcomes produce canonical metadata-only receipts",
    "change classification remains first_seen_pending_review, unchanged, or changed_pending_review",
    "no network implementation, persistence, automatic retry, body retention, parsing, recommendation, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "concrete HTTPS client invocation and real source request",
    "scheduler service, filesystem writes, databases, queues, or background threads",
    "HTML parsing, facts, coverage approval, catalogs, signing, distribution, addon, or UI",
    "changes outside the four authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `official_source_cycle_coordinator_0_1_authorized_for_implementation`.

## Active implementation — Official receipt atomic store 0.1

This block persists only canonical receipt metadata in one bounded JSON ledger
per source. It is a recoverable local file boundary, not a database or content
archive.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "official_source_receipt_atomic_store_0_1",
  "title": "Persist bounded official-source receipt metadata atomically",
  "baseline_commit": "c11599ab215452aed7fd141bdf5bf2b6ba6e14e9",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "official_source_receipt_atomic_store_0_1-20260801-daniel-next-blocks",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T15:42:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/official_source_store.py",
      "desktop-app/tests/test_official_source_store.py",
      "knowledge/schemas/official_source_receipt_ledger_0_1.json",
      "docs/OFFICIAL_SOURCE_ACQUISITION.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/official_source_receipt_atomic_store_0_1/implementation.json",
      ".dpslab/quality-gates/official_source_receipt_atomic_store_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "knowledge/snapshots/**", "knowledge/catalogs/**", "profiles/**",
      "scenarios/**", "variants/**", "comparisons/**", "results/**", "config/**",
      "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "tests.test_official_source_store", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "full": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "baseline_test_count": 910,
    "minimum_test_count": 924
  },
  "protected_files": {
    "desktop-app/src/dpslab/official_source_cycle.py": "d60211431519454511ff11678d8deec1725dc85844776e2122fd45f490c5e04e",
    "desktop-app/src/dpslab/official_source_change.py": "d07f1a1c8d59264122bf9e20fa9a70ffd4503c5854dea8d2aec98410eed33982",
    "desktop-app/src/dpslab/official_source_receipt.py": "cae5e9a03780b8e3b13bb9be44ef3a2eab6c0d5ef99562ac9e3b1a4206fe9186",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "one canonical hash-bound ledger stores at most 32 metadata-only receipts per source",
    "source identity and strictly increasing receipt history remain enforced",
    "write uses a same-directory temporary file, flush, fsync, and atomic replace",
    "replace failure preserves the prior ledger and removes temporary residue",
    "root must be an existing absolute non-symlink directory and the filename is derived only from a validated source token",
    "no response body, database, network, parser, recommendation, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "real production receipt creation or source request",
    "HTML storage, extracted facts, catalog mutation, signing, distribution, addon, or UI",
    "background service, scheduler registration, queue, or automatic retry",
    "changes outside the five authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `official_source_receipt_atomic_store_0_1_authorized_for_implementation`.

## Active implementation — Attended official source operator 0.1

This adapter joins the published coordinator, public HTTPS client, and atomic
ledger behind an exact attended confirmation. Tests inject transport and use
temporary roots; no live request belongs to this implementation block.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "attended_official_source_operator_0_1",
  "title": "Implement attended one-shot official-source operation with atomic receipt persistence",
  "baseline_commit": "26a465628519d99eeee0b1deab17794b44ebdc29",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "attended_official_source_operator_0_1-20260801-daniel-next-blocks",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T15:51:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/official_source_operator.py",
      "desktop-app/tests/test_official_source_operator.py",
      "docs/OFFICIAL_SOURCE_ACQUISITION.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/attended_official_source_operator_0_1/implementation.json",
      ".dpslab/quality-gates/attended_official_source_operator_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "knowledge/**", "profiles/**", "scenarios/**", "variants/**",
      "comparisons/**", "results/**", "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "tests.test_official_source_operator", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "full": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "baseline_test_count": 924,
    "minimum_test_count": 936
  },
  "protected_files": {
    "desktop-app/src/dpslab/official_source_cycle.py": "d60211431519454511ff11678d8deec1725dc85844776e2122fd45f490c5e04e",
    "desktop-app/src/dpslab/official_source_store.py": "f70d2b923d28005533d5746075153d0c99826fe50c798cdfe810a875de32c9d2",
    "desktop-app/src/dpslab/official_source_http.py": "423a28a8db7fdbffbe9d46a28ca652ba756d318752b6902f4286edf280c7b1a9",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "operation requires an exact source- and receipt-bound confirmation token",
    "the latest validated ledger receipt is the only previous state",
    "at most one injected or concrete fetch is delegated to the coordinator",
    "only a successful metadata receipt is appended atomically",
    "not_due, backoff, and evidence_unavailable never mutate the ledger",
    "return value exposes status and receipt count without response content or secrets",
    "tests use injected fetchers and temporary roots with zero live network dependency"
  ],
  "express_exclusions": [
    "live source request or production receipt creation during implementation",
    "background operation, automatic confirmation, retry loop, scheduler registration, or database",
    "HTML parsing, facts, coverage approval, catalogs, signing, distribution, addon, UI, or SimulationCraft",
    "changes outside the four authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Implementation-entry verdict: `attended_official_source_operator_0_1_authorized_for_implementation`.

## Published implementation — Blizzard patch-note HTML extractor 0.1

The first attended integrated operation persisted one metadata-only receipt as
`first_seen_pending_review`. Extraction remains a separate pure boundary: it
receives injected bytes bound to that receipt and may emit only cited
structured evidence pending review.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "blizzard_patch_notes_html_extractor_0_1",
  "title": "Implement fail-closed extraction of cited Blizzard patch-note assertions",
  "baseline_commit": "fe6ac364e90c82f09d45bc0bd4756959f70419fa",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "blizzard_patch_notes_html_extractor_0_1-20260801-ci-eol-remediation",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T15:58:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/blizzard_patch_notes_extractor.py",
      "desktop-app/tests/test_blizzard_patch_notes_extractor.py",
      "knowledge/schemas/blizzard_patch_notes_extraction_0_1.json",
      "knowledge/fixtures/blizzard_patch_notes_synthetic_0_1.html",
      "knowledge/snapshots/blizzard_patch_notes_extraction_synthetic_0_1.json",
      "docs/BLIZZARD_PATCH_NOTES_EXTRACTOR.md",
      "docs/NEXT_TASK.md",
      ".gitattributes",
      "tools/tests/test_github_automation.py"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/blizzard_patch_notes_html_extractor_0_1/implementation.json",
      ".dpslab/quality-gates/blizzard_patch_notes_html_extractor_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "profiles/**", "scenarios/**",
      "variants/**", "comparisons/**", "results/**", "config/**", "flasil.simc"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "tests.test_blizzard_patch_notes_extractor", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "full": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "baseline_test_count": 936,
    "minimum_test_count": 954
  },
  "protected_files": {
    "desktop-app/src/dpslab/official_source_operator.py": "14e6598525850400f58d4c968c2ee5a47b27a40ff750ca5f8a120631cd024edb",
    "desktop-app/src/dpslab/official_source_cycle.py": "d60211431519454511ff11678d8deec1725dc85844776e2122fd45f490c5e04e",
    "desktop-app/src/dpslab/patch_evidence.py": "d2f3562e44b2ff92f6319305136887f97465e5b42c1d154f5a547e1de09b9fcf",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "input bytes must match a validated captured_pending_review receipt hash and byte count",
    "parser is source-specific, pure, deterministic, bounded, and uses no browser, JavaScript, CSS selector engine, or network",
    "only explicit headings, nested lists, literal old/new values, and stable citations may become assertions",
    "unknown layout, ambiguous subjects, omitted units, duplicate citations, or unsupported prose fail closed",
    "output remains pending_review and never mutates coverage, catalogs, templates, or recommendations",
    "implementation proposal uses synthetic HTML only and contains no copied Blizzard page body",
    "contractual HTML fixtures are checked out as LF on Windows and CI so byte-bound snapshots are portable",
    "no live request, persistence, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "general-purpose scraping or parsing of community sites",
    "natural-language inference, AI extraction, inferred coefficients, or automatic subject mapping",
    "real HTML fixtures, source-body redistribution, facts, approval, catalog mutation, signing, addon, or UI",
    "changes outside the nine authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `blizzard_patch_notes_html_extractor_0_1_published_with_ci_passed`.

Publication evidence:

- implementation commit: `fe6ac364e90c82f09d45bc0bd4756959f70419fa`;
- LF portability correction: `8578e60dedd7454474e4c7a2da7106dd54672647`;
- local verification: 20 focused and 956 functional tests passed;
- GitHub Actions run `30722814835`: policy, tools, and functional lanes passed;
- authorization consumed; no live source body, evidence approval, catalog
  mutation, recommendation, SimulationCraft, or comparison occurred.

## Published implementation — Blizzard patch-note layout probe 0.1

The published extractor intentionally accepts only a closed synthetic dialect.
A separate metadata-only probe must establish the shape of the real official
page before any production parser revision is proposed.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "blizzard_patch_notes_layout_probe_0_1",
  "title": "Implement a receipt-bound metadata-only probe for official patch-note layout",
  "baseline_commit": "8a703c4cbd2a1d8fa372a7f7c2900d8e4da4ccea",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "blizzard_patch_notes_layout_probe_0_1-20260801-daniel-continued-implementation",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T18:15:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/blizzard_patch_notes_layout_probe.py",
      "desktop-app/tests/test_blizzard_patch_notes_layout_probe.py",
      "knowledge/schemas/blizzard_patch_notes_layout_report_0_1.json",
      "knowledge/fixtures/blizzard_patch_notes_layout_synthetic_0_1.html",
      "knowledge/snapshots/blizzard_patch_notes_layout_synthetic_0_1.json",
      "docs/BLIZZARD_PATCH_NOTES_LAYOUT_PROBE.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/blizzard_patch_notes_layout_probe_0_1/implementation.json",
      ".dpslab/quality-gates/blizzard_patch_notes_layout_probe_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "profiles/**",
      "scenarios/**", "variants/**", "comparisons/**", "results/**",
      "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "tests.test_blizzard_patch_notes_layout_probe", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "full": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "baseline_test_count": 956,
    "minimum_test_count": 974
  },
  "protected_files": {
    "desktop-app/src/dpslab/blizzard_patch_notes_extractor.py": "1fa7c384fa2224a583340d4e896f73925b6843687837f588f7693256e10ff511",
    "desktop-app/src/dpslab/official_source_http.py": "423a28a8db7fdbffbe9d46a28ca652ba756d318752b6902f4286edf280c7b1a9",
    "knowledge/sources/official_patch_source_registry_0_1.json": "665ac715a7ba66b51e5a21886a14177cf39164d9422dd10f441161a147439d7e",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "design binds injected UTF-8 bytes to one validated captured_pending_review receipt",
    "report contains tag names, parent-child edges, attribute names, bounded counts, and boolean hazard indicators only",
    "text, attribute values, URLs, selectors, HTML fragments, headers, cookies, credentials, and source prose are never retained",
    "node, depth, attribute, input, and output cardinality limits fail closed",
    "report remains layout_observed_pending_review and cannot mutate the extractor, evidence, coverage, catalogs, templates, or recommendations",
    "future implementation and tests use synthetic HTML only"
  ],
  "express_exclusions": [
    "live source request, real HTML fixture, browser, JavaScript execution, CSS evaluation, or page-body persistence",
    "balance-fact extraction, natural-language inference, subject mapping, evidence approval, catalog mutation, addon, UI, or SimulationCraft",
    "automatic scheduling, retry, database, signing, distribution, commit, or push",
    "changes outside the seven authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `blizzard_patch_notes_layout_probe_0_1_published_with_ci_passed`.

Publication and attended-observation evidence:

- implementation commit: `3737e3e820dda876fe6fb41b8490331f42f61046`;
- local verification: 22 focused and 978 functional tests passed;
- GitHub Actions run `30724769699`: policy, tools, and functional lanes passed;
- one attended request produced report
  `blizzard.layout-report.20260802t002930z` with status
  `layout_observed_pending_review`;
- content: 274005 bytes, SHA-256
  `fbf289f3068d3bb14f04709f0f735db9ee09183cc90968d5e34384fad657f1e6`;
- report SHA-256:
  `85a2ae9b0d241414a557be25af05453feadc36ee74cac1236e5a6a34b390a0ac`;
- 410 nodes, 26 tag names, maximum depth 25, 12 `article` elements,
  and 12 `div` elements with `data-props` were observed;
- the response body and report were not persisted; no retry, fact extraction,
  catalog mutation, recommendation, SimulationCraft, or comparison occurred.

## Published implementation — Blizzard patch-note semantic anchor probe 0.1

The layout report identifies a repeated structural anchor but does not reveal
its meaning. The next boundary may describe only the JSON key/type shape of
allowlisted `data-props` attributes and must erase all values.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "blizzard_patch_notes_semantic_anchor_probe_0_1",
  "title": "Implement a value-erasing semantic shape probe for official patch-note anchors",
  "baseline_commit": "e746853496e4410a68e4d42b1110264ab2b3284d",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "blizzard_patch_notes_semantic_anchor_probe_0_1-20260801-daniel-proceed-implementation",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T19:35:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/blizzard_patch_notes_semantic_anchor_probe.py",
      "desktop-app/tests/test_blizzard_patch_notes_semantic_anchor_probe.py",
      "knowledge/schemas/blizzard_patch_notes_semantic_shape_0_1.json",
      "knowledge/fixtures/blizzard_patch_notes_semantic_anchor_synthetic_0_1.html",
      "knowledge/snapshots/blizzard_patch_notes_semantic_shape_synthetic_0_1.json",
      "docs/BLIZZARD_PATCH_NOTES_SEMANTIC_ANCHOR_PROBE.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/blizzard_patch_notes_semantic_anchor_probe_0_1/implementation.json",
      ".dpslab/quality-gates/blizzard_patch_notes_semantic_anchor_probe_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "profiles/**",
      "scenarios/**", "variants/**", "comparisons/**", "results/**",
      "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "tests.test_blizzard_patch_notes_semantic_anchor_probe", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "full": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "baseline_test_count": 978,
    "minimum_test_count": 996
  },
  "protected_files": {
    "desktop-app/src/dpslab/blizzard_patch_notes_layout_probe.py": "45f1981b35c3b5105cf5a8608a2e2a97d504b820214acd7b602163533005dadf",
    "desktop-app/src/dpslab/blizzard_patch_notes_extractor.py": "1fa7c384fa2224a583340d4e896f73925b6843687837f588f7693256e10ff511",
    "desktop-app/src/dpslab/official_source_http.py": "423a28a8db7fdbffbe9d46a28ca652ba756d318752b6902f4286edf280c7b1a9",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "design inspects only data-props on div elements that are direct children of article",
    "report retains JSON key paths, JSON types, counts, and bounded cardinalities but no JSON values",
    "duplicate keys, invalid JSON, conflicting path types, empty matches, and every resource-limit breach fail closed",
    "input remains bound to a validated captured_pending_review receipt",
    "output remains semantic_shape_observed_pending_review and cannot approve mappings or mutate evidence, coverage, catalogs, templates, or recommendations",
    "future implementation and tests contain synthetic HTML and invented JSON keys only"
  ],
  "express_exclusions": [
    "live request, real page fixture, copied source wording, JSON values, HTML persistence, browser, JavaScript execution, or CSS evaluation",
    "fact extraction, semantic inference, selector approval, catalog mutation, addon, UI, SimulationCraft, signing, or distribution",
    "automatic scheduling, retry, database, commit, or push",
    "changes outside the seven authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `blizzard_patch_notes_semantic_anchor_probe_0_1_published_with_ci_passed`.

Publication and attended-observation evidence:

- implementation commit: `f933f00ab29286c4ff6b4c9570fed0433b661b0e`;
- local verification: 24 focused and 1002 functional tests passed;
- GitHub Actions run `30725617503`: policy, tools, and functional lanes passed;
- one attended request used unchanged content SHA-256
  `fbf289f3068d3bb14f04709f0f735db9ee09183cc90968d5e34384fad657f1e6`;
- the observation rejected fail-closed as `semantic_anchor_unavailable`, proving
  that direct-child ancestry was not established;
- no response, JSON value, report, or new receipt was persisted; no retry,
  facts, selector approval, catalog mutation, SimulationCraft, or comparison.

## Published implementation — Blizzard patch-note anchor path probe 0.1

The corrective boundary observes only the tag-name ancestry of elements that
carry an attribute named `data-props`. It never reads the attribute value.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "blizzard_patch_notes_anchor_path_probe_0_1",
  "title": "Implement a value-blind ancestry probe for patch-note data-props anchors",
  "baseline_commit": "2d3e98ab71c55a58ac659fb7a36a7a3d8d8abe0c",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "blizzard_patch_notes_anchor_path_probe_0_1-20260801-daniel-continue-implementation",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T19:52:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/blizzard_patch_notes_anchor_path_probe.py",
      "desktop-app/tests/test_blizzard_patch_notes_anchor_path_probe.py",
      "knowledge/schemas/blizzard_patch_notes_anchor_path_report_0_1.json",
      "knowledge/fixtures/blizzard_patch_notes_anchor_path_synthetic_0_1.html",
      "knowledge/snapshots/blizzard_patch_notes_anchor_path_synthetic_0_1.json",
      "docs/BLIZZARD_PATCH_NOTES_ANCHOR_PATH_PROBE.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/blizzard_patch_notes_anchor_path_probe_0_1/implementation.json",
      ".dpslab/quality-gates/blizzard_patch_notes_anchor_path_probe_0_1/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "profiles/**",
      "scenarios/**", "variants/**", "comparisons/**", "results/**",
      "config/**", "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "tests.test_blizzard_patch_notes_anchor_path_probe", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "full": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "baseline_test_count": 1002,
    "minimum_test_count": 1020
  },
  "protected_files": {
    "desktop-app/src/dpslab/blizzard_patch_notes_layout_probe.py": "45f1981b35c3b5105cf5a8608a2e2a97d504b820214acd7b602163533005dadf",
    "desktop-app/src/dpslab/blizzard_patch_notes_semantic_anchor_probe.py": "5ab86448c658d701c956a0f58bfdba0345899a91e67198151379acc4e88e987c",
    "desktop-app/src/dpslab/official_source_http.py": "423a28a8db7fdbffbe9d46a28ca652ba756d318752b6902f4286edf280c7b1a9",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "design detects attribute name data-props without reading or retaining its value",
    "report contains only normalized ancestry tag paths, counts, depths, and unanchored carrier count",
    "nearest article ancestry is explicit and no direct-child relation is inferred",
    "receipt binding, malformed nesting, empty matches, and all resource limits fail closed",
    "output remains anchor_path_observed_pending_review and cannot modify semantic probing policy or downstream evidence",
    "future implementation and tests use invented HTML only"
  ],
  "express_exclusions": [
    "live request, real fixture, attribute values, JSON, text, classes, identifiers, URLs, HTML persistence, browser, JavaScript, or CSS",
    "semantic inference, selector approval, fact extraction, catalog mutation, addon, UI, SimulationCraft, signing, or distribution",
    "automatic scheduling, retry, database, commit, or push",
    "changes outside the seven authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `blizzard_patch_notes_anchor_path_probe_0_1_published_with_ci_passed`.

Publication and attended-observation evidence:

- implementation commit: `a102a7c9ca4cf3195167baefe305c800b9563d2e`;
- local verification: 21 focused and 1023 functional tests passed;
- GitHub Actions run `30726308267`: policy, tools, and functional lanes passed;
- one attended request on content SHA-256
  `fbf289f3068d3bb14f04709f0f735db9ee09183cc90968d5e34384fad657f1e6`
  found 12 carriers, all anchored and none unanchored;
- the sole signature, observed 12 times, was `article` followed by eight
  `div` elements, depth 9;
- report SHA-256:
  `46bb57d9e80d919f19f32903b52a96020baab596b270b0a2adc1682718e95726`;
- no values, HTML, text, report, or receipt were persisted; no retry, fact
  extraction, catalog mutation, SimulationCraft, or comparison occurred.

## Published implementation — Semantic anchor exact-path policy 0.2

This corrective revision replaces the disproved direct-child requirement with
the one exact ancestry signature observed across all twelve carriers. It does
not change JSON shape semantics or approve any key mapping.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "semantic_anchor_exact_path_policy_0_2",
  "title": "Require the observed exact article-to-data-props ancestry in semantic shape probing",
  "baseline_commit": "a102a7c9ca4cf3195167baefe305c800b9563d2e",
  "authorization": {
    "status": "authorized_for_implementation",
    "authorization_id": "semantic_anchor_exact_path_policy_0_2-20260801-daniel-continue",
    "authorized_by": "Daniel",
    "authorized_at": "2026-08-01T20:12:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/blizzard_patch_notes_semantic_anchor_probe.py",
      "desktop-app/tests/test_blizzard_patch_notes_semantic_anchor_probe.py",
      "knowledge/fixtures/blizzard_patch_notes_semantic_anchor_synthetic_0_1.html",
      "knowledge/snapshots/blizzard_patch_notes_semantic_shape_synthetic_0_1.json",
      "docs/BLIZZARD_PATCH_NOTES_SEMANTIC_ANCHOR_PROBE.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/semantic_anchor_exact_path_policy_0_2/implementation.json",
      ".dpslab/quality-gates/semantic_anchor_exact_path_policy_0_2/audit.json"
    ],
    "forbidden_paths": [
      ".github/**", "knowledge/catalogs/**", "profiles/**", "scenarios/**",
      "variants/**", "comparisons/**", "results/**", "config/**",
      "flasil.simc", "tools/**"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "tests.test_blizzard_patch_notes_semantic_anchor_probe", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "full": {"working_directory": "desktop-app", "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"], "environment": {"PYTHONPATH": "src", "PYTHONDONTWRITEBYTECODE": "1"}},
    "baseline_test_count": 1023,
    "minimum_test_count": 1025
  },
  "protected_files": {
    "desktop-app/src/dpslab/blizzard_patch_notes_anchor_path_probe.py": "1cab61ca1a5ef474fb772a59937950a3b6a8cbcde9f5ff865619ccda387fa6ad",
    "desktop-app/src/dpslab/blizzard_patch_notes_layout_probe.py": "45f1981b35c3b5105cf5a8608a2e2a97d504b820214acd7b602163533005dadf",
    "desktop-app/src/dpslab/official_source_http.py": "423a28a8db7fdbffbe9d46a28ca652ba756d318752b6902f4286edf280c7b1a9",
    ".github/workflows/dpslab-ci.yml": "3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit": {"required": true, "independence": "declared_and_procedural"},
  "acceptance_criteria": [
    "only article followed by exactly eight div elements may carry data-props into JSON shape analysis",
    "direct, shorter, longer, non-div, outside-article, or mixed carrier paths fail closed",
    "attribute values remain unavailable until the exact path is validated",
    "existing duplicate-key, value erasure, receipt binding, JSON limits, and pending-review controls remain intact",
    "fixture and tests are synthetic and contain no real keys or source text",
    "no live request, fact extraction, selector approval, catalog mutation, SimulationCraft, commit, or push"
  ],
  "express_exclusions": [
    "changes to layout or anchor-path probes, HTTP, source registry, evidence, catalogs, addon, UI, signing, or distribution",
    "semantic approval of data-props or any JSON key",
    "changes outside the six authorized paths"
  ]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `semantic_anchor_exact_path_policy_0_2_published_with_ci_passed`.

Evidence:

- commit `ad9279b14b6ada493f34ceb168ec6cfdd0045b19`;
- 26 focused and 1025 functional tests passed;
- GitHub Actions run `30726824643` passed all lanes;
- one attended observation found only `iso8601` string and `relative` boolean,
  each 12 times, report SHA-256
  `b01b99ae0578af1faaa96b3614cc55fc9303af30f3f5048535a576e061a234dc`;
- these keys remain unapproved and no value, body, report, or receipt persisted.

## Published implementation — Blizzard patch-note text topology probe 0.1

This boundary identifies only which tag paths beneath `article` contain
visible text and their aggregate lengths. It retains no characters.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "blizzard_patch_notes_text_topology_probe_0_1",
  "title": "Implement a character-erasing text topology probe for patch-note articles",
  "baseline_commit": "ad9279b14b6ada493f34ceb168ec6cfdd0045b19",
  "authorization": {"status":"authorized_for_implementation","authorization_id":"blizzard_patch_notes_text_topology_probe_0_1-20260801-daniel-corrective","authorized_by":"Daniel","authorized_at":"2026-08-01T20:30:00-05:00"},
  "scope": {
    "allowed_paths": [
      "desktop-app/src/dpslab/blizzard_patch_notes_text_topology_probe.py",
      "desktop-app/tests/test_blizzard_patch_notes_text_topology_probe.py",
      "knowledge/fixtures/blizzard_patch_notes_text_topology_synthetic_0_1.html",
      "knowledge/snapshots/blizzard_patch_notes_text_topology_synthetic_0_1.json",
      "docs/BLIZZARD_PATCH_NOTES_TEXT_TOPOLOGY_PROBE.md",
      "docs/NEXT_TASK.md"
    ],
    "generated_paths":[".dpslab/quality-gates/blizzard_patch_notes_text_topology_probe_0_1/implementation.json",".dpslab/quality-gates/blizzard_patch_notes_text_topology_probe_0_1/audit.json"],
    "forbidden_paths":[".github/**","knowledge/catalogs/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc","tools/**"],
    "allow_deletions":false,"allow_renames":false
  },
  "tests": {
    "focused":{"working_directory":"desktop-app","argv":["python","-m","unittest","tests.test_blizzard_patch_notes_text_topology_probe","-v"],"environment":{"PYTHONPATH":"src","PYTHONDONTWRITEBYTECODE":"1"}},
    "full":{"working_directory":"desktop-app","argv":["python","-m","unittest","discover","-s","tests","-v"],"environment":{"PYTHONPATH":"src","PYTHONDONTWRITEBYTECODE":"1"}},
    "baseline_test_count":1025,"minimum_test_count":1043
  },
  "protected_files": {
    "desktop-app/src/dpslab/blizzard_patch_notes_semantic_anchor_probe.py":"a7b68893a251c24b3ec02004e5eddf4f202b0187bf7da2adf941a7a7c6c41515",
    "desktop-app/src/dpslab/blizzard_patch_notes_anchor_path_probe.py":"1cab61ca1a5ef474fb772a59937950a3b6a8cbcde9f5ff865619ccda387fa6ad",
    "desktop-app/src/dpslab/official_source_http.py":"423a28a8db7fdbffbe9d46a28ca652ba756d318752b6902f4286edf280c7b1a9",
    ".github/workflows/dpslab-ci.yml":"3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"
  },
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":[
    "report retains only article-relative tag paths and aggregate text-node lengths",
    "text characters, hashes, attributes, URLs, HTML, scripts, styles, and semantic labels are absent",
    "script, style, noscript, and template text is excluded and only exclusion count remains",
    "receipt binding, nesting, empty visible topology, and resource limits fail closed",
    "output remains text_topology_observed_pending_review",
    "fixtures are synthetic and no live request occurs"
  ],
  "express_exclusions":["fact extraction","selector approval","catalog mutation","SimulationCraft","addon","UI","signing","distribution","commit","push","changes outside six paths"]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `blizzard_patch_notes_text_topology_probe_0_1_published_with_ci_passed`.

Evidence:

- commit `dcc41d070e312e676df342f1f3c0be1fa715f831`;
- 19 focused and 1044 functional tests passed;
- GitHub Actions run `30727184989` passed all lanes;
- attended report `blizzard.text-topology-report.20260802t013748z`, SHA-256
  `dc400b08b806fec21515559010c4bf5fd1e7db8dc5f7513fb6143d5475725bc4`;
- 36 visible nodes across 12 articles and three exact paths; 10 excluded nodes;
- no characters, words, attributes, HTML, report, or receipt were persisted.

## Published implementation — Patch-note structural slots 0.1

Three exact paths may receive neutral slot identifiers. No semantic label is
authorized.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version":"0.1",
  "task_id":"patch_note_structural_slots_0_1",
  "title":"Implement neutral structural slots and stabilize strict Windows temporary cleanup",
  "baseline_commit":"a8281faccb1927702d90b2bb5c9e25fc7b320c42",
  "authorization":{"status":"authorized_for_implementation","authorization_id":"patch_note_structural_slots_0_1-20260801-daniel-continue-implementation","authorized_by":"Daniel","authorized_at":"2026-08-01T20:45:00-05:00"},
  "scope":{"allowed_paths":["desktop-app/src/dpslab/patch_note_structural_slots.py","desktop-app/tests/strict_temporary_cleanup.py","desktop-app/tests/test_patch_note_structural_slots.py","desktop-app/tests/test_result_parser.py","desktop-app/tests/test_runner.py","knowledge/schemas/patch_note_structural_slots_0_1.json","knowledge/snapshots/patch_note_structural_slots_synthetic_0_1.json","docs/PATCH_NOTE_STRUCTURAL_SLOTS.md","docs/NEXT_TASK.md"],"generated_paths":[".dpslab/quality-gates/patch_note_structural_slots_0_1/implementation.json",".dpslab/quality-gates/patch_note_structural_slots_0_1/audit.json"],"forbidden_paths":[".github/**","knowledge/catalogs/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc","tools/**"],"allow_deletions":false,"allow_renames":false},
  "tests":{"focused":{"working_directory":"desktop-app","argv":["python","-m","unittest","tests.test_patch_note_structural_slots","-v"],"environment":{"PYTHONPATH":"src","PYTHONDONTWRITEBYTECODE":"1"}},"full":{"working_directory":"desktop-app","argv":["python","-m","unittest","discover","-s","tests","-v"],"environment":{"PYTHONPATH":"src","PYTHONDONTWRITEBYTECODE":"1"}},"baseline_test_count":1044,"minimum_test_count":1062},
  "protected_files":{"desktop-app/src/dpslab/blizzard_patch_notes_text_topology_probe.py":"304aef3925da27f57155d46aeeb64bbccf83ab5545253cbf255e81e616d67435","desktop-app/src/dpslab/blizzard_patch_notes_semantic_anchor_probe.py":"a7b68893a251c24b3ec02004e5eddf4f202b0187bf7da2adf941a7a7c6c41515",".github/workflows/dpslab-ci.yml":"3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"},
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":["exactly three neutral slot identifiers bind the three observed tag paths","slot names encode no semantic meaning","input and output remain pending review and contain no text","missing additional duplicate or inconsistent paths fail closed","future tests use synthetic reports only","Windows temporary cleanup retries only directory-not-empty error 145 and preserves fail-closed behavior for every other error"],
  "express_exclusions":["live request","text capture","semantic labels","selector approval","fact extraction","catalog mutation","SimulationCraft","addon","UI","signing","distribution","changes outside the nine allowlisted paths"]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `patch_note_structural_slots_0_1_published_with_ci_passed`.

Evidence:

- commit `88a65162f81ccf62585ef24eb0a1e0ee33a8ef8c` is local `HEAD`,
  `origin/main`, and live `refs/heads/main`;
- 19 focused and 1065 functional tests passed, with one expected skip;
- GitHub Actions run `30731508777` passed Policy and contract, Tools tests,
  and Functional suite;
- audit recorded no findings; protected hashes remained unchanged;
- the Windows cleanup correction retries only directory-not-empty error 145
  in the two affected test fixtures and suppresses no other error;
- no live request, retained text, semantic assignment, catalog mutation, or
  SimulationCraft execution occurred.

## Published implementation — Patch-note semantic slot review 0.1

This task designs human semantic review of neutral slots. It does not assign a
meaning to any observed path and cannot extract facts.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version":"0.1",
  "task_id":"patch_note_semantic_slot_review_0_1",
  "title":"Implement fail-closed human semantic review for neutral patch-note slots",
  "baseline_commit":"e25d5b7287ee63dfe197992cec7fe38eee28a738",
  "authorization":{"status":"authorized_for_implementation","authorization_id":"patch_note_semantic_slot_review_0_1-20260801-daniel-continue-implementation","authorized_by":"Daniel","authorized_at":"2026-08-01T23:08:00-05:00"},
  "scope":{"allowed_paths":["desktop-app/src/dpslab/patch_note_semantic_slot_review.py","desktop-app/tests/test_patch_note_semantic_slot_review.py","knowledge/schemas/patch_note_semantic_slot_review_0_1.json","knowledge/snapshots/patch_note_semantic_slot_review_synthetic_0_1.json","docs/PATCH_NOTE_SEMANTIC_SLOT_REVIEW.md","docs/NEXT_TASK.md"],"generated_paths":[".dpslab/quality-gates/patch_note_semantic_slot_review_0_1/implementation.json",".dpslab/quality-gates/patch_note_semantic_slot_review_0_1/audit.json"],"forbidden_paths":[".github/**","knowledge/catalogs/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc","tools/**"],"allow_deletions":false,"allow_renames":false},
  "tests":{"focused":{"working_directory":"desktop-app","argv":["python","-m","unittest","tests.test_patch_note_semantic_slot_review","-v"],"environment":{"PYTHONPATH":"src","PYTHONDONTWRITEBYTECODE":"1"}},"full":{"working_directory":"desktop-app","argv":["python","-m","unittest","discover","-s","tests","-v"],"environment":{"PYTHONPATH":"src","PYTHONDONTWRITEBYTECODE":"1"}},"baseline_test_count":1065,"minimum_test_count":1082},
  "protected_files":{"desktop-app/src/dpslab/patch_note_structural_slots.py":"cd60d08e269c9aa4fdaee5fd974440708fe944827575d3b5c2f101e38c1d24bd","desktop-app/src/dpslab/blizzard_patch_notes_text_topology_probe.py":"304aef3925da27f57155d46aeeb64bbccf83ab5545253cbf255e81e616d67435",".github/workflows/dpslab-ci.yml":"3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"},
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":["no role is inferred from path metrics order or conversation","closed structural-role vocabulary includes unknown and rejected","human attestation binds reviewer time receipt and slot-report hashes","conflicts incomplete coverage altered bindings and stale observations fail closed","semantic review cannot approve selectors facts catalogs or recommendations"],
  "express_exclusions":["live request","text or HTML retention","semantic assignment to observed slots","selector approval","fact extraction","catalog mutation","SimulationCraft","addon","UI","signing","distribution","changes outside six allowlisted paths"]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `patch_note_semantic_slot_review_0_1_published_with_ci_passed`.

Evidence:

- commit `b7a119a9cb6725996360d1a1366b0655140c945c` is synchronized across
  local `HEAD`, `origin/main`, and live `refs/heads/main`;
- 19 focused and 1084 functional tests passed, with one expected skip;
- audit recorded no findings and protected hashes remained unchanged;
- GitHub Actions run `30732037545` passed all three lanes;
- only synthetic slot decisions were used; no real semantic assignment, live
  request, retained content, fact extraction, or catalog mutation occurred.

## Published implementation — Patch-note semantic review ceremony 0.1

This task designs a visible, attended, single-use human review ceremony. It
does not authorize displaying real content.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version":"0.1",
  "task_id":"patch_note_semantic_review_ceremony_0_1",
  "title":"Implement synthetic attended transient semantic review ceremony core",
  "baseline_commit":"b6215d6c9fcdd93954aa404d2e35f2d188ff01c7",
  "authorization":{"status":"authorized_for_implementation","authorization_id":"patch_note_semantic_review_ceremony_0_1-20260805-daniel-continue-implementation","authorized_by":"Daniel","authorized_at":"2026-08-05T00:00:00-05:00"},
  "scope":{"allowed_paths":["desktop-app/src/dpslab/patch_note_semantic_review_ceremony.py","desktop-app/tests/test_patch_note_semantic_review_ceremony.py","docs/PATCH_NOTE_SEMANTIC_REVIEW_CEREMONY.md","docs/NEXT_TASK.md"],"generated_paths":[".dpslab/quality-gates/patch_note_semantic_review_ceremony_0_1/implementation.json",".dpslab/quality-gates/patch_note_semantic_review_ceremony_0_1/audit.json"],"forbidden_paths":[".github/**","knowledge/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc","tools/**"],"allow_deletions":false,"allow_renames":false},
  "tests":{"focused":{"working_directory":"desktop-app","argv":["python","-m","unittest","tests.test_patch_note_semantic_review_ceremony","-v"],"environment":{"PYTHONPATH":"src","PYTHONDONTWRITEBYTECODE":"1"}},"full":{"working_directory":"desktop-app","argv":["python","-m","unittest","discover","-s","tests","-v"],"environment":{"PYTHONPATH":"src","PYTHONDONTWRITEBYTECODE":"1"}},"baseline_test_count":1084,"minimum_test_count":1099},
  "protected_files":{"desktop-app/src/dpslab/patch_note_semantic_slot_review.py":"c129466a5b8b3a936b05dd8131867c720e865f8a8516e1058477398fd47f0aa1","desktop-app/src/dpslab/patch_note_structural_slots.py":"cd60d08e269c9aa4fdaee5fd974440708fe944827575d3b5c2f101e38c1d24bd",".github/workflows/dpslab-ci.yml":"3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"},
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":["pre-display binding verifies receipt content and slot-report hashes","one slot is displayed at a time and content is memory-only","no role suggestion uses order length markup or prior decision","unknown rejected close timeout and source drift fail closed","durable output contains decisions identifiers hashes reviewer timestamp status and no content","real display requires immediate later human confirmation"],
  "express_exclusions":["real display","live request","content persistence","screenshots","clipboard","logging source content","fact extraction","selector approval","catalog mutation","SimulationCraft","addon","distribution","changes outside four allowlisted paths"]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `patch_note_semantic_review_ceremony_0_1_published_with_ci_passed`.

Evidence:

- commit `8a0201e50cb10f6bf7871bba8f1bee2dfcdff7e4` is synchronized across
  local `HEAD`, `origin/main`, and the previously verified live remote;
- 16 focused and 1100 functional tests passed, with one expected skip;
- audit recorded no findings; GitHub Actions run `31008582887` passed all
  three lanes;
- the implementation used callbacks and synthetic mutable buffers only;
- no visible window, real content, live request, or real review occurred.

## Published implementation — Synthetic semantic review window 0.1

This task adds a local visible adapter for synthetic usability review. It does
not connect the window to an official source or authorize a real ceremony.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version":"0.1",
  "task_id":"patch_note_semantic_review_window_0_1",
  "title":"Implement a synthetic local window for attended semantic review",
  "baseline_commit":"8a0201e50cb10f6bf7871bba8f1bee2dfcdff7e4",
  "authorization":{"status":"authorized_for_implementation","authorization_id":"patch_note_semantic_review_window_0_1-20260826-daniel-continue","authorized_by":"Daniel","authorized_at":"2026-08-26T00:00:00-05:00"},
  "scope":{"allowed_paths":["desktop-app/src/dpslab/patch_note_semantic_review_window.py","desktop-app/tests/test_patch_note_semantic_review_window.py","docs/PATCH_NOTE_SEMANTIC_REVIEW_CEREMONY.md","docs/NEXT_TASK.md"],"generated_paths":[".dpslab/quality-gates/patch_note_semantic_review_window_0_1/implementation.json",".dpslab/quality-gates/patch_note_semantic_review_window_0_1/audit.json"],"forbidden_paths":[".github/**","knowledge/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc","tools/**"],"allow_deletions":false,"allow_renames":false},
  "tests":{"focused":{"working_directory":"desktop-app","argv":["python","-m","unittest","tests.test_patch_note_semantic_review_window","-v"],"environment":{"PYTHONPATH":"src","PYTHONDONTWRITEBYTECODE":"1"}},"full":{"working_directory":"desktop-app","argv":["python","-m","unittest","discover","-s","tests","-v"],"environment":{"PYTHONPATH":"src","PYTHONDONTWRITEBYTECODE":"1"}},"baseline_test_count":1100,"minimum_test_count":1115},
  "protected_files":{"desktop-app/src/dpslab/patch_note_semantic_review_ceremony.py":"0eb1285c65036481ddf23eb33a6ce6232e118f35ac909deb199fb23b72427a59","desktop-app/src/dpslab/patch_note_semantic_slot_review.py":"c129466a5b8b3a936b05dd8131867c720e865f8a8516e1058477398fd47f0aa1",".github/workflows/dpslab-ci.yml":"3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"},
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":["window identifies synthetic mode prominently","one slot and one content buffer are visible at a time","role and reason choices are closed and initially unselected","continue is disabled until both choices are explicit","close and cancel return no decision","display text is not copied logged or persisted","headless tests use fake view ports and no real source","native visual verification remains a separate human gate"],
  "express_exclusions":["official-source connection","real content","real ceremony","network","content persistence","clipboard","screenshots as project artifacts","fact extraction","catalog mutation","SimulationCraft","addon","distribution","changes outside four allowlisted paths"]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `patch_note_semantic_review_window_0_1_published_with_ci_and_human_visual_approval`.

Evidence:

- commit `7fdb6c35605819eba40a65c2118a835cdf22c699` is synchronized across
  local `HEAD`, `origin/main`, and live `refs/heads/main`;
- 16 focused and 1116 functional tests passed, with one expected skip;
- audit recorded no findings and protected hashes remained unchanged;
- GitHub Actions run `33030375509` completed with `Success`; Policy and
  contract, Tools tests, and Functional suite all passed;
- Daniel confirmed on 2026-08-26 that the visible synthetic window is legible
  and appropriate for the design phase;
- no official-source connection, real content, real review, catalog mutation,
  or SimulationCraft execution occurred.

## Deferred design task — Attended semantic review execution 0.1

This task designs the final readiness and authorization boundary before one
real human-attended semantic review. It does not authorize that execution.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version":"0.1",
  "task_id":"attended_semantic_review_execution_0_1",
  "title":"Design the one-shot real semantic review execution boundary",
  "baseline_commit":"7fdb6c35605819eba40a65c2118a835cdf22c699",
  "authorization":{"status":"design_only","authorization_id":"attended_semantic_review_execution_0_1-20260826-daniel-continue","authorized_by":"Daniel","authorized_at":"2026-08-26T20:30:00-05:00"},
  "scope":{"allowed_paths":["docs/PATCH_NOTE_SEMANTIC_REVIEW_CEREMONY.md","docs/NEXT_TASK.md"],"generated_paths":[],"forbidden_paths":[".github/**","desktop-app/**","knowledge/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc","tools/**"],"allow_deletions":false,"allow_renames":false},
  "tests":{"focused":{"working_directory":".","argv":["python","-m","unittest","discover","-s","tools/tests","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"full":{"working_directory":".","argv":["python","-m","unittest","discover","-s","tools/tests","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"baseline_test_count":52,"minimum_test_count":52},
  "protected_files":{"desktop-app/src/dpslab/patch_note_semantic_review_window.py":"3d14452f5bc73cd2c7271abf451c42d9764bf1c7a7b8739ca6fd8b8aaee6fa0f","desktop-app/src/dpslab/patch_note_semantic_review_ceremony.py":"0eb1285c65036481ddf23eb33a6ce6232e118f35ac909deb199fb23b72427a59",".github/workflows/dpslab-ci.yml":"3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5"},
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":["execution is one-shot and requires immediate human confirmation","live receipt content and slot hashes are reverified before each display and before finalization","only the approved window and ceremony core may receive transient content","close cancel timeout source drift and any invalid choice produce no approved record","durable output is content-free and written only after complete validated review","real execution authority is consumed regardless of success cancellation or failure","semantic approval does not authorize fact extraction selector approval catalog mutation or recommendations"],
  "express_exclusions":["implementation","real execution","live request","content persistence","fact extraction","selector approval","catalog mutation","SimulationCraft","addon","distribution","changes outside two documentary paths"]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design verdict: `attended_semantic_review_execution_0_1_design_ready_deferred_by_security_foundation`.

The design remains valid evidence but is not an active implementation or real
execution authority. Security foundation work is a prerequisite before this
boundary can be reconsidered.

## Published implementation — Security foundation 0.1

This block makes security a cross-cutting, machine-checkable prerequisite for
future design and implementation. It does not claim production certification
or enable any network, addon, update, signing, or SimulationCraft operation.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version":"0.1",
  "task_id":"security_foundation_0_1",
  "title":"Establish the cross-cutting security philosophy, trust boundaries, beta gates, and machine-checkable baseline",
  "baseline_commit":"f3aac70b5968dd7ff5fb61555d4023af597376dd",
  "authorization":{"status":"authorized_for_implementation","authorization_id":"security_foundation_0_1-20260826-daniel-adjust-and-continue","authorized_by":"Daniel","authorized_at":"2026-08-26T00:00:00-05:00"},
  "scope":{"allowed_paths":["AGENTS.md","SECURITY.md","docs/NEXT_TASK.md","docs/PROJECT_BRIEF.md","docs/ROADMAP.md","docs/SECURITY_ARCHITECTURE.md","security/security_baseline_0_1.json","tools/tests/test_security_baseline.py"],"generated_paths":[".dpslab/quality-gates/security_foundation_0_1/implementation.json",".dpslab/quality-gates/security_foundation_0_1/audit.json"],"forbidden_paths":[".github/**","desktop-app/**","knowledge/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc"],"allow_deletions":false,"allow_renames":false},
  "tests":{"focused":{"working_directory":".","argv":["python","-m","unittest","tools.tests.test_security_baseline","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"full":{"working_directory":".","argv":["python","-m","unittest","discover","-s","tools/tests","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"baseline_test_count":52,"minimum_test_count":57},
  "protected_files":{"profiles/flasil.simc":"f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738","flasil.simc":"f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738","scenarios/st_lightmovement_300s_v1.toml":"93187338a61d1cfc330f5262abb0b9183acb727d310099eca7917138207c09aa",".github/workflows/dpslab-ci.yml":"3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5","desktop-app/src/dpslab/windows_key_protection.py":"27d1bfdce76df7c06666e98aaaa2456cd23e17b06eaccee98f7bb440080ef67b","desktop-app/src/dpslab/official_source_http.py":"423a28a8db7fdbffbe9d46a28ca652ba756d318752b6902f4286edf280c7b1a9","desktop-app/src/dpslab/runner.py":"92dc7712a5fa2001e816f4dc7025e1af6c81b67b2c98b9fd5f52c3301abacc93"},
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":["security is a required input to every future design implementation publication and operation contract","data never becomes executable code and unknown or unsafe input fails closed","desktop addon network CI knowledge update and release-key trust boundaries are explicit","production secrets remain forbidden from repository CI addon logs artifacts and distributed configuration","external beta gates include reproducible dependencies SBOM dependency and secret scanning static analysis adversarial tests signed updates privacy incident response and independent review","the baseline is closed versioned sorted and verified by focused tests","existing CI least-privilege controls and protected runtime files remain unchanged","the deferred semantic-review design is preserved without real execution authority"],
  "express_exclusions":["network calls or live-source observation","addon Lua UI updater packaging distribution or release activation","key generation signing recovery or secret access","SimulationCraft comparison runs results or baseline mutation","dependency installation GitHub settings workflow changes commit push or later blocks","changes outside the eight allowlisted paths"]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `security_foundation_0_1_published_with_ci_passed`.

Evidence:

- commit `a33615df01e9479cb3d453fbd3fd0b6eb163b036` is synchronized across
  local `HEAD`, `origin/main`, and live `refs/heads/main`;
- 5 focused and 57 tools tests passed locally;
- the quality gate and procedural audit passed with no findings;
- GitHub Actions run `33032859558` completed successfully in Policy and
  contract, Tools tests, and Functional suite;
- one transient Windows temporary-directory cleanup error 145 passed on its
  controlled focused repeat and the subsequent complete suite;
- no SimulationCraft, network observation, addon, updater, signing, secret,
  release activation, or product distribution occurred.

## Published implementation — Security threat model 0.1

This block identifies concrete threats, affected assets, current mitigations
and unresolved beta gates. It does not claim that an open threat is resolved.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version":"0.1",
  "task_id":"security_threat_model_0_1",
  "title":"Implement the versioned threat model and bind open threats to external-beta gates",
  "baseline_commit":"a33615df01e9479cb3d453fbd3fd0b6eb163b036",
  "authorization":{"status":"authorized_for_implementation","authorization_id":"security_threat_model_0_1-20260826-daniel-adjust-and-continue","authorized_by":"Daniel","authorized_at":"2026-08-26T00:00:00-05:00"},
  "scope":{"allowed_paths":["docs/NEXT_TASK.md","docs/THREAT_MODEL.md","security/security_baseline_0_1.json","security/threat_model_0_1.json","tools/tests/test_security_threat_model.py"],"generated_paths":[".dpslab/quality-gates/security_threat_model_0_1/implementation.json",".dpslab/quality-gates/security_threat_model_0_1/audit.json"],"forbidden_paths":[".github/**","desktop-app/**","knowledge/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc","AGENTS.md","SECURITY.md","docs/PROJECT_BRIEF.md","docs/ROADMAP.md","docs/SECURITY_ARCHITECTURE.md"],"allow_deletions":false,"allow_renames":false},
  "tests":{"focused":{"working_directory":".","argv":["python","-m","unittest","tools.tests.test_security_threat_model","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"full":{"working_directory":".","argv":["python","-m","unittest","discover","-s","tools/tests","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"baseline_test_count":57,"minimum_test_count":62},
  "protected_files":{"AGENTS.md":"1886e30bdec4abf3669dee0c2f0ce0a7271fa3cf30ed3830dfff24aef49edcb0","SECURITY.md":"b00e680630009bfd062a58b5a8d3129b9c68e45fb8aa284f05133f173fe2daf5","docs/SECURITY_ARCHITECTURE.md":"ebe0dd5624e7149807275dfab891fd52e598f27e7c7afedfec2bd4fbc15fdde5",".github/workflows/dpslab-ci.yml":"3c774c6cfbdf6dd1c9f9d6642786f0815925c157b5d6220a1fd10a72f15f93e5","desktop-app/src/dpslab/windows_key_protection.py":"27d1bfdce76df7c06666e98aaaa2456cd23e17b06eaccee98f7bb440080ef67b","desktop-app/src/dpslab/official_source_http.py":"423a28a8db7fdbffbe9d46a28ca652ba756d318752b6902f4286edf280c7b1a9","desktop-app/src/dpslab/runner.py":"92dc7712a5fa2001e816f4dc7025e1af6c81b67b2c98b9fd5f52c3301abacc93"},
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":["assets adversaries assumptions and trust boundaries are explicit","twelve prioritized threats cover code injection updates keys sources resource exhaustion paths supply chain secrets addon exchange privacy guidance integrity and CI","every threat has closed fields assets status and concrete mitigations","open_beta_gate threats cannot be interpreted as resolved or beta-ready","material addon dependency network persistence key and update changes trigger review","the security baseline requires threat-model review before external beta","existing security architecture CI runtime acquisition and key-protection files remain unchanged"],
  "express_exclusions":["implementing any mitigation updater addon or release mechanism","dependency installation workflow or GitHub settings changes","network calls live sources SimulationCraft comparisons or results","secret key recovery signing publication activation or distribution","commit push or later security gates","changes outside five allowlisted paths"]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `security_threat_model_0_1_published_with_ci_passed`.

Evidence:

- commit `37f695a43d543b06ecacfa444118fcebacf9c6c8` is synchronized across
  local `HEAD`, `origin/main`, and live `refs/heads/main`;
- 5 focused and 62 tools tests passed;
- quality gate and procedural audit passed with no findings;
- GitHub Actions run `33033883517` passed all three lanes;
- twelve threats are explicit and unresolved `open_beta_gate` states remain
  blockers rather than inferred approvals;
- no mitigation implementation, network, addon, updater, key operation,
  SimulationCraft, release activation, or distribution occurred.

## Published implementation — Reproducible dependency inventory 0.1

This block fixes the exact Windows CPython 3.13 dependency bytes installed by
CI and publishes a matching SPDX inventory. Vulnerability and license review
remain separate open gates.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version":"0.1",
  "task_id":"reproducible_dependency_inventory_0_1",
  "title":"Pin hashed Windows Python 3.13 dependencies, publish an SPDX SBOM, and remove silent CI resolution",
  "baseline_commit":"37f695a43d543b06ecacfa444118fcebacf9c6c8",
  "authorization":{"status":"authorized_for_implementation","authorization_id":"reproducible_dependency_inventory_0_1-20260826-daniel-continue","authorized_by":"Daniel","authorized_at":"2026-08-26T00:00:00-05:00"},
  "scope":{"allowed_paths":[".gitattributes",".github/workflows/dpslab-ci.yml","desktop-app/pyproject.toml","desktop-app/requirements-ci-win-py313.lock","docs/DEPENDENCY_SECURITY.md","docs/NEXT_TASK.md","security/sbom-runtime-win-py313.spdx.json","tools/tests/test_dependency_supply_chain.py","tools/tests/test_github_automation.py"],"generated_paths":[".dpslab/quality-gates/reproducible_dependency_inventory_0_1/implementation.json",".dpslab/quality-gates/reproducible_dependency_inventory_0_1/audit.json"],"forbidden_paths":["desktop-app/src/**","desktop-app/tests/**","knowledge/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc","AGENTS.md","SECURITY.md","docs/SECURITY_ARCHITECTURE.md","docs/THREAT_MODEL.md","security/security_baseline_0_1.json","security/threat_model_0_1.json"],"allow_deletions":false,"allow_renames":false},
  "tests":{"focused":{"working_directory":".","argv":["python","-m","unittest","tools.tests.test_dependency_supply_chain","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"full":{"working_directory":".","argv":["python","-m","unittest","discover","-s","tools/tests","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"baseline_test_count":62,"minimum_test_count":67},
  "protected_files":{"AGENTS.md":"1886e30bdec4abf3669dee0c2f0ce0a7271fa3cf30ed3830dfff24aef49edcb0","SECURITY.md":"b00e680630009bfd062a58b5a8d3129b9c68e45fb8aa284f05133f173fe2daf5","docs/SECURITY_ARCHITECTURE.md":"ebe0dd5624e7149807275dfab891fd52e598f27e7c7afedfec2bd4fbc15fdde5","docs/THREAT_MODEL.md":"4784525ec7e8af6073fd2b934f855f5ac8ee2a639cb3ff1200c1811883f8400f","security/security_baseline_0_1.json":"a052db44ed119988fe5e40d244cd08e0f346ffcbe2dc1a7098488af88be88b6b","security/threat_model_0_1.json":"59fdb8dc84e6f0722605a63b5bb627b02e2f0db1e3d5c27e41e1e98391686131","desktop-app/src/dpslab/runner.py":"92dc7712a5fa2001e816f4dc7025e1af6c81b67b2c98b9fd5f52c3301abacc93"},
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":["CI dependency resolution is exact wheel-only and SHA-256 required for every direct transitive and build dependency","setuptools build backend is fixed to the locked version","project installation performs no dependency resolution and no isolated build download","SPDX 2.3 SBOM matches every locked package version hash and dependency relationship","unknown licenses remain NOASSERTION rather than inferred","lock scope is explicitly Windows x86-64 CPython 3.13 and does not claim portability","dependency_audit license review pip provenance and other platform locks remain open gates","existing runtime source threat model and security baseline remain unchanged"],
  "express_exclusions":["vulnerability or license approval claims","installing dependencies on the user workstation","runtime product code tests addon updater or packaging changes","secret scanning static analysis GitHub settings or new external Actions","network activity beyond the completed temporary PyPI wheel resolution","SimulationCraft comparisons results keys signing release activation or distribution","commit push or later security gates","changes outside nine allowlisted paths"]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Publication verdict: `reproducible_dependency_inventory_0_1_published_with_ci_passed`.

Evidence:

- commit `99982db1db1f654dc9b5c605ba91adc85f323ff7` is synchronized across
  local `HEAD`, `origin/main`, and live `refs/heads/main`;
- 5 focused, 16 combined policy/focused, and 67 tools tests passed locally;
- quality gate and procedural audit passed with no findings;
- GitHub Actions run `33035332057` passed Policy and contract, Tools tests,
  and Functional suite using the hash-locked installation;
- CI accepted all six exact wheel hashes and performed project installation
  with no dependency resolution or isolated build download;
- vulnerability and license approval, other platforms, pip provenance, secret
  scanning, static analysis and external-beta readiness remain open;
- no dependency was installed on the user workstation and no downloaded wheel
  was added to the repository.

Next security gate: `dependency_vulnerability_audit_0_1` requires a separate
closed contract for advisory source, scanner provenance, severity policy,
network failure behavior, exception expiry and CI evidence.

## Implemented pending publication — Dependency vulnerability audit 0.1

This task designs how DpsLab will detect known vulnerabilities without making
CI depend on an unpinned scanner or silently accepting an unavailable advisory
service. It authorizes no implementation.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version":"0.1",
  "task_id":"dependency_vulnerability_audit_0_1",
  "title":"Implement a fail-closed known-vulnerability audit for the locked Python dependency set",
  "baseline_commit":"d19f18ea84fb3ec7da5627e5fc8b89a33042c8d3",
  "authorization":{"status":"authorized_for_implementation","authorization_id":"dependency_vulnerability_audit_0_1-20260827-daniel-explicit","authorized_by":"Daniel","authorized_at":"2026-08-27T21:00:00-05:00"},
  "scope":{"allowed_paths":[".github/workflows/dpslab-ci.yml","desktop-app/requirements-security-tools-win-py313.lock","docs/DEPENDENCY_SECURITY.md","docs/NEXT_TASK.md","security/dependency_vulnerability_policy_0_1.json","security/dependency_vulnerability_exceptions_0_1.json","tools/dependency_vulnerability_audit.py","tools/tests/test_dependency_vulnerability_audit.py"],"generated_paths":[".dpslab/quality-gates/dependency_vulnerability_audit_0_1/implementation.json",".dpslab/quality-gates/dependency_vulnerability_audit_0_1/audit.json"],"forbidden_paths":["desktop-app/src/**","desktop-app/tests/**","desktop-app/pyproject.toml","desktop-app/requirements-ci-win-py313.lock","security/security_baseline_0_1.json","security/threat_model_0_1.json","security/sbom-runtime-win-py313.spdx.json","knowledge/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc","AGENTS.md","SECURITY.md","docs/SECURITY_ARCHITECTURE.md","docs/THREAT_MODEL.md"],"allow_deletions":false,"allow_renames":false},
  "tests":{"focused":{"working_directory":".","argv":["python","-m","unittest","tools.tests.test_dependency_vulnerability_audit","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"full":{"working_directory":".","argv":["python","-m","unittest","discover","-s","tools/tests","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"baseline_test_count":67,"minimum_test_count":77},
  "protected_files":{"AGENTS.md":"1886e30bdec4abf3669dee0c2f0ce0a7271fa3cf30ed3830dfff24aef49edcb0","SECURITY.md":"b00e680630009bfd062a58b5a8d3129b9c68e45fb8aa284f05133f173fe2daf5","desktop-app/pyproject.toml":"369c43c979dfffd409fbcc313e8fa60b7a4a09b4f86dd0b5bf2a8cba1cb2c897","desktop-app/requirements-ci-win-py313.lock":"dc6ec391a3cfae053e9a808115f5df4e65ea2a132664fb0af11e9897d1f2c612","docs/SECURITY_ARCHITECTURE.md":"ebe0dd5624e7149807275dfab891fd52e598f27e7c7afedfec2bd4fbc15fdde5","docs/THREAT_MODEL.md":"4784525ec7e8af6073fd2b934f855f5ac8ee2a639cb3ff1200c1811883f8400f","security/sbom-runtime-win-py313.spdx.json":"603d502f18060070dcd35c2d8ec62114b2111970f140740e50b65db5a03062de","security/security_baseline_0_1.json":"a052db44ed119988fe5e40d244cd08e0f346ffcbe2dc1a7098488af88be88b6b","security/threat_model_0_1.json":"59fdb8dc84e6f0722605a63b5bb627b02e2f0db1e3d5c27e41e1e98391686131"},
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":["choose an authoritative advisory source and a scanner with pinned provenance","define whether advisory unavailability fails the lane and how local development degrades","define severity handling for runtime build and security-tool dependencies","exceptions require vulnerability ID justification owner expiry and compensating control","audit consumes the exact locked package versions rather than performing a fresh resolution","scanner output is non-secret minimal retained and does not authorize dependency updates","separate vulnerability detection from license review and automatic remediation"],
  "express_exclusions":["real vulnerability exception creation or approval","automatic dependency remediation or license approval","GitHub settings Actions permissions or secrets","runtime product code tests addon updater packaging SimulationCraft signing release or distribution","commit push or changes outside eight allowlisted paths"]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

Design status: `dependency_vulnerability_audit_0_1_design_ready_for_review`.

### Proposed audit design

The authoritative advisory source is the Python Packaging Advisory Database as
served for exact PyPI distributions. The selected scanner is PyPA
`pip-audit`. Its future installation must use a dedicated security-tool lock
that fixes the scanner and every transitive dependency by version, wheel and
SHA-256; it must never be installed from an unpinned floating requirement.
Before implementation, a focused preflight must verify the exact command-line
and response semantics of the selected pinned release against primary PyPA
documentation. That preflight may fix the version and hashes, but may not
silently substitute a different advisory service.

The audit input is the complete set of package name/version pairs already
fixed in `desktop-app/requirements-ci-win-py313.lock` and represented in
`security/sbom-runtime-win-py313.spdx.json`. The implementation must reject a
lock/SBOM mismatch, duplicate package identity, unsupported requirement form,
missing hash or any attempt by the scanner to resolve a newer dependency set.
The runtime, build and security-tool dependency classes are explicit policy
data and are not inferred from installation order.

The lane has three closed outcomes:

- `audit_clean`, exit 0: the pinned scanner completed against the authoritative
  source and returned no applicable known vulnerability for every exact input;
- `vulnerability_detected`, exit 1: at least one applicable advisory remains
  without a current approved exception;
- `audit_unavailable`, exit 2: advisory access, scanner execution, schema,
  provenance, input integrity or completeness could not be proven.

Both non-zero outcomes fail CI. Local development may continue unrelated work
after `audit_unavailable`, but it cannot describe the dependency set as clean,
approved or release-ready. Cached success never substitutes for a current
online audit. No credentials are required; network access is restricted to the
selected advisory service and package installation is a separate earlier CI
step using the existing hash-locked files.

Every applicable known vulnerability blocks by default even when no numeric
severity is published. Severity is retained only for triage and cannot lower a
finding automatically. Runtime and build findings block the product lane;
security-tool findings invalidate the audit lane itself. An exception is valid
only when a separately approved record contains the vulnerability identifier,
exact package and version, owner, justification, compensating control,
approval reference, creation time and expiry. Expired, ambiguous, wildcard,
unowned or hash-mismatched exceptions fail closed. The proposed maximum life
is 30 days and renewal is a new human decision; this design creates no
exception.

Retained evidence is a minimal non-secret JSON summary containing the scanner
identity and hashes, input lock and SBOM hashes, advisory service identity,
UTC observation time, normalized vulnerability identifiers, exception
references, outcome and exit code. Raw HTTP bodies, environment variables,
absolute personal paths and credentials are forbidden. CI retention is seven
days. Detection does not approve dependency changes, license conclusions,
automatic remediation, releases or external-beta readiness.

### Closed implementation candidate

The implementation candidate is limited to these eight versioned routes:

- `.github/workflows/dpslab-ci.yml`;
- `desktop-app/requirements-security-tools-win-py313.lock`;
- `docs/DEPENDENCY_SECURITY.md`;
- `docs/NEXT_TASK.md`;
- `security/dependency_vulnerability_policy_0_1.json`;
- `security/dependency_vulnerability_exceptions_0_1.json`;
- `tools/dependency_vulnerability_audit.py`;
- `tools/tests/test_dependency_vulnerability_audit.py`.

Its future contract must protect the existing runtime lock, SBOM, security
baseline, threat model and production source; forbid SimulationCraft, addon,
updater, signing, releases, dependency remediation and GitHub setting changes;
and require focused negative tests for advisory outage, scanner drift,
lock/SBOM divergence, incomplete coverage, unknown severity and every invalid
exception state. Implementation, network validation, dependency acquisition,
commit and push remain unauthorized by this design.

Design verdict: `dependency_vulnerability_audit_0_1_design_ready_for_human_review`.

### Implementation evidence

Implementation status:
`dependency_vulnerability_audit_0_1_implemented_ready_for_independent_audit`.

- Daniel explicitly approved the design and the eight-route implementation
  scope on 2026-08-27; commit and push remain unauthorized;
- PyPA `pip-audit 2.10.1` and 28 transitive distributions were acquired from
  PyPI without workstation installation, fixed as 29 exact Windows CPython
  3.13 wheel hashes, and the temporary acquisition directories were removed;
- the adapter validates the runtime lock, matching SPDX SBOM, security-tool
  lock, scanner version, complete result coverage, closed JSON form and an
  empty versioned exception registry before accepting any result;
- scanner execution is isolated with `-I`, removes Python and pip audit
  environment overrides, uses `--require-hashes`, `--disable-pip`, `--strict`
  and the PyPI advisory service, and never passes `--fix` or `--ignore-vuln`;
- 14 focused tests and 81 complete tools tests passed; protected hashes and
  the exact eight-route scope passed the quality-gate preflight and run;
- the attended live observation at `2026-08-28T02:10:58Z` covered 35 exact
  packages and returned `vulnerability_detected`, exit 1, for
  `cryptography 49.0.0` / `PYSEC-2026-3552`, aliases `CVE-2026-69247` and
  `GHSA-g6cj-pr64-35w5`, with `50.0.0` reported as a fix version;
- the live observation used the available local Python 3.12 runtime with the
  same package identities and versions. Windows Python 3.13 installation and
  execution remain unverified until a future authorized publication triggers
  CI;
- no exception, dependency remediation, license decision, product code,
  SimulationCraft, addon, release, commit or push occurred.

The finding is an open dependency-remediation gate, not a failure of the audit
implementation. Publication without remediation would intentionally make the
new CI audit step fail closed.

## Published implementation record — Cryptography dependency remediation 0.1

This task replaced only the vulnerable `cryptography 49.0.0` dependency with
the latest compatible corrected patch, keeps the exception registry empty and
revalidates the combined vulnerability-audit candidate. It authorizes no
functional code change, SimulationCraft, commit or push.

<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version":"0.1",
  "task_id":"cryptography_dependency_remediation_0_1",
  "title":"Upgrade cryptography to the latest compatible corrected patch and revalidate the combined dependency-audit candidate",
  "baseline_commit":"d19f18ea84fb3ec7da5627e5fc8b89a33042c8d3",
  "authorization":{"status":"authorized_for_implementation","authorization_id":"cryptography_dependency_remediation_0_1-20260827-daniel-explicit","authorized_by":"Daniel","authorized_at":"2026-08-27T21:20:00-05:00"},
  "scope":{"allowed_paths":[".github/workflows/dpslab-ci.yml","desktop-app/pyproject.toml","desktop-app/requirements-ci-win-py313.lock","desktop-app/requirements-security-tools-win-py313.lock","desktop-app/tests/strict_temporary_cleanup.py","desktop-app/tests/test_candidate_knowledge_store.py","desktop-app/tests/test_comparator.py","desktop-app/tests/test_comparison_adapter.py","desktop-app/tests/test_comparison_environment.py","desktop-app/tests/test_comparison_execution.py","desktop-app/tests/test_comparison_member_transactions.py","desktop-app/tests/test_comparison_models.py","desktop-app/tests/test_comparison_preflight.py","desktop-app/tests/test_comparison_readiness.py","desktop-app/tests/test_comparison_spec.py","desktop-app/tests/test_config.py","desktop-app/tests/test_deep_audit.py","desktop-app/tests/test_equipment_transform.py","desktop-app/tests/test_knowledge_envelope.py","desktop-app/tests/test_new_artifact_transaction.py","desktop-app/tests/test_official_source_operator.py","desktop-app/tests/test_official_source_store.py","desktop-app/tests/test_parser.py","desktop-app/tests/test_planned_member.py","desktop-app/tests/test_release_key_ceremony_cli.py","desktop-app/tests/test_release_key_ceremony_executor.py","desktop-app/tests/test_runner.py","desktop-app/tests/test_scenario.py","desktop-app/tests/test_simc_identity.py","desktop-app/tests/test_source_coverage.py","desktop-app/tests/test_static_template_catalog.py","desktop-app/tests/test_variant.py","desktop-app/tests/test_windows_key_protection.py","docs/DEPENDENCY_SECURITY.md","docs/NEXT_TASK.md","security/dependency_vulnerability_exceptions_0_1.json","security/dependency_vulnerability_policy_0_1.json","security/sbom-runtime-win-py313.spdx.json","tools/dependency_vulnerability_audit.py","tools/tests/test_dependency_supply_chain.py","tools/tests/test_dependency_vulnerability_audit.py","tools/tests/test_security_baseline.py"],"generated_paths":[".dpslab/quality-gates/cryptography_dependency_remediation_0_1/implementation.json",".dpslab/quality-gates/cryptography_dependency_remediation_0_1/audit.json"],"forbidden_paths":["desktop-app/src/**","knowledge/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc","AGENTS.md","SECURITY.md","docs/SECURITY_ARCHITECTURE.md","docs/THREAT_MODEL.md","security/security_baseline_0_1.json","security/threat_model_0_1.json"],"allow_deletions":false,"allow_renames":false},
  "tests":{"focused":{"working_directory":"desktop-app","argv":["python","-m","unittest","tests.test_runner","-v"],"environment":{"PYTHONPATH":"src","PYTHONDONTWRITEBYTECODE":"1"}},"full":{"working_directory":"desktop-app","argv":["python","-m","unittest","discover","-s","tests","-v"],"environment":{"PYTHONPATH":"src","PYTHONDONTWRITEBYTECODE":"1"}},"baseline_test_count":1117,"minimum_test_count":1117},
  "protected_files":{".github/workflows/dpslab-ci.yml":"49c1f3222d3a1f16108bba2dc652139a10765723bed7e8df0a486f9be4f6f8b1","AGENTS.md":"1886e30bdec4abf3669dee0c2f0ce0a7271fa3cf30ed3830dfff24aef49edcb0","SECURITY.md":"b00e680630009bfd062a58b5a8d3129b9c68e45fb8aa284f05133f173fe2daf5","desktop-app/requirements-security-tools-win-py313.lock":"32cc25f59da407fb3ba6bdfd0a2b37915b75c44b337eca2554b6f3fc0f8561a0","docs/SECURITY_ARCHITECTURE.md":"ebe0dd5624e7149807275dfab891fd52e598f27e7c7afedfec2bd4fbc15fdde5","docs/THREAT_MODEL.md":"4784525ec7e8af6073fd2b934f855f5ac8ee2a639cb3ff1200c1811883f8400f","security/dependency_vulnerability_exceptions_0_1.json":"f59ab7e1c8367f08dac6a6abeb195bb91934497052a1e85e5995cc9cbdb6ddfe","security/security_baseline_0_1.json":"a052db44ed119988fe5e40d244cd08e0f346ffcbe2dc1a7098488af88be88b6b","security/threat_model_0_1.json":"59fdb8dc84e6f0722605a63b5bb627b02e2f0db1e3d5c27e41e1e98391686131","tools/dependency_vulnerability_audit.py":"09c8aa0b6a717254b6137413041bc07d9d5d35b0890f342ce3238dd91442ddad","tools/tests/test_dependency_vulnerability_audit.py":"09da65c753105fcaf12c873dcfdf901baf1351b73ffec09072a257faf2c8bf12"},
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":["select the latest released corrected cryptography patch compatible with Windows x86-64 CPython 3.13","change no resolved runtime package other than cryptography","bind pyproject runtime lock SPDX SBOM and vulnerability policy hashes to the same exact version and wheel bytes","keep the vulnerability exception registry empty and unchanged","preserve the audited vulnerability adapter workflow and security-tool lock byte for byte","adopt one strict Windows-aware cleanup policy for every test module that creates TemporaryDirectory instances","retry only Windows directory-not-empty cleanup failures with bounded backoff and retain failure for every other cleanup error or exhausted retry","run affected modules plus the full tools and functional suites","repeat a live audit of all 35 exact runtime build and security-tool packages and require audit_clean exit 0","record local Python limitations separately from future canonical Windows Python 3.13 CI evidence"],
  "express_exclusions":["vulnerability exception or ignore rule","automatic remediation or unrelated dependency update","functional source addon updater SimulationCraft comparison signing release or distribution","GitHub settings Actions permissions secrets commit or push","changes outside forty-two allowlisted paths"]
}
```
<!-- DPSLAB_HISTORICAL_TASK_CONTRACT_END -->

### Implementation evidence

- `cryptography` changed from `49.0.0` to the latest compatible corrected
  patch `50.0.1`; the canonical Windows x86-64 CPython 3.13/ABI3 wheel is
  pinned by SHA-256
  `aed8db4f6d71c51efb89530e12d9464e7bf2923d46c3205dc794a2a93f8c0648`;
- the other five resolved runtime distributions retained their exact versions
  and wheel hashes; the security-tool lock, vulnerability adapter, workflow
  behavior and empty exception registry were preserved;
- the runtime lock SHA-256 is
  `8d2dfca84345d1c17ef575d50d01eaa36d5cea6fd94c25fc531e7180979e3586`
  and the regenerated SPDX SBOM SHA-256 is
  `0f92571035f4db9263cc2709dc4187f4f70db73b5f4e34e0fa826ded672c648c`;
- 25 focused supply-chain, vulnerability-adapter and security-baseline tests
  passed;
- the attended live audit at `2026-08-28T03:05:35Z` covered all 35 exact
  runtime, build and security-tool packages and returned `audit_clean`, zero
  findings, zero exceptions and exit 0;
- initial full-suite observations exposed a Windows temporary-directory cleanup
  race (`WinError 145`) after otherwise successful assertions; the authorized
  test-only remediation now routes every TemporaryDirectory user through one
  bounded strict cleanup policy;
- the remediation-specific module set passed 282 tests with one expected skip,
  the focused cleanup-helper module passed 23 tests, and the complete local
  functional suite passed 1,117 tests with zero failures and one expected skip;
- canonical Windows Python 3.13 CI execution verified the published candidate:
  GitHub Actions run `33168962221` passed Policy and contract, Tools tests and
  Functional suite on commit
  `9a06c79af389cdb0a3f734c7c2eb88b4507124b3`;
- the commit was published exclusively from `main` to `origin/main`; local,
  tracking and live remote references were verified equal afterwards;
- the authorization was consumed only by Daniel's subsequent explicit human
  approval of the audited candidate, its local commit and its publication;
- no exception, functional source change, SimulationCraft, addon or release
  occurred.

Closure status:
`cryptography_dependency_remediation_0_1_published_with_ci_approved`.

## Consumed design record — Static analysis and secret scanning 0.1

This design establishes the closed implementation boundary for two additional
distribution gates: static analysis of DpsLab's Python source and secret
scanning of the repository. It authorizes design documentation only. In
particular, it does not install scanners, add a workflow, scan history, create
an exception, upload findings or use repository credentials.

<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_BEGIN -->
```json
{
  "contract_version":"0.1",
  "task_id":"static_analysis_and_secret_scanning_0_1_design",
  "title":"Design hash-locked static analysis and credential-free secret scanning gates",
  "baseline_commit":"7a41e1cd031ea0dae8054e3501f6e5f9233d1ba1",
  "authorization":{"status":"design_only","authorization_id":"static_analysis_and_secret_scanning_0_1_design-20260828-daniel-broad-authority","authorized_by":"Daniel","authorized_at":"2026-08-28T06:58:00-05:00"},
  "scope":{"allowed_paths":["docs/DEPENDENCY_SECURITY.md","docs/NEXT_TASK.md"],"generated_paths":[".dpslab/quality-gates/static_analysis_and_secret_scanning_0_1_design/design.json"],"forbidden_paths":[".github/**","desktop-app/**","security/**","knowledge/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc","AGENTS.md","SECURITY.md","docs/SECURITY_ARCHITECTURE.md","docs/THREAT_MODEL.md","tools/**"],"allow_deletions":false,"allow_renames":false},
  "tests":{"focused":{"working_directory":".","argv":["python","-m","unittest","discover","-s","tools/tests","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"full":{"working_directory":".","argv":["python","-m","unittest","discover","-s","tools/tests","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"baseline_test_count":82,"minimum_test_count":82},
  "protected_files":{"AGENTS.md":"1886e30bdec4abf3669dee0c2f0ce0a7271fa3cf30ed3830dfff24aef49edcb0","SECURITY.md":"b00e680630009bfd062a58b5a8d3129b9c68e45fb8aa284f05133f173fe2daf5",".github/workflows/dpslab-ci.yml":"49c1f3222d3a1f16108bba2dc652139a10765723bed7e8df0a486f9be4f6f8b1","desktop-app/pyproject.toml":"53363b1b7fd8bec9ec645596bda81be98c068b1e7bc553674f545eb0f05005a1"},
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":["define a credential-free scanner acquisition and integrity policy with exact version and SHA-256 evidence","define Python static-analysis scope severity threshold sanitized output and fail-closed tool-unavailable behavior","define secret-scanning scope that can scan committed history without sending source code findings or GitHub token to a third-party action","define only fingerprint-specific expiring human-reviewed suppressions and prohibit broad ignores","preserve the existing pinned-action least-privilege CI posture and seven-day sanitized evidence retention","separate scanner design from implementation dependency acquisition findings remediation commit push and release approval"],
  "express_exclusions":["installing or running Bandit Gitleaks or another scanner","workflow modification CI execution or artifact upload","secret scanning of real repository history","credentials tokens secrets exception creation or finding remediation","SimulationCraft addon UI updater signing release or distribution","changes outside two allowlisted documentation paths"]
}
```
<!-- DPSLAB_CONSUMED_DESIGN_CONTRACT_END -->

Design direction: use a hash-locked scanner binary or package in CI rather
than a third-party scanning action that receives `GITHUB_TOKEN`; collect only
sanitized aggregate evidence; treat a scanner failure as a gate failure; and
require an exact, expiring, human-reviewed fingerprint for any future false
positive suppression. GitHub's own hardening guidance confirms that any action
used in a later workflow must remain fixed to a full commit SHA.

Design evidence: Bandit `1.9.4` supplies an attested universal wheel with
SHA-256 `f89ffa663767f5a0585ea075f01020207e966a9c0f2b9ef56a57c7963a3f6f8e`.
Gitleaks `8.30.1` is excluded because a public report identifies a checksum
mismatch for its Windows x64 release asset. The candidate retained for a
future independently verified acquisition is Gitleaks `8.30.0`
`windows_x64.zip`, SHA-256
`54fe94f644b832dd08e8c3a5915efb3bfa862386d59fb27ca0792cb687a83573`.

## Active implementation task — Static analysis and secret scanning 0.1

This task implements the approved scanner controls with exact acquisition
evidence. It may acquire scanner bytes only into a temporary verification
directory, verify their identities before execution, and retain only sanitized
aggregate results. It must not transmit a GitHub token or repository source to
an external scanning service.

<!-- DPSLAB_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version":"0.1",
  "task_id":"static_analysis_and_secret_scanning_0_1",
  "title":"Implement hash-locked static analysis and credential-free secret scanning gates",
  "baseline_commit":"135ee6d41bfb75b47e739ac21951e78699ccdae5",
  "authorization":{"status":"authorized_for_implementation","authorization_id":"static_analysis_and_secret_scanning_0_1-20260828-daniel-broad-authority","authorized_by":"Daniel","authorized_at":"2026-08-28T07:16:00-05:00"},
  "scope":{"allowed_paths":[".github/workflows/dpslab-ci.yml","desktop-app/requirements-security-tools-win-py313.lock","docs/DEPENDENCY_SECURITY.md","docs/NEXT_TASK.md","security/static_analysis_policy_0_1.json","security/secret_scan_policy_0_1.json","security/secret_scan_exceptions_0_1.json","security/dependency_vulnerability_policy_0_1.json","tools/static_security_analysis.py","tools/tests/test_dependency_supply_chain.py","tools/tests/test_dependency_vulnerability_audit.py","tools/tests/test_github_automation.py","tools/tests/test_security_baseline.py","tools/tests/test_static_security_analysis.py"],"generated_paths":[".dpslab/quality-gates/static_analysis_and_secret_scanning_0_1/implementation.json",".dpslab/quality-gates/static_analysis_and_secret_scanning_0_1/audit.json"],"forbidden_paths":["desktop-app/src/**","desktop-app/tests/**","knowledge/**","profiles/**","scenarios/**","variants/**","comparisons/**","results/**","config/**","flasil.simc","AGENTS.md","SECURITY.md","docs/SECURITY_ARCHITECTURE.md","docs/THREAT_MODEL.md","security/security_baseline_0_1.json","security/threat_model_0_1.json","security/dependency_vulnerability_exceptions_0_1.json","security/sbom-runtime-win-py313.spdx.json"],"allow_deletions":false,"allow_renames":false},
  "tests":{"focused":{"working_directory":".","argv":["python","-m","unittest","tools.tests.test_static_security_analysis","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"full":{"working_directory":".","argv":["python","-m","unittest","discover","-s","tools/tests","-v"],"environment":{"PYTHONDONTWRITEBYTECODE":"1"}},"baseline_test_count":82,"minimum_test_count":86},
  "protected_files":{"AGENTS.md":"1886e30bdec4abf3669dee0c2f0ce0a7271fa3cf30ed3830dfff24aef49edcb0","SECURITY.md":"b00e680630009bfd062a58b5a8d3129b9c68e45fb8aa284f05133f173fe2daf5","desktop-app/pyproject.toml":"53363b1b7fd8bec9ec645596bda81be98c068b1e7bc553674f545eb0f05005a1","security/security_baseline_0_1.json":"a052db44ed119988fe5e40d244cd08e0f346ffcbe2dc1a7098488af88be88b6b"},
  "audit":{"required":true,"independence":"declared_and_procedural"},
  "acceptance_criteria":["Bandit and every required Python dependency are version and SHA-256 locked before CI execution","Bandit scans only versioned Python product and tooling source with high-severity findings failing closed and no baseline suppression","Gitleaks 8.30.0 Windows x64 archive is downloaded from its official release only after SHA-256 verification and scans full committed history without GITHUB_TOKEN","raw scanner reports are temporary and only closed-schema sanitized counts identifiers and status may enter a seven-day artifact","tool failure integrity mismatch missing coverage or any unsuppressed finding returns a nonzero gate result","a future suppression is limited to one fingerprint with explicit human approval owner justification and expiry; empty exception registry is the initial state","no scanner operates on SimulationCraft profiles results local configuration addon or external network sources"],
  "express_exclusions":["scanner exception approval or finding remediation","Gitleaks 8.30.1 or unverified scanner bytes","third-party scanning action GITHUB_TOKEN or other credentials","SimulationCraft addon UI updater signing release distribution or external beta","changes outside twelve allowlisted paths"]
}
```
<!-- DPSLAB_TASK_CONTRACT_END -->
