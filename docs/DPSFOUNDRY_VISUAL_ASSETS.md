# Foundry visual assets

## Background — 2026-09-20

Product asset: `desktop-app/src/dpslab/assets/foundry-background.png`.
Generated using the built-in ImageGen tool with the user-supplied
`concept_02_foundry_flagship.png` as visual reference. The original reference
contains the discarded RaidForge name; the new background contains no text,
UI, characters or logos. It is packaged as Python package data and included
by the reduced installer. `FoundryBackdrop` paints a dark overlay over it to
preserve foreground readability; the source image remains unmodified.

Generation prompt:

> Create a clean atmospheric BACKGROUND ASSET for the DpsFoundry desktop application,
> inspired by the attached concept art. Remove ALL UI panels, ALL letters, words,
> logos, icons, figures and diagrams. Only environment remains: dark forged steel /
> volcanic fortress and distant forge furnace, subdued embers and subtle orange
> reflections at the edges. Wide 16:9 cinematic matte painting. Keep center and
> left 75% very dark charcoal with low visual complexity for readable data panels;
> distant fortress and molten orange glow primarily at upper-right and lower outer
> edges. Restrained, sophisticated, low saturation, no distracting sparks across
> center, no text, no watermark. Preserve visual atmosphere of reference but produce
> a coherent original background, not a collage or screenshot.

## Native vector mark and frame

### Variantes del 2026-09-20

Generadas mediante ImageGen integrado, usando el mismo concepto 02 como
referencia; sin textos, UI, logos ni personajes. Rutas de producto:
`desktop-app/src/dpslab/assets/foundry-comparison.png` y
`desktop-app/src/dpslab/assets/foundry-simulation.png`.

Prompt comparación:

> Generate one wide 16:9 background painting for DpsFoundry's COMPARE screen,
> same graphite steel dark fantasy forge aesthetic as reference. NO UI, NO text,
> NO icons, NO logos or characters. A cavernous armory workbench and forged steel
> buttresses in the far-right and lower edge; small molten orange light reflected
> on hammered metal. Center and left 75% nearly black, low-contrast smoke and steel
> for placing dense readable comparison tables. Subtle realistic grain, premium
> cinematic concept art, not saturated, not bright fire. Different scene from
> outdoor castle dashboard, keep same restrained orange/charcoal palette.

Prompt simulación:

> Create one wide 16:9 background art for DpsFoundry SIMULATION screen using this
> dark fantasy forged metal concept as atmosphere reference. NO UI panels, NO words,
> NO logos, NO icons, NO characters. View into a massive industrial fantasy smelting
> chamber, distant furnace ring and restrained orange embers at upper right edge,
> heavy charcoal steel plates framing bottom corners. Dark graphite, warm copper
> highlights, subtle smoky air, center and left 75% quiet and almost black for
> legible tables. Different composition from outdoor fortress or armory. Premium
> detailed cinematic material painting, understated glow, no distracting bright areas.

### Detalle del marco

La revisión añade 16 píxeles de biseles y railes con desgaste determinista y
placas remachadas en las esquinas. Los controles de contenido tienen cursor
propio para no heredar el cursor transitorio del borde. Brillo en marca e
indicadores principales, sin aplicarlo a los textos de lectura prolongada.

Original Qt line drawing: an anvil with three sparks, replacing the abstract DF
mark. No WoW assets or icon-font dependencies. The title and mark have a restrained
glow. A native Qt frame draws steel edges, inset line and corner rivets; titlebar
buttons provide minimize, maximize/restore and close. Movement and resize use Qt
system movement APIs rather than implementing a separate window positioning loop.
Human Windows review of dragging, resizing and snapping remains necessary.

## DPS display

Dashboard and table show signed percent difference: `(DPS / reference - 1) * 100`.
Default reference is the highest DPS of the current comparison. The player can
select a different simulated build from the dashboard. Equal values and single
build results do not display a delta; a zero reference does not produce a percent.
This does not aggregate saved runs across characters or incompatible scenarios.
