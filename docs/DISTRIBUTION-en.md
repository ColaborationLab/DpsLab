# DpsLab — Windows distribution guide

## Package and installation

The beta installer includes DpsFoundry Core, simc.exe, the DpsLabAddon folder
and SIMULATIONCRAFT_NOTICE.txt. A separate SimulationCraft
installation or external simc.exe path is not required.

1. Run DpsFoundry-Core-*-Setup.exe and accept the proposed user folder.
2. Copy DpsLabAddon from the installed folder to World of Warcraft/_retail_/Interface/AddOns/DpsLab.
3. Close WoW if an older addon is installed and replace its contents.
4. Run DpsFoundry Core and choose Auto, ES, EN or PT-BR.
5. In WoW run /dpslab export app and confirm /reload.
6. In the app click Detect export, choose one to four builds and run it.
7. Save the profile when you want to retain character, gear, builds and results.

One build can be simulated as well; it has no relative delta. External strings
remain hypothetical simulations.

## Weights and scores

After a simulation produces weights, import them into the addon, open
/dpslab config and choose whether to replace current weights, keep them, or save
a copy before activating the new ones. Use /reload if requested and enable Show
item scores. Compatible profiles add scores to equipped, inventory and
comparative tooltips. (b) marks the generic beginner reference. Missing data is
shown as unavailable; zero is never fabricated.

## Languages, data and privacy

Auto follows esES/esMX for Spanish and ptBR for Brazilian Portuguese; other
locales use English. The preference is stored in
%LOCALAPPDATA%/DpsLab/language.json. Paths and profiles use separate files.
No network is required to detect exports or run SimC. Exports can contain a
character name, realm, gear, talents and builds; review them before sharing.

## Updates and troubleshooting

Close WoW and Core before replacing the addon or updating the installation. To
start without path or language preferences, remove only
%LOCALAPPDATA%/DpsLab/workspace_paths.json and language.json; this does not
delete saved character profiles. If the app does
not open, reinstall the complete package and keep _internal intact. If no export
is detected, install the matching addon version, run /reload and click Detect
export. If a score is missing, verify the compatible weight profile and enable
Show item scores. Incomplete builds and characters below max level are excluded.

## Beta feedback

Report issues or suggestions through [GitHub Issues](https://github.com/ColaborationLab/DpsLab/issues/new?title=Beta+feedback%3A+).
Do not post a character name, realm, or complete export unless it is essential.

SimulationCraft is distributed under GPL v3. See
SIMULATIONCRAFT_NOTICE.txt for the included binary SHA-256 and exact source revision.
