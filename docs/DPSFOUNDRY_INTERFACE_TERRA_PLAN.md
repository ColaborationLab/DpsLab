# DpsFoundry — plan visual revisado para Terra

## Dirección y estado — 2026-09-19

Autoridad: AGENTS.md y SCOPE_CORRECTION_0_1.md actualizados por Daniel en
origin/main, commit fe6206f313a83273429a8095d644fcdc53876dba, incorporados al
checkout por el principal. Esta revisión sustituye el plan A–F anterior.
El objetivo de interfaz continúa abierto: esta aclaración no acredita su cierre.

Prueba de valor: sí, permite que un jugador reconozca, entienda y use Core/Link
en el recorrido analizar → decidir → sincronizar → jugar → refinar.

Responsable: principal; Terra continúa como ejecutor interno del lote visual
cuando se retome implementación. No representa la antigua cuenta externa.
Este encargo documental no inicia agentes, simulaciones, commit ni publicación.

Base local: ffe7ccd63344f57c6739ffaaa6cf6b6e07b80cc7, rama
codex/dpsfoundry-interface-scope. Se conservan cambios no confirmados de A+B en
qt_loadout_ui.py, dpsfoundry_theme.py, test_qt_loadout_ui.py y los dos documentos
de diseño/aceptación. No son una baseline visual aprobada.
Antes de delegar, principal entrega el diff y hashes actuales junto al SHA;
el SHA por sí solo no describe estos cambios. Un editor por componente.

## Diagnóstico de la revisión de Daniel

La captura del 2026-09-19 demuestra una estructura de navegación con colores
básicos, no el sistema visual maestro completo. Hay títulos negros sobre oscuro,
ausencia de iconografía, jerarquía tipográfica débil, paneles planos repetitivos,
grandes vacíos y una cabecera que no transmite la identidad del concepto.
La barra de título nativa tiene un acento del sistema que compite con Foundry.
Los menús, bordes, superficies y distribución requieren diseño explícito.

La ausencia de perfil explica que no haya resultados; no explica esos defectos.
Los estados vacíos deben tener la misma calidad visual que una pantalla poblada.
A y B quedan parciales y pendientes de aceptación visual, no terminados.
Los tests funcionales no prueban parecido al concepto. La cifra previa de 20%
no es una medición válida de avance visual y no se reutiliza.

## Referencia y criterio visual

Concepto 02 del paquete RAIDFORGE_INTERFACE_OBJECTIVE_HANDOFF_v0.1.0.zip.
SHA-256: 802ac824b1ac129d39e846ef12c82173c90705084d94d7eefeaa1ca2be3245af.
Las cuatro artes fueron inspeccionadas en la sesión anterior; la captura de
Daniel vuelve a mostrar el concepto Foundry al lado de la app.
La marca final es DpsFoundry. El arte orienta material, proporción, jerarquía
y atmósfera; no se inserta como fondo ni se copian cifras/personajes.

| Elemento | Dirección comprobable en pantalla |
| --- | --- |
| Superficies | Carbón y acero oscuro con profundidad sutil, planos diferenciados y gradientes contenidos |
| Bordes | Aristas finas, separadores y realce interior coherentes; radios pequeños, sin tarjetas genéricas gigantes |
| Tipografía | Familia instalada o distribuible con licencia conocida; títulos claros, cuerpo legible, cifras dominantes; ningún título negro sobre oscuro |
| Iconos | Familia propia o permitida coherente en navegación, acciones y métricas; tamaño, trazo y alineación uniformes; no emojis como sustituto |
| Cabecera | Marca reconocible, contexto personaje/spec y estado de intercambio; no repetir títulos grandes sin función |
| Navegación | Icono y texto, selección naranja contenida, hover/foco/disabled visibles; distancias y alineación constantes |
| Composición | Sidebar proporcionada, cabecera compacta, cuadrícula de métricas y paneles de datos; espacio útil sin rellenar por decoración |
| Controles | Menús desplegables, tabs, tablas, scrollbar, tooltips y diálogos con el mismo lenguaje |
| Datos | DPS primero; pesos y comparación legibles; estados sin datos conservan estructura sin inventar valores |
| Ventana | Evaluar título oscuro nativo; cualquier marco propio debe conservar arrastre, resize, minimizar, maximizar, teclado y accesibilidad |

Especificar medidas y tokens efectivos en DPSFOUNDRY_DESIGN_SYSTEM.md antes de
multiplicar pantallas. Qt Widgets se conserva; no hay una limitación demostrada
que justifique migrar tecnología para resolver esta captura.
Iconos y recursos finales propios/permitidos; no extraer assets de WoW.

