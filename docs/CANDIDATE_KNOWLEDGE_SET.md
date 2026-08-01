# Candidate knowledge-set application 0.1

This pure boundary creates an unpublished candidate envelope, candidate
catalog, and single-use receipt in memory. It performs no filesystem access.

A closed physical policy translates proposal fields to exact synthetic
guidance statement positions and before/after text keys. Unknown operations,
paths, or stale before-values fail closed. The source envelope and catalog are
preserved unchanged.

The candidate catalog retains the source entry and adds a pending-review
successor. The candidate envelope remains unsigned and records proposal and
review provenance. The receipt binds every source and candidate hash while
marking consumption as pending a later durable transaction.

This output is not durable application, approval, signature, publication, or
recommendation selection.

## Transactional persistence

`candidate_knowledge_store` can persist an already validated candidate set as
one immutable generation under the declared single-writer model. Envelope,
catalog, receipt, and commit manifest are staged and rehashed before an atomic
`current.json` marker makes the generation visible. The commit manifest, not a
mutation of the original receipt, records durable single-use consumption.

Readers accept only canonical files whose hashes agree with both the commit
manifest and visibility marker. Exact replay is idempotent; divergent reuse of
the proposal or decision fails closed. An interrupted staging operation cannot
replace the previously visible generation. This boundary still does not
approve, sign, publish, select, or distribute guidance.

## Human review decision

`candidate_knowledge_review` creates a pure immutable decision bound to the
exact visibility marker, commit manifest, candidate artifacts, receipt, and
source hashes. Approval requires explicit currentness, applicability, complete
source coverage, role safety, no-automation confirmation, and a human
attestation identifier. Version 0.1 records this attestation and a content hash;
it does not claim a cryptographic reviewer signature.

An approved review makes only that exact generation eligible for a later
publication transaction. Rejection is also immutable. Neither outcome edits
the candidate generation, changes the visible marker, activates catalog
content, packages the addon, or distributes guidance.

## Unsigned release bundle

`candidate_release_bundle` builds an internal release-candidate copy from one
eligible human review. Only the reviewed pending entry is promoted in that
copy; its source entry is preserved without inferred deprecation. The manifest
binds the durable generation, review, compatibility bounds, envelope, and
catalog bytes.

The bundle remains `signature_pending` and the envelope remains unsigned. It
is not an active catalog, distributable addon payload, desktop update, or
published recommendation. Signing and publication require later transactions
that bind the exact manifest hash and separately managed credentials.

## Detached release-signature verification

`release_signing` signs the exact canonical manifest bytes through an external
signer callback and verifies detached Ed25519 signatures against a public-key
trust registry. The registry is closed, content-hashed, time-bounded, and
fail-closed for unknown, revoked, malformed, or incorrectly rotated keys.

The repository contains only a clearly identified synthetic public key for
tests. It contains no private key and provides no production-key storage.
A valid signature makes the exact candidate release eligible for a later
publication decision; it does not publish, activate, distribute, or select it.
