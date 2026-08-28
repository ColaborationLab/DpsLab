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
eliminan la selección silenciosa y hacen auditable qué se instaló.

## Auditoría de vulnerabilidades conocidas

`tools/dependency_vulnerability_audit.py` usa `pip-audit 2.10.1` y la Python
Packaging Advisory Database mediante el servicio JSON de PyPI. La herramienta
y sus 28 dependencias transitivas están fijadas por wheel y SHA-256 en
`desktop-app/requirements-security-tools-win-py313.lock`.

La auditoría ejecuta dos consultas independientes: una para el lock funcional
y otra para el lock de herramientas de seguridad. En ambos casos usa
`--require-hashes`, `--disable-pip` y `--strict`, por lo que no realiza una
resolución nueva. Antes de aceptar el resultado verifica hashes, concordancia
lock/SBOM, cobertura completa, versión del scanner y esquema de salida.

Los resultados son cerrados:

- `audit_clean` y exit 0: no queda un hallazgo sin excepción humana vigente;
- `vulnerability_detected` y exit 1: existe al menos un hallazgo no exceptuado;
- `audit_unavailable` y exit 2: no se pudo demostrar identidad, integridad,
  cobertura, acceso a avisos o ejecución correcta.

Toda vulnerabilidad conocida bloquea por defecto aunque no tenga severidad
numérica. El registro versionado de excepciones está vacío. Una excepción
futura requiere decisión separada, paquete y versión exactos, identificador,
propietario, justificación, control compensatorio y caducidad máxima de 30
días. La auditoría no usa `--ignore-vuln`, no actualiza dependencias y no decide
licencias.

CI conserva únicamente un resumen JSON saneado durante siete días. No persiste
respuestas HTTP, variables de entorno, credenciales ni rutas personales.

### Observación vigente de implementación

La observación real atendida de `2026-08-28T03:05:35Z`, ejecutada localmente
con `pip-audit 2.10.1`, cubrió los 6 paquetes funcionales y los 29 paquetes del
lock de herramientas. El lock funcional usa `cryptography 50.0.1`; su wheel
Windows x86-64 CPython 3.13/ABI3 está fijado por SHA-256
`aed8db4f6d71c51efb89530e12d9464e7bf2923d46c3205dc794a2a93f8c0648`.
Los otros cinco paquetes funcionales conservaron exactamente sus versiones y
hashes anteriores.

El resultado fue `audit_clean`, exit 0, con 35 paquetes cubiertos, cero
hallazgos y cero excepciones. El lock funcional quedó ligado por SHA-256
`8d2dfca84345d1c17ef575d50d01eaa36d5cea6fd94c25fc531e7180979e3586`
y el SBOM SPDX por SHA-256
`0f92571035f4db9263cc2709dc4187f4f70db73b5f4e34e0fa826ded672c648c`.
La observación local usó Python 3.12 con los mismos nombres y versiones; la
instalación y ejecución canónica Windows Python 3.13 queda pendiente de una
futura ejecución CI posterior a publicación autorizada.

## Límites pendientes

- El lock inicial no cubre Linux, macOS ni otras versiones de Python.
- La versión del propio `pip` proviene de la distribución Python fijada por CI;
  deberá incluirse en la procedencia del build distribuible.
- Falta verificar licencias y generar el SBOM desde un build reproducible.
- La revisión de licencias y la procedencia reproducible del `pip` usado para
  construir un distribuible permanecen separadas.
- Otras plataformas necesitan locks y auditorías independientes.
- Ningún artefacto descargado durante la resolución se versiona.

## Diseño pendiente: análisis estático y secretos

El siguiente diseño de seguridad separa dos controles que no deben compartir
credenciales: análisis estático de Python y detección de secretos. La dirección
propuesta es adquirir cada scanner por versión y SHA-256 verificables, ejecutar
con privilegios mínimos, conservar sólo un resultado saneado y fallar cerrado
si la identidad, la cobertura o la ejecución no pueden demostrarse.

Un eventual scanner de secretos no usará una acción externa a la que se
entregue `GITHUB_TOKEN`. Las futuras excepciones, si se autorizan por separado,
serán específicas de una huella, con propietario y caducidad; no se permitirán
patrones amplios ni exclusiones permanentes. Este diseño no activa scanners ni
autoriza la exploración del historial del repositorio.
