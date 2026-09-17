# Comparador Qt y navegación del addon — Plan para Terra

Fecha de preparación: 2026-09-13. Estado: objetivo cerrado; commit autorizado el 2026-09-17.

## Cierre verificado (2026-09-17)

Daniel aprobó visualmente app y addon y posteriormente cambió el objetivo.
Se incorporaron DPS primero, referencia de mayor DPS, diferencias con signo
solo cuando existen y estadística/peso en una única celda.
La migración Qt incluye arranque y empaquetado con SimC integrado; los archivos
de dependencias existentes se sincronizaron con PySide6, sin ampliar seguridad.
Prueba de valor: el jugador puede comparar hasta cuatro builds lado a lado y
utilizar los recorridos aprobados de la app y el addon.
Verificación actual: 10 pruebas focales aprobadas; suite app 1363 ejecutadas,
1362 aprobadas y una omitida; herramientas 162 aprobadas. Códigos de salida 0.
El quality gate no completó: encontró docs/LOCALIZATION_LUNA_PLAN.md fuera
del alcance anterior; ese archivo pertenece al objetivo siguiente y queda
fuera de este commit. No se ejecutó SimulationCraft ni se publicó nada.
Las secciones siguientes conservan el plan original como antecedente.
Base de código: 11767d3a94a86de5fc23e1b035a231127c72324d,
rama codex/live-export-balance-package, más esta preparación documental.
Scope: blob remoto 4c4338192207b8df2e2a50f22797a615a0b9ed3f,
incorporado con historial restaurado. SHA-256 local en protected_files de NEXT_TASK.

## Valor y alcance

Sí: el jugador podrá navegar addon y app con ayuda contextual y comparar de
una a cuatro builds por estadísticas, pesos y DPS en una tabla legible.
Se cumplen tanto el encabezado como los puntos 1 y 2 de la sección 1.
Una sola simulación sigue siendo válida; cinco selecciones requieren reducir
la selección, sin ocultar builds del catálogo ni borrar datos.

La aplicación actual usa Tkinter (loadout_ui.py); el empaquetador depende de
Tcl/Tk y pyproject.toml no declara Qt. La migración es una parte necesaria,
no basta añadir una tabla al texto existente. Reutilizar lógica de negocio.
Elegir PySide6 como binding previsto, fijar versión compatible con Python del
paquete tras verificar disponibilidad y requisitos oficiales en implementación.
Usar QTableWidget nativo, salvo necesidad demostrada de QTableView, y una sola
hoja de estilo. Sin temas configurables, animaciones ni paneles flotantes.

La prohibición nueva de expansión fuera de Balance se interpreta como no
añadir clases/specs: se conserva el registro existente y se comprueba regresión
de sus 39 entradas. No implica retirar funciones ya aprobadas.
No se generan los ocho defaults pendientes ni se amplía el motor.

## Responsabilidad y ejecución

Terra (gpt-5.6-terra) será ejecutor local subordinado y único escritor del lote
activado; el principal conserva gobierno, revisión, integración y entrega.
No se crea tarea externa, Issue ni PR durante esta preparación.
Antes de activarlo: verificar HEAD, hashes de documentos y exclusividad;
aceptar solo estos cambios documentales sobre la base. Si hay trabajo nuevo,
conciliarlo primero; no descartar cambios ajenos.
El mensaje actual autoriza preparar el plan, no ejecutar sus lotes.
Al activarse, el principal entrega este encargo con hashes actuales y Terra
realiza los lotes serialmente; no hay dos agentes escribiendo los mismos archivos.

## Actividades y aceptación

1. Inventario funcional y datos de comparación.
   Revisar loadout_ui, loadout_recommendation, item_score_profiles,
   loadout_profiles y el punto de entrada. Mapear las acciones actuales:
   detectar/pegar exportación, perfil con equipo, builds externas guardadas,
   selección, simulación, pesos elegidos, copia/pegado, casos y limpieza.
   Separar valor de estadística de peso calculado. Usar datos realmente
   disponibles; una estadística no disponible es N/D, nunca cero inventado.
   Si todas las builds comparten equipo, mostrar sus stats iguales.
   No inferir stats efectivos de combate de un peso o de un item_level.

2. Ventana Qt de la app.
   Migrar el espacio de trabajo conservando los servicios existentes. Agrupar
   personaje/perfil, builds, simulación y resultados; rutas en configuración
   accesible. Tooltips, nombres claros, foco/teclado, redimensionamiento y
   estados vacíos/errores. Conservar el significado de Recordar rutas.
   Trabajo de simulación fuera del hilo gráfico; progreso honesto, sin
   bloqueo de UI ni consola. Conservar manejo de errores y recuperación.
   No cambiar opciones, métricas o presupuesto de SimC en este lote.

3. Tabla comparativa.
   Una columna de etiquetas y entre una y cuatro columnas identificadas por
   nombre de build (ID disponible en ayuda cuando haya nombres repetidos).
   Filas para crítico, celeridad, maestría, versatilidad, atributo primario,
   sus pesos por build y DPS resultante; unidades y procedencia visibles.
   No sustituir un peso ausente por el default sin etiquetarlo.
   Elegir build de referencia; mostrar diferencias absolutas y relativas
   cuando el denominador sea válido; para cero/N/D evitar división y ranking.
   Resaltar mayor dispersión relativa por fila con texto o icono además del
   color, sin comparar unidades diferentes. Peso mayor no significa build mejor.
   Error/incertidumbre disponible en ayuda; no afirmar diferencia significativa
   por el color. Un único resultado no tiene delta comparativo.
   Conservar exportación explícita de pesos de la build elegida y bloqueo de
   exportación como loadout real de una build externa que no exista en WoW.

