# AGENTS.md

## Propósito

Coordinar el trabajo futuro en DpsLab sin ampliar implícitamente su alcance ni
romper la integridad de perfiles, escenarios, variantes o ejecuciones.

## Estado confirmado

- La aplicación Python vive en `desktop-app/` y requiere Python 3.11 o posterior.
- El parser de perfiles y el snapshot `results/flasil_snapshot.json` están implementados.
- El snapshot usa esquema `0.1`, dataclasses tipadas y separa `equipped_gear` de `bag_gear`.
- El runner local de SimulationCraft está implementado con `subprocess`, lista de argumentos, `shell=False`, timeout y artefactos aislados por run.
- El intérprete genera `run_summary.json`; el código actual usa esquema `0.3` y acepta metadatos/resúmenes 0.1, 0.2 y 0.3.
- Existen escenarios TOML reproducibles e independientes de la configuración local.
- Existen variantes TOML de perfil, perfiles efectivos binarios y verificación before/after.
- La baseline formal canónica es `results/runs/20260715T072501.415324Z-95439dae`.
- Se implementaron auditorías semánticas, comparativas y profundas reproducibles.
- El comparador A/B de collar schema 0.1 está implementado, pero no se ha
  ejecutado ni existe un `comparison_result` real.
- El Subbloque 2.2.b1 permanece aprobado (`block_2_2_b1_approved`): el alta
  planificada pura y copy-on-write conserva intacto su contrato.
- El Subbloque 2.2.b2 está implementado, auditado y publicado en
  `d8bc2406b6b9ea2acc46bf16e5b4811d01573243`: la persistencia transaccional
  reutiliza el candidato puro, confirma el estado durable y mantiene
  idempotencia sin escritura bajo el modelo single-writer declarado.
- Automation Foundation fue implementada, auditada mediante independencia
  declarada y procedimental, y registrada en el commit
  `3828c098946f6842885fc520f841ef4fdb4e12af`
  (`automation_foundation_0_1_committed`).
- La decisión humana posterior aprobó el cierre GitHub inicialmente publicado.
  GitHub Automation 0.1 fue implementada, auditada y publicada. El `main`
  local, `origin/main` y el remoto vivo apuntan a
  `bf2db644bfebeb07246f8e967f39101a7aa3e77a`.
- Las pruebas focales de 2.2.b1 registraron 20 pruebas aprobadas, 55 subtests
  aprobados y código de salida 0.
- La incidencia de fixture de `comparison_models` fue corregida únicamente en
  su prueba mediante el commit
  `6bff15c2d6b03c96a65ed520ca4f800161d53d2c`, auditado y publicado.
- La baseline funcional aprobada registró 208/208 pruebas. La ejecución viva
  de GitHub Actions `29645964849`, sobre el Python 3.13.14 fijado, aprobó Policy
  and contract, Tools tests y Functional suite.

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
  `SCOPE_CORRECTION_0_1.md`, sección 3.

## Restricciones de alcance

- No iniciar comparaciones de equipo o talentos sin una tarea expresamente aprobada.
- No ejecutar matrices ni generar combinaciones automáticamente sin aprobación.
- No implementar GUI, addon de WoW, módulos multiclase o entrenador de combate sin alcance aprobado.
- No procesar todavía Weekly Reward Choices, currencies, high watermarks o achievements.
- Alcance aprobado para el ciclo actual: pantalla mínima de ejecución en la
  app y visualización del resultado real en el addon, para Druida
  Restauración, según `SCOPE_CORRECTION_0_1.md`. Ninguna otra clase, GUI
  adicional o módulo nuevo sin nueva aprobación explícita de Daniel.

## Verificación

- Ejecutar toda la suite después de cambios de código y reportar por separado
  pruebas aprobadas, subtests, fallos y código de salida. La baseline funcional
  aprobada es 208/208 y su verificación remota concluyó satisfactoriamente.
