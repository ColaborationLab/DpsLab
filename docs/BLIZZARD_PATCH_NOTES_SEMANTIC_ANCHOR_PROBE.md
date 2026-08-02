# Blizzard Patch Notes Semantic Anchor Probe 0.1

## Purpose

The real layout observation found twelve `article` elements and twelve
descendant `div` elements carrying `data-props`. This is structural evidence,
not evidence that the attribute contains balance facts. A second bounded probe
is required before designing a production extractor.

The semantic-anchor probe describes only the shape of allowlisted JSON
attributes. It never emits JSON values, article text, source prose, URLs, HTML,
selectors, or recommendations.

## Closed observation model

The probe may inspect only `data-props` on a `div` that is a direct child of an
`article`. Each value must be UTF-8 JSON and must satisfy closed resource
limits before traversal. The report may contain:

- the number of matching article anchors;
- canonical JSON key paths made only from object-key names and the array marker
  `[]`;
- the observed JSON type for each key path;
- bounded occurrence, maximum array-length, and maximum object-key counts;
- receipt, content, probe-revision, and report hashes;
- a `semantic_shape_observed_pending_review` status.

Object values, string contents, numbers, booleans, null values, array items,
source text, markup, and attribute values are discarded. Keys are metadata but
still require conservative token validation and cardinality limits.

## Fail-closed rules

The operation rejects malformed HTML, non-JSON attributes, duplicate JSON
keys, non-object roots, excessive JSON bytes, depth, keys, arrays, anchors, or
report paths. Conflicting types at the same canonical path also reject the
entire report. Receipt byte-count and SHA-256 binding is mandatory.

An empty match is `semantic_anchor_unavailable`, not success. A valid shape
report cannot approve a selector or demonstrate that any key is semantically a
class, specialization, ability, coefficient, build, date, or change.

## Separation from a future parser

Human review must decide whether the discovered key paths expose sufficiently
explicit and stable fields for a source-specific parser revision. Any later
mapping from a key path to a DpsLab fact requires a separate contract, copied
source-free synthetic tests, and an independent review.

No live request belongs to implementation. A future real observation requires
one new attended authorization and must discard the response body immediately.

## Approved ancestry candidate for revision 0.2

The attended anchor-path observation on unchanged source bytes found exactly
twelve carriers. All twelve shared one normalized nearest-article path:
`article` followed by eight `div` elements. No unanchored carrier was present.

Revision 0.2 may therefore accept only that exact path. It must reject a direct
child, any shorter or longer chain, any intervening non-`div` element, a carrier
outside `article`, or mixed path populations. This structural policy does not
approve the meaning of `data-props` or any JSON key.

## Proposed implementation paths

1. `desktop-app/src/dpslab/blizzard_patch_notes_semantic_anchor_probe.py`;
2. `desktop-app/tests/test_blizzard_patch_notes_semantic_anchor_probe.py`;
3. `knowledge/schemas/blizzard_patch_notes_semantic_shape_0_1.json`;
4. `knowledge/fixtures/blizzard_patch_notes_semantic_anchor_synthetic_0_1.html`;
5. `knowledge/snapshots/blizzard_patch_notes_semantic_shape_synthetic_0_1.json`;
6. `docs/BLIZZARD_PATCH_NOTES_SEMANTIC_ANCHOR_PROBE.md`;
7. `docs/NEXT_TASK.md`.
