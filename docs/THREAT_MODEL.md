# Modelo de amenazas de DpsLab 0.1

## Alcance y supuestos

Este modelo cubre la aplicación local, el futuro addon, el intercambio entre
ambos, fuentes de conocimiento, actualización, GitHub Actions y custodia de
claves. No supone que el equipo del usuario, GitHub, Blizzard, un fansite, una
descarga o un archivo local sean siempre confiables.

El addon opera dentro del sandbox de World of Warcraft, pero aún puede recibir
datos manipulados, consumir recursos excesivos, degradar la experiencia o
presentar guía incorrecta. La aplicación de escritorio tiene mayor impacto
porque accede a archivos, red y procesos locales.

## Activos protegidos

- equipo y cuenta de Windows del usuario;
- cuenta y experiencia de juego, sin automatización prohibida;
- datos de personaje y preferencias locales;
- disponibilidad y corrección de la guía;
- autenticidad de binarios, addon y paquetes de conocimiento;
- claves de publicación y confianza de recuperación;
- repositorio, CI y trazabilidad de releases;
- privacidad y consentimiento del usuario.

## Adversarios y fallos considerados

- contenido remoto o paquete deliberadamente malicioso;
- dependencia o infraestructura de publicación comprometida;
- archivo local manipulado, corrupto o excesivo;
- atacante con acceso parcial al equipo o medios de recuperación;
- error del mantenedor, configuración insegura o publicación accidental;
- incompatibilidad por parche, rollback, repetición o reloj incorrecto;
- fallo de disponibilidad usado para inducir una degradación insegura.

## Escenarios prioritarios

### TM-01 — Datos convertidos en ejecución

Un perfil, SavedVariables, catálogo, HTML o manifiesto intenta introducir un
comando o código. Mitigación: formatos declarativos cerrados, ninguna carga
dinámica, argumentos estructurados y prohibición de `eval`/`loadstring`.
Estado: control arquitectónico establecido; requiere pruebas adversariales por
componente antes de distribución.

### TM-02 — Actualización manipulada o degradada

Un intermediario, mirror o estado local intenta activar bytes distintos,
repetir una versión vulnerable o bajar el piso de seguridad. Mitigación futura:
manifiesto Ed25519, hashes, canal y compatibilidad enlazados, contador/piso
anti-retroceso, staging completo, activación atómica y última versión conocida.
Estado: puerta de beta abierta; el actualizador aún no está implementado.

### TM-03 — Compromiso de clave de publicación

La clave se filtra, copia o usa fuera de una ceremonia autorizada. Mitigación:
DPAPI de usuario, recuperación cifrada independiente, separación de operaciones,
registro público, rotación y revocación. Estado: custodia inicial implementada;
falta ejercitar revocación y recuperación operativa antes de beta.

### TM-04 — Fuente externa falsa, ambigua u obsoleta

Una fuente entrega contenido alterado o una página cambia de estructura. La
captura podría convertirse en consejo incorrecto. Mitigación: host y HTTPS
permitidos, límites, recibos hash, cuarentena, revisión y cobertura vigente.
Estado: controles de adquisición implementados; ninguna fuente aprueba sola.

### TM-05 — Agotamiento de recursos

Entradas profundas, grandes o repetitivas consumen memoria, CPU, disco o tiempo
y afectan al juego o al equipo. Mitigación: límites de bytes, profundidad,
cardinalidad, retención y timeout; el addon debe degradar sin bloquear WoW.
Estado: parcial; cada parser y el intercambio addon deben probar sus límites.

### TM-06 — Escape o confusión de rutas

Una ruta absoluta, traversal, enlace simbólico o archivo colisionante causa
lectura o escritura fuera del destino. Mitigación: raíces preexistentes,
confinamiento por resolución, rechazo de symlinks, no sobrescritura y reemplazo
atómico. Estado: parcial; requiere campaña adversarial transversal.

### TM-07 — Cadena de suministro comprometida

Una dependencia, Action o herramienta introduce código no revisado. Mitigación
actual: Actions por SHA, CI de lectura y rangos superiores. Falta: lock
reproducible, SBOM, auditoría de vulnerabilidades y análisis estático.
Estado: puerta de beta abierta.

### TM-08 — Secreto expuesto por CI, logs o paquete

Un token, contraseña, clave o credencial termina versionado o publicado.
Mitigación: ubicaciones prohibidas, CI sin secretos y evidencia no secreta.
Falta escaneo automático y prueba de artefactos. Estado: puerta de beta abierta.

### TM-09 — Abuso o corrupción del intercambio addon–escritorio

SavedVariables falsificadas o incompatibles alteran guía, estado o recursos.
Mitigación futura: schema/versiones cerrados, tamaños máximos, doble validación,
paquetes firmados hacia el addon y ninguna instrucción ejecutable desde él.
Estado: diseño pendiente; bloquea addon distribuible.

### TM-10 — Privacidad y telemetría inesperada

Se envían datos de personaje, equipo o uso sin comprensión o consentimiento.
Mitigación: operación local, telemetría ausente y futuro opt-in revocable y
minimizado. Estado: seguro por ausencia actual; una función de red debe reabrir
la revisión de privacidad.

### TM-11 — Guía incorrecta presentada como confiable

Datos históricos, incompletos o para otra build se muestran como actuales.
Mitigación: procedencia, vigencia, compatibilidad, cobertura por rol y resultado
`guidance_unavailable`. Estado: controles de conocimiento en desarrollo; toda
presentación futura debe conservar el motivo de degradación.

### TM-12 — Compromiso de CI o publicación directa en `main`

Un cambio evita revisión o una automatización obtiene escritura. Mitigación:
permisos mínimos, credenciales no persistidas, Actions fijadas y auditoría
posterior. La ausencia de protección de rama no debe presentarse como control.
Estado: riesgo residual conocido; requiere controles compensatorios y revisión
de configuración antes de una release.

## Criterio de aceptación de riesgo

Un riesgo no se cierra sólo porque existan pruebas. Debe tener control
implementado, evidencia negativa, propietario, impacto residual y decisión
humana. Los escenarios marcados como puerta de beta impiden distribución
externa, pero no investigación o desarrollo sintético dentro de límites.

El modelo se revisa cuando cambien permisos, dependencias, red, persistencia,
formato de paquete, API de WoW, canal de actualización o custodia de claves.

