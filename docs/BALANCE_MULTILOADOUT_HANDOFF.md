# Entrega completa — Balance multiloadout 0.1

Estado: ready_for_human_activation. Preparación solicitada por Daniel en esta
sesión; no se ha iniciado un ejecutor. Responsable recomendado: Terra, como
único ejecutor. Luna puede sustituirlo al activar, nunca en paralelo.
La asignación expresa de Daniel a Terra/Luna cubre la implementación de este
objetivo completo; las restricciones de la antigua cuenta colaboradora no
impiden esta sustitución local del agente principal.

El campo audit del formato legado se conserva para compatibilidad del parser;
rige la excepción de AGENTS.md: revisión directa de Daniel durante este ciclo.

## Fuente y punto de partida

Leer AGENTS.md, SCOPE_CORRECTION_0_1.md y este documento.
Objetivo recibido en origin/main 35b28f54b232e1019d40d282235765a3367a07ad.
Baseline funcional integrada: 0897bbc0077938848846512401f278884ba3bab4.
Rama de entrega: codex/live-export-balance-package.
Comenzar desde el commit publicado que incorpora este plan, verificando que
la baseline sea ancestro y el árbol esté limpio. Registrar su SHA exacto al
activar. No usar el checkout principal: contiene trabajo ajeno sin integrar.
Crear un worktree aislado para el ejecutor. El principal no implementará en
paralelo; comprobar de nuevo tareas activas y estado Git al activar.

Prueba de valor: sí, permite comparar loadouts propias e importadas lado a
lado y obtener pesos de estadísticas para el equipo simulado.

protected_files (SHA-256 de los bytes locales actuales):
- AGENTS.md: d1b67f089fb267ef94390588785e892a1f1bdc6e84bdb6f3ccf0840813ad1495
- SCOPE_CORRECTION_0_1.md: 3751ad5864ceb62cad2c82a8d4a0f2c384be1e0c0aa555d8a5eb3092d00f8bbf

Estos hashes son de archivos locales; Git puede normalizar CRLF/LF en otro
checkout. Ante diferencia, comparar el contenido con la baseline y verificar
si solo cambian finales de línea antes de diagnosticar una edición. Registrar
los hashes reales del checkout de ejecución; no alterar el objetivo para
hacer coincidir un hash.

## Entrega y orden de implementación

1. Exportación y selección. Ampliar el flujo existente de dos loadouts a una
   lista de hasta cuatro seleccionadas. Leer las builds guardadas que WoW
   exponga y permitir añadir manualmente un nombre y string de talentos.
   Mantener lectura de exportaciones históricas de dos builds. Validar clase,
   especialización Balance, formato, longitud, duplicados, lista vacía y límite;
   rechazar sin ejecutar los datos inválidos. No descargar guías.
   Registrar la fecha/id de la acción explícita de exportar en el payload:
   la mtime de SavedVariables puede renovarse sin una nueva exportación.
   Distinguir exportación nueva, última exportación e historial guardado.

2. Ejecución. Reutilizar runner y creación de perfiles, con el mismo equipo
   y escenario para las 2–4 builds elegidas. No generar combinaciones.
   Mantener la interfaz receptiva con progreso, errores por build y recuperación
   de una ejecución fallida; impedir comparaciones simultáneas involuntarias.
   Cada run tiene artefactos propios. Usar exclusivamente el SimC incluido en
   el paquete para el usuario final. No introducir un motor nuevo.

3. Comparativa y detalles. Mostrar columnas por build con DPS, diferencia
   absoluta/porcentual respecto a una referencia identificada, incertidumbre
   cuando exista, duración, iteraciones, escenario y versión SimC. Ofrecer
   detalle por build: estadísticas/equipo, talentos, contribución de habilidades
   y reporte HTML de SimC cuando esté disponible. Datos ausentes se indican
   como no disponibles. No prometer paridad con todos los simuladores.
   El selector debe cambiar el detalle real, no solo su etiqueta.

4. Biblioteca local optativa. Guardar solo cuando el usuario pulse Guardar,
   con nombre del caso, fecha, builds, equipo/escenario, resúmenes y artefactos
   necesarios para reabrirlo. Mantenerla en el perfil del usuario, fuera del
   paquete y del repositorio. Escritura atómica y casos independientes.
   Reabrir tras reiniciar sin ejecutar SimC otra vez; identificarlo como caso
   guardado. Primera instalación en perfil vacío no muestra casos de pruebas.
   No incorporar rutas personales ni exportaciones reales a Git.

5. Pesos y exportación. Solicitar explícitamente al SimC incluido el cálculo
   de pesos para la build seleccionada y su equipo/escenario; conservar valores
   absolutos y normalizados cuando SimC los ofrezca. No calcular pesos a partir
   de porcentajes DPS ni inventar valores. Exportar resultados JSON/CSV y un
   estructura compatible con Pawn, visible en la app, con copia/archivo a
   elección del usuario. La estructura sirve para compatibilidad, no exige
   exportar un formato Pawn concreto.
   Entregar también los pesos y el contexto al addon DpsLab para que Advisor
   pueda consumirlos y mostrar sugerencias de equipo vinculadas a ese caso.
   No basta con un archivo que el addon no lea. Validar contexto y datos;
   cambios de equipo/build invalidan aplicabilidad. No convertir pesos locales
   en un optimizador universal ni automatizar acciones de juego.

