# Blizzard Patch Notes Anchor Path Probe 0.1

## Purpose

The first semantic-shape observation rejected `data-props` because the
implementation required the carrying `div` to be a direct child of `article`.
The earlier layout report proved only that both structures existed; it did not
prove they were the same edge.

This corrective probe observes ancestry topology without reading attribute
values. It determines whether elements named `div` with an attribute named
`data-props` occur beneath an `article`, and reports only their tag paths.

## Output boundary

For each matching element, the report may retain:

- the ordered tag-name path from the nearest `article` ancestor to the
  `data-props` carrier, inclusive;
- occurrence count and path depth;
- counts for carriers with no `article` ancestor;
- receipt, content, probe-revision, and report hashes;
- status `anchor_path_observed_pending_review`.

It must not retain text, attribute values, other attribute names, element
classes, identifiers, URLs, selectors, HTML fragments, source prose, or JSON.
Tag names are normalized and validated conservatively.

## Fail-closed behavior

Receipt mismatch, invalid UTF-8, malformed nesting, excessive input, nodes,
depth, matches, unique paths, or path length rejects the report. An observation
with no `data-props` carrier is unavailable. Carriers outside `article` are
counted but never silently treated as anchored.

The report cannot relax the semantic-shape probe automatically. A human must
review the observed paths and approve one exact ancestry policy in a separate
contract.

Implementation and tests must use invented HTML only. A future real
observation requires one new attended authorization and no retries.

## Proposed paths

1. `desktop-app/src/dpslab/blizzard_patch_notes_anchor_path_probe.py`;
2. `desktop-app/tests/test_blizzard_patch_notes_anchor_path_probe.py`;
3. `knowledge/schemas/blizzard_patch_notes_anchor_path_report_0_1.json`;
4. `knowledge/fixtures/blizzard_patch_notes_anchor_path_synthetic_0_1.html`;
5. `knowledge/snapshots/blizzard_patch_notes_anchor_path_synthetic_0_1.json`;
6. `docs/BLIZZARD_PATCH_NOTES_ANCHOR_PATH_PROBE.md`;
7. `docs/NEXT_TASK.md`.
