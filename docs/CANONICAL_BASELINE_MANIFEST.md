# Canonical Baseline Manifest — DpsLab

## Baseline funcional

- Run canónica: `results/runs/20260715T072501.415324Z-95439dae`
- DPS formal: `88511.37941600244`
- Escenario: `st_lightmovement_300s_v1`
- SimulationCraft: `1205-01`
- Perfil protegido: `profiles/flasil.simc`

`results/runs/` permanece deliberadamente fuera de Git. La run canónica debe
conservarse íntegra en almacenamiento local o en un respaldo externo; este
manifiesto documenta su identidad y sus hashes, pero no incorpora los
resultados completos de SimulationCraft.

## SHA-256 verificados de la run canónica

```text
65813f5c1658c42ec445de7d18727cc0900ad179275c1a3c89c59b6193e777b9  metadata.json
efe71734450544a2f6aab04c76f5914d2a67435c3937ed978b17cab112a8045b  run_summary.json
584be536bfda7c0f0fe4260140741ba3ca9f5ec2bfeecf54128c0eabb9de070e  simc.json
951ca0b3e505ccb4f03f6310dd9ef4fd37606d2bc63dd91e3adc2c49e053418d  stderr.txt
e049ee209c9e82e5789f89288583c5ffae6e82d5e98dc8124ad6df2ba561ca88  stdout.txt
```

## SHA-256 del perfil protegido

```text
f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738  profiles/flasil.simc
```
