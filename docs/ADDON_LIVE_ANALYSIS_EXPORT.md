# Exportación real de Druida Restauración y Balance 0.4

`/dpslab export analysis` abre un texto para copiar con el equipo equipado,
especialización Restauración o Balance activa y dos loadouts de talentos reales: el
activo y el primer loadout guardado alternativo. El jugador puede usar
`/dpslab export analysis 2` para escoger el segundo alternativo disponible.
No se leen mochilas, inventario, candidatos ni datos sintéticos.

La exportación se rechaza si el personaje no es Druida Restauración o Balance, si falta
información real de un objeto o si no existe otro loadout guardado de la misma
especialización. El addon usa las APIs del cliente para el nivel de objeto y
la cadena de talentos; no inventa configuraciones.

La aplicación acepta el sobre canónico `DPSLAB-LIVE-ANALYSIS-0.1` con esquema
`0.4` y crea en memoria dos perfiles de SimulationCraft con el mismo equipo
real y talentos distintos. Los comandos `restoration` y `balance` ejecutan
esa comparación local y escriben el texto acotado que el addon muestra con
`/dpslab result`.
