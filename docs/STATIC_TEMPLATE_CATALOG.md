# Static Template Catalog 0.1

## Purpose

The catalog is a repository-local, versioned index of immutable DpsLab
knowledge envelopes. It is not a database, simulation archive, update channel,
approval service, or source of live World of Warcraft balance claims.

Validation proves canonical structure, hashes, copied indexing keys, and
governance consistency. It never creates human approval. Selection requires
separate approval evidence binding the exact catalog, entry, envelope, human
decision, reviewer, and time.

## Canonical representation and lifecycle

Catalog JSON is canonical UTF-8 with sorted keys, compact separators, and one
trailing LF. Its SHA-256 projection omits only `integrity.catalog_sha256`.
Envelope paths are confined to repository-relative JSON files immediately
below `knowledge/fixtures/`, and copied index keys must equal the envelope.

`draft`, `pending_review`, `rejected`, `deprecated`, and `withdrawn` entries
are unavailable. `approved` also remains unavailable without matching external
human evidence. Invalid, stale, incomplete, incompatible, or ambiguous state
returns `guidance_unavailable`; ordering and newest-file guesses are forbidden.

## Current-only and role-aware policy

Canonical state is immutable envelopes plus one current catalog. Git history
supports audit and recovery only. No database, remote catalog state, or
retrospective simulation store participates in selection.

- Damage guidance remains bounded by safety and encounter obligations.
- Tank damage is subordinate to survival, mitigation, threat, and obligations.
- Healer damage is subordinate to ally survival, healing, dispels, emergency
  capacity, and resource safety.

Version 0.1 cannot prove dynamic tank or healer safety from static files, so
such guidance remains unavailable without a future authorized observation
contract. Nothing in this module automates gameplay.

## Synthetic fixture and exclusions

The sole fixture is `pending_review`, declares incomplete source coverage, and
references the existing synthetic envelope. It contains no real class names,
balance data, statistics, talents, equipment, rotations, personal paths,
credentials, or current-patch claim. It is test evidence, not player guidance.

This block excludes live templates, patch intake, SimulationCraft,
comparisons, addon or desktop UI, networking, packaging, keys, signatures,
distribution, approval storage, databases, and publication.
