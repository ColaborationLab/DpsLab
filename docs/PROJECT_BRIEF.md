# Project Brief — DpsLab

## Propósito

DpsLab es una solución local compuesta por aplicación de escritorio, addon de
WoW y paquetes de conocimiento gobernados. Busca ayudar a mejorar el desempeño
de personajes de World of Warcraft mediante observación consentida, plantillas
vigentes, recomendaciones explicables y análisis reproducible. Para tanks, el
DPS se subordina a supervivencia, mitigación y amenaza; para healers, a la
curación y seguridad del grupo. El proyecto prioriza reproducibilidad,
procedencia, privacidad, denegación por defecto y conservación byte a byte de
las entradas analíticas.

## Arquitectura actual

- `profiles/`: perfiles base inmutables.
- `scenarios/`: condiciones reproducibles de combate y precisión.
- `variants/`: overrides declarativos y restringidos aplicados a perfiles efectivos.
- `config/`: configuración dependiente del computador; el archivo local no se versiona.
- `desktop-app/src/dpslab/`: parser, modelos, configuración, runner, escenarios, variantes, resumen y auditoría.
- `addon/DpsLab/`: addon sintético local, guía no accionable y exportación
  manual acotada mediante SavedVariables.
- `knowledge/`: esquemas, fuentes, snapshots sintéticos, candidatos, revisiones,
  catálogos y registros públicos de confianza.
- `security/`: baseline, modelo de amenazas, SBOM y políticas de análisis.
- `tools/`: quality gate, auditorías de dependencias y seguridad, y ensayos de
  separación del addon público.
- `.github/workflows/`: CI de política, herramientas, funcionalidad y seguridad.
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
- Pipeline current-only de conocimiento: cobertura de fuentes, adquisición
  oficial atendida, adaptación estructural, revisión semántica, propuestas y
  candidatos que nunca superan `pending_review` automáticamente.
- Fundamentos de release: bundles candidatos, firma Ed25519, registro de
  confianza, custodia/recuperación de clave y evaluación fail-closed de
  readiness; no existe todavía un canal público de actualización.
- Addon sintético con comandos `/dpslab synthetic`,
  `/dpslab export synthetic` y `/dpslab export clear`. Declara únicamente
  `DpsLabObservationExport`, no observa datos reales y no automatiza acciones.
- Parser de transporte sintético en la aplicación, cerrado a una asignación
  exacta y sin `eval`, ejecución de Lua, filesystem o red.
- Flujo local sintético de extremo a extremo: selección Retail explícita,
  almacenamiento atómico local, interlock nativo que exige `Wow.exe` detenido,
  adquisición acotada de SavedVariables, coordinador saneado y comandos
  `addon-configure`/`addon-import`. No descubre instalaciones o cuentas, no
  vigila archivos y no imprime rutas, bytes crudos ni contenido observado.
- Locks con hashes, SBOM, auditoría de vulnerabilidades, análisis estático y
  escaneo de secretos integrados en las cuatro lanes actuales de CI.

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
- No existe todavía GUI. El addon fue probado de forma atendida dentro de WoW,
  pero su observación continúa siendo sintética y no accionable.
- La adquisición explícita y el enlace local addon–aplicación están
  implementados para el transporte sintético. Aún no existe un esquema de
  observación real minimizado ni una prueba adversarial completa con un payload
  disponible escrito por WoW.
- Los catálogos versionados son sintéticos o candidatos: no constituyen todavía
  cobertura vigente aprobada para todas las clases y especializaciones.
- No existe instalador, actualizador público, canal estable/beta operativo ni
  release autorizada para usuarios externos.
- Las fuentes de daño manuales no pudieron normalizarse completamente porque
  el objeto JavaScript correspondiente no era JSON válido.
- Algunos artefactos históricos conservan esquema 0.2 y no se regeneran automáticamente.
- La configuración local y `results/runs/` están excluidos del control de versiones.

## Eje transversal de seguridad

DpsLab adopta seguridad por diseño y denegación por defecto. Datos externos,
archivos locales, salida de procesos, paquetes de conocimiento y el
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
Antes de ampliar cobertura, el primer producto útil será un vertical slice del
Druida como clase prototipo: Balance y Feral para daño, Guardian para tanque y
Restauración para sanación con daño auxiliar. Esto permite validar en una sola
clase que el contexto de función cambia las prioridades sin convertir DpsLab en
una guía de rotación de una especialización.

Para Guardian, el daño siempre queda subordinado a supervivencia, mitigación y
amenaza. Para Restauración, el daño auxiliar queda subordinado a mantener la
curación y la seguridad del grupo. Balance y Feral pueden priorizar desempeño
de daño dentro del contexto declarado. El DK Sangre será el segundo contraste
para probar la política de tanque.

La información debe ser current-only: las fuentes oficiales de Blizzard son la
autoridad primaria; Wowhead y otros fansites pueden servir para contraste,
investigación o detectar discrepancias, pero no sustituyen la revisión de la
fuente primaria. No se construirá una base de datos histórica para alimentar
recomendaciones obsoletas. La aplicación debe indicar no disponible cuando la
vigencia, procedencia o aplicabilidad no puedan demostrarse.

La siguiente secuencia de trabajo es: contexto de función, plantilla vigente
del Druida, recomendación explicable, actualización controlada y experiencia
de usuario. La expansión multiclase, la matriz masiva de combinaciones y el
entrenador de combate quedan después del vertical slice y requieren contratos
separados.
