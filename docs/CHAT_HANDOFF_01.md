# DpsLab — Chat Handoff 01

## Objetivo general

DpsLab es una aplicación local de Python para interpretar perfiles de
SimulationCraft, ejecutar simulaciones reproducibles y auditables, resumir
resultados y preparar comparaciones controladas de talentos y equipo. La
integridad de entradas y la procedencia de cada dato son requisitos centrales.

## Arquitectura prevista

El diseño separa cuatro capas:

1. Perfil base: estado exportado del personaje, tratado como inmutable.
2. Escenario: combate y precisión reproducibles.
3. Variante: cambios declarativos al perfil, independientes del escenario.
4. Configuración local: ejecutable, hilos, timeout, HTML y directorio de runs.

La futura comparación deberá orquestar estas capas sin mezclarlas. No está diseñada todavía.

## Estado actual

- Python 3.11 o posterior; aplicación en `desktop-app/`.
- Parser y snapshot implementados.
- Runner real de SimulationCraft implementado y probado.
- Resúmenes hasta esquema 0.3, con compatibilidad 0.1/0.2.
- Escenarios y variantes implementados.
- Baseline formal creada.
- Auditorías profundas reproducibles implementadas.
- Comparador A/B de collar schema 0.1 implementado con evidencia, spec congelado,
  transformación de equipo, orquestación simulable y análisis estadístico.
- Suite actual: 208 pruebas.
- No existe autorización para ejecutar el comparador ni SimulationCraft.

## Árbol relevante

```text
DpsLab/
├── AGENTS.md
├── profiles/flasil.simc
├── scenarios/st_lightmovement_300s_v1.toml
├── variants/flasil_soul_shards_0_v1.toml
├── config/
│   ├── dpslab.example.toml
│   └── dpslab.local.toml          # local, ignorado
├── desktop-app/
│   ├── pyproject.toml
│   ├── README.md
│   ├── src/dpslab/
│   │   ├── parser.py, models.py
│   │   ├── config.py, runner.py
│   │   ├── scenario.py, variant.py
│   │   ├── result_models.py, result_parser.py
│   │   ├── deep_audit.py
│   │   └── __main__.py
│   └── tests/                     # 208 pruebas
├── results/
│   ├── flasil_snapshot.json
│   ├── runs/20260715T072501.415324Z-95439dae/
│   └── audits/
└── docs/
    ├── PROJECT_BRIEF.md
    ├── ROADMAP.md
    ├── NEXT_TASK.md
    └── CHAT_HANDOFF_01.md
```

## Modelos y esquemas

- Snapshot `0.1`: personaje, talentos, loadouts, equipo equipado y bolsas.
- Metadata/run summary actuales `0.3`; lectura compatible con `0.1` y `0.2`.
- La run canónica conserva históricamente un `run_summary.json` 0.2 y no debe
  regenerarse sin solicitud explícita.
- Dataclasses principales: snapshot, escenario, precisión, variante, overrides,
  identificación, escenario de run, variante de run, DPS, ejecución y diagnósticos.
- Auditorías profundas: `audit_schema_version = "0.1"`.

## Comandos disponibles

Desde `desktop-app/`, configurando `PYTHONPATH=src`:

```powershell
python -m dpslab snapshot --input ../profiles/flasil.simc --output ../results/flasil_snapshot.json
python -m dpslab simulate --profile ../profiles/flasil.simc --scenario ../scenarios/st_lightmovement_300s_v1.toml
python -m dpslab simulate --profile ../profiles/flasil.simc --scenario ../scenarios/st_lightmovement_300s_v1.toml --variant ../variants/flasil_soul_shards_0_v1.toml
python -m dpslab summarize ../results/runs/<run-id>
python -m dpslab.deep_audit --manual-html ../flasil.simc.html --profile ../profiles/flasil.simc --run ../results/runs/20260715T072501.415324Z-95439dae --output ../results/audits/manual_vs_baseline_deep_20260715
python -m unittest discover -s tests -v
```

No ejecutar `simulate` sin autorización específica.

## Configuración local

- Prioridad de `simc.exe`: `--simc-exe`, `DPSLAB_SIMC_EXE`, `config/dpslab.local.toml`.
- El ejemplo versionado es `config/dpslab.example.toml`.
- Valores locales actuales previstos: 2 hilos, timeout 900 s, HTML desactivado.
- `config/dpslab.local.toml` puede contener una ruta personal y está ignorado.
- Nunca copiar esa ruta al ejemplo ni a documentación versionada.

## Perfil, escenario y variante

- Perfil canónico: `profiles/flasil.simc`.
- Perfil raíz `flasil.simc`: respaldo; no mover ni eliminar.
- HTML manual: `flasil.simc.html`; no usar como perfil de entrada.
- Escenario: `st_lightmovement_300s_v1`, LightMovement, un objetivo, 300 s,
  variación 0.20, modo adaptativo `target_error=0.10`, `iterations=0`.
