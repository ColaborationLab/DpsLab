# Blizzard Patch Notes Text Topology Probe 0.1

## Boundary

This probe locates text-bearing topology without retaining text. For every
non-whitespace text node beneath the nearest `article`, it records only the
normalized tag path, occurrence count, aggregate character count, and maximum
single-node character count.

`script`, `style`, `noscript`, and `template` subtrees are excluded and counted
only as excluded nodes. Text, words, character hashes, attribute names or
values, URLs, markup, and semantic labels never enter the report.

The input must match one validated `captured_pending_review` receipt. Invalid
UTF-8, malformed nesting, no visible article text, or resource-limit breaches
fail closed. Output remains `text_topology_observed_pending_review` and cannot
approve selectors, extract facts, or change catalogs or recommendations.

Implementation and tests use invented HTML only. A future live observation
requires a new one-request attended authorization.
