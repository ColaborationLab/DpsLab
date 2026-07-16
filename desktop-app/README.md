# DpsLab

Aplicación local DpsLab. Interpreta un perfil de SimulationCraft, genera un
snapshot JSON y contiene un ejecutor aislado para una simulación base. No usa
el archivo HTML del addon como entrada y no genera combinaciones de equipo.
El snapshot incluye versión de esquema, procedencia y SHA-256 del perfil,
checksum de SimC, datos del personaje, talentos y equipo.

## Requisitos

- Python 3.11 o posterior.
- SciPy 1.11 o posterior y anterior a 2.0 para el análisis comparativo.

## Comparador A/B controlado

El contrato congelado vive en
`comparisons/flasil_neck_50228_vs_249368_v1.toml`. La implementación transforma
exclusivamente `neck`, conserva `ProfileVariant` separado, orquesta ocho bloques
con seeds cerradas y analiza Welch–delta con sensibilidad t emparejada.

Esto no autoriza por sí solo ejecutar SimulationCraft. Un resultado real solo
puede crearse, tras autorización independiente, bajo
`results/comparisons/<comparison-id>/<comparison-execution-id>/`.

## Generar el snapshot

Desde `desktop-app`:

```powershell
$env:PYTHONPATH = "src"
python -m dpslab snapshot --input ../profiles/flasil.simc --output ../results/flasil_snapshot.json
```

También se puede instalar localmente en modo editable:

```powershell
python -m pip install -e .
dpslab snapshot --input ../profiles/flasil.simc --output ../results/flasil_snapshot.json
```

## Configurar SimulationCraft

Copia `config/dpslab.example.toml` como `config/dpslab.local.toml`. La
configuración local está ignorada por Git y puede contener la ruta absoluta de
este computador:

```toml
[simulationcraft]
simc_exe = "C:/Programas/SimulationCraft/simc.exe"
threads = 2
timeout_seconds = 900
generate_html = false
runs_dir = "results/runs"
```

La ruta del ejecutable se resuelve en este orden:

1. `--simc-exe`.
2. Variable de entorno `DPSLAB_SIMC_EXE`.
3. `config/dpslab.local.toml`.

## Ejecutar una simulación base

Desde `desktop-app`:

```powershell
$env:PYTHONPATH = "src"
python -m dpslab simulate --profile ../profiles/flasil.simc --html
```

Cada intento crea una carpeta nueva bajo `results/runs/`. El JSON es obligatorio
y el HTML solo se solicita con `--html` o mediante la configuración local. La
configuración local, los valores predeterminados generales son cuatro hilos y
600 segundos. Este computador está configurado localmente con dos hilos y 900
segundos.
Después de una simulación correcta, DpsLab genera automáticamente
`run_summary.json` usando el mismo intérprete del comando `summarize`. Si este
postprocesamiento falla, la simulación conserva su estado `completed` y el
comando informa el fallo por separado.

Para indicar el ejecutable directamente:

```powershell
python -m dpslab simulate --profile ../profiles/flasil.simc --simc-exe "C:/ruta/a/simc.exe" --html
```

Prueba de humo de baja carga:

```powershell
python -m dpslab simulate --profile ../profiles/flasil.simc --threads 1 --iterations 100 --max-time 60 --vary-combat-length 0 --timeout 180 --html
```

## Ejecutar las pruebas

Desde `desktop-app` y sin instalar dependencias:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

Las pruebas unitarias simulan el proceso externo y no ejecutan `simc.exe` real.

## Resumir una ejecución existente

El resumen portable y versionado puede generarse o regenerarse sin ejecutar
SimulationCraft:

```powershell
$env:PYTHONPATH = "src"
python -m dpslab summarize ../results/runs/<run-id>
```

El comando lee `simc.json`, `metadata.json` y `stderr.txt`, y escribe
`run_summary.json` atómicamente en la misma carpeta. Es idempotente y no
modifica los artefactos originales. Los metadatos y resúmenes nuevos usan el
esquema `0.2`; el intérprete acepta también ejecuciones antiguas `0.1`.

El bloque `execution` distingue tres conceptos temporales:

- `duration_seconds`: duración total observada por el runner de DpsLab,
  incluyendo inicio del proceso, informes y postprocesamiento previo al resumen.
- `simc_elapsed_seconds`: tiempo físico interno informado por SimulationCraft;
  se obtiene primero de `sim.statistics.elapsed_time_seconds` y, si falta, de
  una línea inequívoca `WallSeconds` en stdout.
- `total_simulated_combat_seconds`: suma del tiempo de combate de todas las
  muestras, obtenida exclusivamente de
  `sim.statistics.simulation_length.sum`.

`sim.statistics.simulation_length.mean` representa la duración media de un
combate y no se usa como sustituto de ninguno de esos campos.

## Escenarios reproducibles

Los escenarios TOML contienen condiciones de combate y precisión, sin rutas,
hilos, timeout ni generación HTML. El escenario inicial es
`scenarios/st_lightmovement_300s_v1.toml`.

```powershell
$env:PYTHONPATH = "src"
python -m dpslab simulate --profile ../profiles/flasil.simc --scenario ../scenarios/st_lightmovement_300s_v1.toml
```

La prioridad es CLI explícito, escenario, comportamiento anterior y valor
predeterminado. Se pueden sobrescribir `--fight-style`, `--desired-targets`,
`--max-time`, `--vary-combat-length`, `--iterations` y `--target-error`.

`iterations=0` requiere `target_error>0` y activa precisión adaptativa. Con
`iterations>0` el modo es fijo. Si el CLI cambia un escenario adaptativo a fijo
sin indicar `--target-error`, DpsLab no hereda el error objetivo del escenario.
La ruta portable y el SHA-256 before/after quedan registrados sin modificar el
archivo TOML.
## Semántica de precisión en los resúmenes

`iterations_parameter` conserva el valor enviado a SimC. En modo adaptativo
vale `0`, `iterations_requested` es `null` y `iterations_completed` registra
el trabajo efectivo comunicado por SimC. `dps_sample_count` cuenta las muestras
estadísticas y puede diferir de las iteraciones completadas sin ser un error.

`target_error_percent` es el umbral configurado, no el error obtenido.
`observed_relative_error_percent` se deriva de la media y su error cuando la
fórmula es inequívoca; `simc_reported_error_percent` conserva el porcentaje que
SimC comunica expresamente.
## Variantes de perfil

Una variante aplica cambios versionados sin modificar el perfil base:

```powershell
python -m dpslab simulate --profile ../profiles/flasil.simc `
  --scenario ../scenarios/st_lightmovement_300s_v1.toml `
  --variant ../variants/flasil_soul_shards_0_v1.toml
```

El escenario describe el combate, la variante modifica el perfil y la
configuración local conserva los recursos del computador. Con variante, DpsLab
crea `effective_profile.simc` dentro del run mediante escritura binaria atómica;
sus bytes comienzan exactamente con los del perfil base. El checksum del addon
se refiere solo a ese prefijo original.

Los resúmenes 0.3 separan `target_error_percent`,
`observed_relative_error_percent` y `simc_displayed_error`. Este último incluye
valor absoluto, porcentaje, fuente, localizador y función semántica.
