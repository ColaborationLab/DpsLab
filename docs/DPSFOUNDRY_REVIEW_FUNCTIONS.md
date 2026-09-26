# Qué probar en la revisión Foundry — 2026-09-20

Revisión de navegación: build/foundry-navigation-20260920/DpsLab/DpsLab.exe.
La app inicia en Simulación: detectar/pegar, abrir personaje guardado y elegir
builds. Comparar y Personaje son las siguientes entradas. Rutas, idioma y motor
se consultan en Ajustes; Setup queda reservado. Personaje muestra retrato neutro
y equipo compacto con scroll; las stats completas se consultan en tooltip.
La futura capa 2 de equipo/gemas/encantamientos está solo planificada en
docs/DPSFOUNDRY_TWO_LAYER_PLAN.md; no hay nueva simulación disponible.

Revisión arte/idioma: el paquete build/foundry-art-language-20260920 incluye
las tarjetas D/E, fondos de todas las rutas Foundry, menú sobre arte y superficies
translúcidas. Cambiar ES/EN/PT-BR actualiza la interfaz sin reinicio y conserva
perfil, importaciones escritas y resultados. Los nombres del jugador y nombres
de ítems importados no se traducen. El metal rústico es exclusivo de Foundry.
Prueba manual: alternar idioma con perfil abierto y cadena sin guardar, navegar
por las ocho rutas y comprobar lectura sobre el arte. Los iconos CASC siguen
pendientes; no confundir el marcador neutro con el icono real del ítem.

Antecedente D/E (superado por el paquete arte/idioma): Simulación y Comparar usan
tarjetas, Personaje muestra equipo importado y Recomendaciones enumera cambios
alternativos de loadout con variación porcentual. Los iconos locales reales
siguen pendientes y se indica su ausencia. No hay comparaciones de piezas ni
deltas de stats por ítem porque el resultado actual comparte un único equipo.
La tabla siguiente conserva el alcance funcional; la presentación de Comparar
es ahora mediante tarjetas en lugar de la tabla cruda original.

Esta revisión se entrega como paquete local con SimC. La entrada del producto
usa los perfiles de la ubicación habitual de DpsLab en el equipo. Abrir el
módulo CLI desde el checkout no equivale a probar ese paquete.

| Área | Qué debe funcionar ahora | Qué falta |
| --- | --- | --- |
| Ventana | Mover por la cabecera, redimensionar por el marco, minimizar, maximizar/restaurar y cerrar; cursor normal sobre contenido | Validación manual Windows de estos gestos |
| Configuración inicial | Detectar exportación, pegar exportación manual, elegir addon, recordar rutas, idioma; motor incluido sin selector de SimC | Acabado y localización total del shell nuevo |
| Personaje | Abrir/guardar/eliminar perfil con equipo, builds y resultados locales | Resumen visual completo de equipo y talentos |
| Simulación | Guardar build externa sin simular, elegir 1–4 builds, simular, progreso, resultados; borrar builds y limpiar con aviso | Refinar distribución; una ejecución real requiere datos válidos y la acción del usuario |
| Inicio | Resumen de la comparación de esta sesión, pesos de la build preferida y referencia porcentual seleccionable | Resumen histórico agregado entre ejecuciones compatibles |
| Comparar | Tabla real de la comparación de esta sesión, DPS primero, porcentajes y pesos | Selector de referencia dentro de la propia sección; por ahora se elige en Inicio |
| Pesos | Exportar pesos elegidos, copiar/pegar pesos desde los controles de Simulación | Reorganizar estos controles en Link/Intercambio |
| Recomendaciones | Resumen textual del loadout preferido tras simular | Panel de recomendaciones detallado |
| Link/Intercambio | Estado textual de exportación local | Centro completo de acciones y HUD nuevo del addon; no es conexión en tiempo real |
| Ajustes | Cambiar tema; Foundry es el acabado en revisión | Escalado interno deshabilitado; tres temas alternativos sin pulido completo |

No hay datos de ejemplo en el paquete para el jugador. Las capturas con
ejemplos se generan aparte para revisar diseño. Los flujos previos no deben
fallar por estar en fase visual: un botón conectado que no responde es un
defecto, no un placeholder aceptable. No se declara validación real de SimC
en este lote: los tests ejercitan la integración con un runner controlado.
