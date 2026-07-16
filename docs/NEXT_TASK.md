# Next Task — DpsLab

## Estado

El primer bloque técnico está finalizado. Parser, snapshot, runner, intérprete,
escenarios, variantes, baseline y auditorías están implementados y cubiertos
por 208 pruebas.

La implementación del comparador A/B de collar fue aprobada sin autorizar una
ejecución real de SimulationCraft.

El Subbloque 2.2.b1 está aprobado (`block_2_2_b1_approved`). La creación
planificada de un miembro y su reserva es pura, copy-on-write y no persistente.

## Próxima tarea candidata

Subbloque 2.2.b2: diseñar e implementar exclusivamente el commit transaccional
del alta producida por 2.2.b1, sin crear carpetas físicas de run, sin ejecutar
el Comparator y sin invocar SimulationCraft.

Esta candidatura no constituye autorización. Requiere alcance explícito para
los archivos modificables, contrato de atomicidad, validación del delta,
idempotencia, rollback y pruebas de fallos físicos.

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
