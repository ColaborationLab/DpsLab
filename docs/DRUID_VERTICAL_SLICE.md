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

## Synthetic guidance coordination 0.1

The next boundary joins the validated identity-context result to the existing
governed static-template catalog. It creates a compatibility context in memory,
asks the catalog for an exact eligible entry, and returns only the semantic
role policy, entry identifier, and bounded guidance statements. It retains no
character identity and performs no acquisition, persistence, network access,
simulation, or game-fact lookup.

Identity and role validation happen before knowledge selection. Invalid
identity therefore cannot probe the catalog. Pending, incomplete, stale,
ambiguous, mismatched, unapproved, or malformed knowledge returns
`guidance_unavailable`; it is never replaced by the nearest template. A valid
role policy may remain visible when knowledge is unavailable, but its statement
set is empty and it is not presented as a recommendation.

Tests use the pre-existing synthetic damage fixture and an injected synthetic
Druid registry. They do not establish live Druid identifiers, current balance
facts, spells, rotations, talents, equipment, or real recommendations. Current
knowledge acquisition and approval remain separate future work.

## Attended specialization-registry observation 0.1

The next product-facing evidence boundary asks the live Retail client for the
current player's class identifier and the four specialization identifiers and
roles exposed for that class. Capture occurs only after the player types
`/dpslab export specialization-registry`. It uses the same single WoW-managed
SavedVariable as the other mutually exclusive manual exports; it does not add
a watcher, timer, event handler, network request, or historical store.

The captured registry contains build, interface, class identifier, four unique
specialization identifiers, normalized roles and capture time. It deliberately
omits specialization names, character name, realm, account, GUID, equipment,
talents and gameplay events. The shape must be exactly two damage roles, one
tank and one healer role. Any other shape is unavailable rather than guessed.

The application decodes the assignment as bounded lowercase hex and canonical
JSON without evaluating Lua. Acquisition remains blocked while WoW is running,
and the public import result does not expose raw bytes or a filesystem path.
The immutable result is evidence only: it does not assert that the class is a
Druid, bind semantic names to specialization identifiers, approve a catalog,
or enable guidance. Those transitions require an attended observation followed
by a separate human review and current-source evidence.
