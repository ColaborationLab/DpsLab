# Roadmap — DpsLab

## Primer bloque técnico — completado

- [x] Parser de perfiles SimulationCraft.
- [x] Dataclasses y snapshot JSON 0.1.
- [x] Runner local seguro de SimulationCraft.
- [x] Intérprete y resumen versionado de resultados.
- [x] Escenarios reproducibles TOML.
- [x] Variantes de perfil y perfil efectivo atómico.
- [x] Baseline formal canónica.
- [x] Auditorías comparativa, semántica y profunda.
- [x] Infraestructura y cobertura automática establecidas.
- Estado de verificación: la última suite global documentada registró 208
  pruebas aprobadas, 573 subtests aprobados, 1 prueba fallida y código de
  salida 1. La incidencia de `comparison_models` permanece abierta y separada
  de los bloques aprobados.

## Comparador A/B de collar — implementado, no ejecutado

- [x] `comparison_spec` y `comparison_result` schema 0.1 cerrados.
- [x] Evidencia visual versionada y normalización aprobada.
- [x] Transformación exclusiva de `neck` independiente de `ProfileVariant`.
- [x] Ocho bloques, seeds fijas, alternancia, pausas y reintentos.
- [x] Welch–delta principal y t emparejado de sensibilidad con SciPy.
- [x] Subbloque 2.2.a: identidad efímera de runs planificados.
- [x] Subbloque 2.2.b1: alta planificada pura y no persistente de miembros
  (`block_2_2_b1_approved`).
- [ ] Subbloque 2.2.b2: persistencia transaccional del alta planificada,
  candidata no autorizada y pendiente de autorización específica.
- [ ] Ejecución real del experimento, sujeta a autorización independiente.

## Etapas posteriores no aprobadas

- Generación automática de combinaciones y optimización.
- Interfaz gráfica local.
- Addon de WoW.
- Arquitectura multiclase.
- Entrenador o analizador de combate.
- Weekly Reward Choices, currencies, high watermarks y achievements.
