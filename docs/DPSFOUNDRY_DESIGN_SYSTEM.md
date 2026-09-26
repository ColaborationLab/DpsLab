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
| Setup | choose bundled/local SimulationCraft and detect or paste Link export | existing local controls |
| Home | show the next player action | controlled state derived from loaded export/result |
| Character | save/open the active local profile | existing profile controls |
| Simulation | select supported loadouts and start the existing runner | existing service-backed workspace |
| Compare | explain where the selected result is available | controlled state; existing comparison table stays in Simulation |
| Recommendations | distinguish simulated guidance from universal rules | controlled state from comparison result |
| Link / Sync | explain local file exchange and its next step | controlled state; no live connection is claimed |
| Settings | select an appearance-only theme | local theme preference |

## State contract

Every connected surface can render `loading`, `ready`, `empty`,
`unavailable`, `error`, `blocked`, or `success`. Each maps to a textual title
and instruction in `StatePanel`; an invalid state is rejected. Class/spec data
belongs in reserved cards or slots, not in a specialization-specific shell.

Guide remains a future information boundary only. This system does not add
combat capture, a trainer, a simulator, or new class/spec data.
