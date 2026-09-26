# SCOPE_CORRECTION_0_1.md

## Autorización de Daniel — corrección de alcance obligatoria

Este documento tiene prioridad sobre cualquier tarea, contrato o autorización
previa en `docs/NEXT_TASK.md` o `AGENTS.md` que no esté directamente
relacionada con el objetivo único definido en la sección 1. Ninguna tarea
nueva puede aprobarse ni implementarse sin pasar primero la prueba de la
sección 2. Esta corrección permanece vigente hasta que Daniel la levante
explícitamente por escrito.

## 1. Objetivo único vigente

**Estado real de la suite (2026-09-19):** el core técnico (addon + app)
funciona de punta a punta para cualquier clase y especialización del juego,
verificado personalmente por Daniel en juego: comparación de hasta 4
loadouts, importación externa, pesos estadísticos, score de items, `simc.exe`
empaquetado, traducción a inglés/español/portugués. La suite se llama
**DpsFoundry**. El trabajo de construcción de interfaz visual reemplaza,
como objetivo operativo, a cualquier objetivo anterior de este documento.

**El único trabajo autorizado en este ciclo es construir una interfaz
funcional, coherente y guiada para DpsFoundry Core y DpsFoundry Link**,
reutilizando las capacidades que ya existen y sin reconstruir el núcleo
técnico que ya funciona.

El resultado debe permitir que un jugador use la suite sin conocer
SimulationCraft, archivos `.simc`, SavedVariables, contratos internos ni la
arquitectura del repositorio.

La experiencia general que debe transmitir la suite:

**analizar → decidir → sincronizar → jugar → refinar**

El objetivo no es dibujar una maqueta. El objetivo es convertir las
capacidades existentes en una experiencia usable.

### 1.1 Identidad de producto aprobada

**Suite: DpsFoundry.**

**Componente de escritorio: DpsFoundry Core** — centro de simulación,
análisis y decisión; recibe datos de Link; ejecuta los flujos de simulación
ya existentes; compara configuraciones; presenta recomendaciones, impacto
esperado, incertidumbre y límites; gestiona perfiles y sincronización; punto
futuro de recepción de retroalimentación resumida de Guide.
Descriptor: *Simulation · Analysis · Optimization*.

**Addon activo en este ciclo: DpsFoundry Link** — observa/capta la
información permitida del personaje; transporta el perfil entre WoW y Core;
recibe pesos estadísticos; calcula y muestra scores de equipamiento; ofrece
comparación rápida dentro de los límites ya soportados; muestra un HUD/panel
compacto de perfil, pesos, item score y estado de sincronización.
Descriptor: *Character · Gear Intelligence · Sync*.

**Componente futuro: DpsFoundry Guide** — asistente/trainer de ejecución y
rotación. Durante este ciclo: NO se implementa funcionalmente, NO se crea un
motor de entrenamiento, NO se amplía captura de combate para construirlo;
solo se preserva compatibilidad visual y una frontera futura de integración.
Descriptor futuro: *Combat Guidance · Training*.

### 1.2 Decisión estructural de interfaz

DpsFoundry tendrá **una sola arquitectura funcional de interfaz**. Queda
descartado: interfaz distinta por tema, navegación duplicada, layouts
incompatibles, cuatro versiones funcionales separadas. Los cuatro conceptos
visuales son **temas** (piel) sobre el mismo sistema de componentes,
navegación, jerarquía y estados — nunca comportamiento.

Temas oficiales: `arcane_vanguard` (01), `foundry` (02, **flagship/default**),
`runebound_command` (03), `celestial_foundry` (04).

**Alcance de este ciclo: solo `foundry` queda validado de punta a punta.**
Los otros tres se prueban únicamente para confirmar que el sistema de tokens
no está hardcodeado a un tema — no requieren pulido ni validación completa
todavía (ver sección 7, criterio ajustado).

### 1.3 Arquitectura visual generalizable

