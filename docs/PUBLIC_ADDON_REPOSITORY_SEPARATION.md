# Public Addon Repository Separation 0.1

## Status

`design_only`. No repository, branch, clone, export, release package, or
GitHub setting is created or changed by this document.

The future public addon repository is an outbound publication target, never a
mirror of the private DpsLab repository. Publication is deny-by-default: an
item is private unless an approved export manifest explicitly classifies it as
public-safe.

## Asset classification

| Classification | May enter future public addon repository | Examples |
| --- | --- | --- |
| `public_safe_addon` | Yes, only after a reviewed export manifest | addon Lua/XML/TOC source, safe localization, build instructions, notices, issue/reporting guidance |
| `public_safe_documentation` | Yes, after provenance and rights review | user documentation, accessibility notes, supported-game-version statement, contribution guidance |
| `review_required` | No by default; requires a source-rights and privacy decision | static game facts, generated template extracts, screenshots, benchmarks, compatibility reports |
| `private_only` | Never | desktop application, signing or recovery material, keys, tokens, user data, browser captures, raw external-source captures, internal research, CI secrets, private diagnostics, non-public roadmaps |
| `external_reference_only` | No copied content; link only after rights review | Blizzard, community, and third-party pages or data governed by their own terms |

`review_required` remains private if approval is absent. A fact being useful to
the addon does not make its source, provenance, license, freshness, or
redistribution rights public-safe.

## One-way publication procedure

1. Start from a clean, reviewed commit in the private repository; never from an
   arbitrary working tree or a synchronized mirror.
2. Produce a proposed export manifest with exact paths, SHA-256 values,
   classification, copyright/notices, and source-rights status for every item.
3. Materialize that manifest into a fresh disposable staging directory outside
   both repositories. No copy command may use a broad directory wildcard.
4. Run the approved secret, credential, private-path, and prohibited-content
   preflight against the staged tree. A finding, unknown file, broken link, or
   missing notice fails closed.
5. Independently compare the staged tree with the approved manifest and record
   its aggregate hash and file count. Confirm that no desktop code, signing
   material, raw source capture, personal data, or internal governance record
   was exported.
6. Obtain a separate authorization for public-repository creation and initial
   publication. That authorization must name the exact staging output, public
   repository identity, default branch, license/notice texts, and release
   policy.
7. After publication, verify the remote tree and keep the private source of
   truth independent. Changes flow through a new reviewed export; public
   changes are never automatically merged back into private material.

## Minimum public repository boundary

Before a public repository can be created, a separately reviewed scope must
define at least:

- the addon-only directory layout and supported client/interface versions;
- the legal notice and contributor terms reviewed for a free, source-visible
  Blizzard-compatible addon;
- a public security-reporting route that does not expose private contacts,
  credentials, or vulnerability details;
- release artifacts and hashes produced from public-safe inputs only;
- a no-advertising/no-donation/no-premium-feature check for every in-game
  string, UI element, and release package;
- a contribution intake process that prevents unverified rights or secrets from
  entering the public tree.

The desktop application, desktop updater, commercial Qt entitlement evidence,
Patreon member data, release keys, recovery procedures, and internal quality
gate records remain outside this repository.

## Required rehearsal before a real publication

The first implementation must be a synthetic rehearsal. It may use only
invented addon files and synthetic metadata to demonstrate that the exporter:

- permits allowlisted `public_safe_addon` and `public_safe_documentation`
  inputs;
- rejects an unclassified path, a desktop path, a secret-shaped value, an
  external capture, an absent notice, or a changed hash;
- generates no network request, repository, branch, tag, release, or public
  artifact;
- leaves both the private repository and all protected signing material
  unchanged.

Only an audited rehearsal may become evidence for a separate decision on an
actual addon export.

## Explicit exclusions

This design does not authorize GitHub repository creation, visibility changes,
repository splitting, cloning, source export, license text, trademark claim,
Patreon account, payment, addon implementation, external data collection,
SimulationCraft, comparisons, or releases.
