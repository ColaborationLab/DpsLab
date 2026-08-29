# DpsLab Addon MVP Architecture 0.1

## Status and purpose

`design_only`. No Lua, TOC, SavedVariables parser, game API call, release
package, data package, or desktop exchange is implemented by this document.

The MVP is a local, read-only guidance surface inside the WoW addon sandbox. It
helps the player inspect already validated, compatible declarative guidance; it
does not play the character, choose actions automatically, simulate, optimize,
contact the network, or collect telemetry.

## MVP operating modes

| Mode | Permitted input | Player-visible result |
| --- | --- | --- |
| `static_fallback` | bundled, approved, compatible static template | clearly labelled general guidance and limitations |
| `desktop_exchange` | optional versioned payload that passes every validation gate | clearly labelled imported guidance and provenance summary |
| `unavailable` | absent, expired, synthetic, pending-review, invalid, incompatible, or untrusted input | no recommendation; explain why it is unavailable |

The addon must start and remain usable in `unavailable` mode. The desktop
application is optional; its absence must never impair WoW or make the addon
retry, scan local files, or prompt for credentials.

## Data boundary and exchange

All addon inputs are declarative data with a closed schema and finite limits.
They can contain text keys, identifiers, applicability ranges, freshness,
provenance references, warnings, and ordered non-executable guidance
statements. They cannot contain Lua source, arbitrary expressions, callbacks,
URLs to retrieve, commands, binary data, credentials, or hidden fields.

A future desktop exchange may use a single explicitly selected SavedVariables
payload only after separate authorization. Both sides must validate:

1. exact schema and protocol version;
2. byte, nesting, item-count, string-length, and statement-count limits;
3. WoW product, build, interface, class, specialization, role, and context
   applicability;
4. payload hash, declared publisher identity, freshness, and review state;
5. no unknown fields, executable-looking content, or unsupported encoding.

Any failed gate discards the payload for guidance purposes and enters
`unavailable`; it must not partially merge, repair, or retain the data as a
recommendation. The addon may display only a non-sensitive failure category.

## Player-control and combat boundary

The MVP may show information only after ordinary player interaction with the
addon UI. It may not generate input, issue protected actions, cast spells,
target units, move the character, accept quests, send chat messages, inspect
other players, or act during combat in place of the user.

It has no network client, browser, webhook, account link, advertisement,
donation control, purchase, tracking pixel, or telemetry. It stores no token,
key, password, recovery material, or payment data. Any future external update
or desktop transfer is user-initiated, versioned, local, and separately
approved.

## Role-aware presentation

The initial view is intentionally small:

1. **Readiness:** active mode, data validity, build/interface compatibility,
   freshness, and known limitations.
2. **Guidance:** ordered, declarative statements only when the selected data is
   approved and applicable.
3. **Evidence:** non-sensitive template identity, version, provenance IDs, and
   warnings.

Damage guidance is always contextual. Tank guidance must put survival,
mitigation, threat, incoming-damage context, and obligations ahead of DPS.
Healer guidance must put ally survival, healing, dispels, emergency capacity,
and resource safety ahead of DPS. If that role safety context is absent, the
MVP shows no DPS direction for that role.

## Required safe degradation

The addon must visibly produce `unavailable`—rather than a fallback claim—when
any of the following applies: unknown class/specification; unsupported build;
expired evidence; pending review; synthetic-only data; missing provenance;
invalid exchange; source coverage incomplete; or role-safety requirements
unmet. Status cannot rely only on colour, and it must remain readable with
keyboard navigation and scalable text.

## Future implementation boundary

A separate implementation contract may introduce only synthetic Lua-compatible
fixtures and a deterministic local renderer. It must contain negative tests
for schema rejection, size limits, unknown fields, incompatible build, expired
data, role safety, combat restriction, and no-data startup. It may not use real
game facts, contact WoW or external services, parse a real SavedVariables file,
create a public repository, or make a release.
