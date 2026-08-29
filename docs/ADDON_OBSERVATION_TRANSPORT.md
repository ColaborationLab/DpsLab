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
