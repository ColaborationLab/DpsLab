# SCOPE_CORRECTION_0_1.md

## Autorización de Daniel — corrección de alcance obligatoria

Este documento tiene prioridad sobre cualquier tarea, contrato o autorización
previa en `docs/NEXT_TASK.md` o `AGENTS.md` que no esté directamente
relacionada con el objetivo único definido en la sección 1. Ninguna tarea
nueva puede aprobarse ni implementarse sin pasar primero la prueba de la
sección 2. Esta corrección permanece vigente hasta que Daniel la levante
explícitamente por escrito.

## Historial breve de objetivos cumplidos

- 2026-09-10 — Comparación de loadouts de Druida Balance y Restauración, con simulación individual o comparativa, nombres y resultados en WoW: cumplido.
- 2026-09-12 — Exportación y comparación multiclase y multiespecialización, con limpieza manual de la interfaz: cumplido por confirmación de Daniel; publicado en d354f9c.
- 2026-09-12 — Perfiles locales con equipo, builds reales y externas, simulación desde perfiles y limpieza con confirmación: cierre aprobado por Daniel y publicado en dd61f94. La base genérica de pesos y builds sugeridas quedó pendiente y se incorpora explícitamente al objetivo actual; este cierre no acredita esa función.

- 2026-09-13 — Perfiles de pesos editables, importación elegida y scores en tooltips mouseover y comparativos: aprobado visualmente por Daniel y publicado en 11767d3. Defaults trazables en 31 specs; ocho sin defaults permanecen como limitación documentada, sin acreditar simulación real de las 39.

- 2026-09-17 — Comparador Qt y navegación del addon: objetivo cerrado por cambio de objetivo de Daniel, tras aprobación visual del 2026-09-16; ajustes de tabla incorporados localmente. Commit local 49d88bb; push pendiente.

- 2026-09-18 — Suite ES/EN/PT-BR y documentación: objetivo cerrado por cambio de objetivo de Daniel. Revisión técnica detecta localización parcial y pruebas/empaquetado pendientes; correcciones previas a distribución registradas en docs/PENDING_COMMIT_REVIEW_2026_09_18.md. Cambios todavía sin commit; no se acredita publicación ni validación visual multilingüe.

## Transición de objetivo — 2026-09-19

Distribución, CurseForge, donaciones y auto-actualización quedan pausadas por instrucción de Daniel; no se registran como cumplidas. Los avances Qt y de localización anteriores fueron integrados en main mediante PR #12 el 2026-09-19. Las notas fechadas anteriores conservan su estado al momento de escribirse.

Las cláusulas siguientes se incorporan al Scope existente desde el borrador de interfaz entregado por Daniel. La marca vigente es DpsFoundry; los nombres antiguos del paquete de referencias se conservan solo como procedencia. Esta edición sustituye las restricciones anteriores incompatibles con el ciclo de interfaz.

## 1. Objetivo único vigente del nuevo ciclo

El único trabajo autorizado en este ciclo será **construir una interfaz
funcional, coherente y guiada para DpsFoundry Core y DpsFoundry Link**, reutilizando
las capacidades que ya existen en el proyecto y sin reconstruir el núcleo
técnico que ya funciona.

El resultado debe permitir que un jugador use la suite sin conocer
SimulationCraft, archivos `.simc`, SavedVariables, contratos internos ni la
arquitectura del repositorio.

La experiencia general que debe transmitir la suite es:

**analizar → decidir → sincronizar → jugar → refinar**

El objetivo no es dibujar una maqueta. El objetivo es convertir las capacidades
existentes en una experiencia usable.

---

## 1.1 Identidad de producto aprobada

### Suite

**DpsFoundry**

DpsFoundry es el nombre visible de la suite.

### Componente de escritorio

**DpsFoundry Core**

Función:
- centro de simulación, análisis y decisión;
- recepción de datos provenientes de Link;
- ejecución de los flujos de simulación ya existentes;
- comparación de configuraciones cuando la capacidad esté ya soportada;
- presentación de recomendaciones, impacto esperado, incertidumbre y límites;
- gestión de perfiles y sincronización;
- punto futuro de recepción de retroalimentación resumida de DpsFoundry Guide.

Descriptor recomendado:

**Simulation · Analysis · Optimization**

### Addon activo en este ciclo

**DpsFoundry Link**

Link no se define como un simple sincronizador.

Funciones de producto:
- observar/captar la información permitida del personaje;
- transportar el perfil entre WoW y Core según los mecanismos ya aprobados;
- recibir/captar pesos estadísticos producidos por el flujo analítico
  correspondiente;
- aplicar esos pesos para calcular y mostrar scores de equipamiento;
- ofrecer comparación rápida de piezas dentro de los límites que ya soporte el
  proyecto;
