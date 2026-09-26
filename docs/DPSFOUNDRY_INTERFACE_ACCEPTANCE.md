# DpsFoundry Core interface acceptance — A+B

## Astra visual sample — pending human acceptance

Direct implementation supersedes Terra delegation. Home now uses original
line icons, legible shared foregrounds, compact typography, gradient steel
surfaces and a dashboard grid. Actual comparison data supplies its results and
the preferred build supplies its weights. Empty states contain no invented DPS.
Reviewed rendered screenshots with Segoe UI: 1240×800 and 1060×700, scrollable
at the smaller size. Review examples are isolated in ignored build/ files.
No claim of full Foundry/Core/Link acceptance: remaining pages, native titlebar,
Windows scaling and in-game approval remain pending.

## Current status — 2026-09-19 visual review

NOT visually accepted. Daniel's screenshot confirms navigation exists but the
Foundry direction is not achieved: black headings on dark surfaces, absent
iconography, weak typography, flat repeated panels and excessive empty space.
The sections below describe structural work only, not completed A+B acceptance.
Use DPSFOUNDRY_INTERFACE_TERRA_PLAN.md for the revised next delivery: a rendered
Qt visual sample with readable fonts, empty/populated states, menus and dialogs.
Foundry alone receives full polish this cycle; other themes prove token reuse.
Automated tests and offscreen captures with missing glyphs do not prove visual
quality. No objective closure or percentage of visual completion is claimed.

## Delivered visible flow

A player can open **DpsFoundry Core**, move between Setup, Home, Character,
Simulation, Compare, Recommendations, Link / Sync, and Settings, then return
to the existing Simulation controls without losing the in-memory export or
loadout selection.

1. In **Setup**, choose the existing local/bundled requirement and detect or
   paste a Link export.
2. **Home** changes from an explicit empty state to ready and directs the
   player to a supported simulation.
3. In **Character**, save or reopen the local profile.
4. In **Simulation**, select one to four existing supported loadouts and use
   the already implemented background runner. This delivery does not run it.
5. After a result, **Compare** and **Recommendations** expose a successful or
   ready state and direct the player to the existing table, while **Link /
   Sync** states that weights require an explicit post-simulation export.

## Acceptance evidence

| Check | Evidence |
| --- | --- |
| One architecture and eight routes | `QtLoadoutWorkspace._pages` and navigation test |
| Foundry default and four equivalent themes | semantic `THEMES`; UI test saves/loads a theme |
| Setup → export → Simulation is understandable | UI test loads a controlled export and retains three loadouts after navigation |
| Textual states | `StatePanel` validates all seven required states |
| Existing service boundary preserved | the runner, parser, profile model and Link transport were not edited |
| No fictitious real-time sync | Link page describes local export/import and explicit next action |

## Verification to run

From `desktop-app` with the packaged Python:

```powershell
$env:QT_QPA_PLATFORM='offscreen'; $env:PYTHONPATH='src'
& '..\build\installer-py313\Scripts\python.exe' -m unittest tests.test_qt_loadout_ui -v
& '..\build\installer-py313\Scripts\python.exe' -m unittest discover -s tests -v
```

No SimulationCraft execution is part of these checks. A real in-game Link
visual pass, actual runner authorization, and the later Link panel/theme
delivery remain outside A+B.
