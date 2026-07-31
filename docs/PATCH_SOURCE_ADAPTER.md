# First-party patch source adapter 0.1

This component is a pure capture boundary. It validates a synthetic source
registry and injected response objects; it performs no DNS lookup, HTTP call,
browser access, scraping, or interpretation of real patch notes.

The allowlist binds source identity, canonical and redirect hosts, accepted
media types, byte limits, locale policy, and review ownership. Successful bytes
are content-addressed with SHA-256. A duplicate is reported without replacing
known-good evidence. A `not_modified` response may reuse prior evidence only
when a previously verified hash and matching cache validator exist.

Unknown sources, hosts, redirects, response statuses, formats, oversized or
empty bodies, partial transfers, and malformed prior records fail closed as
`evidence_unavailable`. Valid new bytes become `captured_pending_review`; they
are not parsed, approved, or published.

Structured evidence handoff delegates to `patch_evidence`, whose outcomes are
limited to quarantine states. Real source acquisition, format-specific parsing,
licensing review, catalog mutation, signatures, updates, and recommendations
remain separate future work.