- mostrar un HUD/panel compacto de perfil, pesos estadísticos, item score y
  estado de sincronización;
- servir como capa de inteligencia in-game complementaria a Core.

Descriptor recomendado:

**Character · Gear Intelligence · Sync**

### Componente futuro

**DpsFoundry Guide**

Guide será el asistente/trainer de ejecución y rotación.

Durante este ciclo:
- NO se implementa funcionalmente;
- NO se crea un motor de entrenamiento;
- NO se amplía captura de combate para construirlo;
- únicamente se preserva compatibilidad visual y una frontera futura de
  integración para que Core pueda recibir más adelante una retroalimentación
  resumida del trainer.

Descriptor futuro:

**Combat Guidance · Training**

---

## 1.2 Decisión estructural de interfaz

DpsFoundry tendrá **una sola arquitectura funcional de interfaz**.

Queda expresamente descartado:
- construir una interfaz distinta por tema;
- duplicar navegación;
- mantener layouts incompatibles;
- crear cuatro versiones funcionales separadas.

Los cuatro conceptos visuales aprobados son **temas** sobre el mismo sistema de
componentes, navegación, jerarquía y estados.

### Tema insignia y predeterminado

**Foundry** — Concepto visual 02.

Características:
- grafito / carbón;
- metal oscuro y acero;
- naranja de forja como acento primario;
- verde reservado para confirmaciones/mejoras;
- paneles robustos y técnicos;
- decoración contenida que nunca compite con los datos.

### Temas oficiales

1. `arcane_vanguard` — Concepto 01.
2. `foundry` — Concepto 02 — **flagship/default**.
3. `runebound_command` — Concepto 03.
4. `celestial_foundry` — Concepto 04.

Los temas cambian apariencia, no comportamiento.

---

## 1.3 Arquitectura visual generalizable

La interfaz debe funcionar con múltiples clases y especializaciones sin
crear un layout distinto por cada una.

La base visual común debe admitir módulos variables para:
- recurso principal;
- recursos secundarios;
- cooldowns o estados relevantes;
- pesos estadísticos;
- perfil/loadout;
- equipo y score;
- resultados de simulación;
- recomendaciones.

Las características particulares de cada clase/spec se insertan en módulos
reservados. No se codifica la geometría principal alrededor de una sola clase.

Los colores de clase/spec son una capa secundaria de contexto y nunca reemplazan
los tokens del tema activo.

Este alcance autoriza **generalización visual**, no la creación de datos,
rotaciones o conocimiento nuevo para clases que todavía no estén soportadas por
el núcleo existente.

---

## 1.4 Alcance mínimo de DpsFoundry Core

La primera arquitectura funcional de Core debe contemplar estas áreas:

1. **Onboarding / Setup**
   - explicar qué es Core y qué es Link;
   - detectar o permitir elegir los requisitos locales ya soportados;
   - mostrar estado de conexión/importación;
   - guiar al usuario hacia su primera simulación.

2. **Home / Dashboard**
   - personaje/perfil activo;
   - especialización;
   - estado de sincronización;
   - resumen del último análisis;
   - recomendación principal;
   - accesos claros a siguiente acción.

3. **Character / Profile**
   - perfil activo;
   - equipo;
   - talentos/loadout si los datos ya existen;
   - pesos estadísticos vigentes;
   - procedencia básica y estado.

4. **Simulation**
   - selección de escenario ya soportado;
   - ejecución mediante las capacidades existentes;
   - progreso visible;
   - resultado;
   - error comprensible;
   - sin exponer complejidad técnica innecesaria por defecto.

5. **Compare**
   - comparación explícita de alternativas soportadas;
   - estado A/B;
   - diferencia;
   - incertidumbre cuando exista;
   - limitaciones del resultado.

6. **Recommendations**
   - acciones sugeridas;
   - impacto estimado;
   - explicación breve;
   - distinción entre dato medido, simulación y orientación.

7. **Link / Sync Center**
   - estado del intercambio con DpsFoundry Link;
   - última información recibida;
   - datos preparados para Link;
   - pasos necesarios cuando WoW deba cerrarse o abrirse según el transporte
     real existente.

8. **Settings**
   - configuración estrictamente necesaria para uso;
   - tema visual;
   - escala/accesibilidad;
   - rutas o dependencias solo cuando el proyecto realmente las necesite.

La navegación puede refinarse durante implementación, pero estas funciones no
deben fragmentarse en flujos incoherentes.

---

## 1.5 Alcance mínimo de DpsFoundry Link

Link debe ser pequeño en pantalla, pero completo en sus entregables.

Debe contemplar:

1. **Estado de Link**
   - perfil activo;
   - personaje/spec;
   - estado de sincronización;
   - vigencia del paquete de pesos;
   - estado disponible/no disponible claramente visible.

