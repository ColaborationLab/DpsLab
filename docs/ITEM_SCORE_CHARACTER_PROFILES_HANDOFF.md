# Scores de equipo y perfiles de personajes — preparación para Terra

Fecha: 2026-09-12. Estado: histórico, cerrado en dd61f94.
Sustituido por docs/DEFAULT_WEIGHTS_TERRA_PLAN.md; no activar este plan.
Esta preparación no inicia implementación, simulaciones ni publicación.

## Autoridad, baseline y responsable

Petición de Daniel: revisar el nuevo objetivo, recalcular SHA, registrar cierres
y preparar su ejecución con Terra. Autoridad funcional: sección 1 del Scope
recuperada de `origin/main` en `0145b7e0c93c0caaa91af7cd7a37ccc3cdc6fd3b`.
Baseline de código: `eeeba7e99033012481634943817d1baf16db99e6`, rama
`codex/live-export-balance-package`, más esta preparación documental.
SHA-256 del Scope integrado con historial:
`0ccaf35aadfb534a20748b036d35d806ec4a6502ca88d35335e8ab2eddf97b04`.
Baseline de AGENTS: `59336d24041f8a84f293662aefa24528a5b13d340b18ffec76307d39a233247f`.

Ejecutor previsto: Terra (`gpt-5.6-terra`), único implementador, trabajo serial.
El principal conserva coordinación, documentos protegidos y revisión final.
No reutilizar la autorización consumida del colaborador multiclase ni lanzar
agentes adicionales. Al activar: registrar el commit limpio que incluya esta
preparación y comprobar que no hay otro escritor en las rutas del trabajo.
Un cambio de objetivo o baseline exige revalidar el plan.

Las restricciones antiguas a Balance en AGENTS y secciones 3/5 del Scope se
leen conforme al nuevo permiso explícito de la sección 1, no como veto a él.
Esto no levanta el resto de frentes congelados.

Prueba de valor: sí, permite comparar equipo con scores de specs/builds elegidas
y conservar personajes, equipo, pesos y simulaciones actualizables por exportación.

## Entrega funcional y orden de trabajo

1. **Modelo compartido mínimo.** Reutilizar el transporte de exportación y
   resultados existente. Definir su extensión versionada antes de conectar UI:
   personaje → spec → build con ID y nombre → simulación, equipo y pesos.
   Separar identidad estable del personaje de nombres editables; impedir
   colisiones entre personajes de igual clase o nombre en distintos reinos.
   Usar solo datos locales necesarios, sin telemetría ni datos reales en fixtures.
   Conservar lectura de formatos anteriores y migración no destructiva.
2. **Pesos y score.** Reutilizar `balance_stat_weights.py` y llevar el resultado
   al flujo multiclase de `loadout_recommendation.py`. Preferir pesos de una
   simulación compatible guardada del personaje/spec/build; si faltan, usar
   pesos realmente generados con SimC a partir de un perfil genérico compatible.
   Guardar fuente, versión de SimC, escenario, métrica y perfil de referencia;
   mostrar claramente «genérico» o «personalizado». No inventar pesos ni usar
   pesos de Balance para otra spec. Datos ausentes/incompatibles: explicar
   indisponibilidad. DPS no representa curación ni supervivencia.
   Score aditivo con claves estadísticas compatibles con Pawn, sin exigir
   cadena de exportación Pawn. Comparar candidato y equipado bajo los mismos
   pesos; tratar ranuras dobles y armas explícitamente. No prometer que un
   score lineal simula procs, efectos especiales o DPS real del ítem, ni que
   escalas normalizadas de specs distintas son directamente comparables.
3. **Biblioteca de la app.** Extender `loadout_comparison_library.py` y
   `loadout_ui.py`: crear/seleccionar personaje, navegar specs/builds con nombres,
   conservar equipo exportado y simulaciones/pesos, y recuperarlos tras reinicio.
   Actualizar desde exportación sin borrar otros personajes/specs o ejecuciones.
   Mostrar scores y procedencia de pesos. Mantener simulación individual,
   comparación de hasta cuatro, importaciones nombradas y limpieza manual:
   limpiar pantalla no borra biblioteca ni obliga a limpiar automáticamente.
4. **Addon y configuración visible.** Persistir pesos por personaje/spec/build
   y preferencias locales. Añadir menú visible para activar scores, elegir una
   o varias specs/builds, y configurar su presentación/comportamiento. Mostrar
   en la vista de equipo o tooltip los nombres, scores y origen elegidos sin
   cambiar la spec activa. La app calcula y entrega pesos; el addon no ejecuta
   SimC ni automatiza el juego. Mantener exportación voluntaria y /reload.