4. Navegación del addon.
   Organizar entradas visibles para perfiles/builds, pesos y transferencia.
   Selectores claros; guardar, activar, eliminar y ayuda junto a su contexto.
   Mantener edición por build, defaults (b), scores mouseover/comparativos y
   estados N/D. Importación con decisiones explícitas y confirmación visible;
   cerrar diálogo después de decidir. Conservar exportación/reload y strings.
   Evitar depender de recordar comandos slash para completar el recorrido.
   Copy selecciona el texto y explica Ctrl+C si WoW no permite portapapeles.

5. Empaquetado y regresión.
   Incluir Qt, plugin de plataforma Windows y simc del paquete existente.
   Ajustar requisitos Tcl/Tk solo donde se sustituya el frontend.
   Paquete reducido sin perfiles ni exportaciones de pruebas; lectura de datos
   locales detectados no equivale a datos incluidos en el paquete.
   Comprobar inicio desde el paquete fuera del árbol fuente, con rutas con
   espacios, DPI 100/150%, ventana pequeña y ausencia de consola.

6. Prueba de valor con Daniel.
   Abrir el ejecutable empaquetado; detectar una exportación real y sus nombres,
   elegir 2 y luego 4 builds; verificar columnas, stats, pesos, diferencias y DPS.
   Repetir con una sola build, perfil guardado sin WoW y build externa.
   Guardar/abrir/renombrar/eliminar según opciones actuales; limpiar con aviso.
   Exportar pesos de una build elegida que no sea ganadora; en WoW aceptar,
   conservar o guardar copia y verificar perfiles y tooltips comparativos.
   Completar navegación con controles visibles y tooltips. Registrar lo observado
   por Daniel separado de las pruebas automatizadas; no declarar cierre por mocks.
   Las corridas reales deben identificar entrada/configuración y usar autorización
   aplicable a esa corrida; las pruebas de UI previas usan resultados de fixtures.

## Frontera de archivos al activar

Terra puede editar loadout_ui.py, un módulo nuevo qt_loadout_ui.py y uno de
presentación comparison_table.py si hace falta, __main__.py para entrada,
item_score_profiles.py y loadout_recommendation.py solo para exponer datos
ya calculados; todos bajo desktop-app/src/dpslab/.
Pruebas asociadas bajo desktop-app/tests/test_loadout_ui.py,
test_qt_loadout_ui.py, test_comparison_table.py, test_item_score_profiles.py,
test_loadout_recommendation.py y test_loadout_profiles.py.
Addon: addon/DpsLab/ItemScoreProfiles.lua, DpsLab.lua y DpsLab.toc;
tools/tests/test_addon_item_score_profiles.py.
Empaquetado: desktop-app/pyproject.toml, installer/build_reduced.py,
installer/README-WINDOWS.md y archivos de dependencias existentes necesarios
para Qt, identificados por nombre al activar el lote de empaquetado.
Documentos de gobierno, Scope, commits/push y despliegue: principal.
Prohibido modificar runs existentes, perfiles personales, escenarios, seguridad,
fuentes automáticas, CI o módulos synthetic. Sin reparación global de Python.

## Verificación y entrega de Terra

Pruebas significativas: 1/2/4 builds, rechazo de 5, nombres repetidos, selección
persistente, datos ausentes/cero, pesos por build, deltas correctos, unidades,
perfil offline, build externa, intercambio y errores del proceso de simulación.
Qt se prueba con entorno offscreen para lógica/eventos y con paquete visible
para renderizado real. Lua cubre controles y tooltips sin depender de WoW.
Luego suites completas de app y herramientas; mínimo de referencia: 1355 app
(1354 aprobadas, una omitida) y 162 herramientas. Subtests por separado.
Usar quality gate con tarea vigente si lo requiere el repositorio; el contrato
histórico de defaults no autoriza ni valida el objetivo Qt.

Entregar diff por lote, lista de archivos, pruebas/códigos de salida, capturas
del paquete, limitaciones y un recorrido visual reproducible. No afirmar
simulación real de 39 specs por haber comprobado su generación de perfiles.
Ante datos ausentes, conservar N/D y explicar; si hace falta modificar el motor,
una métrica o un archivo ajeno al lote, detener solo esa ampliación y reportarla.
Autoridad de Terra termina al entregar los lotes activados al principal.
La finalización del objetivo requiere aceptación visual de Daniel; commit,
push, merge y publicación se tramitan según autorización vigente.

## Prompt de activación

Implementa serialmente este plan sobre la base verificada, como Terra.
Reutiliza el flujo existente al migrar a Qt, cumple las dos secciones de UI
y conserva los recorridos aprobados. Entrega cada lote con pruebas, sin
atribuir a fixtures validez de simulaciones reales. Revisa el Scope vigente
y los hashes antes de empezar. El principal integra y coordina la prueba visual.
