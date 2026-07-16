# Automation Foundation — DpsLab

## Propósito

El quality gate aplica el contrato autorizado de `docs/NEXT_TASK.md` sin
modificar la lógica funcional de DpsLab. El ciclo es:

```text
autorización → implementación → pruebas focales → suite completa
→ auditoría independiente → actualización de estado
```

Ningún resultado autoriza automáticamente la tarea siguiente.

## Comandos

Desde la raíz:

```powershell
python tools/quality_gate.py preflight
python tools/quality_gate.py run
python tools/quality_gate.py audit --auditor "<actor-id>" --implementer "<actor-id>" --decision "<approved|changes_required|blocked>"
python tools/quality_gate.py verify
```

`run` valida el contrato y el delta, comprueba hashes, ejecuta primero las
pruebas focales y luego la suite completa, y genera `implementation.json`.
`audit` es una fase separada que genera `audit.json`. `verify` comprueba el
contrato, el delta, hashes y resultados existentes sin ejecutar pruebas.

Durante una implementación el repositorio real puede estar legítimamente
sucio. El gate valida ese delta real con Git sin ocultarlo, neutralizarlo ni
alterar HEAD, index o configuración. Después materializa exactamente el estado
candidato autorizado en un directorio temporal fuera del árbol, inicializa allí
un repositorio Git efímero sin remotes, crea un commit efímero y verifica que
quede limpio. La suite funcional se ejecuta en ese snapshot candidato limpio.
No se utiliza un `GIT_DIR` falso. El temporal se elimina tanto en éxito como en
fallo.

## Alcance

- `allowed_paths`: rutas versionables que la tarea puede crear o modificar.
  Eliminaciones y renames requieren además autorización explícita.
- `generated_paths`: resultados locales ignorados producidos por el gate. No
  forman parte del delta funcional autorizado.
- `forbidden_paths`: prevalecen siempre sobre cualquier ruta permitida.

Las rutas deben ser relativas, canónicas y permanecer dentro del repositorio.
El gate rechaza traversal, rutas absolutas y enlaces no autorizados.

## Árbol limpio

Cada tarea futura comienza con `git status --short` vacío y sin archivos no
rastreados no ignorados. Los cambios previos no se adoptan, eliminan, restauran
ni mezclan automáticamente. La excepción de bootstrap solo aplica a la creación
inicial de este quality gate.

## Auditoría

La independencia es declarada y procedimental: implementador y auditor deben
declararse distintos y la auditoría se ejecuta como fase separada. Esto no
ofrece una garantía criptográfica de identidad o independencia real.
`audit` exige una decisión explícita: `approved`, `changes_required` o
`blocked`.

## Escalamiento

Se escala a Daniel cuando se necesita ampliar archivos permitidos, autorizar
deletions o renames, cambiar el mínimo de pruebas, alterar hashes protegidos,
resolver un árbol previamente sucio o introducir cualquier excepción al
contrato. El quality gate no invoca SimulationCraft ni autoriza Comparator,
runner, adapter, preflight funcional, runs físicos o tareas posteriores.