6. Paquete y comprobación real. Reconstruir la distribución reducida completa
   con Python/Tcl/Tk y SimC incluidos, aviso GPL y acceso al código fuente.
   Probar extracción en carpeta distinta y perfil de usuario limpio.
   Verificar ausencia de biblioteca, rutas y datos reales de desarrollo.
   Entregar un ZIP inequívocamente versionado y su SHA-256, guía breve y evidencia.
   La prueba visual de Daniel en el juego y la aplicación sigue siendo necesaria.

## Archivos y recursos autorizados al activar

Escritura dentro del objetivo:
- desktop-app/src/dpslab/ (solo flujo de exportación, perfiles, simulación,
  presentación, biblioteca y exportaciones descritos arriba);
- desktop-app/tests/ (pruebas correspondientes);
- desktop-app/launch_dpslab.py;
- addon/DpsLab/ (exportación, recepción de resultados/pesos y Advisor real);
- tools/tests/ (pruebas correspondientes del addon/empaquetado);
- installer/; docs/BALANCE_MULTILOADOUT_HANDOFF.md; docs/NEXT_TASK.md.
Artefactos generados: build/ y .dpslab/ ignorados; biblioteca y pruebas de
persistencia en directorios temporales elegidos para la prueba.
Leer módulos existentes y recursos de build disponibles; no reparar Python
global ni instalar herramientas ajenas como parte de este objetivo.

Congelados: otras clases/especializaciones nuevas, conocimiento gobernado,
fuentes automáticas, SBOM, firmas, nuevas funciones synthetic, CI/settings,
secretos, perfiles y runs históricos, escenarios/variantes canónicos,
AGENTS.md y SCOPE_CORRECTION_0_1.md. Conservar compatibilidad de Restauración;
la funcionalidad nueva es Balance. No borrar ni renombrar trabajo ajeno.

## Verificación y evidencia exigida

- Antes de cambios: árbol limpio, baseline, intérprete y hashes.
- Pruebas focales existentes de adquisición, transporte, rutas, perfiles y
  recomendaciones; añadir cobertura de 3/4 builds, imports inválidos,
  duplicados, errores parciales, biblioteca/reapertura y exportaciones de pesos.
- Caso de regresión: /reload ordinario no convierte un payload antiguo en
  una exportación recién solicitada.
- Suite completa desde desktop-app: PYTHONPATH=src,
  python -m unittest discover -s tests -v.
- Suite de herramientas desde raíz:
  python -m unittest discover -s tools/tests -v.
- Actualizar la tarea activa al activar la implementación, con esta baseline,
  allowlist y pruebas; ejecutar python tools/quality_gate.py run.
  No dejar activo el antiguo contrato synthetic ni relajar validaciones para
  ocultar fallos. Reportar pruebas, subtests y códigos de salida por separado.
- Verificación real: abrir paquete extraído, exportar Balance desde WoW,
  seleccionar tres y cuatro builds incluyendo una importada, comparar,
  inspeccionar detalles, guardar/reabrir, visualizar pesos compatibles con Pawn
  y ver el caso/pesos en
  Advisor. Verificar que los números coinciden con los artefactos de SimC.
- Las invocaciones reales de SimC y la modificación de la instalación de WoW
  se coordinan con Daniel para esa prueba concreta, conforme a AGENTS.md.
  Mientras tanto completar código, pruebas y empaquetado; no simular aprobación
  visual ni usar mocks como evidencia de ejecución real.

## Límites de la entrega

La activación autoriza implementación y verificaciones locales descritas.
El ejecutor entrega diff, pruebas, paquete y reporte al principal; commit/push
de la implementación se rigen por la autorización vigente al activarlo.
No autoriza merge en main, publicación de Release, despliegue automático,
mensajes a colaboradores, acceso a cuentas ni trabajo posterior.
Detener únicamente la parte afectada si necesita otro alcance, permisos de
sistema, edición inesperada de archivos protegidos o existe conflicto de dueño;
continuar lo independiente. Nunca incorporar el trabajo CASC del checkout
principal a esta tarea.

Cierre: todos los seis entregables verificables, pruebas técnicas aprobadas y
revisión visual de Daniel. La autoridad termina con esa entrega; no iniciar
otro objetivo. Reportar qué puede hacer el jugador, cualquier excepción y la
proporción de trabajo directamente dirigida al objetivo.

## Prompt de activación

Actúa como único ejecutor de docs/BALANCE_MULTILOADOUT_HANDOFF.md desde el
commit publicado que contiene este plan. Lee el objetivo vigente, confirma
baseline y ausencia de solapamientos, prepara un worktree aislado y completa
los seis entregables para Druida Balance. Reutiliza lo implementado, informa
avances y prepara el paquete para la prueba real de Daniel. Mantén separadas
las pruebas técnicas y la validación visual; no hagas merge ni Release.
