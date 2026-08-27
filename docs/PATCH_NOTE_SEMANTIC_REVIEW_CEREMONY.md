# Patch Note Semantic Review Ceremony 0.1

## Purpose

Define one attended observation in which Daniel may classify the three neutral
slots after seeing transient, local-only evidence. The ceremony produces only
a signed-off decision record; it does not preserve source content.

## Readiness

Before display, the operator must verify the official-source receipt, content
hash, structural-slot report hash, exact three-slot topology, reviewer identity,
and a single-use ceremony identifier. Any mismatch stops before display.

## Transient display

The future launcher may show one slot at a time in a visible local window. It
must clearly show slot identifier and the closed role choices. Content exists
only in memory for the current choice and must be erased before advancing.
Copy, export, logging, screenshots, browser cache reuse, diagnostics containing
content, and unattended defaults are forbidden.

Daniel may choose `unknown` or `rejected` at every step. The launcher must not
suggest a role from path position, text length, markup depth, or prior choices.
Closing the window, timeout, source change, or incomplete review yields no
approved mapping.

## Output and limits

The only permitted durable output is a semantic review record validated by
`patch_note_semantic_slot_review_0_1`: hashes and identifiers, reviewer and UTC
timestamp, closed role and reason codes, status, and integrity hash. No source
characters, HTML, attributes, URLs, facts, selectors, or recommendations may
appear in it.

One real attended execution requires a later explicit confirmation immediately
before display. Implementation, synthetic tests, commit, and publication do not
authorize that execution.

## Synthetic window boundary

The first visible adapter is restricted to synthetic content. Its title and
body must identify synthetic mode prominently. It presents one slot, requires
an explicit role and reason selection, and returns no decision on close or
cancel. Automated tests validate its presentation contract without starting a
native window; native usability remains a separate human confirmation.
