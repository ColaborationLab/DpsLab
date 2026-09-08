# Exportación real de Druida Restauración 0.4

`/dpslab export analysis` abre un texto para copiar con el equipo equipado,
especialización Restauración activa y dos loadouts de talentos reales: el
activo y el primer loadout guardado alternativo. El jugador puede usar
`/dpslab export analysis 2` para escoger el segundo alternativo disponible.
No se leen mochilas, inventario, candidatos ni datos sintéticos.

La exportación se rechaza si el personaje no es Druida Restauración, si falta
información real de un objeto o si no existe otro loadout guardado de la misma
especialización. El addon usa las APIs del cliente para el nivel de objeto y
la cadena de talentos; no inventa configuraciones.

La aplicación acepta el sobre canónico `DPSLAB-LIVE-ANALYSIS-0.1` con esquema
`0.4` y crea en memoria dos perfiles de SimulationCraft con el mismo equipo
real y talentos distintos. Aún no ejecuta esos perfiles ni muestra una
recomendación: esas son las siguientes etapas del slice.