La interfaz debe funcionar con múltiples clases y specs sin crear un layout
distinto por cada una. La base visual común admite módulos variables para:
recurso principal, recursos secundarios, cooldowns/estados, pesos
estadísticos, perfil/loadout, equipo y score, resultados de simulación,
recomendaciones. Las particularidades de cada clase/spec se insertan en
módulos reservados; no se codifica la geometría alrededor de una sola clase.
Los colores de clase/spec son contexto secundario y nunca reemplazan los
tokens del tema activo. Esto autoriza **generalización visual**, no creación
de datos, rotaciones o conocimiento nuevo para clases no soportadas por el
núcleo existente.

### 1.4 Alcance mínimo de DpsFoundry Core

1. **Onboarding/Setup** — qué es Core y Link, requisitos locales, estado de
   conexión/importación, guía a la primera simulación.
2. **Home/Dashboard** — personaje/perfil activo, spec, sincronización,
   resumen del último análisis, recomendación principal, siguiente acción.
3. **Character/Profile** — perfil, equipo, talentos/loadout si existen,
   pesos vigentes, procedencia básica.
4. **Simulation** — escenario soportado, ejecución, progreso, resultado,
   error comprensible, sin exponer complejidad técnica innecesaria.
5. **Compare** — alternativas soportadas, estado A/B, diferencia,
   incertidumbre, limitaciones.
6. **Recommendations** — acciones sugeridas, impacto estimado, explicación
   breve, distinción entre dato medido/simulación/orientación.
7. **Link/Sync Center** — estado del intercambio, última información
   recibida, datos preparados para Link, pasos cuando WoW deba cerrarse.
8. **Settings** — configuración estrictamente necesaria, tema visual,
   escala/accesibilidad, rutas solo si el proyecto realmente las necesita.

### 1.5 Alcance mínimo de DpsFoundry Link

1. **Estado de Link** — perfil activo, personaje/spec, sincronización,
   vigencia del paquete de pesos, disponible/no disponible.
2. **HUD de perfil** — nombre corto, pesos vigentes, compacto/expandido, sin
   ocupar espacio de combate innecesario.
3. **Item scoring** visible en tooltip/panel.
4. **Comparación rápida** de piezas dentro de lo ya soportado.
5. **Sync/Export** — controles coherentes con el transporte local real;
   ninguna apariencia de conexión en tiempo real inexistente; mensajes de
   siguiente paso comprensibles.
6. **Tema** — mismo `theme_id` conceptual que Core, mismo layout, puede
   reducir decoración respecto de Core para legibilidad in-game.

### 1.6 Relación futura Core ↔ Guide

Core queda preparado para recibir en el futuro retroalimentación resumida de
Guide. En este ciclo solo se permite reservar el concepto en la arquitectura
de información y evitar decisiones de UI que bloqueen esa entrada futura. No
se permite implementar el trainer, inferencia de rotación, logging de combate
adicional ni recomendaciones nuevas bajo esta cláusula.

### 1.7 Decisión de dirección (2026-09-08): empaquetar, no reconstruir

Daniel evaluó construir un motor de simulación propio y decidió **no
hacerlo**. La vía elegida es empaquetar el binario real de SimulationCraft
dentro del instalador. Pendiente para cuando se active distribución: incluir
el aviso de licencia GPL v3 de SimulationCraft y la disponibilidad de su
código fuente — requisito legal, no ceremonia.

**Actualización (2026-09-19): el motor propio queda sin dueño asignado.** La
cuenta colaboradora que lo iba a investigar fue removida del proyecto. Se
mantiene en la lista de congelados de la sección 4, sin fecha, hasta que
Daniel decida retomarlo con algún agente.

### 1.8 Decisión de dirección (2026-09-14): interfaz antes que distribución

Publicación en CurseForge, donativos y auto-actualización quedan **pausados,
no cancelados**, hasta cerrar el baseline funcional de interfaz (sección 7).

## 2. Prueba de valor obligatoria

Antes de proponer o implementar una tarea, Codex responde en una frase:

> **¿Esta tarea hace que DpsFoundry Core o DpsFoundry Link sean más fáciles
> de instalar, entender o usar por un jugador dentro del flujo analizar →
> decidir → sincronizar → jugar → refinar?**

- Si es **no**, la tarea queda congelada.
- "Seguridad", "gobernanza", "procedencia", "refactor", "future-proofing",
  "limpieza" o "arquitectura" no son justificación suficiente por sí solas.
