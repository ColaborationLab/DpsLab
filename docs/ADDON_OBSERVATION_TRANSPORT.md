# DpsLab Synthetic Addon Observation Transport 0.1

This block defines a deliberately narrow, local and non-executing rehearsal of
the future addon-to-desktop observation channel. It does not declare a real
SavedVariables entry and it does not collect character or combat data.

The only accepted transport is one complete assignment:

`DpsLabObservationExport = "<lowercase hexadecimal>"`

The hexadecimal content decodes to at most 4096 bytes of canonical UTF-8 JSON.
The JSON must use the closed synthetic observation schema 0.1, end in exactly
one LF, declare its exact byte count, and pass identity, compatibility,
subject, signal-total and safety validation. Duplicate keys, non-finite
numbers, alternate whitespace, additional assignments, Lua expressions,
uppercase hexadecimal, unknown fields and partial documents fail closed.

Hexadecimal is intentional: its alphabet needs no Lua string escapes and lets
the desktop recognize a minimal grammar without parsing or evaluating general
Lua. The parser accepts bytes supplied by a caller and has no filesystem,
process, network or persistence capability.

The synthetic fixture contains no name, realm, equipment, talents, account
identifier or real measurements. A future real channel requires separate
contracts for addon-side serialization, an explicit SavedVariables declaration,
user-selected file acquisition, privacy review, WoW-closed preflight and
adversarial resource tests. This block cannot make guidance actionable.

The addon-side synthetic serializer now rehearses the same representation. It
uses a schema-specific fixed key order, validates the complete fixture before
serialization, verifies the declared byte count, emits two lowercase hex
digits per payload byte, and exposes the result only as an in-memory synthetic
value. It is not a general JSON or Lua serializer and is not persisted.

## Manual persistence design boundary

The first eligible persistence block is intentionally synthetic and opt-in.
It may declare exactly one account-wide SavedVariables name,
`DpsLabObservationExport`, and may expose only two exact player commands:

- `/dpslab export synthetic` copies the already validated in-memory synthetic
  transport string into that variable;
- `/dpslab export clear` assigns `nil` to remove the retained export.

The variable must remain absent by default. Addon load, login, reload, combat,
zone change, logout and update events may not create, refresh, repair or replace
it. A pre-existing unknown value must never be adopted as valid or overwritten
automatically. The command may report only a short status and reason; it must
never print the payload, character information or a filesystem path.

WoW, not DpsLab, decides when the declared variable is flushed to disk. The
addon must not claim that the file was written merely because the in-memory
assignment succeeded. Retention lasts until the player issues the clear
command, resets addon data, or removes it through normal WoW controls. Clearing
must be idempotent and must not affect guidance, configuration or other addons.

This synthetic persistence does not authorize combat observation, event
registration, timers, frames, game APIs, names, realms, equipment, talents,
statistics, automatic export, desktop file discovery or import. Any future
real observation requires a separate privacy and minimization decision.

### Closed implementation scope

A future implementation may change only these exact paths:

- `addon/DpsLab/DpsLab.toc`;
- `addon/DpsLab/DpsLab.lua`;
- `tools/tests/test_addon_synthetic_renderer.py`;
- `tools/tests/test_addon_synthetic_persistence.py`;
- `docs/ADDON_OBSERVATION_TRANSPORT.md`;
- `docs/NEXT_TASK.md`.

It must prove: one exact SavedVariables name; no load-time assignment; exact
commands; serializer success required before retention; unknown command and
invalid serializer states leave the variable unchanged; clear is idempotent;
the payload is never printed; no event, frame, network or gameplay surface is
introduced. Publication still requires the locked remote functional suite.
