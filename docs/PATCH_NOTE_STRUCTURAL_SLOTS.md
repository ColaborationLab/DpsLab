# Patch Note Structural Slots 0.1

## Purpose

The attended text-topology observation found three stable visible-text paths,
each occurring once in all twelve articles. This document defines a neutral
classification boundary for those paths without assigning meaning or retaining
text.

## Neutral slots

The candidate classifier may recognize only these exact signatures:

- `slot.path_01`: `article` followed by five `div` elements;
- `slot.path_02`: `article` followed by eight `div` elements;
- `slot.path_03`: `article`, four `div` elements, then `p`.

The identifiers encode no semantic claim. In particular, they do not mean
title, date, summary, body, class, specialization, ability, or balance change.

## Contract

Input is a validated `text_topology_observed_pending_review` report. Output may
contain only the source report hash, the three slot identifiers, exact tag
paths, occurrence counts, and aggregate length metrics. Missing, additional,
duplicated, reordered, or count-inconsistent paths fail closed.

Output remains `structural_slots_pending_review`. It cannot authorize text
capture, selectors, semantic mapping, facts, evidence, catalogs, templates, or
recommendations. Implementation and tests use synthetic reports only.
