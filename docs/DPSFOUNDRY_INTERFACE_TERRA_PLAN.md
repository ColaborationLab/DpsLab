# DpsFoundry — dirección de implementación con Terra

## Autoridad y entrega

Preparación solicitada por Daniel el 2026-09-19. Fuente única de alcance:
`SCOPE_CORRECTION_0_1.md`, incluidas sus secciones 1 a 10 y 13 criterios de
aceptación. Estado: preparado para continuar con Terra; no iniciado.
Responsable ejecutor: Terra (gpt-5.6-terra), supervisado por el agente principal.
La cuenta externa anterior no participa. No hay asignación externa ni nuevo Issue.

Base de código: `997648b301ba5b17fc95093b70c419229c7b8e74`.
Rama de preparación: `codex/dpsfoundry-interface-scope`.
La preparación documental local se añade a esa base; antes de activar, el
principal debe conservarla en un commit y entregar su SHA exacto a Terra.
Este parámetro de activación no autoriza adoptar otros cambios del árbol.
Comprobar escritores activos y permitir un solo editor por componente.

Valor: sí, este trabajo permite al jugador comprender y completar el recorrido
analizar → decidir → sincronizar → jugar → refinar desde Core y Link.

## Base que debe reutilizarse

- `desktop-app/src/dpslab/qt_loadout_ui.py`: ventana Qt real, selección de builds,
  perfiles, importación, ejecución en segundo plano, tabla y transferencia.
- `comparison_table.py`: presentación de DPS, estadísticas, pesos y diferencias.
- `item_score_profiles.py`, `loadout_comparison_library.py`: perfiles y persistencia.
- `loadout_recommendation.py`, `loadout_profiles.py`, `runner.py`: servicios ya
  implementados; consumirlos sin reescribir su lógica para acomodar la UI.
- `addon/DpsLab/ItemScoreProfiles.lua`, `DpsLab.lua`: pesos, tooltips y exportación.
- `i18n.py`, `locales/`, `addon/DpsLab/Localization.lua`: conservar ES/EN/PT-BR.
- `launcher.py`, `installer/build_reduced.py`: entrada y empaquetado existentes.

Los documentos antiguos de arquitectura read-only son antecedentes; el Scope
vigente autoriza la UI de ejecución existente. Los nombres internos DpsLab,
SavedVariables y transporte permanecen compatibles.

## Referencias de diseño

Paquete seleccionado por Daniel: `RAIDFORGE_INTERFACE_OBJECTIVE_HANDOFF_v0.1.0.zip`.
SHA-256: `802ac824b1ac129d39e846ef12c82173c90705084d94d7eefeaa1ca2be3245af`.
El borrador independiente tiene SHA-256
`ce75e955a293c434690da7fb76794abd8c10f2b6cb4dfe22e75664198a0986f7`.
Ubicación de entrada: carpeta Descargas seleccionada por Daniel; no añadir rutas
personales al repositorio. El principal proveerá las referencias a Terra.
El manifiesto interno de nueve entradas fue verificado en la revisión previa.
Antes de diseñar, abrir visualmente los cuatro PNG; el concepto 02 orienta Foundry.
Las imágenes no han sido revisadas visualmente durante esta preparación.
La marca de sus renders está descartada: usar DpsFoundry Core/Link/Guide.
No copiar números ficticios ni incorporar los renders como fondos de producto.

## Secuencia completa y pruebas de valor

| Lote | Entrega visible y alcance | Evidencia para aceptar |
| --- | --- | --- |
| A | Sistema maestro Foundry: tokens, tipografía, espaciado, foco, estados, componentes y slots de spec; especificación breve en docs/DPSFOUNDRY_DESIGN_SYSTEM.md | Tokens semánticos comunes; ejemplos legibles de loading, empty, error, unavailable y success; estados también textuales |
| B | Shell Qt con Setup, Home, Character/Profile, Simulation, Compare, Recommendations, Link/Sync Center y Settings | Navegación y vuelta atrás conservan selección; datos controlados identificados; primera ruta setup→perfil→simulación comprensible |
| C | Panel Link compacto/expandido, perfil, Gear/Stats, pesos y sync | Abrir, cerrar y reabrir; tooltips mouseover y comparativos conservan score; muestra perfil que da significado al score |
| D | arcane_vanguard, foundry, runebound_command y celestial_foundry sobre los mismos componentes | Foundry predeterminado; cambiar tema conserva datos, geometría y resultados en Core y Link |
| E | Integrar servicios existentes: perfiles, equipo, talentos, simulación, resultados, recomendación y transferencia | Sustituir fixtures; todos los flujos previamente aprobados continúan operativos; errores reales con siguiente acción útil |
| F | Paquete local y recorrido completo con Daniel | Setup→perfil→análisis→recomendación→Link→pesos/score→Core; criterios 1–13 del Scope con evidencia individual |

