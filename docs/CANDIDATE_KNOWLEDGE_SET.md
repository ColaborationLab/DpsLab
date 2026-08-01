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
