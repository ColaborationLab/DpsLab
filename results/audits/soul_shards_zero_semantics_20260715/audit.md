# Semántica de `warlock.soul_shards=0` — 2026-07-15

## Alcance

- SimulationCraft: `1205-01`
- Revisión: `a81c39d`
- Opción: `warlock.soul_shards`
- Valor analizado: `0`

## Evidencia del código fuente

El constructor observado inicializa `initial_soul_shards()` y la opción se
registra mediante:

```text
add_option(opt_int("warlock.soul_shards", initial_soul_shards))
```

Después de `player_t::init_resources(force)`, la sustitución del recurso solo
ocurre bajo esta condición:

```text
initial_soul_shards > 0
```

La asignación condicionada es:

```text
resources.current[RESOURCE_SOUL_SHARD] = initial_soul_shards
```

## Conclusión

`no_op_by_source`: el valor predeterminado es `0`; especificar explícitamente
`warlock.soul_shards=0` vuelve a establecer `0`, pero no activa la asignación
condicionada. Omitir la opción y declararla con valor cero son equivalentes en
la revisión `a81c39d` respecto de esta lógica.

Por tanto, esta opción no puede explicar el diferencial de
`6.703788481212528 %` entre el informe manual y la línea base formal.

No se realizó una simulación para comprobarlo porque ambos casos producen el
mismo estado interno de esta opción según el código fuente exacto utilizado.
La capa de variantes se conserva para futuros experimentos de talentos y
equipo.