5. **Integración y paquete.** Conservar SimC incluido, sin pedir ruta externa.
   Empaquetar app, dependencias Tcl/Tk, addon actualizado y avisos de SimC, sin
   perfiles privados, rutas personales ni resultados del desarrollador.
   Verificar arranque del ejecutable empaquetado, no solo del script. Entregar
   instrucciones de instalación y prueba completa con WoW para Daniel.

## Rutas y límites de ejecución

Lectura: repositorio y distribución local de SimC seleccionada por Daniel.
Escritura de implementación, al activar: `desktop-app/src/dpslab/`,
`desktop-app/tests/`, `addon/DpsLab/` excepto módulos `*Synthetic*.lua`,
`tools/tests/` para pruebas de esta integración, y scripts existentes de
empaquetado bajo `tools/` solo cuando sean necesarios para este paquete.
Documentación de entrega: este archivo. Artefactos nuevos: `build/`, `dist/`
y `.dpslab/`, sin sobrescribir ejecuciones previas. Datos de prueba aislados.
El principal actualiza `docs/NEXT_TASK.md` y los documentos protegidos.

No cambiar perfiles canónicos, escenarios, variantes, resultados históricos,
CI, seguridad, secretos, catálogos ni módulos synthetic. No crear motor propio,
SBOM, firma, adquisición automática de fuentes ni dependencias innecesarias.
No reparar Python global: usar el entorno funcional del proyecto, validando
dependencias y Tk al activar. No instalar en WoW ni modificar ajustes reales,
hacer commit/push, merge o release por el mero hecho de completar pruebas.

La generación real de pesos genéricos forma parte de la entrega requerida,
pero cada corrida concreta de SimC requiere autorización según AGENTS:
antes de ejecutarla, presentar perfiles, specs, escenario, cantidad de corridas
y directorio nuevo de salida. Preparar primero implementación y pruebas con
fixtures; no sustituir esa evidencia real por pesos inventados. Si una spec
no está soportada por la distribución, informar el límite sin declararla lista.

## Verificación y cierre

- Pruebas focales: round-trip y migración; aislamiento entre personajes;
  nombres y selección de specs/builds no activas; prioridad personalizado/genérico;
  pesos ausentes, inválidos y obsoletos; scores comparados con igual normalización;
  persistencia tras reinicio y actualizaciones sin pérdida; limpieza solo visual.
- Regresión: una a cuatro builds, Unicode/tildes, selección importada, exportación
  multiclase, progreso y ejecución sin consola negra. Leer controles Tk en hilo
  principal antes del worker; mantener UI responsiva y comunicar errores.
- Ejecutar focales, suite completa de `desktop-app/tests`, `tools/tests` y
  `python tools/quality_gate.py run` con el intérprete funcional del proyecto.
  Reportar aprobadas, subtests, fallos y exit codes por separado. No eximir un
  fallo como histórico sin evidencia ni modificar tests para esconderlo.
- Comprobar hashes protegidos y `git diff --check`. Revisar que paquete no
  incluya datos de prueba o rutas personales y sí incluya addon y SimC.
- Tras autorización de corrida e instalación, prueba real de Daniel: exportar
  dos personajes, guardar más de una spec/build, ejecutar, reiniciar app,
  recuperar perfiles, transferir pesos y observar scores configurables en WoW
  sin cambiar spec. Probar ausencia de simulación guardada y fallback genérico.

Entrega: diff y resumen de módulos, comandos/resultados, hashes, artefacto
instalable y pendientes explícitos. La evidencia técnica no sustituye la
aceptación visual de Daniel. Detener solo la parte afectada ante nueva autoridad,
conflicto de escritor, datos incompatibles o necesidad de ampliar rutas; continuar
lo separable. La delegación termina al entregar esta revisión o cambiar el Scope.

## Prompt de activación para Terra

Implementa este objetivo en serie sobre la baseline limpia registrada al activar.
Lee AGENTS, Scope y este plan; confirma hashes y ausencia de escritor concurrente.
Reutiliza los módulos existentes y cubre las cinco entregas en el orden indicado.
No lances subagentes. No ejecutes SimC real, instales, publiques ni alteres archivos
protegidos sin la autorización correspondiente. Devuelve cambios verificables y
el estado real de cada criterio; no declares completa la prueba visual pendiente.
