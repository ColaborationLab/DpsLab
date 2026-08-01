# Official source acquisition 0.1

## Purpose

DpsLab needs current World of Warcraft evidence without turning arbitrary web
content into live recommendations. Acquisition is therefore a maintenance
pipeline, not an addon behavior and not an unreviewed desktop feature.

## First-party source roles

The World of Warcraft Content Update Notes index at
`https://worldofwarcraft.blizzard.com/en-us/content-update-notes` is the
canonical discovery surface for official content updates and hotfix notices.
Its role is change detection and provenance, not automatic numerical guidance.

The Battle.net World of Warcraft Game Data APIs documented at
`https://community.developer.battle.net/documentation/world-of-warcraft/game-data-apis`
are the preferred structured source where a documented endpoint covers the
required parameter family. Absence of an endpoint remains a coverage gap; it
does not authorize scraping, guessing, or silently substituting third-party
data.

## Governed flow

1. A scheduled maintenance job checks allowlisted first-party discovery
   endpoints using bounded requests and records validators and byte hashes.
2. New or changed bytes are quarantined as evidence pending review.
3. A source-specific adapter extracts only explicitly supported facts and
   binds them to source revision, build, interface, locale, time, and hash.
4. Coverage assessment requires every parameter family declared for the exact
   class, specialization, role, and content context.
5. Human review confirms currentness, applicability, license class, source
   coverage, and role safety.
6. Candidate construction, attended signature, publication approval, and
   distribution occur as separate transactions.

Historical captures may be retained content-addressed for audit and change
comparison. They never satisfy current coverage and never reactivate guidance.

## Desktop and addon boundary

The addon remains lightweight and offline during combat. It consumes only
bundled or locally supplied, verified DpsLab guidance. The desktop application
may check for signed DpsLab package updates, verify them against the published
trust registry, and stage them for activation. It must not convert a live web
response into advice.

Blizzard API credentials must not be embedded in the addon, desktop package,
catalog, log, or repository. If authenticated API acquisition is required, it
belongs to a controlled maintainer service or an explicit operator-owned
credential flow; that choice requires a later security and operational review.

## Fail-closed conditions

Acquisition is unavailable on an unknown host or redirect, unexpected media
type, partial or oversized response, ambiguous locale, missing validator,
unknown build/interface, stale capture, incomplete role coverage, licensing
uncertainty, authentication failure, or parser ambiguity. No condition may be
resolved by selecting the newest-looking result or reusing historical evidence
as current.

## Inert request planning

`official_source_request` constructs immutable request plans without importing
or invoking an HTTP client. Content-update discovery is fixed to HTTPS, the
exact first-party host, the canonical `en-us` path, and HTML. Game Data plans
are fixed to the official US API host, `/data/wow/` paths, an explicit static
or dynamic namespace, `en_US`, and JSON.

API plans state that an external bearer credential is required but never
accept or emit one. Conditional ETag and Last-Modified values are bounded and
reject control characters. The eventual transport must independently enforce
the same host, redirect, size, media-type, completeness, and credential rules
before handing bytes to quarantine.

## Injected transport boundary

`official_source_transport` accepts an immutable request plan and an injected
sender. The module contains no HTTP client, socket, DNS, credential, or file
operation. It validates the simulated or externally obtained response and
hands accepted bytes to the existing `InjectedResponse` quarantine boundary.

Only exact HTTPS targets, accepted media types, complete bounded byte bodies,
sanitized cache validators, and status 200 or a structurally valid 304 pass.
Transport errors are reduced to typed public reasons. Plans requiring an
external bearer credential return `credential_required` without invoking the
sender; authenticated transport remains a later block.

## Public HTTPS client

`official_source_http` is the concrete credential-free transport for public
plans. It uses the Python standard-library HTTPS stack, denies redirects before
following them, forwards only plan headers, applies a bounded timeout, and
reads at most `max_bytes + 1`. Content-Length disagreement and every network
or HTTP exception fail closed without exposing exception details.

The result remains quarantined in memory. The client does not persist or parse
responses, approve coverage, update guidance, or accept authenticated plans.

## Canonical public HTML source

`knowledge/sources/official_patch_source_registry_0_1.json` registers exactly
the Blizzard Content Update Notes source on
`worldofwarcraft.blizzard.com`. Its policy permits `text/html`, denies redirect
hosts, fixes the canonical `en_US` locale, limits responses to one mebibyte,
and assigns review to the DpsLab maintainer.

HTML belongs to the adapter's closed media-type vocabulary only so an explicit
source policy can allow it. JSON-only sources still reject HTML. A valid HTML
capture remains `captured_pending_review`; registry membership never approves,
parses, persists, signs, publishes, or converts the response into guidance.

The initial live diagnostic observed HTTP 200 from the exact official host,
`text/html`, a complete 274005-byte body, and SHA-256
`fbf289f3068d3bb14f04709f0f735db9ee09183cc90968d5e34384fad657f1e6`.
The response body was not stored and the observation does not establish source
coverage or authorize another request.

## Metadata-only capture receipts

A future capture receipt should make change detection auditable without
retaining source content. The canonical receipt binds source ID, capture time,
transport and capture status, final host, media type, completeness, byte count,
content SHA-256, and sanitized ETag or Last-Modified values when present.

Receipts contain no response body, extracted prose, cookies, credentials,
personal paths, semantic facts, or recommendations. Their maximum state is
`captured_pending_review`; identical content hashes are recorded as duplicates
and never interpreted as current coverage. Initial implementation should use
only synthetic responses and an injected clock. Real receipt persistence and
retention policy require a later, separate authorization.
