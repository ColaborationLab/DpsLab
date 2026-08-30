# Druid vertical slice

## Product question

The first vertical slice asks whether DpsLab can interpret the same kind of
character context differently for every combat role while remaining a
performance assistant rather than a class guide. Druid is the prototype
because Balance, Feral, Guardian and Restoration cover ranged damage, melee
damage, tanking and healing in one class.

## Role-context contract 0.1

The role context is a semantic ordering of objectives, not a recommendation:

| Specialization | Role | Primary objectives | Secondary objective |
| --- | --- | --- | --- |
| Balance | damage | damage output | none |
| Feral | damage | damage output | none |
| Guardian | tank | survival, active mitigation, threat stability | damage output |
| Restoration | healer | ally survival, healing stability, dispel readiness, emergency capacity | damage output |

Encounter obligations and character survival are hard constraints for every
role. A damage recommendation can never silently override them. Guardian
damage is subordinate to tank safety and stability. Restoration damage is
subordinate to group safety and healing capacity.

Only the exact lowercase semantic specialization tokens `balance`, `feral`,
`guardian` and `restoration` are recognized in this block. The observed role
must exactly match the specialization role. Unknown, differently normalized
or mismatched input produces `context_unavailable`; there is no fuzzy match,
role guess or nearest-template fallback.

## Deliberate boundary

This block does not contain specialization IDs, spells, rotations, talents,
equipment, statistics, coefficients, build ranges or patch facts. It does not
consume a character observation, select a catalog entry or emit guidance. A
later block must bind verified identity to this policy, and another must bind
current, approved knowledge before any recommendation becomes available.

DpsLab may eventually explain why an objective has priority and how a current
recommendation serves it. It must not present a fixed sequence as a universal
guide to playing the class or specialization.

## Identity-context binding 0.1

The next internal boundary accepts the already validated immutable character
identity and an injected Druid registry. The registry must contain exactly one
unique binding for each of Balance, Feral, Guardian and Restoration. Class,
specialization and role must all match exactly before the semantic policy is
returned.

The registry is injected rather than hardcoded because class and
specialization identifiers are game facts. Tests use deliberately synthetic
bounded values. A later knowledge-evidence block must establish the current
real mapping and its review status before a real observation can cross this
boundary.

The binding result contains only `status`, a bounded static `reason`, and the
semantic role policy. It does not retain or expose build, interface, class,
specialization ID, level, race or capture time. Invalid registries, forged
observations, class mismatch, unmapped specialization and role mismatch all
produce `context_unavailable`.
