# AGENTS.md

## Propósito

Coordinar el trabajo futuro en DpsFoundry sin ampliar implícitamente su
alcance ni romper la integridad de perfiles, escenarios, variantes o
ejecuciones.

## Estado real de la suite (2026-09-19)

La suite se llama **DpsFoundry**. Tiene tres componentes: **Core**
(app de escritorio: simulación, análisis, optimización), **Link** (addon
activo: observación de personaje, transporte, item scoring) y **Guide**
(futuro: entrenador/rotación — sin empezar).

El núcleo técnico (Core + Link) funciona de punta a punta para cualquier
clase y especialización del juego, con datos reales, verificado en juego por
Daniel: comparación de hasta 4 loadouts identificados por nombre,
importación de build externa por string de talentos, pesos estadísticos por
spec, score de equipamiento, `simc.exe` empaquetado en el instalador,
traducción a inglés/español/portugués.

**El objetivo activo y el alcance exacto del ciclo en curso viven en
`SCOPE_CORRECTION_0_1.md`, sección 1** — ese archivo es la fuente de verdad
sobre qué se está construyendo ahora mismo. Este documento no repite esa
descripción para no quedar desactualizado cada vez que el objetivo cambia.

El detalle de contratos y cierres históricos anteriores a esta corrección
vive en `docs/NEXT_TASK.md` como registro de auditoría; no es necesario
leerlo para trabajar en el objetivo vigente.

## Integridad obligatoria

- No modificar `profiles/flasil.simc`; conservar también `flasil.simc` raíz como respaldo.
- `flasil.simc.html` es referencia histórica y fuente de auditoría, nunca perfil de entrada.
- No modificar escenarios, variantes ni artefactos de runs existentes durante análisis.
- Calcular SHA-256 antes y después de operaciones que usen archivos protegidos.
- Crear perfiles efectivos y resultados JSON mediante escritura atómica cuando corresponda.
- Nunca sobrescribir una ejecución previa; cada simulación usa una carpeta nueva.
- No guardar rutas personales absolutas en archivos versionados.
- No ejecutar `simc.exe` sin autorización explícita para esa ejecución concreta.

## Seguridad transversal obligatoria

- Mantener las prácticas de seguridad ya integradas (validación de entradas
  no confiables, prohibición de convertir datos en código ejecutable,
  prohibición de credenciales en el repositorio) sin ampliarlas. No iniciar
  trabajo nuevo de SBOM, firma de releases, modelo de amenazas formal o
  adquisición automática de fuentes salvo autorización nueva y explícita de
  Daniel que mencione esa característica por nombre. Ver
  `SCOPE_CORRECTION_0_1.md`, sección 4 — ahí también está el detalle de qué
  quedó en cola (como la firma de releases) frente a lo que sigue sin fecha.

## Restricciones de alcance

- No iniciar comparaciones de equipo o talentos sin una tarea expresamente aprobada.
- No ejecutar matrices ni generar combinaciones automáticamente sin aprobación.
- No procesar todavía Weekly Reward Choices, currencies, high watermarks o achievements.
- **Guide** (entrenador/rotación) y el **motor de simulación propio**
  permanecen fuera de alcance — ver `SCOPE_CORRECTION_0_1.md`, sección 4.
- El alcance exacto vigente es el de `SCOPE_CORRECTION_0_1.md`, sección 1 —
  no se repite aquí para evitar que quede desactualizado.

## Verificación

- Ejecutar toda la suite después de cambios de código y reportar por separado
  pruebas aprobadas, subtests, fallos y código de salida.
- Mantener compatibilidad de lectura con esquemas históricos.
- Regenerar snapshots o resúmenes existentes solo cuando la tarea lo solicite explícitamente.
- Informar hashes protegidos y cualquier artefacto ignorado por `.gitignore`.

## Quality gate y autorizaciones

- Cuando Daniel cambie el objetivo de la sección 1 de `SCOPE_CORRECTION_0_1.md`,
  tratar el objetivo anterior como cumplido, añadir una línea breve y fechada
  en su historial de objetivos cumplidos, recalcular el SHA-256 real del
  documento y actualizar `protected_files` antes de iniciar el objetivo nuevo.
- Mientras `SCOPE_CORRECTION_0_1.md` esté vigente, el cierre de alcance para
  tareas dentro de su objetivo único NO requiere contrato formal, `task_id`,
  ni "auditoría independiente declarada y procedimental". Basta una entrada
  breve en el archivo de tareas activo con: qué se hizo, qué archivo(s) se
  tocaron, y el resultado de la prueba de valor (sección 2 de la corrección de
  alcance). La revisión directa de Daniel sustituye la auditoría formal durante
  este ciclo.
- Cuando Daniel edite `AGENTS.md` o `SCOPE_CORRECTION_0_1.md` directamente, la
  siguiente tarea abierta debe primero recalcular el hash SHA-256 real de esos
  archivos y registrarlo como nueva línea base en `protected_files`, antes de
  continuar con cualquier otro trabajo. Esto es una actualización mecánica de
  referencia, no requiere contrato completo ni auditoría, y nunca se resuelve
  revirtiendo la edición de Daniel para hacer coincidir el hash anterior.

## Protocolo de agentes subordinados y trabajo remoto — histórico, inactivo

**La cuenta colaboradora fue removida del proyecto (2026-09-19).** Ver
`SCOPE_CORRECTION_0_1.md`, sección 9. Lo de abajo queda como referencia
histórica del protocolo formal original — solo aplica si Daniel decide
explícitamente volver a un esquema de Issues/contrato completo para un
colaborador externo nuevo. Mientras el proyecto tenga una sola cuenta activa,
no rige nada de esta sección.

- La colaboración remota, en su versión formal, se regía por
  `docs/REMOTE_AGENT_WORKFLOW.md` y las plantillas de `.github/`.
- Todo colaborador externo, bajo ese esquema formal, debía recibir un Issue
  con `task_id`, baseline, allowlist, exclusiones, pruebas y criterio de
  cierre, trabajar en una rama `agent/<task_id>/<slug>` de su fork privado y
  entregar un PR; nunca directamente en `main`.
- `desktop-app/src/**`, `addon/**`, `knowledge/**`, `security/**`, CI,
  settings, secretos, perfiles, escenarios, resultados, SimulationCraft,
  observación real, releases y claves permanecían bajo responsabilidad
  exclusiva de la cuenta principal.
- Un PR, una prueba verde o una revisión técnica nunca equivalen a
  aprobación, merge, commit, push o publicación, en ningún esquema, formal o
  liviano.