- Una tarea técnica de soporte solo entra si es necesaria para una función
  de interfaz incluida explícitamente en la sección 1.

## 3. Decisiones técnicas que se conservan

Este ciclo no reabre decisiones técnicas ya tomadas salvo que bloqueen la UI:
núcleo de parser/snapshot; runner existente de SimulationCraft;
escenarios/variantes existentes; comparación existente; transporte local
addon↔aplicación ya implementado; empaquetar SimC en vez de motor propio;
dirección PySide6 + Qt Widgets para Core, salvo limitación demostrable;
validación estricta de datos externos; separación entre datos y código
ejecutable.

## 4. Trabajo congelado explícitamente

No se inicia ni expande, salvo autorización nueva y explícita de Daniel:

- DpsFoundry Guide funcional; entrenador/analizador de combate.
- Motor de simulación propio (sin dueño asignado — ver 1.7).
- Nuevas matrices masivas de equipo/talentos; generación automática
  indiscriminada de combinaciones.
- Nuevo pipeline de knowledge; nueva adquisición automática de fuentes
  oficiales/notas de parche (se actualiza a mano).
- Expansión funcional a clases/specs solo para "probar la interfaz".
- Nuevas ceremonias de firma, SBOM, modelo de amenazas o gobernanza más allá
  del escaneo básico ya integrado. Excepción ya en cola, no congelada: firma
  de código (Windows code-signing) para cuando se active distribución —
  evita la advertencia de SmartScreen al descargar el instalador.
- Rediseño de CI que no sea indispensable para probar la UI.
- Auto-actualizador; sistema de donaciones; publicación en CurseForge —
  pausados, no cancelados (ver 1.8).
- Migración masiva del nombre interno `DpsLab`/`RaidForge` a `DpsFoundry` en
  todo el código.
- Separación física inmediata del addon actual en dos paquetes si no es
  necesaria para construir la interfaz.
- Cualquier archivo del addon marcado como "synthetic" (placeholder previo a
  esta corrección, sin uso real).

## 5. Metodología obligatoria de construcción

**A — Sistema visual maestro:** design tokens semánticos, tipografía,
escalas, espaciado, bordes, estados, botones, tabs, cards, tablas, gráficos,
tooltips, estados loading/empty/error/unavailable, slots variables por
clase/spec. Una sola especificación base.

**B — Shell funcional de Core:** navegación y componentes con datos
controlados. No conectar todas las capacidades a la vez.

**C — Shell funcional de Link:** HUD/panel compacto y estados esenciales.

**D — Tema `foundry`:** aplicarlo por completo sobre los componentes de B y
C — es la referencia. Los otros tres temas se prueban solo para validar que
el sistema de tokens no está hardcodeado (ver 1.2); su pulido queda para un
ciclo posterior.

**E — Integración progresiva:** conectar la UI a capacidades reales
(perfil, importación, simulación, resultados, pesos, score, comparación,
sincronización). Cada conexión reemplaza un fixture/control sintético
existente; no crea un camino paralelo permanente.

**F — Recorrido de usuario:** validar instalación/configuración inicial,
perfil disponible, análisis/simulación, lectura de recomendación,
transferencia/uso en Link, revisión de item score/pesos, regreso a Core para
refinar.

## 6. Reglas de implementación visual

1. El arte conceptual es referencia de dirección, no fuente de datos,
   geometría pixel-perfect ni texto contractual.
2. No copiar errores de texto, nombres ni números ficticios de los renders.
3. No introducir assets de terceros extraídos de WoW.
4. Los iconos y recursos finales deben ser propios, permitidos o generados
   para el proyecto.
5. El tema no puede modificar lógica, resultados, cálculos ni permisos.
6. Estados críticos no dependen solo del color.
7. Debe soportarse escalado de texto y densidad razonable para pantallas
   comunes.
8. La UI debe ofrecer modo compacto donde corresponda en Link.

## 7. Criterios de aceptación del ciclo

1. Core tiene interfaz funcional navegable, no una maqueta.
2. Un jugador llega desde setup hasta una simulación/análisis sin terminal
   ni edición manual de archivos en el flujo normal previsto.