Terra comienza por A y B como primera entrega revisable. Después continúa C–F
en orden tras revisión del principal, dentro de la activación del ciclo. Guide
no recibe datos de combate ni funcionalidad; su frontera futura es conceptual.
Una capacidad ausente se presenta como no disponible, con causa; no se inventa.

## Rutas y fronteras de edición

Terra puede editar los módulos de presentación `qt_loadout_ui.py`,
`comparison_table.py`, `launcher.py`, `i18n.py`, `locales/*.py`; añadir módulos
UI/temas en `desktop-app/src/dpslab/`; y sus pruebas de presentación en
`desktop-app/tests/test_*ui*.py`, `test_comparison_table.py`, `test_i18n.py`
y nuevas pruebas de temas. Puede editar `addon/DpsLab/ItemScoreProfiles.lua`,
`DpsLab.lua`, `DpsLab.toc`, `Localization.lua`, añadir módulos de panel/tema y
ajustar sus pruebas en `tools/tests/test_addon_item_score_profiles.py` y nuevas
pruebas UI/temas. Puede documentar el diseño y la evidencia en
`docs/DPSFOUNDRY_DESIGN_SYSTEM.md` y `docs/DPSFOUNDRY_INTERFACE_ACCEPTANCE.md`.
El lote F permite ajustar `installer/build_reduced.py`, `build_addon_zip.py`
y sus pruebas solo para incluir recursos de UI y mantener el arranque.

AGENTS, Scope, NEXT_TASK y este plan los mantiene el principal. Dominio,
schemas, parser, runner y transporte son de lectura para Terra; si una conexión
requiere modificar su contrato, informar el cambio mínimo al principal.
Perfiles personales, resultados/runs existentes, escenarios, variantes,
knowledge, seguridad y CI quedan fuera de escritura. No se autorizan nuevas
dependencias, rename masivo, publicación, cambios de permisos ni simulaciones
reales desde este encargo documental.

## Verificación y no regresión

Ejecutar primero pruebas Qt de navegación/estado y modelo de tabla, con
QT_QPA_PLATFORM=offscreen y datos temporales; después las suites app y tools
con el Python del proyecto y dependencias existentes. Reportar ejecutadas,
aprobadas, omitidas y fallidas sin equiparar omisiones a cobertura.
Usar el quality gate existente conforme a la excepción documental de AGENTS;
no reactivar contratos históricos para hacerlo pasar.

La matriz de regresión debe cubrir: detección y pegado manual; perfil con equipo
reabierto sin WoW; build externa guardada sin simular; simulación individual y
comparación de 2–4; selección entre más de cuatro; talentos incompletos/nivel;
nombres; borrado de builds/perfiles; limpiar con aviso; DPS primero y diferencias
solo cuando existen; progreso sin consola; precisión y pesos Intellect;
exportar solo builds reales a Link; importación/reemplazo/guardar copia;
scores equipado/candidato y trinkets sin dato como no disponibles; tres idiomas.

Cada lote entrega capturas renderizadas o evidencia visual equivalente, diff,
pruebas, limitaciones y recorrido reproducible. Pruebas simuladas de servicios
no acreditan WoW real. La prueba final de SimC requiere autorización concreta
para el personaje/escenario y la prueba visual in-game la confirma Daniel.

## Activación y cierre

Prompt para Terra: lee AGENTS, Scope y este plan desde la baseline entregada;
inspecciona las artes; implementa A+B usando la UI y servicios existentes;
verifica y entrega el recorrido visible con evidencias. No modifiques documentos
del principal ni reabras la colaboración externa. Resuelve fallos rutinarios
dentro de las rutas permitidas. Informa solo bloqueos que requieran nueva
capacidad, una ruta adicional o una decisión de producto no resuelta.

El principal integra/revisa cada entrega y mantiene NEXT_TASK. La autoridad de
Terra termina al entregar F o cuando Daniel suspenda su ejecución. El cierre del
objetivo exige la aceptación visible de Daniel de los 13 criterios del Scope.
Esta preparación no inicia Terra ni acredita implementación, commit o push.