2. **HUD de perfil**
   - nombre corto del perfil;
   - pesos estadísticos vigentes;
   - opción compacta y expandida;
   - sin ocupar espacio de combate innecesario.

3. **Item scoring**
   - score de pieza equipada;
   - score de pieza evaluada cuando el dato esté disponible;
   - diferencia relativa;
   - indicador claro de mejora/empeoramiento;
   - no presentar el score como verdad universal fuera del perfil/pesos activos.

4. **Gear / Stats**
   - resumen de estadísticas;
   - pesos;
   - score;
   - comparación rápida.

5. **Sync / Export**
   - controles y estados coherentes con el transporte local real;
   - ninguna apariencia de conexión en tiempo real si técnicamente no existe;
   - mensajes de siguiente paso comprensibles.

6. **Tema**
   - Link adopta el mismo `theme_id` conceptual que Core;
   - conserva el mismo layout para los cuatro temas;
   - puede reducir decoración respecto de Core para mantener legibilidad in-game.

---

## 1.6 Relación futura Core ↔ Guide

Core debe quedar preparado para recibir en el futuro una retroalimentación
resumida de Guide sobre ejecución/rotación.

En este ciclo únicamente se permite:
- reservar el concepto en la arquitectura de información;
- evitar decisiones de UI que bloqueen esa futura entrada;
- definir, si resulta necesario para desacoplar la interfaz, un placeholder
  tipado o contrato conceptual sin datos reales.

No se permite implementar el trainer, inferencia de rotación, logging de combate
adicional ni recomendaciones nuevas bajo esta cláusula.

---

## 2. Prueba de valor obligatoria

Antes de proponer o implementar una tarea durante este ciclo, Codex debe
responder en una frase simple:

> **¿Esta tarea hace que DpsFoundry Core o DpsFoundry Link sean más fáciles de
> instalar, entender o usar por un jugador dentro del flujo
> analizar → decidir → sincronizar → jugar → refinar?**

- Si la respuesta es **sí**, la tarea puede evaluarse dentro de este alcance.
- Si la respuesta es **no**, queda congelada.
- “Seguridad”, “gobernanza”, “procedencia”, “refactor”, “future-proofing”,
  “limpieza” o “arquitectura” no son justificación suficiente por sí solas.
- Una tarea técnica de soporte solo entra si es necesaria para una función de
  interfaz incluida explícitamente en este documento.

---

## 3. Decisiones técnicas que se conservan

Este ciclo no reabre decisiones técnicas ya tomadas salvo que bloqueen la UI.

Se conserva:
- el núcleo de parser/snapshot;
- el runner existente de SimulationCraft;
- escenarios/variantes existentes;
- comparación existente;
- transporte local addon ↔ aplicación ya implementado;
- decisión previa de **empaquetar SimulationCraft y no construir un motor de
  simulación propio**;
- dirección previamente estudiada de **PySide6 + Qt Widgets** para Core, salvo
  que una limitación demostrable obligue a reconsiderarla;
- validación estricta de datos externos;
- separación entre datos y código ejecutable.

---

## 4. Trabajo congelado durante este ciclo

No se inicia ni expande, salvo autorización nueva y explícita de Daniel:

- DpsFoundry Guide funcional;
- entrenador/analizador de combate;
- motor de simulación propio;
- nuevas matrices masivas de equipo/talentos;
- generación automática indiscriminada de combinaciones;
- nuevo pipeline de knowledge;
- nueva adquisición automática de fuentes;
- expansión funcional a clases/specs solo para “probar la interfaz”;
- nuevas ceremonias de firma, SBOM, modelo de amenazas o gobernanza;
- rediseño de CI que no sea indispensable para probar la UI;
- auto-actualizador;
- sistema de donaciones;
- publicación CurseForge;
- migración masiva del nombre interno `DpsLab` a `DpsFoundry`;
- separación física inmediata del addon actual en dos paquetes si esa operación
  no es necesaria para construir la interfaz.

Los objetivos de distribución, actualización y donaciones quedan **pausados, no
cancelados**, hasta cerrar el baseline funcional de interfaz.

---

## 5. Metodología obligatoria de construcción

### Etapa A — Sistema visual maestro

Definir primero:
- design tokens semánticos;
- tipografía y escalas;
- espaciado;
- bordes;
- estados;
- botones;
- tabs;
- cards;
- tablas;
- gráficos;
- tooltips;
- estados loading/empty/error/unavailable;
- slots variables para clase/spec.

Debe existir una sola especificación base.

### Etapa B — Shell funcional de Core

Implementar navegación y componentes con datos controlados.
No conectar todas las capacidades a la vez.

### Etapa C — Shell funcional de Link

Implementar el HUD/panel compacto y los estados esenciales.

### Etapa D — Motor de temas

Aplicar los cuatro temas sobre los mismos componentes.

