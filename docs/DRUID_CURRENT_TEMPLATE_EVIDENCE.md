# Druid current-template evidence 0.1

This is a synthetic, in-memory gate. It does not acquire sources, observe the
game client, retain a receipt, select catalog content, or present advice.

`review_eligible` means only that four supplied synthetic receipts agree:

1. a reviewed registry receipt covering the supplied build and interface;
2. a reviewed semantic mapping whose exact policy specialization and role
   agree;
3. a reviewed primary-source applicability receipt covering that same range;
   and
4. a closed template receipt whose exact role uses the required safety-first
   ordering.

Every receipt must be explicitly synthetic and carry bounded identifiers and
SHA-256-shaped fingerprints. A missing, stale, malformed, non-synthetic,
unreviewed, conflicting, or incompatible receipt returns
`evidence_unavailable`. The decision retains only a bounded template identifier
and the existing semantic role policy; it never retains source text, URLs,
display names, character identifiers, specialization IDs, spells, items,
statistics, rotations, or balance claims.

This gate is deliberately insufficient to make Advisor available. Real
evidence acquisition, human approval, current-content catalogs, game capture,
and user-facing presentation each remain separately governed work.
