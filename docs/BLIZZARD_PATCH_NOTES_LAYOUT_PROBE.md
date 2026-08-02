# Blizzard Patch Notes Layout Probe 0.1

## Purpose

Before a production parser can consume Blizzard Content Update Notes, DpsLab
needs evidence about the public page structure actually returned by the
allowlisted source. The probe is a bounded, attended diagnostic boundary. It
does not extract balance facts and does not retain page content.

## Input boundary

The probe may receive only injected UTF-8 bytes that already match a validated
`captured_pending_review` receipt by byte count and SHA-256. Network access,
receipt persistence, scheduling, and confirmation remain outside the probe.

The implementation and its tests must use synthetic HTML only. A future live
invocation requires its own attended authorization and exactly one fresh
official-source response.

## Allowed structural observations

The output may contain only bounded metadata needed to design a parser:

- receipt identity, content SHA-256, byte count, and probe revision;
- ordered tag names and parent-to-child tag edges;
- attribute names, never attribute values;
- counts capped by explicit node, depth, attribute, and output limits;
- boolean indicators for comments, declarations, scripts, styles, and
  embedded JSON without retaining their contents;
- one canonical SHA-256 over the closed report.

No text nodes, URLs, attribute values, CSS selectors, script bodies, comments,
HTML fragments, cookies, headers, credentials, or source prose may appear in
the report. Unknown encoding, malformed markup, receipt mismatch, excessive
size, depth, nodes, attributes, or report cardinality must fail closed.

## Human review boundary

A report is always `layout_observed_pending_review`. It can support a human
decision about a future source-specific parser revision, but cannot modify the
existing extractor, declare source coverage, approve evidence, update a
catalog, or generate recommendations.

The human reviewer must decide whether the observed structure is sufficiently
stable and semantically explicit. Text meaning and numerical changes remain a
separate extraction and review problem.

## Proposed implementation scope

The implementation contract should be limited to:

1. `desktop-app/src/dpslab/blizzard_patch_notes_layout_probe.py`;
2. `desktop-app/tests/test_blizzard_patch_notes_layout_probe.py`;
3. `knowledge/schemas/blizzard_patch_notes_layout_report_0_1.json`;
4. `knowledge/fixtures/blizzard_patch_notes_layout_synthetic_0_1.html`;
5. `knowledge/snapshots/blizzard_patch_notes_layout_synthetic_0_1.json`;
6. `docs/BLIZZARD_PATCH_NOTES_LAYOUT_PROBE.md`;
7. `docs/NEXT_TASK.md`.

Tests must prove receipt binding, deterministic ordering, content erasure,
closed fields, canonical hashing, and every resource limit. They must not make
a live request or use copied Blizzard markup.
