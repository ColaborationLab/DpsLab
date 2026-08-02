# Patch Note Semantic Slot Review 0.1

## Purpose

Define a human-review boundary that may assign a constrained semantic role to
each neutral structural slot. Metrics, path depth, ordering, repetition, or
prior conversation cannot establish meaning.

## Allowed review outcomes

Each `slot.path_*` must receive exactly one of these outcomes:

- `article_title`;
- `publication_label`;
- `article_body`;
- `non_content_metadata`;
- `unknown`;
- `rejected`.

The vocabulary describes page structure only. It does not identify a class,
specialization, ability, numeric change, recommendation, or balance fact.

## Human attestation

A future attended review must record the reviewer, observation timestamp,
official-source receipt identifier and hash, structural-slot report identifier
and hash, one decision per slot, and a short reason selected from a closed
reason-code vocabulary. At least one `unknown` or `rejected` outcome is valid;
the process must never force complete semantic coverage.

No HTML, text, attribute value, URL, JSON value, screenshot, or page fragment
may be stored by this boundary. Review evidence records decisions and hashes
only. Conflicting reviewers, incomplete coverage, altered source bindings,
unknown roles, duplicate role assignments, or stale observations remain
`semantic_slot_review_pending` and fail closed.

## Downstream boundary

An approved structural-role mapping would only permit a later, separately
authorized design for transient fact extraction. It cannot itself approve a
selector, retain content, update a catalog, claim currentness, or generate a
recommendation.
