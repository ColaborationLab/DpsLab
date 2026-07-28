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
- Estado de verificación: la incidencia de prueba de `comparison_models` fue
  corregida de forma determinista, auditada y publicada sin cambios
  productivos. La baseline funcional aprobada registró 208/208 pruebas y
  GitHub Actions run `29645964849`, sobre Python 3.13.14, aprobó sus tres
  lanes. La observación intermitente posterior de Python 3.12 fue corregida,
  auditada y publicada en `b19fb6eae2a44240467cc8684adfd2733e09f0bb`;
  la verificación local pasó 213/213 y GitHub Actions run `30326263409`
  aprobó sus tres lanes. La persistencia transaccional 2.2.b2 fue publicada en
  `d8bc2406b6b9ea2acc46bf16e5b4811d01573243`; la suite vigente pasó 219/219 y
  GitHub Actions run `30328581221` aprobó sus tres lanes.
- [x] GitHub Automation 0.1 implementada, auditada, publicada y operativa en
  `bf2db644bfebeb07246f8e967f39101a7aa3e77a`.

## Comparador A/B de collar — implementado, no ejecutado

- [x] `comparison_spec` y `comparison_result` schema 0.1 cerrados.
- [x] Evidencia visual versionada y normalización aprobada.
- [x] Transformación exclusiva de `neck` independiente de `ProfileVariant`.
- [x] Ocho bloques, seeds fijas, alternancia, pausas y reintentos.
- [x] Welch–delta principal y t emparejado de sensibilidad con SciPy.
- [x] Subbloque 2.2.a: identidad efímera de runs planificados.
- [x] Subbloque 2.2.b1: alta planificada pura y no persistente de miembros
  (`block_2_2_b1_approved`).
- [x] Subbloque 2.2.b2: persistencia transaccional del alta planificada,
  auditada, publicada y verificada bajo modelo single-writer.
- [ ] Ejecución real del experimento, sujeta a autorización independiente.

## Etapas posteriores no aprobadas

- Generación automática de combinaciones y optimización.
- Interfaz gráfica local.
- Addon de WoW.
- Arquitectura multiclase.
- Entrenador o analizador de combate.
- Weekly Reward Choices, currencies, high watermarks y achievements.
