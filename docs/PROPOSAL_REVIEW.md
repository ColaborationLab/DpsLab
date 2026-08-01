# Proposal review decision 0.1

A review decision is immutable evidence of a human decision about one exact
proposal. It binds proposal, catalog, and evidence hashes plus reviewer,
authority reference, UTC time, outcome, reason codes, acknowledged limitations,
and its own canonical SHA-256.

Approval is eligible only inside the proposal validity window. Caller-supplied
consumption sets prevent replay of decision IDs or proposal hashes. Rejection
is preserved as a distinct outcome.

An eligible decision is not catalog application, publication, signing, or
recommendation selection. The later durable application transaction must
revalidate every binding and record single-use consumption atomically.
