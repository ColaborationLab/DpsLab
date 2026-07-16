# Auditoría manual frente a línea base formal — 2026-07-15

`flasil.simc.html` sí es el informe citado: contiene `DPS=82950.55`. La línea
base formal registra 88511.37941600244 DPS. La diferencia es
5560.829416002438 DPS, o 6.703788481212528 % respecto del informe manual.

## Coincidencias

Coinciden SimC 1205-01/revisión `a81c39d`, WoW 12.0.7.68453, hotfix,
identidad, talentos, los 15 objetos con encantamientos, gemas, bonus IDs y
atributos creados (normalizando su orden), consumibles, APL predeterminada,
LightMovement, 300 s ±20 %, latencia, objetivo, APM y tiempo de espera.

## Diferencias exactas

- DPS: 82950.55 frente a 88511.37941600244.
- Precisión: 13520 iteraciones manuales; base adaptativa con parámetro 0,
  objetivo 0.1 %, 3405 iteraciones completadas y 3403 muestras.
- Hilos: 8 frente a 2; probablemente irrelevante para la media.
- Scale factors: presentes solo en el manual; probablemente irrelevantes.
- El HTML incrusta `warlock.soul_shards=0`; el perfil formal no lo contiene.
  El valor inicial efectivo formal no queda expuesto inequívocamente.

## No comparables

El HTML no expone inequívocamente `desired_targets`, el detalle de raid events,
todos los overrides ni el error objetivo. Las fuentes de daño formales se
reparten entre actor y mascotas y no se normalizaron para evitar una comparación
engañosa.

## Hipótesis — causalidad no establecida

1. Investigar primero `warlock.soul_shards=0` y el recurso inicial formal.
2. Reconstruir argumentos manuales no preservados: raid events y overrides.
3. La precisión distinta cambia incertidumbre, pero no debería explicar sola
   una separación sistemática del 6.70 %.
4. Hilos y scale factors son probablemente irrelevantes.

No se ejecutó SimulationCraft ni se alteraron los informes originales.
