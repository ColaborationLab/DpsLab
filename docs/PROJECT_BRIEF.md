# Project Brief — DpsLab

## Propósito

DpsLab es una aplicación local para convertir perfiles de SimulationCraft en
datos tipados, ejecutar simulaciones reproducibles y auditables, interpretar
sus resultados y comparar de forma controlada talentos y equipo. El proyecto
prioriza reproducibilidad, procedencia y conservación
byte a byte de las entradas.

## Arquitectura actual

- `profiles/`: perfiles base inmutables.
- `scenarios/`: condiciones reproducibles de combate y precisión.
- `variants/`: overrides declarativos y restringidos aplicados a perfiles efectivos.
- `config/`: configuración dependiente del computador; el archivo local no se versiona.
- `desktop-app/src/dpslab/`: parser, modelos, configuración, runner, escenarios, variantes, resumen y auditoría.
- `results/`: snapshot, runs locales y auditorías versionables.
- `desktop-app/tests/`: suite unitaria con procesos simulados y fixtures mínimos.

## Componentes implementados

- Parser `.simc`, dataclasses y snapshot 0.1.
- Extracción de personaje, talentos, loadouts, equipo equipado y bolsas.
- Runner seguro de SimulationCraft y metadatos de ejecución.
- Intérprete de resultados, tiempos diferenciados y escritura atómica.
- Esquema actual de nuevas ejecuciones/resúmenes: 0.3; lectura compatible con 0.1 y 0.2.
- Escenarios TOML tipados, validados y verificados por SHA-256.
- Variantes TOML y `effective_profile.simc` construido desde bytes.
- Auditoría profunda ejecutable mediante `python -m dpslab.deep_audit`.
- Cobertura automática local y GitHub Automation 0.1 establecidas. La
  incidencia de prueba en `comparison_models` fue corregida, auditada y
  publicada sin cambios productivos. La baseline funcional aprobada registró
  208/208 pruebas y la ejecución remota `29645964849`, sobre Python 3.13.14,
  concluyó satisfactoriamente en sus tres lanes. La observación intermitente
  posterior de Python 3.12 fue corregida mediante timestamps lógicos
  estrictamente crecientes y validación durable fail-closed. La verificación
  local resultante pasó 213/213 y GitHub Actions run `30326263409` aprobó sus
  tres lanes. La persistencia transaccional del alta planificada de miembros
  (Subbloque 2.2.b2) fue implementada, auditada y publicada en
  `d8bc2406b6b9ea2acc46bf16e5b4811d01573243`; la suite vigente pasó 219/219 y
  GitHub Actions run `30328581221` aprobó sus tres lanes.
- Comparador A/B schema 0.1 implementado para el contrato cerrado de `neck`,
  con transformación de equipo separada de `ProfileVariant`, procedencia por
  bloque/intento/miembro y análisis Welch–delta/emparejado.
- Primera comparación real auditada: `cmp-3120334d365b4ba2922cdbb25afe0d7f`.
  Sus 8/8 bloques y 16/16 runs fueron válidos, sin reintentos. Ambos métodos
  clasificaron `winner_b`: Eternal Voidsong Chain obtuvo una ventaja estimada
  de `0.9687020358080112 %` (Welch, IC95 %
  `[0.925919404270558, 1.0114846673454643]`). Este resultado se limita al
  perfil, escenario, versiones y dos collares congelados en el contrato.
- CI reproducible en GitHub para política/contrato, herramientas y suite
  funcional, con permisos mínimos, Actions fijadas por SHA y evidencia
  retenida durante siete días.

## Entradas y salidas

Entradas principales:

- `profiles/flasil.simc`
- `scenarios/st_lightmovement_300s_v1.toml`
- Variante disponible: `variants/flasil_soul_shards_0_v1.toml`
- Configuración local: `config/dpslab.local.toml`

Salidas principales:

- `results/flasil_snapshot.json`
- `results/runs/<run-id>/metadata.json`, `simc.json`, stdout, stderr y `run_summary.json`
- `effective_profile.simc` dentro del run cuando se usa una variante
- Auditorías bajo `results/audits/`

## Baseline y referencia histórica

- Baseline canónica: `results/runs/20260715T072501.415324Z-95439dae`
- DPS formal: `88511.37941600244`
- Referencia manual histórica: `82950.55`
- Diferencia respecto de la referencia manual: `6.703788 %`
- La causa permanece sin demostrar.

La APL manual reconstruida pudo recuperarse, pero la APL formal completa no
está expuesta en los artefactos. El HTML solo identifica `LightMovement` y no
expone su expansión completa de raid events. Estas son las principales
limitaciones de la comparación actual.

`warlock.soul_shards=0` es `no_op_by_source` en SimC revisión `a81c39d` y no
explica el diferencial.

## Limitaciones conocidas

- La primera comparación cerrada ya fue ejecutada y auditada. No existe
  autorización vigente para repetirla, generalizar el resultado a otros
  personajes o iniciar otra matriz.
- No se ejecutan matrices ni se generan combinaciones.
- No existe GUI ni addon de WoW.
- Las fuentes de daño manuales no pudieron normalizarse completamente porque
  el objeto JavaScript correspondiente no era JSON válido.
- Algunos artefactos históricos conservan esquema 0.2 y no se regeneran automáticamente.
- La configuración local y `results/runs/` están excluidos del control de versiones.

## Eje transversal de seguridad

DpsLab adopta seguridad por diseño y denegación por defecto. Datos externos,
archivos locales, salida de procesos, paquetes de conocimiento y el futuro
intercambio con el addon cruzan límites de confianza y deben validarse con
esquemas cerrados, límites de recursos, procedencia e integridad antes de uso.

Los datos nunca son código. La distribución futura requiere actualización
firmada y atómica, protección contra retroceso, privacidad por defecto,
dependencias reproducibles, inventario SBOM, análisis de vulnerabilidades,
secretos y código, pruebas adversariales, respuesta a incidentes y revisión
independiente. Estos requisitos están definidos en `SECURITY.md`,
`docs/SECURITY_ARCHITECTURE.md` y
`security/security_baseline_0_1.json`. No se declarará preparación para beta
externa hasta que todas las puertas obligatorias tengan evidencia vigente.

## Visión multiclase futura

La arquitectura busca admitir múltiples clases mediante modelos comunes,
adaptadores específicos por clase y comparación reproducible de variantes.
Esta visión no autoriza todavía implementar módulos multiclase, reglas de
optimización ni un entrenador de combate.
