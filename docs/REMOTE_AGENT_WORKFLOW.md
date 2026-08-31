# DpsLab — trabajo remoto de agentes 0.1

Este documento define el protocolo operativo para colaboradores externos y
agentes subordinados. No concede autoridad por sí mismo: cada tarea debe tener
un Issue y un contrato cerrado aprobado por N0-GOV.

## Roles

- **N0-GOV / Daniel**: decide alcance, excepciones, permisos externos,
  aprobación humana, publicación y activación.
- **Codex principal**: mantiene la arquitectura y la integración final; es el
  único responsable de aceptar cambios en `main`, producción, addon,
  conocimiento, seguridad, CI, claves y releases.
- **Work / N1-OPS**: prepara diagnósticos, contratos, auditorías y
  verificaciones remotas sin convertirlas en autorización.
- **Agente subordinado o colaborador externo**: ejecuta únicamente el Issue
  asignado en una rama propia y entrega un PR auditable.

## Flujo obligatorio

1. N0-GOV publica un Issue con `task_id`, baseline, rutas permitidas,
   rutas prohibidas, pruebas y criterio de cierre.
2. Con permiso `Read`, el colaborador crea un fork privado y abre allí
   `agent/<task_id>/<slug>` desde la baseline indicada. Solo una autorización
   posterior de `Write` permite crear la rama directamente en el repositorio.
3. Trabaja solo dentro de la allowlist, sin secretos ni datos reales.
4. Ejecuta las pruebas indicadas y abre un PR con la plantilla del repositorio.
5. Codex principal revisa diff, hashes protegidos, pruebas y límites.
6. La aprobación humana, el merge y el push son decisiones separadas; no se
   usa el PR como autorización implícita.

Nunca se trabaja directamente sobre `main`, se hace force-push, se cambia el
remoto, se crean releases ni se habilitan workflows desde una tarea delegada.

## Matriz de propiedad

| Área | Agente subordinado | Codex principal |
|---|---|---|
| `docs/**`, salvo documentos protegidos | Solo con Issue cerrado | Revisión final |
| `tools/tests/**` sintéticos | Solo con Issue cerrado | Revisión final |
| `desktop-app/src/**`, `addon/**`, `knowledge/**`, `security/**` | No | Exclusivo |
| `.github/workflows/**`, settings, secretos y permisos | No | Exclusivo |
| perfiles, escenarios, variantes, comparaciones y resultados | No | Exclusivo |
| SimulationCraft, observación real, releases y claves | No | Exclusivo y con autorización separada |

La matriz orienta la revisión y no sustituye las protecciones de GitHub.

## Seguridad y datos

No se aceptan nombres, reinos, GUID, SavedVariables, perfiles personales,
tokens, claves privadas, logs con identificadores ni datos capturados del juego.
Se prefieren fixtures sintéticos y resultados fail-closed. Un dato no puede
convertirse en código, comando o módulo ejecutable. Cualquier hallazgo se
reporta sin incluir secretos y sigue el flujo diagnóstico → corrección →
auditoría → aprobación.

## Invitación de colaboradores

La invitación se realiza en GitHub, no desde una conversación de Work/Codex:
repositorio `dpcs90/DpsLab` → **Settings** → **Collaborators** (o
**Collaborators and teams**) → **Add people** → escribir el nombre exacto de
la cuenta → asignar inicialmente **Read**. Tras aceptar, se configura el
alcance del conector para `DpsLab` y se mantiene la regla de fork, rama y PR.
No se debe compartir una contraseña, token personal ni clave de firma.

Para elevar permisos a Write/Maintain/Admin hace falta una decisión humana
posterior y una justificación de necesidad mínima. Sin el nombre exacto de la
cuenta no se debe enviar ninguna invitación.
