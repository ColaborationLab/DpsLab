# Structured patch format adapter 0.1

This pure adapter converts one closed, synthetic JSON dialect into the existing
`patch_evidence` quarantine record. It does not parse HTML, Markdown, prose, or
real patch notes and performs no network activity.

Semantic kinds are mapped to canonical parameter families only through an
explicit caller-supplied mapping. Unknown or ambiguous kinds, conflicting
targets, duplicate IDs, malformed ranges, and ineffective operations fail
closed. Input order does not affect canonical output.

The generated record retains source, build, subject, citation, lifecycle, and
content lineage and is validated by `patch_evidence`. Conversion does not
approve evidence, mutate a catalog, select guidance, or publish an update.
