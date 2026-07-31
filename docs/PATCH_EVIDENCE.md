# Patch evidence intake 0.1

This boundary validates already captured, structured patch or hotfix evidence.
It does not browse, scrape, call a network service, parse prose, or publish a
recommendation. Source-specific acquisition remains a separate future adapter.

The immutable evidence record keeps source identity, timestamps, licensing and
authenticity classifications, Retail build/interface bounds, typed assertions,
citations, and a canonical SHA-256. Closed fields and deterministic ordering
make accidental semantic expansion visible.

The only outcomes are `no_relevant_change`, `pending_review`,
`coverage_invalidated`, and `evidence_unavailable`. `pending_review` is a
quarantine state, never approval. Ambiguous assertions, unknown parameter
families, incompatible builds, and historical-only evidence fail closed.

Historical records are intentionally retained. They may support explicit
build-to-build comparison, regression analysis, audit, and rollback, but they
cannot generate a current candidate. Real data acquisition, license review,
catalog mutation, signing, network updates, and publication require separate
work packages.
