# Traducciones de DpsLab

Este lote establece un catálogo pequeño y estable para la interfaz visible de
la app Qt y del addon. Los idiomas incluidos son español (`es`), inglés
(`en`) y portugués brasileño (`pt-BR`). El inglés es el fallback.

## Inventario inicial

Las claves cubren títulos, grupos de fuente/perfil/builds, detección y pegado
de exportaciones, simulación y progreso, resultados y pesos, importaciones,
casos, guardar/abrir/eliminar, limpiar interfaz y las etiquetas de la tabla
(DPS, equipo, peso, mayor DPS y mayor peso). El addon incluye además los
mensajes de pesos, importación/exportación, confirmación, borrado y la marca
`(b)` de referencia beginner.

No se traducen nombres de personaje, reino, builds, specs, strings de talentos,
comandos `/dpslab`, rutas, números, claves de intercambio, salida cruda de
SimulationCraft ni payloads persistidos.

## Añadir un idioma

1. Copia `desktop-app/src/dpslab/locales/en.py` y conserva exactamente sus
   claves y placeholders.
2. Añade el alias en `normalize_locale()` y en `SUPPORTED_LOCALES`.
3. Para el addon, agrega un catálogo en `Localization.lua` y resuelve el
   locale antes de consumir `DpsLabLocalization.Get`.
4. Usa UTF-8, no cambies las claves y ejecuta `desktop-app/tests/test_i18n.py`.

Las traducciones requieren revisión humana nativa. Una clave ausente debe
volver al inglés; nunca debe causar un error ni alterar datos del usuario.

## Glosario

| Español | English | Português (BR) |
|---|---|---|
| DPS | DPS | DPS |
| estadística | stat | atributo |
| peso | weight | peso |
| loadout/build | loadout/build | loadout/build |
| beginner | beginner | beginner |
| perfil | profile | perfil |

La app y el addon usan el catálogo para etiquetas, acciones, ayudas, estados
de exportación/simulación y gestión de perfiles de pesos. Los nombres y datos
del jugador siguen siendo datos, no textos traducibles. La ventana se vuelve a
abrir tras cambiar el idioma para refrescar controles ya creados sin descartar
ediciones locales.
