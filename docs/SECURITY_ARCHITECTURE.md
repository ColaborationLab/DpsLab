# Arquitectura de seguridad de DpsLab

## Objetivo

DpsLab debe ayudar al jugador sin convertir datos no confiables, contenido
remoto o archivos locales manipulados en código, recomendaciones aprobadas o
actualizaciones activas. La seguridad protege al usuario, su equipo, su cuenta
de juego, sus datos locales y la autenticidad del producto.

No se promete ausencia de vulnerabilidades. Se exige reducción de superficie,
defensa en profundidad, evidencia reproducible y una respuesta segura ante la
incertidumbre.

## Principios obligatorios

1. **Denegar por defecto.** Entrada desconocida, ambigua, obsoleta,
   sobredimensionada, incompatible o sin procedencia produce indisponibilidad,
   no una aproximación silenciosa.
2. **Datos nunca son código.** Ningún catálogo, SavedVariables, respuesta HTTP,
   manifiesto o resultado puede introducir módulos, comandos o Lua ejecutable.
3. **Privilegio mínimo.** Procesos, CI, red, archivos y credenciales reciben
   sólo la capacidad imprescindible y durante el tiempo imprescindible.
4. **Autenticidad antes de activación.** TLS transporta; firma, hashes,
   compatibilidad, vigencia y piso anti-retroceso autorizan elegibilidad.
5. **Separación de decisiones.** Capturar, analizar, aprobar, firmar, publicar,
   descargar y activar son estados distintos.
6. **Privacidad por defecto.** Sin telemetría implícita. Si se autoriza en el
   futuro será opt-in, revocable, minimizada y no condicionará actualizaciones.
7. **Recuperación comprobable.** La última versión compatible conocida se
   conserva; rotación, revocación y recuperación de claves se ensayan sin
   exponer secretos.
8. **Límites medibles.** Toda entrada no confiable tiene tamaño, profundidad,
   cardinalidad, tiempo y vocabulario cerrados.

## Límites de confianza

### Aplicación de escritorio

Son no confiables los perfiles importados, rutas elegidas por el usuario,
resultados externos, paquetes descargados, SavedVariables y salida de procesos.
Se validan antes de persistir y se escriben mediante operaciones atómicas. Los
procesos se lanzan con listas de argumentos, `shell=False`, timeout y ejecutable
identificado por hash cuando el contrato lo requiera.

### Addon

El futuro addon se limita a APIs permitidas por WoW y datos declarativos. No
puede descargar o ejecutar código, guardar credenciales, automatizar combate ni
aceptar campos no definidos. El intercambio con escritorio debe ser versionado,
acotado y validado en ambos extremos. Datos inválidos degradan a guía no
disponible y nunca bloquean el juego.

### Red y conocimiento

Sólo se consultan fuentes explícitamente permitidas mediante HTTPS, con host,
redirección, tipo, tamaño y tiempo controlados. Una captura entra en cuarentena.
La información histórica sirve para auditoría y contraste, no para declarar
vigencia. Fuentes secundarias nunca sustituyen silenciosamente a una fuente
oficial ni elevan por sí mismas una recomendación.

### Actualización y publicación

El actualizador futuro verificará manifiesto firmado, clave confiable, hashes,
canal, compatibilidad, vigencia y piso anti-retroceso antes de preparar una
versión. La preparación ocurre fuera de la ubicación activa y la activación es
atómica. TLS sin firma no es suficiente. Una firma válida hace un artefacto
elegible, no aprobado ni activado.

### Claves y secretos

Las claves privadas de producción permanecen fuera del repositorio, CI, addon,
logs y paquetes. La clave actual usa Ed25519, protección DPAPI del usuario de
Windows y recuperación cifrada independiente. No se introducen credenciales de
Blizzard en el addon ni en binarios distribuidos.

## Puertas de seguridad del ciclo de trabajo

Todo contrato futuro debe declarar:

- activos y límites de confianza afectados;
- entradas no confiables y límites de recursos;
- rutas permitidas, rutas protegidas y privilegios requeridos;
- datos personales, secretos, red y persistencia involucrados;
- fallos esperados y degradación segura;
- pruebas negativas y evidencia de auditoría;
- impacto en actualización, addon y compatibilidad histórica.

Antes de una beta externa son obligatorios:

- modelo de amenazas revisado para el alcance distribuido;
- dependencias reproducibles e inventario SBOM;
- análisis de dependencias, código y secretos en CI;
- formato de actualización firmado y pruebas contra repetición, degradación y
  manipulación;
- firma de confianza del ejecutable/instalador de Windows o una decisión de
  riesgo humana documentada;
- pruebas adversariales de parsers, archivos, paquetes y comunicación con el
  addon;
- política de privacidad, respuesta a incidentes, revocación y rollback;
- revisión independiente de seguridad.

## Prohibiciones permanentes

- secretos o claves privadas versionados;
- `eval`, ejecución dinámica de datos, `loadstring` o comandos construidos con
  entrada no confiable;
- actualización activada únicamente por fecha, nombre de archivo o TLS;
- telemetría oculta o necesaria para usar funciones locales;
- aceptar contenido remoto como vigente por ser el más reciente disponible;
- omitir una validación para mantener recomendaciones visibles;
- afirmar protección de rama, escaneo o firma de plataforma que no exista.

