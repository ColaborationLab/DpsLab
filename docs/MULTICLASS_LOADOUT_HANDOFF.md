# Continuación: loadouts de todas las clases y especializaciones

## Valor para el jugador

Sí: este trabajo permite exportar y comparar loadouts de cualquier personaje
según su clase y especialización, conservando el flujo ya probado de Balance.

## Estado y responsable

Plan preparado el 2026-09-10; estado ready_for_human_activation.
Responsable recomendado: Terra (gpt-5.6-terra), único ejecutor, razonamiento alto.
Luna puede ejecutar este mismo plan secuencial si Daniel elige ese modelo.
No hay tareas delegadas iniciadas por esta planificación.
El principal revisa la entrega y coordina la prueba visual de Daniel.

Baseline de código: aba066e77c46d02557b3a90fdb73e9c44c22d77d,
rama codex/live-export-balance-package.
Objetivo nuevo: SCOPE_CORRECTION_0_1.md en origin/main,
commit 9c3410e2bb0e646d11645a0b69df00ec1e723740.
Aplicar sobre la baseline los documentos de esta preparación; al activar,
registrar el commit exacto que los contiene, comprobar árbol limpio y ausencia
de otro ejecutor sobre estos archivos antes de crear un worktree aislado.
No sustituir código probado por el checkout de main sin revisar diferencias.

SHA-256 local de SCOPE_CORRECTION_0_1.md:
52a980d27788bb9710722ce44b25f0011ea62356d1e68f7740877ba195981d30
SHA-256 local de AGENTS.md:
d1b67f089fb267ef94390588785e892a1f1bdc6e84bdb6f3ccf0840813ad1495
Comprobar bytes y terminadores al activar; una diferencia de checkout requiere
comparar con la fuente, no alterar el objetivo para ajustarlo al hash.

La sección 1 autoriza todas las clases/specs, pero la sección 3 aún prohíbe
salir de Balance y la 5 conserva el cierre antiguo. La petición actual de
Daniel manda preparar el nuevo objetivo multiclase: esas frases antiguas no
bloquean este plan. No editar el documento de Daniel para corregirlas.

## Evidencia actual y límites

- Inspección local autorizada el 2026-09-10, sin ejecutar el motor:
  `D:\Torrent Games\SimC\simc-1210.01.9839551-win64\simc.exe`, SHA-256
  `8f3496cb10d8dd659b6384a6b551b450e0a89cb4b2f7f325ef55362ae3da82c7`.
  El paquete contiene `profiles/CI.simc` y perfiles MID1/MID2. Es evidencia
  de vocabulario/perfiles disponibles, no una ejecución válida de cada spec.
- `profiles/CI.simc` muestra Demon Hunter Devourer, pero no aporta el ID de
  especialización de la API de WoW. Mantener esa asociación no disponible
  hasta una fuente o prueba autorizada; no adivinar el ID.

- El exportador ya toma el rol que devuelve el cliente y no contiene un
  allowlist de Druida; la app conserva un registro cerrado para validar la
  correspondencia clase/spec antes de generar un perfil.
- El transporte ya posee class_id, specialization_id y role.
- Los generadores de perfiles y la pantalla son específicos de Druida.
- El perfil de Restauración fuerza role=attack: el DPS obtenido no demuestra
  capacidad de analizar curación ni de recomendar una build por HPS.
- Los resultados incluyen nombres de loadouts exportados y UTF-8.
- El flujo de UI usa un hilo y una cola; conservar actividad visible y evitar
  carreras si el usuario cambia exportación o caso mientras calcula.
- Advisor y los pesos están especializados en Balance/102. No entregar esos
  pesos a otra spec por retirar solamente una validación.
- 28 pruebas focales pasaron y Daniel validó visualmente las correcciones.
  La suite completa no tiene resultado concluyente reciente: Python global
  carecía de dependencias y hubo procesos de pruebas sin resultado capturado.
  No atribuirlo a un defecto histórico sin identificarlo.

## Secuencia de implementación al activar

1. Comprobar capacidades del SimC empaquetado.
   Identificar versión/hash y recursos oficiales correspondientes disponibles.
   Crear una tabla acotada clase/spec -> token SimC, rol, estadística primaria,
   métricas admitidas y soporte comprobado. Verificar con código/documentación
   oficial y pruebas; no inferir soporte por la existencia de un token.
   Cubrir todas las clases/specs presentes en la versión de WoW objetivo.
   Si el motor no implementa una spec/métrica, mostrar motivo preciso y reportar
   esa parte del objetivo pendiente; un mensaje de no disponible no equivale
   a completar soporte universal. Sin motor propio ni métricas inventadas.

2. Generalizar exportación y validación.
   Obtener clase/spec/rol de las APIs del juego y capturar talentos con nombres,
   equipo y stats necesarios. Admitir personaje con un solo loadout.
   Conservar exportación voluntaria y /reload, compatibilidad de payloads
   anteriores, frescura y validación de entradas.
   Si faltan campos para una clase, versionar solamente el intercambio necesario.
   Validar correspondencia clase/spec y rechazar combinaciones contradictorias.

