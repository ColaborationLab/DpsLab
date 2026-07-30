# Knowledge Envelope 0.1

`knowledge_envelope_0_1` is a closed, versioned exchange format for guidance
that can be validated before it reaches any future addon or desktop consumer.
It is not an execution format and does not authorize live recommendations.

## Scope

Version 0.1 supports Retail envelopes with explicit build, interface, subject,
level, race and content-context bounds. Unknown fields, products, ranges,
statement types and evidence tiers are rejected.

The three evidence tiers are:

- `static_fallback_template`: conservative synthetic or curated fallback;
- `imported_analytical_evidence`: externally produced evidence with method,
  run count, confidence interval and source hashes;
- `character_observation`: a reserved shape for bounded observations.

Static fallback data cannot claim analytical runs or confidence intervals.
The included fixture is synthetic contract evidence only. It is not balance
data, a personalized simulation, a best-in-slot list or a live recommendation.

## Canonical representation and integrity

Envelope bytes use UTF-8 JSON, lexicographically sorted object keys, compact
separators, no non-finite numbers and exactly one trailing LF.

`integrity.payload_sha256` is calculated from that canonical representation
after omitting exactly these two members:

- `integrity.payload_sha256`;
- `integrity.signature`.

`integrity.signature_algorithm` and `integrity.publisher_key_id` remain in the
hashed projection. Any implementation that removes additional members or
includes either omitted member is incompatible with this contract.

Version 0.1 deliberately uses `signature_algorithm: placeholder-none` and a
null signature. A non-null signature or another algorithm fails validation.
Real key management and cryptographic signing are outside this block.

## Validation and selection

Validation checks the closed field families, scalar types, ordered ranges,
sequential statement order, tokenized text identifiers, provenance
requirements, safety declarations and payload hash.

Selection is fail-closed. Guidance is available only when product, build,
interface, class, specialization, level, content context, optional race and
expiry all match. Character-bound envelopes additionally require an exact
fingerprint match. External context fields are type-checked before comparison;
booleans are never accepted as numeric identifiers. The reserved
`character_observation` tier cannot be selected in version 0.1. Unknown or
incompatible state returns
`guidance_unavailable` with no fallback to the newest package.

Guidance statements carry text keys and bounded token lists. They contain no
scripts, commands, addon behavior or arbitrary executable payloads.

## Explicit exclusions

This schema does not:

- execute SimulationCraft or any comparison;
- create runs or comparison results;
- read the network, patch notes, accounts, secrets or real signing keys;
- integrate an addon, UI or live recommendation path;
- define publishing, update distribution or automatic adoption;
- authorize any later implementation block.

The authoritative declarative schema is
`knowledge/schemas/knowledge_envelope_0_1.json`. The synthetic fixture is
`knowledge/fixtures/static_fallback_template_synthetic_0_1.json`.
