# DpsFoundry design system 0.1

## Purpose

DpsFoundry Core uses one Qt Widgets shell for every supported class and
specialization. The default visual theme is **Foundry**: graphite surfaces,
dark steel panels, an orange action accent, and green reserved for confirmed
success or improvement. Theme selection changes presentation only.

The shell follows the player journey:

**analyze → decide → sync → play → refine**

It uses visible product names (`DpsFoundry Core` and `DpsFoundry Link`) while
retaining DpsLab package and transport identifiers for compatibility.

## Semantic tokens

`dpsfoundry_theme.py` owns the four token maps. Components use semantic QSS
roles rather than a theme colour name.

| Token role | Foundry use |
| --- | --- |
| root, panel, raised, input | charcoal workspace and tiered steel surfaces |
| primary, secondary, muted | readable data, supporting copy, low-priority context |
| accent, accent secondary | primary action and contained forge emphasis |
| success, warning, error, info | secondary status cues; each status also has text |
| border, focus | panel separation and keyboard focus |

The official theme ids are `arcane_vanguard`, `foundry`,
`runebound_command`, and `celestial_foundry`. They share the same geometry,
routes, data and behavior.

## Components and spacing

- Shell: top product bar, persistent left navigation, and one stacked content
  area.
- Cards: raised panel with one clear heading and a single primary action where
  applicable.
- Inputs, lists and tables: dark input surface, visible border and focused
  state.
- Status panel: title plus plain-language next step. It never relies only on
  colour.
- Tables: values remain absent/unavailable when the service has no value; no
  placeholder number is invented.
- Tooltips explain the existing action without exposing implementation detail
  in the normal flow.

Base layout margins are 10px around the shell and 18px within routes; cards and
sections use a 12px rhythm. The native layouts resize, wrap status copy, and
keep text readable under normal Qt/system accessibility scaling.

## Route contract

| Route | User-visible responsibility | Data source in this delivery |
| --- | --- | --- |
| Setup | reserved entry for guided onboarding refinement | no duplicate detection controls |
| Home | comparison summary, preferred weights and reference selection | current comparison; dashboard navigation refinement pending |
| Character | save/open/delete profile and show compact equipment | imported profile/equipment; neutral portrait/icon fallback |
| Simulation | detect/paste export, open profile, select builds and run | existing service-backed workspace; result cards |
| Compare | display comparison results and equipment cards | existing comparison; no invented item substitutions |
| Recommendations | numbered loadout alternatives with signed impact | existing comparison result, not new gear recommendations |
| Link / Sync | explain local file exchange and its next step | controlled state; no live connection is claimed |
| Settings | addon path, language, appearance and bundled motor status | existing local preferences; no SimC path prompt in packaged UI |

## Accepted refinements — 2026-09-26

Foundry uses the approved forged raster wordmark over continuous contextual
backgrounds. Navigation and build rows share selected/hover emphasis; hover
is weaker than selection. The primary Run Simulation action has restrained
emphasis. Status badges accompany text. Core points 1–4 are approved; points
5–6 remain open. This is not acceptance of every theme or all scaling settings.

Link uses LinkTheme.lua, the same emblem converted losslessly to TGA, dark
surfaces and amber focus/selection. Its circular minimap entry and compact
menu reuse existing actions. Configuration and weights are mutually exclusive
windows with a return path. See the current acceptance record, not the early
A+B plan, for approval status. No functional architecture is duplicated.

## State contract

Every connected surface can render `loading`, `ready`, `empty`,
`unavailable`, `error`, `blocked`, or `success`. Each maps to a textual title
and instruction in `StatePanel`; an invalid state is rejected. Class/spec data
belongs in reserved cards or slots, not in a specialization-specific shell.

Guide remains a future information boundary only. This system does not add
combat capture, a trainer, a simulator, or new class/spec data.