3. Core presenta resultados, recomendaciones y comparación soportada con
   jerarquía comprensible.
4. Link dispone de panel/HUD para perfil, pesos, item scoring y sync.
5. La interacción Link↔Core respeta el transporte que realmente existe.
6. Existe una sola arquitectura UI.
7. El sistema de tokens permite aplicar temas sin cambiar layout,
   **demostrado con `foundry`**; los otros tres quedan pendientes de una
   autorización posterior para su pulido completo.
8. `foundry` es el tema predeterminado.
9. La arquitectura admite módulos visuales por clase/spec sin hardcodear
   toda la interfaz a una especialización.
10. Guide sigue sin implementación funcional.
11. El núcleo de simulación, comparación y scoring no fue reescrito solo
    para acomodar la UI.
12. Los estados de error, sin datos, incompatibilidad y proceso en curso
    son comprensibles para un usuario no técnico.
13. El recorrido de usuario de la Etapa F puede demostrarse de extremo a
    extremo, **verificado por Daniel jugando**, no por el reporte de sesión.

## 8. Formato de reporte obligatorio

Al final de cada sesión, en lenguaje llano, sin JSON de gobernanza:

1. Qué parte visible de Core o Link puede usar ahora un jugador que antes
   no podía usar.
2. Qué flujo concreto de usuario quedó más cerca de completarse.
3. Si se tocó algo fuera de UI/integración de UI, y por qué.
4. Qué queda bloqueando la siguiente experiencia visible.
5. Qué porcentaje aproximado de la sesión fue directamente hacia el
   objetivo de interfaz.

Si el punto 1 queda vacío dos sesiones seguidas, la siguiente sesión se
dedica exclusivamente a explicar el bloqueo concreto, sin nueva
infraestructura.

## 9. Coordinación de cuentas — histórico, inactivo

**La cuenta colaboradora fue removida del proyecto (2026-09-19).** Esta
sección queda como referencia histórica de cómo se coordinó mientras existió
(contrato de datos previo a trabajo paralelo, frontera técnica escrita,
rama protegida, reportes separados) — no aplica mientras el proyecto tenga
una sola cuenta activa. Si en el futuro vuelve a haber una segunda cuenta,
se retoma desde aquí en vez de reinventarla.

Confirmar en GitHub → Settings → Branches que "Include administrators" /
"Enforce for administrators" esté activado, para que la protección de `main`
también aplique a la cuenta principal.

## 10. Vigencia

Esta corrección es la disciplina operativa permanente del proyecto — no
expira al cerrar un objetivo. Solo la sección 1 y el historial cambian con
cada ciclo; las demás secciones se mantienen salvo que Daniel decida
modificarlas explícitamente, por separado de un cambio de objetivo.

Este ciclo específico (interfaz de Core + Link) permanece vigente hasta que
se cumplan los criterios de la sección 7. Solo Daniel puede: cerrarlo,
reemplazarlo, ampliar Guide, reactivar distribución/donaciones/auto-update,
autorizar una separación física distinta de los componentes, o cambiar la
identidad visual flagship.

## Historial de objetivos cerrados

- 2026-09-08: Restauración de Druida real de punta a punta — verificado en
  juego.
- ~2026-09-09/10: Balance de Druida como segunda spec; multi-loadout (hasta
  4); nombres de build identificables; pesos estilo Pawn; `simc.exe`
  empaquetado — verificado visualmente.
- ~2026-09-10/12: Generalización a todas las clases y especializaciones del
  juego — verificado por Daniel en juego.
- 2026-09-17: Tabla comparativa Qt lado a lado — verificado por Daniel
  (commit `49d88bb`, rama `codex/live-export-balance-package`).
- 2026-09-19: Score de items (addon + app) con pesos por defecto vía SimC;
  importación de build externa por string de talentos; traducciones a
  inglés, español y portugués — verificado por Daniel (commit `47dc4aa`,
  misma rama; import por string aún pendiente de revisión independiente).
- 2026-09-19: Identidad de marca del ciclo de interfaz definida — suite
  **DpsFoundry**, componentes **Core**, **Link**, **Guide** (futuro).
