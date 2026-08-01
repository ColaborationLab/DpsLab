# Blizzard Patch Notes HTML Extractor 0.1

## Boundary

The extractor is a pure, source-specific conversion boundary for injected
Blizzard Content Update Notes bytes. It does not fetch, persist, browse,
execute JavaScript, approve evidence, or produce guidance.

Every input is bound to a validated metadata receipt with status
`captured_pending_review`. The byte count and SHA-256 must match before parsing.
The parser revision and exact receipt hash accompany every result.

## Recognized structure

The initial parser may recognize only a closed synthetic representation of:

- one document title and explicitly published build or patch token;
- class and specialization headings named by an exact mapping table;
- nested unordered lists beneath those headings;
- literal ability names and explicit source-provided old/new values;
- stable citation tokens derived from deterministic structural positions.

It may normalize whitespace and HTML entities but cannot paraphrase, infer a
missing subject, calculate a coefficient, supply an omitted unit, or interpret
comparative language as a numeric change.

## Fail-closed outcomes

Unknown layout, malformed nesting, duplicate citation position, unsupported
tag, ambiguous class/spec ownership, missing build applicability, mismatched
receipt, oversized depth or node count, and prose without explicit semantics
produce `evidence_unavailable` or `pending_manual_extraction`.

Successful structural conversion produces only `pending_review` patch evidence.
It cannot mark coverage current, edit a catalog, create a template, sign a
package, or change a recommendation.

## Proposed implementation

The implementation contract should be limited to:

1. `desktop-app/src/dpslab/blizzard_patch_notes_extractor.py`;
2. `desktop-app/tests/test_blizzard_patch_notes_extractor.py`;
3. `knowledge/schemas/blizzard_patch_notes_extraction_0_1.json`;
4. `knowledge/fixtures/blizzard_patch_notes_synthetic_0_1.html`;
5. `knowledge/snapshots/blizzard_patch_notes_extraction_synthetic_0_1.json`;
6. `docs/BLIZZARD_PATCH_NOTES_EXTRACTOR.md`;
7. `docs/NEXT_TASK.md`.

Fixtures must be wholly synthetic and must not copy Blizzard wording or page
markup. Tests should mutate receipt hashes, byte counts, nesting, tag sets,
subjects, values, units, citations, build tokens, and parser limits. No test may
access the network or a real captured body.