## Orden de trabajo y salidas

1. **A revisada: muestra visual en Qt.** Afinar tipografía, superficies, bordes,
   iconografía, controles y estados. Componer Home con contexto y paneles
   representativos; mostrar estado vacío y estado poblado de demostración
   inequívocamente identificado, con datos temporales fuera de perfiles reales.
   El resultado debe ejecutarse en la app, no ser únicamente un render.
2. **B revisada: aplicar a Core.** Tras revisión visual del principal y Daniel,
   extender a Setup, Character/Profile, Simulation, Compare, Recommendations,
   Link/Sync y Settings. Conservar flujos reales ya existentes durante la
   reorganización. Ningún control editable sin efecto (incluido text scale).
   Localizar los nuevos textos en ES/EN/PT-BR; no mantener el shell en inglés fijo.
3. **C: Link.** Panel/HUD compacto y expandido con perfil, pesos, score, comparación
   y transporte local. Adoptar el lenguaje Foundry con decoración reducida.
   Mantener scores en mouseover y comparativos e importación con decisión clara.
4. **D: acabado Foundry.** Validar el tema completo en Core y Link. Los otros tres
   temas solo demuestran intercambiabilidad de tokens; su pulido queda pendiente
   de autorización posterior, conforme al Scope actualizado.
5. **E: completar integración.** Cada área consume los servicios existentes;
   fixtures de revisión se sustituyen por datos reales, sin ruta ficticia
   permanente. Compare muestra la comparación y no solo redirige a Simulation.
6. **F: paquete y recorrido.** Revisión instalada y prueba de Daniel jugando:
   setup → perfil → análisis → recomendación → Link → pesos/score → refinamiento.
   Registrar evidencia por cada uno de los 13 criterios del Scope.

La próxima entrega se limita al punto 1, con revisión del sistema visual; no se
amplían ocho pantallas superficialmente antes de resolver su calidad compartida.

## Evidencia y condiciones de aceptación visual

- Capturas de la app Windows real, con fuentes renderizadas, junto al concepto
  a escala comparable: muestra vacía, poblada, menú abierto y diálogo.
- Revisar 1366×768 y 1920×1080; escalado Windows 100%, 125% y 150% cuando esté
  disponible. Registrar configuraciones efectivamente probadas y pendientes.
- Contraste objetivo 4.5:1 para texto normal y 3:1 para texto grande/controles
  relevantes; foco visible y navegación de teclado; sin truncar acciones críticas.
- Si la captura no muestra glifos, falla la comprobación visual; no se declara
  validado el aspecto por existir una imagen offscreen.
- Describir diferencias deliberadas con el concepto y comprobar las diez filas
  de la tabla visual. La aprobación de navegación no sustituye el acabado.
- El principal verifica ventana visible, no solo proceso existente. Daniel
  confirma la aceptación del diseño; ninguna prueba automatizada la reemplaza.

## Frontera de ejecución y no regresión

Terra: presentación Qt, tema, componentes/iconos propios y recursos UI,
comparison_table.py cuando sea presentación, i18n.py/locales, pruebas de UI,
DPSFOUNDRY_DESIGN_SYSTEM.md y DPSFOUNDRY_INTERFACE_ACCEPTANCE.md.
En C: presentación en ItemScoreProfiles.lua, DpsLab.lua, DpsLab.toc,
Localization.lua y módulos UI propios con pruebas correspondientes.
En F: empaquetado solo para recursos UI y arranque.
Principal: AGENTS, Scope, NEXT_TASK y este plan.

Reutilizar parser, perfiles, runner, comparación y transporte. No reescribirlos.
No tocar addon synthetic, seguridad/CI, datos personales, runs existentes,
escenarios/variantes ni ampliar capacidades. Guide y distribución siguen pausados.
Nuevas dependencias o cambios de contratos se justifican al principal antes
de ampliar el lote; no son el medio inicial para resolver el diseño.

Tras cambios de código: pruebas focales y suites requeridas por AGENTS con
Python del proyecto; declarar ejecutadas, aprobadas, omitidas y fallos.
Verificar detección/pegado manual, perfiles con equipo sin WoW, builds externas,
una simulación o comparación de 2–4, selección entre más de cuatro, errores,
nombres, borrado, limpieza con aviso, DPS/diferencias, progreso, pesos,
transferencia de builds reales, importación con copia y scores/trinkets.
SimC real requiere autorización concreta. Validación in-game: Daniel.

Entregar diff, capturas legibles, resultados de pruebas y pendientes reales.
El lote termina al entregar la muestra para revisión; no autoriza commit/push.
La planificación conserva el historial y no marca este objetivo como cumplido.
