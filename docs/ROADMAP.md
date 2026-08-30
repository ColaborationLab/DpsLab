# Roadmap — DpsLab

## Estado general conciliado — 2026-08-29

- Fundación técnica y de seguridad interna: **aproximadamente 65 %**.
- Producto integral distribuible para usuarios: **aproximadamente 40 %**.

Estas cifras son estimaciones de planificación, no estados aprobatorios. La
primera mide componentes internos implementados y verificados; la segunda
incluye todavía GUI, integración real aplicación–addon, conocimiento vigente
multiclase, empaquetado, actualización y puertas de beta.

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

## Comparador A/B de collar — implementado y primera ejecución completada

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
- [x] Ejecución real auditada:
  `cmp-3120334d365b4ba2922cdbb25afe0d7f`, 8/8 bloques, 16/16 runs válidos,
  sin reintentos; ambos análisis clasifican `winner_b`.

## Fundación de conocimiento, distribución y addon — implementada internamente

- [x] Esquemas cerrados de conocimiento y catálogo estático current-only con
  estados de revisión y denegación por defecto.
- [x] Pipeline gobernado para fuentes oficiales de Blizzard, evidencia de
  parche y candidatos `pending_review`; no aprueba recomendaciones solo.
- [x] Firma Ed25519, registro de confianza, custodia y recuperación de clave de
  release bajo ceremonias atendidas; no constituye todavía un canal público.
- [x] Dependencias reproducibles, locks con hashes, SBOM, auditoría de
  vulnerabilidades, análisis estático y escaneo de secretos en CI.
- [x] Addon sintético local con guía no accionable, intercambio direccional,
  observación cerrada, serialización y exportación manual mediante la única
  SavedVariable `DpsLabObservationExport`.
- [x] Parser de escritorio estricto para el transporte sintético, sin ejecutar
  Lua, descubrir archivos automáticamente ni acceder a red.

## Camino restante hacia un producto distribuible

- [x] Prueba atendida dentro de WoW de exportación y limpieza sintéticas, con
  persistencia observada y lectura saneada del estado `cleared` después de
  cerrar completamente el juego.
- [x] Adquisición de SavedVariables mediante instalación Retail elegida
  explícitamente, almacenamiento local acotado, preflight nativo de WoW
  cerrado, límites y rechazo de symlinks/rutas ambiguas; nunca edita el archivo
  del juego in situ.
- [ ] Observación real mínima y consentida, separada de nombres, cuenta,
  telemetría y datos no necesarios.
- [ ] Catálogo vigente aprobado para clases, especializaciones y roles,
  priorizando supervivencia para tanks y curación para healers.
- [ ] Interfaz gráfica local accesible y empaquetado reproducible para Windows.
- [ ] Actualizador firmado con canales estable/beta, anti-rollback, revocación
  y recuperación verificadas.
- [ ] Empaquetado y distribución pública del addon con revisión de licencias,
  privacidad, propiedad intelectual y términos de plataforma.
- [ ] Revisión independiente de seguridad y piloto cerrado antes de beta.

## Fuera del alcance inmediato

- Generación automática de combinaciones y optimización.
- Entrenador o analizador de combate.
- Weekly Reward Choices, currencies, high watermarks y achievements.

## Seguridad transversal

- [x] Filosofía de denegación por defecto, datos nunca ejecutables, privilegio
  mínimo, privacidad por defecto y decisiones de seguridad separadas.
- [x] Límites de confianza iniciales para aplicación, addon, fuentes, CI,
  paquetes, actualización y claves.
- [x] Política de reporte responsable y baseline legible por pruebas.
- [x] Modelo de amenazas versionado y probado; conserva puertas abiertas para
  beta en lugar de declararlas cerradas.
- [x] Dependencias reproducibles, SBOM y auditoría automática de vulnerabilidades.
- [x] Análisis estático y escaneo de secretos en CI.
- [ ] Canal de actualización firmado con protección contra repetición,
  degradación y rollback malicioso.
- [x] Contrato, parser estricto y pruebas negativas del transporte sintético
  aplicación–addon.
- [ ] Ensayo adversarial de extremo a extremo del estado `available` con un
  payload realmente escrito por WoW y seleccionado por el usuario; el estado
  `cleared` ya fue observado de forma atendida.
- [ ] Política de privacidad y procedimiento de respuesta, revocación y
  recuperación ejercitado.
- [ ] Revisión de seguridad independiente antes de beta externa.
- [ ] Firma de confianza de Windows para ejecutable e instalador, o aceptación
  humana explícita y documentada del riesgo residual.

Los elementos pendientes son puertas de distribución; no impiden desarrollar
componentes internos bajo contratos seguros, pero sí impiden declarar el
producto listo para usuarios externos.
