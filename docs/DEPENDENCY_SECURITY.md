# Seguridad de dependencias

## Alcance inicial

La resolución reproducible inicial corresponde exclusivamente a GitHub Actions
en `windows-latest`, CPython 3.13.14 y arquitectura x86-64. El archivo
`desktop-app/requirements-ci-win-py313.lock` fija cada dependencia directa,
transitiva y de construcción, exige wheels y enlaza el SHA-256 del wheel
resuelto para ese entorno.

CI instala primero el lock con `--require-hashes`. Después instala DpsLab con
`--no-deps --no-build-isolation`, por lo que la construcción no puede resolver
dependencias adicionales. El `pyproject.toml` fija también la versión exacta de
setuptools requerida por el backend.

## Inventario SBOM

`security/sbom-runtime-win-py313.spdx.json` registra DpsLab y los seis paquetes
resueltos. Conserva nombres, versiones, relaciones, PURLs y hashes SHA-256 de
los wheels cuando aplican. Una licencia no revisada se mantiene como
`NOASSERTION`; el SBOM no inventa conclusiones legales.

## Actualización

Actualizar una dependencia requiere una tarea separada que:

1. resuelva para el mismo entorno declarado;
2. descargue sin instalar y calcule hashes de bytes;
3. actualice lock, SBOM y relaciones en una sola transacción;
4. ejecute pruebas focales, herramientas y suite funcional;
5. realice auditoría de vulnerabilidades y licencia por separado;
6. publique sólo después de revisión y CI satisfactoria.

El lock y el SBOM no prueban que una versión carezca de vulnerabilidades. Sólo
eliminan la selección silenciosa y hacen auditable qué se instaló. La puerta
`dependency_audit` permanece abierta hasta integrar una fuente de avisos,
política de severidad y excepciones con caducidad.

## Límites pendientes

- El lock inicial no cubre Linux, macOS ni otras versiones de Python.
- La versión del propio `pip` proviene de la distribución Python fijada por CI;
  deberá incluirse en la procedencia del build distribuible.
- Falta verificar licencias y generar el SBOM desde un build reproducible.
- Falta escaneo automático de vulnerabilidades y revisión de dependencias
  transitivas nuevas.
- Ningún artefacto descargado durante la resolución se versiona.