- La observación intermitente de Python 3.12 sobre `updated_at` fue
  diagnosticada como dependencia incorrecta del avance estricto del reloj de
  pared. Quedó corregida, auditada y publicada en
  `b19fb6eae2a44240467cc8684adfd2733e09f0bb`: la verificación local Python
  3.12.13 pasó 213/213 y GitHub Actions run `30326263409` aprobó sus tres lanes
  en Python 3.13.14.
- Mantener compatibilidad de lectura con esquemas históricos.
- Regenerar snapshots o resúmenes existentes solo cuando la tarea lo solicite explícitamente.
- Informar hashes protegidos y cualquier artefacto ignorado por `.gitignore`.

## Incidencia global cerrada

- Prueba anteriormente afectada:
  `tests/test_comparison_models.py::ComparisonModelTests::test_global_frozen_field_matrix_is_individual_and_prephysical`.
- Causa confirmada: la fixture asignaba `True` incluso cuando el estado
  original ya era `True`, por lo que no producía una mutación real.
- Corrección cerrada: matriz determinista `False→True`, `True→False` y
  `None→False`, limitada al archivo de prueba.
- El cierre preservó `block_2_2_b1_approved` y no modificó código productivo.

## Quality gate y autorizaciones

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

## Protocolo de agentes subordinados y trabajo remoto

- La colaboración remota se rige por `docs/REMOTE_AGENT_WORKFLOW.md` y las
  plantillas de `.github/`; son guías operativas y no sustituyen una
  autorización de N0-GOV.
- Todo colaborador externo debe recibir un Issue con `task_id`, baseline,
  allowlist, exclusiones, pruebas y criterio de cierre. Debe trabajar en una
  rama `agent/<task_id>/<slug>` de su fork privado y entregar un PR; nunca
  directamente en `main`. El acceso inicial recomendado es `Read`.
- `desktop-app/src/**`, `addon/**`, `knowledge/**`, `security/**`, CI,
  settings, secretos, perfiles, escenarios, resultados, SimulationCraft,
  observación real, releases y claves permanecen bajo responsabilidad
  exclusiva de Codex principal y autorizaciones separadas.
- Un PR, una prueba verde o una revisión técnica no equivalen a aprobación,
  merge, commit, push o publicación. Las invitaciones de GitHub se realizan
  manualmente con el nombre exacto de la cuenta y el mínimo permiso necesario.

- No modificar el árbol sin una tarea explícitamente autorizada y con alcance
  cerrado en `docs/NEXT_TASK.md`.
- Iniciar cada tarea futura desde un árbol Git limpio; los cambios previos no
  se adoptan ni se reparan automáticamente.
- Ejecutar `python tools/quality_gate.py run` después de implementar una tarea
  autorizada. Las pruebas focales deben pasar antes de la suite completa.
- Requerir una auditoría independiente declarada y procedimental antes de
  aprobar el bloque; esta separación no constituye una garantía criptográfica
  de identidad.
- El quality gate no autoriza ni invoca SimulationCraft y no amplía el alcance
  funcional de la tarea.
- No aprobar ni iniciar automáticamente el bloque siguiente.
- La autorización `planned_member_transactional_commit_0_1` está consumida;
  GitHub Actions run `30328581221` aprobó Policy and contract, Tools tests y
  Functional suite. Este cierre no autoriza ejecución real ni el bloque
  siguiente.
- El contrato de GitHub Automation 0.1 está consumido y se conserva en
  `docs/NEXT_TASK.md` como evidencia histórica legible por la CI; no autoriza
  nuevas mutaciones.
- La autorización `comparison_timestamp_monotonicity_0_1` también está
  consumida; su cierre no autoriza tareas posteriores ni una ejecución de
  SimulationCraft.
- Escalar a Daniel cualquier archivo adicional, eliminación, rename, cambio de
  alcance o excepción no incluida expresamente en el contrato autorizado.
