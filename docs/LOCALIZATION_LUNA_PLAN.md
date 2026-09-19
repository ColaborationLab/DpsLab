# Suite multilingüe — Encargo preparado para Luna

Fecha: 2026-09-17. Estado al 2026-09-18: objetivo cerrado por cambio de Scope;
implementación parcial conservada, revisión técnica en PENDING_COMMIT_REVIEW_2026_09_18.md.
Plan vigente: PUBLIC_DISTRIBUTION_PLAN.md. Lo siguiente conserva el encargo original;
las referencias a no iniciado o activación pendiente son históricas.
Ejecutor previsto: Luna (gpt-5.6-luna), un lote a la vez y sin escritores concurrentes.
Principal: integración, documentos de gobierno, revisión y entrega a Daniel.

## Valor y objetivo completo

Sí: este trabajo hace que un jugador disponga de la suite completa en español,
inglés y portugués, con instrucciones para incorporar otros idiomas.
Cubre sección 1.1 (addon), sección 1.2 (app) y prueba de valor del Scope.
Portugués inicial: pt-BR, coincidente con el locale del cliente WoW; no afirmar
traducción pt-PT. Conservar español y permitir fallback cuando falte una clave.

## Base y autoridad

HEAD: 49d88bbeb081e55bccaee646706912372218167e.
Rama: codex/live-export-balance-package.
Scope remoto: blob 2cbb255cb920293f6a46c7d160f8907154e6d671,
incorporado localmente conservando historial; hash vigente en NEXT_TASK.
La migración Qt y ajustes aprobados del objetivo anterior están en el commit
local indicado; push pendiente. El árbol conserva solo la preparación documental
multilingüe sin commit. No descartar ni sobrescribir esa preparación.
Antes de activar: el principal registra status y SHA-256 de cada archivo
modificado/no rastreado de código y documentación relevante y entrega ese
snapshot a Luna; comprobar HEAD y protected_files. Si cambian, conciliar
solo diferencias antes de editar. No exigir borrar cambios ni inventar
un commit como requisito. No reutilizar autorizaciones históricas.
La petición actual autoriza preparación, no implementación, simulaciones,
instalación, commit, push, PR ni publicación. La activación será posterior.

## Lotes secuenciales

1. Inventario y catálogo mínimo.
   Recorrer todos los textos visibles del flujo vigente, no solo títulos:
   botones, tooltips, errores, confirmaciones, progreso, tabla, perfiles,
   casos, builds, pesos, scores, transferencia manual y automática.
   Identificar productores de mensajes en servicios llamados por Qt.
   Adoptar claves estables y diccionarios pequeños, sin servicio de traducción,
   nuevas dependencias ni framework general. Preservar placeholders y Unicode.
   Datos del usuario y nombres de builds/personajes/reinos nunca se traducen.
   Tampoco comandos, strings de talentos, claves de intercambio, Pawn,
   rutas, números persistidos ni identificadores de clase/spec.

2. Addon.
   Cargar catálogo Lua antes de consumidores en DpsLab.toc.
   Resolver GetLocale: esES/esMX -> español, enUS/enGB -> inglés,
   ptBR -> portugués; otros -> inglés. Ofrecer selector accesible Auto/ES/EN/PT-BR,
   persistido como preferencia; si requiere /reload, explicarlo.
   Traducir navegación, pesos, importación/sobrescritura/guardar actuales,
   borrado y tooltips mouseover/comparativos; explicación de (b).
   No modificar cálculo ni detección de items/talentos. Conservar comandos.
   Textos de fuentes traducibles no equivalen a modificar módulos synthetic
   ni ampliar defaults, clases o specs.

3. App Qt.
   Selector de idioma persistente y disponible sin abrir un perfil; detección
   inicial de locale del sistema, elección explícita prevalece y fallback inglés.
   ES/EN/PT-BR completos en ventana, tabla DPS primero, diferencias con signo,
   mayor DPS/mayor peso, ayudas, diálogos, errores y resultados.
   Cambio sin perder datos sin guardar; preferir refrescar etiquetas; si hace
   falta reinicio, informar y pedir confirmación sin descartar contenido.
   Mantener 1-4 builds, perfiles con equipo, imports externos, borrado,
   limpieza confirmada y SimC empaquetado sin pedir distribución externa.
   No traducir salida cruda de SimC como si fuera propia: identificarla como
   diagnóstico original y añadir explicación localizada cuando sea posible.

4. Guía de contribución.
   Documentar dónde añadir idioma, claves, fallback, placeholders, UTF-8,
   cómo probar app/addon y lista de revisión. Glosario ES/EN/PT-BR para
   DPS, stat, weight, loadout, beginner y perfiles. Ejemplo de idioma nuevo
   sin implementarlo. Explicar que traducciones requieren revisión humana.

5. Verificación y entrega.
   Pruebas de paridad de claves, placeholders, fallback, selección guardada y
   errores; ningún KeyError por locale/clave faltante, ni traducción de payload.
   Qt offscreen en tres idiomas: abrir, seleccionar, guardar/cargar perfil,
   importar build, simular con runner falso, exportar pesos y limpiar.
   Probar tabla con una, dos y cuatro builds, empates, N/D y diferencias.
   Lua con mocks: locales, preferencias y tooltips principal/comparativos;
   confirmar que intercambio y scores siguen iguales entre idiomas.
   Ejecutar suites completas app y tools; comparar totales y skips con estado
   previo, sin atribuir a este lote fallos ya presentes. No ejecutar SimC real.
   Construir paquete reducido con catálogos incluidos, sin reintroducir Tcl
   ni DLLs incompatibles; arranque de paquete en los tres idiomas.
   Principal entrega a Daniel prueba visual real app + addon: navegación,
   exportación -> detección -> selección de 1-4 -> simulación autorizada ->
   importación elegida de pesos -> scores comparativos, en EN y PT-BR,
   y regresión ES. No declarar aceptación visual sin confirmación.

## Fronteras de edición

Luna: desktop-app/src/dpslab/qt_loadout_ui.py, comparison_table.py,
nuevo i18n.py y locales/**; addon/DpsLab/DpsLab.lua,
ItemScoreProfiles.lua, DpsLab.toc y nuevos Localization.lua/locales/**;
pruebas relacionadas en desktop-app/tests y tools/tests; docs/TRANSLATIONS.md.
installer/build_reduced.py solo para incluir recursos de idiomas si necesario.
Si servicios adicionales generan mensajes visibles, identificar rutas exactas
y pedir al principal ampliar esa frontera antes de tocarlas; mantener sus
contratos y lógica. No editar Tk legacy salvo que sea entrada aún distribuida,
en cuyo caso documentarlo primero.
Principal exclusivamente: AGENTS, Scope, NEXT_TASK y este plan.
Prohibidos: .github, security, knowledge, datos personales/perfiles/resultados,
módulos Synthetic*, motor/opciones/presupuesto de SimC, dependencias nuevas,
expansión de clases/specs, firma/SBOM o adquisición automática de fuentes.

## Entrega y cierre

Por lote: archivos cambiados, comandos y resultados de tests, limitaciones,
capturas/pruebas pendientes, sin afirmar publicación. Detener el lote ante
cambio concurrente de base, necesidad de editar fuera de frontera o de
alterar contratos persistidos. Completar antes lo independiente permitido.
Preparado para activación de Luna; no se ha despachado ejecución.
El objetivo solo se presenta para cierre cuando ambas superficies y la guía
cumplan todos los puntos y Daniel confirme la prueba de valor.
