# Next Task — DpsLab

## Vigencia del contrato

El contrato `automation_foundation_0_1` conservado a continuación corresponde
a una autorización histórica ya consumida. Su implementación fue auditada
mediante independencia declarada y procedimental y quedó registrada en el
commit `3828c098946f6842885fc520f841ef4fdb4e12af`.

Estado conciliado: `automation_foundation_0_1_committed`.

El schema contractual 0.1 no dispone de un estado `consumed`. Por ello,
`design_only` se utiliza exclusivamente como estado operativo de desactivación:
impide que `quality_gate.py run` trate el contrato anterior como autorización
vigente. No describe retrospectivamente el estado original de la autorización,
cuya identidad, autoridad y fecha se conservan en el contrato.

Este contrato no autoriza repetir la implementación, regenerar artefactos,
modificar archivos, crear commits ni operar sobre remotes. Una tarea futura
requerirá una decisión humana nueva y el reemplazo explícito de este contrato
por otro contrato autorizado y de alcance cerrado.

<!-- DPSLAB_TASK_CONTRACT_BEGIN -->
```json
{
  "contract_version": "0.1",
  "task_id": "automation_foundation_0_1",
  "title": "Infraestructura mínima de autorización y quality gate",
  "baseline_commit": "b4098ae01799544e4e8aa207166dd06f45b65489",
  "authorization": {
    "status": "design_only",
    "authorization_id": "automation_foundation_0_1-20260716-daniel",
    "authorized_by": "Daniel",
    "authorized_at": "2026-07-16T00:00:00-05:00"
  },
  "scope": {
    "allowed_paths": [
      ".gitignore",
      "AGENTS.md",
      "docs/NEXT_TASK.md",
      "tools/quality_gate.py",
      "tools/tests/test_quality_gate.py",
      "docs/AUTOMATION_FOUNDATION.md",
      "desktop-app/tests/test_config.py"
    ],
    "generated_paths": [
      ".dpslab/quality-gates/automation_foundation_0_1/implementation.json",
      ".dpslab/quality-gates/automation_foundation_0_1/audit.json"
    ],
    "forbidden_paths": [
      "desktop-app/src/dpslab/**",
      "profiles/**",
      "scenarios/**",
      "variants/**",
      "comparisons/**",
      "results/runs/**",
      "results/comparisons/**",
      "DpsLab_migration_*/**",
      "DpsLab_migration_*.zip"
    ],
    "allow_deletions": false,
    "allow_renames": false
  },
  "tests": {
    "focused": {
      "working_directory": ".",
      "argv": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tools/tests",
        "-v"
      ],
      "environment": {
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "full": {
      "working_directory": "desktop-app",
      "argv": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v"
      ],
      "environment": {
        "PYTHONPATH": "src",
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    "baseline_test_count": 208,
    "minimum_test_count": 208
  },
  "protected_files": {
    "profiles/flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "flasil.simc": "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738",
    "desktop-app/src/dpslab/planned_member.py": "8e9aac859576abefc3f810f152e93f2541880d673825d1cfa1474f04b1e6a2b2",
    "desktop-app/tests/test_planned_member.py": "5d68029c3e21d98695d5f5c9d83fd14cfa72ae6634fa3c7b8c6f879f616a9d89"
  },
  "audit": {
    "required": true,
    "independence": "declared_and_procedural"
  },
  "acceptance_criteria": [
    "solo siete archivos autorizados en el delta",
    "sin eliminaciones ni renames",
    "pruebas focales aprobadas",
    "suite funcional con al menos 208 pruebas",
    "hashes protegidos intactos",
    "implementation.json generado e ignorado por Git",
    "sin SimulationCraft ni cambios funcionales o de schema"
  ],
  "express_exclusions": [
    "2.2.b2",
    "2.2.b3",
    "SimulationCraft",
    "runs físicos",
    "cambios funcionales",
    "cambios de schema",
    "commits y remotes"
  ]
}
```
<!-- DPSLAB_TASK_CONTRACT_END -->

