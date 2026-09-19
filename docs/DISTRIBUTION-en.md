# DpsLab — Windows distribution guide

## Package and installation

The reduced package includes DpsLab.exe, its internal files, simc.exe, the
DpsLabAddon folder and SIMULATIONCRAFT_NOTICE.txt. A separate SimulationCraft
installation or external simc.exe path is not required.

1. Extract the complete ZIP to a writable local folder.
2. Copy DpsLabAddon to World of Warcraft/_retail_/Interface/AddOns/DpsLab.
3. Close WoW if an older addon is installed and replace its contents.
4. Run DpsLab.exe and choose Auto, ES, EN or PT-BR.
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

Close WoW and the app before replacing the addon or updating the package. To
start without path or language preferences, remove only
%LOCALAPPDATA%/DpsLab/workspace_paths.json and language.json; this does not
delete saved character profiles. If the app does
not open, extract the complete ZIP again and keep _internal intact. If no export
is detected, install the matching addon version, run /reload and click Detect
export. If a score is missing, verify the compatible weight profile and enable
Show item scores. Incomplete builds and characters below max level are excluded.

SimulationCraft is distributed under GPL v3. See
SIMULATIONCRAFT_NOTICE.txt for the included binary SHA-256 and source repository.
