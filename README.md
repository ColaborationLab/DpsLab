# DpsFoundry — Core + Link

Core es la aplicación de escritorio para simulación y comparación; Link es el
addon de WoW para intercambio local y scores de equipamiento. Guide es futuro,
sin implementación. Los nombres internos `DpsLab` se conservan por compatibilidad.

## Estado de lectura — 2026-09-27

El baseline de interfaz, íconos locales e identidad fue aprobado por Daniel
el 2026-09-27, con autorización de commit/push y transición al objetivo 1.10.
La entrega se mantiene en la rama
[`codex/dpsfoundry-interface-scope`](https://github.com/ColaborationLab/DpsLab/tree/codex/dpsfoundry-interface-scope),
con antecedente `0b9d5f00691b6310b257052686a7fb795603ffea`. No está fusionado en `main`.
Publicar una rama no equivale a distribuir un instalador ni cerrar el objetivo.

## Por dónde empezar

- [Objetivo y límites vigentes](SCOPE_CORRECTION_0_1.md): autoridad de alcance.
- [Instrucciones de trabajo](AGENTS.md): integridad y autorizaciones.
- [Aceptación actual](docs/DPSFOUNDRY_INTERFACE_ACCEPTANCE.md): aprobado frente a pendiente.
- [Funciones para revisión](docs/DPSFOUNDRY_REVIEW_FUNCTIONS.md): qué esperar de la interfaz.
- [Registro de sesiones](docs/NEXT_TASK.md): estado vigente primero, antecedentes después.
- [Sistema visual](docs/DPSFOUNDRY_DESIGN_SYSTEM.md) y
  [recursos visuales](docs/DPSFOUNDRY_VISUAL_ASSETS.md).
- [Referencia técnica de escritorio](desktop-app/README.md) e
  [instrucciones de empaquetado Windows](installer/README-WINDOWS.md).

Código: `desktop-app/src/dpslab/` (Core), `addon/DpsLab/` (Link).
Pruebas: `desktop-app/tests/` y `tools/tests/`.
Las instrucciones técnicas no autorizan ejecutar SimulationCraft automáticamente.

## Qué contiene este repositorio

Código, pruebas, documentación y assets propios usados por el producto.
Los ZIP de referencia visual, instaladores generados, respaldos, logs y datos
locales ignorados no forman parte de esta entrega. No se redistribuyen iconos
extraídos de WoW. La lectura del código no requiere esos artefactos; reproducir
el entorno de ejecución sí requiere las dependencias y el motor correspondientes.

La beta pública de Scope 1.10 es el siguiente objetivo autorizado, todavía no
implementado. Donativos y autoactualización siguen pausados.
