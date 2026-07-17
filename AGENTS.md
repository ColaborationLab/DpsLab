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
- El Subbloque 2.2.b1 está aprobado (`block_2_2_b1_approved`): el alta
  planificada de miembros es pura, copy-on-write y no persistente.
- Automation Foundation fue implementada, auditada mediante independencia
  declarada y procedimental, y registrada en el commit
  `3828c098946f6842885fc520f841ef4fdb4e12af`
  (`automation_foundation_0_1_committed`).
- Según la evidencia recopilada el 2026-07-17, `main` y `origin/main`
  apuntaban a `3828c098946f6842885fc520f841ef4fdb4e12af`. El estado remoto
  acreditado es `github_remote_0_1_published`, no
  `github_remote_0_1_approved`.
- Las pruebas focales de 2.2.b1 registraron 20 pruebas aprobadas, 55 subtests
  aprobados y código de salida 0.
- La suite global recopilada el 2026-07-17 registró 208 pruebas aprobadas,
  573 subtests aprobados, 1 prueba fallida y código de salida 1. Por tanto,
  no debe describirse como una suite global limpia.

## Integridad obligatoria

- No modificar `profiles/flasil.simc`; conservar también `flasil.simc` raíz como respaldo.
- `flasil.simc.html` es referencia histórica y fuente de auditoría, nunca perfil de entrada.
- No modificar escenarios, variantes ni artefactos de runs existentes durante análisis.
- Calcular SHA-256 antes y después de operaciones que usen archivos protegidos.
- Crear perfiles efectivos y resultados JSON mediante escritura atómica cuando corresponda.
- Nunca sobrescribir una ejecución previa; cada simulación usa una carpeta nueva.
- No guardar rutas personales absolutas en archivos versionados.
- No ejecutar `simc.exe` sin autorización explícita para esa ejecución concreta.

## Restricciones de alcance

- No iniciar comparaciones de equipo o talentos sin una tarea expresamente aprobada.
- No ejecutar matrices ni generar combinaciones automáticamente sin aprobación.
- No implementar GUI, addon de WoW, módulos multiclase o entrenador de combate sin alcance aprobado.
- No procesar todavía Weekly Reward Choices, currencies, high watermarks o achievements.

## Verificación

- Ejecutar toda la suite después de cambios de código y reportar por separado
  pruebas aprobadas, subtests, fallos y código de salida. El último resultado
  documentado no es limpio: 208 pruebas aprobadas, 573 subtests aprobados,
  1 prueba fallida y código de salida 1.
- Mantener compatibilidad de lectura con esquemas históricos.
- Regenerar snapshots o resúmenes existentes solo cuando la tarea lo solicite explícitamente.
- Informar hashes protegidos y cualquier artefacto ignorado por `.gitignore`.

## Incidencia global abierta

- Prueba fallida:
  `tests/test_comparison_models.py::ComparisonModelTests::test_global_frozen_field_matrix_is_individual_and_prephysical`.
- Fallo observado: `AssertionError: ComparisonResultError not raised`.
- Esta incidencia no revoca automáticamente `block_2_2_b1_approved`.
- Su registro no autoriza corregir `comparison_models`, modificar código ni
  ejecutar una intervención técnica.

## Quality gate y autorizaciones

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
- El Subbloque 2.2.b2 permanece como trabajo futuro candidato y no autorizado.
- Escalar a Daniel cualquier archivo adicional, eliminación, rename, cambio de
  alcance o excepción no incluida expresamente en el contrato autorizado.