## Estado

El primer bloque técnico está finalizado. Parser, snapshot, runner, intérprete,
escenarios, variantes, baseline y auditorías están implementados.

La implementación del comparador A/B de collar fue aprobada sin autorizar una
ejecución real de SimulationCraft.

El Subbloque 2.2.b1 está aprobado (`block_2_2_b1_approved`). La creación
planificada de un miembro y su reserva es pura, copy-on-write y no persistente.

Automation Foundation fue implementada, auditada mediante independencia
declarada y procedimental, y registrada en el commit
`3828c098946f6842885fc520f841ef4fdb4e12af`.

Estado conciliado: `automation_foundation_0_1_committed`.

La autorización de implementación asociada fue consumida. No permanece activa
y no autoriza una nueva ejecución del quality gate.

## Estado Git y GitHub

Según la evidencia recopilada el 2026-07-17:

- rama local `main`: `3828c098946f6842885fc520f841ef4fdb4e12af`;
- `origin/main`: `3828c098946f6842885fc520f841ef4fdb4e12af`;
- tag `baseline-block-2.2.b1-approved`: objeto
  `5496df72af18562597d6e5986e3dac755c62f67f`;
- target del tag: `b4098ae01799544e4e8aa207166dd06f45b65489`;
- estado conciliado: `github_remote_0_1_published`.

`published` acredita la publicación de las refs verificadas, pero no equivale
a `github_remote_0_1_approved`. Este registro no autoriza commits, pushes,
tags ni cambios de remoto.

## Estado de verificación

Las pruebas focales de 2.2.b1 finalizaron con:

- 20 pruebas aprobadas;
- 55 subtests aprobados;
- código de salida 0.

La suite global recopilada el 2026-07-17 finalizó con:

- 208 pruebas aprobadas;
- 573 subtests aprobados;
- 1 prueba fallida;
- código de salida 1.

## Incidencia global abierta

Prueba fallida:

`tests/test_comparison_models.py::ComparisonModelTests::test_global_frozen_field_matrix_is_individual_and_prephysical`

Fallo observado:

`AssertionError: ComparisonResultError not raised`

Esta incidencia impide describir la suite global como limpia. Permanece
separada de `block_2_2_b1_approved`: no revoca automáticamente esa aprobación
y no autoriza corregir `comparison_models`.

## Próxima tarea candidata — no autorizada

Subbloque 2.2.b2: diseñar e implementar exclusivamente el commit transaccional
del alta producida por 2.2.b1, sin crear carpetas físicas de run, sin ejecutar
el Comparator y sin invocar SimulationCraft.

Estado: `not_authorized`.

Esta candidatura no constituye autorización para diseño, implementación,
pruebas, persistencia, creación de carpetas físicas, integración con Comparator
o runner, ejecución de SimulationCraft, modificación documental, commits o
pushes. Una eventual intervención requiere una decisión humana nueva y un
contrato de alcance independiente que defina los archivos modificables,
atomicidad, validación del delta, idempotencia, rollback y pruebas de fallos
físicos.

## Expresamente excluido hasta aprobación

- Ejecución de matrices de simulaciones.
- Generación automática de combinaciones.
- Comparaciones reales de talentos o equipo.
- GUI.
- Addon de WoW.
- Módulos multiclase.
- Entrenador de combate.
- Nuevas ejecuciones de SimulationCraft.
- Creación física de carpetas de run u ownership markers.
- Integración del alta planificada con Comparator, runner o preflight.

## Contexto que debe conservarse

- Baseline: `results/runs/20260715T072501.415324Z-95439dae`.
- DPS formal: `88511.37941600244`.
- Referencia manual: `82950.55`.
- Diferencial sin causa demostrada: `6.703788 %`.
- APL formal completa y expansión manual de LightMovement no comparables con
  los artefactos disponibles.
- `warlock.soul_shards=0` es `no_op_by_source` en SimC `a81c39d`.