- Variante disponible: `flasil_soul_shards_0_v1`.
- `warlock.soul_shards=0` es un no-op demostrado por código fuente en SimC
  revisión `a81c39d`; no ejecutar esa variante como prueba causal.

## Run canónica y baseline

Ruta: `results/runs/20260715T072501.415324Z-95439dae`

- SimulationCraft: `1205-01`, revisión `a81c39d`, JSON report `2.0.0`.
- Personaje: Flasil, Demonology Warlock, nivel 90.
- Escenario: `st_lightmovement_300s_v1`.
- Threads: 2.
- Iteration mode: adaptive; parámetro 0.
- Iteraciones completadas: 3405.
- Muestras DPS: 3403.
- DPS medio: `88511.37941600244`.
- Mediana: `88455.53696582395`.
- Mínimo: `80428.88622535217`.
- Máximo: `97976.4928775221`.
- Error relativo derivado: `0.05027079866239182 %`.
- Duración DpsLab: `20.994239212002867 s`.
- Tiempo interno SimC: `19.737585154 s`.

## Referencia manual y diferencial

- Referencia histórica: `flasil.simc.html`.
- DPS manual: `82950.55`.
- Diferencia relativa: `6.703788 %`.
- La causa no está demostrada.
- La APL formal completa no pudo recuperarse.
- La expansión manual de LightMovement no está expuesta.

## Auditorías realizadas

- `manual_vs_baseline_20260715`: comparación inicial.
- `soul_shards_zero_semantics_20260715`: demuestra `no_op_by_source`.
- `manual_vs_baseline_deep_20260715`: opciones, perfiles, APL, raid events,
  daño y Soul Shards con procedencia y disponibilidad separadas.

La auditoría profunda encontró 91 candidatos JSON en el HTML: 85 válidos y
6 objetos JavaScript rechazados como `parse_failed`. No halló una diferencia
demostrablemente material; dejó APL y raid events como `unavailable`.

## Hashes importantes

- Perfil: `f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738`
- Escenario: `93187338a61d1cfc330f5262abb0b9183acb727d310099eca7917138207c09aa`
- Variante: `9bce78ef272626a1b1bec04b3a72cd21cb217ed7a780d34383c8326b1f8e390b`
- Baseline metadata: `65813f5c1658c42ec445de7d18727cc0900ad179275c1a3c89c59b6193e777b9`
- Baseline simc.json: `584be536bfda7c0f0fe4260140741ba3ca9f5ec2bfeecf54128c0eabb9de070e`
- Baseline stdout: `e049ee209c9e82e5789f89288583c5ffae6e82d5e98dc8124ad6df2ba561ca88`
- Baseline stderr: `951ca0b3e505ccb4f03f6310dd9ef4fd37606d2bc63dd91e3adc2c49e053418d`
- Baseline run summary: `efe71734450544a2f6aab04c76f5914d2a67435c3937ed978b17cab112a8045b`

## Decisiones descartadas o cerradas

- Ejecutar `warlock.soul_shards=0` como prueba causal: descartado; es no-op.
- Interpretar el target error como error observado: corregido; son conceptos separados.
- Interpretar tiempo de combate acumulado como tiempo físico de SimC: corregido.
- Tratar el perfil incrustado del HTML como entrada manual original: descartado;
  es `manual_report_embedded_profile` reconstruido o ampliado.
- Ejecutar JavaScript del HTML para extraer gráficos: prohibido.

## Restricciones que no deben romperse

- No modificar perfil, escenario, variante ni runs existentes.
- No sobrescribir runs ni regenerar resúmenes históricos automáticamente.
- No ejecutar SimC sin aprobación concreta.
- No usar `shell=True` ni comandos interpolados.
- No inferir causalidad de diferencias observacionales.
- No iniciar comparaciones, matrices, combinaciones, GUI, addon o multiclase
  sin una tarea aprobada.

## Siguiente fase candidata

Revisión final y, únicamente con autorización explícita separada, ejecución
real del comparador de collar. La implementación existente no autoriza SimC.

## Recuperación de contexto para un nuevo agente

1. Leer `AGENTS.md`, este handoff, `PROJECT_BRIEF.md`, `ROADMAP.md` y `NEXT_TASK.md`.
2. Confirmar que los hashes protegidos coinciden.
3. Ejecutar las 208 pruebas desde `desktop-app/` sin ejecutar SimC.
4. Revisar la run canónica y las tres carpetas de auditoría.
5. Tratar `results/runs/` como artefactos locales ignorados, no eliminarlos.
6. Esperar una tarea aprobada antes de diseñar o implementar la fase siguiente.
