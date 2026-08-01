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