`foundry` debe estar completo primero y servir de referencia.
Los otros tres deben demostrar equivalencia funcional sin cambiar layouts.

### Etapa E — Integración progresiva

Conectar la UI a capacidades reales ya existentes:
- perfil;
- importación;
- simulación;
- resultados;
- pesos;
- score;
- comparación;
- sincronización.

Cada conexión debe reemplazar un fixture/control sintético existente; no crear
un camino paralelo permanente.

### Etapa F — Recorrido de usuario

Validar al menos:
1. instalación/configuración inicial;
2. perfil disponible;
3. análisis/simulación;
4. lectura de recomendación;
5. transferencia/uso en Link;
6. revisión de item score/pesos;
7. regreso a Core para refinar.

---

## 6. Reglas de implementación visual

1. El arte conceptual es **referencia de dirección**, no fuente de datos,
   geometría pixel-perfect ni texto contractual.
2. No copiar errores de texto, nombres ficticios, números ficticios o
   personajes mostrados en los renders.
3. No introducir assets de terceros extraídos de WoW.
4. Las imágenes conceptuales pueden orientar proporción, material, atmósfera y
   jerarquía; los iconos y recursos finales deben ser propios, permitidos o
   generados para el proyecto.
5. El tema no puede modificar lógica, resultados, cálculos ni permisos.
6. Estados críticos no dependen solo del color.
7. Debe soportarse escalado de texto y una densidad razonable para pantallas
   comunes.
8. La UI debe ofrecer modo compacto donde corresponda en Link.

---

## 7. Criterios de aceptación del ciclo

El objetivo se considera cumplido cuando Daniel pueda comprobar que:

1. DpsFoundry Core tiene una interfaz funcional navegable, no una maqueta.
2. Un jugador puede llegar desde setup hasta una simulación/análisis sin usar
   terminal ni editar archivos manualmente en el flujo normal previsto.
3. Core presenta resultados, recomendaciones y comparación soportada con una
   jerarquía comprensible.
4. DpsFoundry Link dispone de panel/HUD para perfil, pesos estadísticos,
   item scoring y sync.
5. La interacción Link ↔ Core respeta el transporte que realmente existe y no
   simula capacidades de conexión inexistentes.
6. Existe una sola arquitectura UI.
7. Los cuatro temas pueden aplicarse sin cambiar layout ni comportamiento.
8. `foundry` es el tema predeterminado.
9. La arquitectura admite módulos visuales por clase/spec sin hardcodear toda
   la interfaz a una especialización.
10. Guide sigue sin implementación funcional.
11. El núcleo de simulación, comparación y scoring no fue reescrito solo para
    acomodar la UI.
12. Los estados de error, sin datos, incompatibilidad y proceso en curso son
    comprensibles para un usuario no técnico.
13. El recorrido de usuario definido en la Etapa F puede demostrarse de extremo
    a extremo con las capacidades que estén autorizadas y disponibles.

---

## 8. Formato de reporte obligatorio

Al final de cada sesión, Codex reportará en lenguaje llano:

1. Qué parte visible de Core o Link puede usar ahora un jugador que antes no
   podía usar.
2. Qué flujo concreto de usuario quedó más cerca de completarse.
3. Si se tocó algo fuera de UI/integración de UI y por qué.
4. Qué queda bloqueando la siguiente experiencia visible.
5. Qué porcentaje aproximado de la sesión fue directamente hacia el objetivo
   de interfaz.

Sin JSON de gobernanza en el reporte al usuario.

---

## 9. Coordinación entre cuentas/agentes

La ejecución queda a cargo del agente principal y de Terra cuando Daniel active el encargo preparado. La colaboración externa anterior permanece cerrada operativamente; retirar su membresía organizacional sigue pendiente y no bloquea este ciclo.

Se mantiene el principio vigente:
- una sola cuenta modifica documentos de gobierno;
- trabajo paralelo solo con frontera escrita;
- ninguna cuenta interpreta un render como autorización de funcionalidad;
- `main` no se modifica sin el flujo aprobado por Daniel;
- cada agente informa su propio trabajo.

Para UI, las fronteras naturales recomendadas son:
- Core / escritorio;
- Link / addon;
- design system / tokens;
- pruebas de presentación.

Dos agentes no deben editar el mismo conjunto de componentes simultáneamente.

---

## 10. Vigencia

Estas cláusulas, incorporadas por instrucción de Daniel, permanecen vigentes hasta
que el baseline funcional de **DpsFoundry Core + DpsFoundry Link** cumpla los
criterios de la sección 7.

Solo Daniel puede:
- cerrarlo;
- reemplazarlo;
- ampliar Guide;
- reactivar distribución/donaciones/auto-update;
- autorizar una separación física distinta de los componentes;
- cambiar la identidad visual flagship.
