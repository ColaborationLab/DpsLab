# DpsLab Minimal Real Addon Observation 0.1 — Design Only

## Status and objective

This document is a closed design. It does not authorize addon code, WoW API
access, SavedVariables writes, a live character capture, or a desktop parser
change.

The first real observation is one manually requested identity snapshot used
only to decide whether local guidance can apply to the current character. It
is not a combat analyzer, simulator input, character archive, telemetry event,
or recommendation approval.

## Consent and lifecycle

The only candidate entry is the exact player command
`/dpslab export identity`. Executing that command is the capture request. Addon
load, login, specialization change, equipment change, talent change, zone
change, group change, combat state, reload and logout must not capture,
refresh, repair or replace the export.

The command must first collect all allowed values into memory, normalize and
validate the complete candidate, serialize it canonically, verify its size,
and only then replace `DpsLabObservationExport`. Any unavailable, ambiguous or
invalid value preserves the prior export and reports only a bounded reason.
`/dpslab export clear` remains the sole deletion action and is idempotent. The
single SavedVariable stores only the most recent successful manual export; no
history, database, secondary variable or automatic migration is permitted.

## Closed schema

The future canonical payload has exactly these families and fields:

- `schema_version`: exact value `0.1`;
- `observation_type`: exact value `character_identity_snapshot`;
- `compatibility`: `wow_product=retail`, integer `build`, integer
  `interface_version`;
- `subject`: integer `class_id`, integer `specialization_id`, normalized
  `role`, integer `level`, integer `race_id`;
- `capture`: integer UTC epoch `captured_at`, exact mode `manual_command`;
- `safety`: `contains_character_data=true`, `contains_direct_identifiers=false`,
  `actionable=false`, `executable=false`, `no_automation=true`.

All integers reject booleans, fractions and values outside declared bounds.
Role accepts only `damage`, `tank` or `healer`. Unknown build, interface,
class, specialization, role, level, race or time fails closed. A future
implementation must verify the precise WoW API allowlist against the installed
Retail build through a separate attended, metadata-only probe before using it.

## Privacy boundary

The class, specialization, role, level and race tuple is treated as local
character data even though it contains no direct identifier. It remains local,
is never logged, and is not transmitted. The design forbids character name,
realm, GUID, Battle.net or WoW account, guild, group, location, friends,
contacts, chat, screenshots and any stable derived fingerprint.

It also forbids equipment, item IDs, item levels, enchants, gems, talents,
loadouts, stats, action bars, cooldowns, auras, currencies, quests,
achievements, combat-log events, damage, healing, incoming damage and encounter
history. Each future category requires a separate minimization and consent
decision. Race is included because applicability can differ by race; it may
not be combined into a durable identity key.

## Transport and desktop boundary

The payload uses deterministic canonical UTF-8 JSON, lowercase hexadecimal and
the existing one-assignment transport grammar. It remains bounded to 4096 JSON
bytes and 8192 hexadecimal characters. The real payload and existing synthetic
payload are distinct schemas selected by the exact `observation_type`; neither
may be silently interpreted as the other.

The desktop must add an independent strict parser and immutable typed result.
It may retain the parsed snapshot only in memory for an explicit import
attempt. It must not store raw bytes, general Lua, source paths, account folder
names or a history of character snapshots. Compatibility or subject mismatch
produces guidance unavailable, never a nearest-template guess.

## Failure and security behavior

- No partial or failed candidate replaces a valid prior export.
- No error includes a field value, path, character detail or exception text.
- No API value becomes code, a command, a module name or executable Lua.
- No frame, event registration, timer, polling, network, process launch,
  telemetry or automatic retry is introduced.
- The snapshot does not authorize a recommendation, simulation or comparison.
- Clearing affects only `DpsLabObservationExport`.

## Candidate implementation routes

A later implementation contract may consider only:

- `addon/DpsLab/CharacterIdentityObservation.lua`;
- `addon/DpsLab/DpsLab.lua`;
- `addon/DpsLab/DpsLab.toc`;
- `tools/tests/test_addon_character_identity_observation.py`;
- `desktop-app/src/dpslab/addon_character_identity_transport.py`;
- `desktop-app/tests/test_addon_character_identity_transport.py`;
- `docs/ADDON_REAL_OBSERVATION.md`;
- `docs/NEXT_TASK.md`.

Before implementation, human review must confirm the field set, manual command,
single-value replacement policy, privacy classification, exact API allowlist,
test fixtures and eight-route maximum. Approval of this design is not approval
to capture a real character.
