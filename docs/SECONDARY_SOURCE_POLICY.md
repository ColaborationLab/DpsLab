# Secondary Source Policy 0.1

## Purpose

DpsLab may use community and analytical World of Warcraft sources to discover
coverage gaps, corroborate details, or explain mechanics that Blizzard does not
publish in a structured form. These sources are evidence inputs, never direct
recommendations or implicit authority.

This policy does not approve or allowlist Wowhead or any other named site. A
candidate requires a separate source-specific review before any acquisition is
designed or implemented.

## Authority order

1. Exact first-party Blizzard structured data for the applicable product,
   build, interface, locale, class, specialization, role, and content context.
2. Exact first-party Blizzard published notes or documentation.
3. Reproducible DpsLab measurements whose method and inputs are independently
   reviewable; these cannot rewrite Blizzard's declared facts.
4. Reviewed community or analytical sources with permitted use and complete
   provenance.
5. Unverified community statements, search snippets, forum posts, videos, and
   social content: discovery leads only.

A lower tier cannot silently overwrite a higher tier. Authority does not imply
completeness: an absent first-party fact remains a coverage gap until the
secondary-evidence procedure is satisfied.

## Permitted roles

Secondary sources may:

- identify a possible missing parameter or recent change;
- point reviewers to a first-party source;
- corroborate an explicitly cited fact;
- explain a mechanic while preserving its source and uncertainty;
- support a `pending_review` candidate when first-party coverage is absent.

They may not independently approve a fact, activate a catalog, generate live
guidance, resolve a contradiction, establish license permission, or bypass
role-safety review.

## Candidate-source review

Before allowlisting, record and review:

- stable source ID, owner, canonical host, content type, and intended role;
- applicable product, build/interface, locale, class, specialization, role,
  and content context;
- publication/revision identity, capture time, freshness limit, and
  invalidation triggers;
- terms of use, robots policy, API availability, rate limits, attribution,
  storage, derived-use, and redistribution treatment;
- acquisition method, redirects, authentication, byte limit, and failure
  behavior;
- known editorial methodology, correction process, and independence from other
  sources used for corroboration.

Unclear permission is `license_review_required`, not permission. DpsLab stores
the minimum evidence necessary—preferably citation metadata and hashes—and
does not retain or redistribute page bodies without explicit permission.

## Corroboration and conflicts

When first-party evidence covers the fact, it controls unless a human reviewer
records a narrowly scoped exception supported by newer first-party evidence.
Community disagreement produces `conflict_pending_review`.

When first-party coverage is genuinely absent, a secondary assertion may only
advance to `pending_review` with either:

- two independently produced, compatible secondary sources; or
- one reviewed secondary source plus a reproducible DpsLab measurement.

Shared copying, common upstream data, or mirrored text does not constitute
independence. Build, locale, role, or context mismatch is a contradiction, not
corroboration. Review can accept, reject, defer, or mark guidance unavailable;
it cannot manufacture missing evidence.

## Freshness and role safety

Every accepted fact is bound to the current product and explicit build range.
A new patch, hotfix, source withdrawal, changed bytes under the same revision,
expired freshness window, or changed class/spec/role applicability invalidates
the affected coverage until reviewed again.

Damage advice remains role-aware. Tank guidance must preserve survival and
incoming-damage constraints; healer damage guidance must preserve ally-healing
responsibilities. Secondary popularity rankings or generalized rotations never
override those constraints.

## Fail-closed outcomes

The only pre-approval outcomes are `discovery_only`, `license_review_required`,
`evidence_unavailable`, `conflict_pending_review`, `pending_review`, or
`guidance_unavailable`. None means approved, current, signed, or distributable.

No network request, scraping, browser automation, parsing, catalog mutation,
recommendation, signing, publication, addon change, or SimulationCraft
execution is authorized by this document.
