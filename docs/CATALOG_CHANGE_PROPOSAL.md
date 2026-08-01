# Catalog change proposal 0.1

This pure boundary converts validated current patch evidence into an immutable,
content-addressed proposal. It validates but never opens or writes a catalog
path. Every proposal binds exact catalog and evidence hashes, source revision,
build/interface range, subject, citations, limitations, creation time, and
expiry.

The review state is fixed to `pending_review`; approval fields must remain
empty. Historical or ambiguous evidence, unknown families, conflicting
operations, and missing safety evidence fail closed. Tank and healer damage
changes require matching safety-family evidence.

A proposal is not a recommendation, approval, catalog mutation, signature, or
release. Those remain separate transactions that must bind the exact proposal
hash.