3. Reutilizar el flujo de simulación.
   Extraer lo común de los perfiles existentes a un generador compartido,
   parametrizado por el registro de capacidades. Conservar adaptadores antiguos
   cuando sean necesarios para compatibilidad.
   Considerar armas/mano secundaria, estadísticas primarias, raza y talentos;
   no limitar equipamiento al caso Druida. No deducir equipo ausente.
   Una build produce resultado individual; de dos a cuatro comparan.
   Más de cuatro disponibles permanecen seleccionables, con máximo cuatro por run.
   Mantener imports manuales nombrados, nombres hasta el addon y mismo equipo/
   escenario para comparaciones válidas.
   Mostrar métrica y escenario reales. No comparar DPS y HPS como equivalentes.

4. Generalizar pantalla, biblioteca y resultado recibido por el addon.
   Detectar clase/spec desde la exportación y actualizar título, etiquetas,
   detalles y pesos sin selector fijo de Druida.
   Guardar/reabrir casos conservando identidad de spec, nombres, métrica y
   contexto; leer casos históricos.
   Propagar nombre del import manual, no solo nombres nativos de WoW.
   Validar contexto de resultados/Advisor: nunca reutilizar pesos de Balance en
   otra spec. Si SimC no entrega pesos válidos, indicarlo explícitamente.
   Mantener UTF-8, límites del mensaje Lua y escape seguro de nombres.

5. Verificar y empaquetar.
   Pruebas parametrizadas de la tabla completa, clase/spec inválida, datos
   incompletos, selección individual/2/3/4, imports, nombres y tildes, errores
   del motor, biblioteca y contaminación de contexto entre specs.
   Regresión de Balance/Restauración y actividad de UI con runner controlado.
   Ejecutar focales primero, suite desktop, suite tools y quality gate.
   Usar el entorno de dependencias del proyecto; registrar intérprete y códigos
   de salida. Ante bloqueo, capturar prueba exacta y diagnóstico, sin lanzar
   copias de una suite aún activa ni cambiar Python global.
   Construir paquete reducido con SimC/Tcl/Tk y avisos existentes. Entregar ZIP
   versionado, SHA-256, instrucciones y sin datos/rutas de desarrollo.
   Prueba real coordinada: Balance como control, Feral, otra clase DPS y
   representantes de tanque/sanador con métricas admitidas. El soporte de todas
   las specs exige matriz comprobada, no extrapolar de esos ejemplos.
   Daniel valida pantalla de app y resultado dentro del juego.

## Recursos y frontera de escritura

Lectura: repositorio, objetivo, instrucciones, artefactos del SimC incluido y
documentación oficial pertinente; exports locales solo para la prueba acordada.
Escritura al activar:
- addon/DpsLab/: captura, intercambio y presentación real correspondiente;
- desktop-app/src/dpslab/: transporte/adquisición, perfiles, capacidades,
  runner/config, UI, biblioteca, resultados y pesos del flujo descrito;
- desktop-app/launch_dpslab.py;
- desktop-app/tests/ y tools/tests/: cobertura correspondiente;
- installer/: empaquetado y guía del producto;
- docs/NEXT_TASK.md y docs/MULTICLASS_LOADOUT_HANDOFF.md.
Nuevos módulos permitidos solo para sustituir/generalizar esas responsabilidades.
Generados: build/ y .dpslab/ ignorados; pruebas con directorios temporales.
No modificar AGENTS.md ni SCOPE_CORRECTION_0_1.md por el delegado.

Exclusiones: motor propio, fuentes automáticas, SBOM, firmas, nuevos módulos
synthetic, CI/settings/secretos, perfiles/escenarios/variantes/runs históricos,
instalaciones globales, gameplay automatizado, adquisición de cuentas.
No borrar o renombrar trabajo ajeno. No desplegar en WoW, ejecutar SimC real,
fusionar main, publicar Release o enviar mensajes externos sin la autorización
aplicable. La planificación actual no concede esas acciones por sí misma.

## Entrega y cierre

Entregar diff acotado, tabla de capacidades con evidencia, pruebas y sus fallos
si existen, paquete con hash, limitaciones por spec/métrica y pasos de prueba.
La implementación local requiere activar este plan; commit/push y despliegue
se coordinan con el principal según la autorización vigente.
Parar únicamente la parte que requiera otro recurso/autoridad o tenga conflicto
de dueño; continuar lo independiente. No ocultar una carencia de SimC.
Cierre: capacidades verificadas para todo el objetivo, regresiones resueltas,
paquete reproducible y prueba visual de Daniel. Si hay specs sin soporte, el
objetivo total permanece pendiente con causa y siguiente decisión concretas.
La autoridad delegada termina con la entrega o una revocación de Daniel.

## Prompt para Terra o Luna

Actúa como único ejecutor de docs/MULTICLASS_LOADOUT_HANDOFF.md. Lee el objetivo
actual y el plan, verifica baseline/hash y ausencia de trabajo simultáneo.
Implementa secuencialmente la captura y simulación multiclase reutilizando el
flujo aprobado. Empieza por comprobar capacidades reales del SimC incluido.
Preserva pruebas de Balance y nombres, UTF-8, progreso y máximo de cuatro builds.
Completa pruebas y paquete antes de pedir la prueba visual coordinada. Reporta
limitaciones verificadas sin equiparar DPS con curación/supervivencia. No
inicies otros agentes, despliegues, merges ni Releases.
