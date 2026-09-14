# Plan completo para Terra — Base sugerida y scores configurables

Fecha: 2026-09-12. Estado: lote real ejecutado el 2026-09-13; integración y
prueba visual de addon pendientes.
Responsable previsto: Terra (gpt-5.6-terra), un único implementador en serie;
el principal mantiene documentos protegidos, integración y revisión final.
No delegar a otros agentes ni reutilizar autorizaciones de publicación consumidas.

## Autoridad y baseline

Petición de Daniel: revisar nuevo Scope, dejar historial y planificar TODO el
objetivo para Terra. Fuente remota: adc01eccde429f3b8e4e5355697c16dd81bca0b8.
Baseline de código: dd61f94ba697b46b4f977f87ff9d7c03917377c6, rama
codex/live-export-balance-package. Preparación local encima de esa baseline:
Scope actualizado con historial, NEXT_TASK y este plan.
Scope SHA-256: 13b3edea86fe94cc4b9e4e0b4cc7dc0068c6fb9c145afb2834d7ec2902ac60f3.
AGENTS SHA-256: 59336d24041f8a84f293662aefa24528a5b13d340b18ffec76307d39a233247f.
Antes de activar: comprobar baseline, hashes, diff documental exacto y ausencia
de otro escritor; fijar commit de preparación o manifiesto de sus hashes.
El plan no autoriza commit, push, merge, release ni nuevas instalaciones.

Prueba de valor completa: sí, el jugador podrá comparar sus ítems mediante
scores para distintas specs y builds, elegir su presentación y pesos mediante
configuraciones del addon y guardar ítems, builds y pesos estadísticos en
perfiles que puedan actualizarse con resultados elegidos en la app.

El historial registra el cierre humano anterior; NO prueba que los defaults
hayan existido. La generación e inclusión real de esa base sigue pendiente.
La compatibilidad multiclase ya aprobada se conserva. Cubrir las specs del
registro existente con estado individual verificable; no añadir nuevas clases
o specs ajenas a ese registro. No interpretar el límite histórico a Balance
como permiso para eliminar compatibilidad ya solicitada por Daniel.
Si una spec no permite obtener pesos útiles desde SimC, declararla pendiente
y explicar la métrica; DPS de tanque/healer no representa supervivencia/HPS.

## Matriz obligatoria de entrega y aceptación

| Scope | Entrega concreta | Evidencia exigida |
| --- | --- | --- |
| Objetivo principal | Pesos personales compatibles sustituyen el default de esa spec/build en el tooltip | Mismo ítem antes/después; fuente y perfil visibles, score calculado con pesos elegidos |
| 1.1 | Build inicial por spec y pesos sugeridos reales; edición de pesos y restauración de valores iniciales | Instalación sin datos personales ya muestra scores; cadena seleccionable y copiable al editor de talentos; edición persiste tras reload |
| 1.2 | Importación con Reemplazar / Crear nuevo / Cancelar | Cancelar no cambia nada; reemplazar modifica solo perfil elegido; crear conserva anterior; otros personajes/specs intactos |
| 1.3 | Selector de resultados de loadout y botón Exportar pesos | Exportar el loadout no ganador y verificar sus pesos exactos; no exportar automáticamente el ganador ni todos |
| 1.4 | Tooltip del ítem con score, comparación contra equipado y clasificación | Sustancial / marginal / igual o peor, nombre y origen; ítems equipados e inventario; no cambiar spec activa |
| Sección 2: distintas specs/builds | Selección múltiple configurable y persistente | Cambiar selecciones modifica únicamente líneas visibles; desactivar scores elimina todas |
| Sección 2: conservar información | Persistencia de equipo, candidatos guardados, builds y pesos | Cerrar app y reload WoW, abrir otro personaje y volver; no pérdida ni mezcla; simulación offline real e importada |
| Sección 1.1 empaquetado | SimC, addon, defaults y licencias dentro del paquete reducido | Ejecutable empaquetado funciona sin Python externo, sin rutas/perfiles privados incluidos |

Todos los criterios deben tener resultado y evidencia, nunca solo “implementado”.
Si uno no se cumple, el objetivo entero no se declara cerrado.

## Hallazgos que deben resolverse dentro de estas entregas

- Hay soporte para source=generic, pero no una base real genérica distribuida.
- ItemScoreProfiles.imported devuelve item_scores; Refresh busca character_id
  dentro de ese objeto aunque la app lo coloca en la raíz. Corregir el contrato
  y verificar persistencia real, no solo un test de fragmentos de texto.
- Los tooltips leen el último documento importado en lugar de seleccionar
  perfiles persistidos del personaje. Usar identidad del juego compatible con
  nombre/reino/clase exportados; no asumir que un UUID de la app identifica
  por sí solo al personaje actualmente conectado.
- enabled=false devuelve una tabla vacía, pero el consumidor interpreta entradas
  ausentes como habilitadas. Probar el interruptor completo.
- La configuración corta a ocho perfiles y usa hook OnTooltipSetItem. Verificar
  API Retail vigente y adaptar con comprobación de disponibilidad; listas
  desplazables cuando correspondan, sin truncamiento silencioso.
- La app exporta resultados al terminar y escribe nuevamente perfiles de pesos.
  Convertirlo en acción explícita posterior a la selección del usuario.
- Mantener imports externos locales conforme a la decisión vigente: no atribuir
  sus IDs temporales a loadouts del juego. Explicar en el selector de exportación
  por qué esa build no corresponde a un loadout creado en el personaje.
- Persistencia offline actual conserva equipo/nivel/raza, pero reconstruye
  compatibilidad con valores 1 y omite estados de talento/max_level. Conservar
  contexto real por spec, procedencia y validez, sin fingir observación reciente.
  Verificar nuevas imports después de abrir perfil, IDs temporales sin colisiones,
  selección de spec y eliminación sin resucitar builds ni duplicarlas.
- Captura actual guarda equipados, no candidatos de bolsa en ese flujo; no
  afirmar que candidatos persisten hasta comprobar y completar su recorrido.
- Mapeo estadístico actual omite Strength. Cubrir estadísticas pertinentes de
  las specs soportadas en captura, parser, pesos, editor y cálculo.
- Generador actual emite ID e ilvl de equipo. Verificar qué encantamientos,
  gemas y bonus se conservan al simular; corregir pérdida de información que
  invalide pesos usados para scores. No prometer precisión que no se comprobó.

## Secuencia de trabajo

1. Leer Scope/AGENTS/plan y comprobar el estado publicado. Inventariar specs
   soportadas, distribución de SimC y perfiles genéricos disponibles. No usar
   datos privados como defaults ni presentar perfiles de CI como builds óptimas.
2. Fijar una extensión mínima del formato existente: identidad personaje,
   class/spec/build reales, nombre, origen generic/personalized/user_modified,
   valores, cadena de referencia, versión de juego/SimC, escenario y revisión.
   Preservar lectura histórica; identificar contexto faltante sin inventarlo.
3. Preparar base por spec con perfiles genéricos, cadena importable y pesos
   calculados. Registrar procedencia/licencia y comprobar que cadena, equipo
   de referencia y pesos pertenecen a la misma corrida. Incluirla en addon y
   app para funcionar desde la primera instalación. Los datos se actualizan
   manualmente con versión explícita, sin adquisición automática.
4. Implementar edición/selección de perfiles y copia de cadena en addon:
   texto seleccionable con Ctrl+C; el usuario pega en talentos. No modificar
   talentos ni accionar gameplay. Persistir pesos editados distinguiéndolos
   de los calculados, restaurar defaults solo por acción del usuario.
5. Implementar exportación elegida en app. Mostrar nombre, spec, origen,
   resultado y pesos del loadout seleccionado. Resultado pendiente o incompatible
   no se exporta. Mantener simulación offline y guardado de nuevas cadenas.
6. Importar en addon como oferta pendiente, con reemplazo/creación/cancelación.
   Repetir reload no debe duplicar perfiles ni sobrescribir ediciones. Elegir
   perfil destino explícito y actualizar score solo después de aceptar.
7. Calcular score y delta contra equipado bajo el mismo perfil. Propuesta
   inicial de umbral configurable: delta <= 0 igual/peor; 0 < delta < 5%
   marginal; >= 5% sustancial. Mostrar porcentaje y umbral al usuario; es
   clasificación del score lineal, no de DPS. Referencia cero/slot desconocido
   da comparación no disponible. Anillos/trinkets: mostrar ambas referencias;
   armas 1H/2H: comparar conjunto válido o explicar falta de referencia.
   Peso negativo/cero real no debe descartarse silenciosamente: definir
   tratamiento compatible con normalización y validar sin NaN/infinito.
8. Integrar y verificar en paquete completo; pruebas con personajes y
   especializaciones ya soportadas. No cerrar con screenshots de resultados
   DPS solamente: se exige observar scores y cambios de perfiles en WoW.

## Generación real de la base

La entrega requiere corridas reales de SimC. Esta petición planifica; no
inicia corridas. AGENTS exige autorización explícita para ejecución concreta.
Terra debe preparar un manifiesto revisable con binario y SHA, perfiles/specs,
cadena, escenario, métrica, iteraciones, parámetros de escala, número de
corridas, costo estimado y carpeta nueva de salida antes de solicitar la
autorización de esa generación. Reutilizar autorización previa solo si cubre
exactamente ese lote; las simulaciones personales anteriores no cubren este.
Continuar implementación y pruebas independientes mientras se resuelve el lote.
Si falta fuente actual o soporte de spec, señalar la entrada afectada y no
rellenarla con pesos de otra spec. No basta empaquetar registros vacíos.

### Manifiesto preparado, pendiente de autorización de ejecución

- Binario localizado: `D:\Torrent Games\SimC\simc-1210.01.9839551-win64\simc.exe`;
  SHA-256 `8f3496cb10d8dd659b6384a6b551b450e0a89cb4b2f7f325ef55362ae3da82c7`.
- Referencia Balance disponible: `profiles/MID1/MID1_Druid_Balance.simc`, nivel
  90, talento `CYG...`; debe copiarse al directorio nuevo de salida y ejecutarse
  una vez con `calculate_scale_factors=1`, `iterations=1000`, `max_time=300`,
  `fight_style=Patchwerk`, cuatro hilos y artefactos nuevos.
- Restauración: esta distribución no contiene un perfil `*Restoration*.simc`.
  No se puede declarar una base genérica de Restauración a partir de Balance ni
  de un perfil personal. Hace falta que Daniel autorice una fuente de referencia
  apta para Restauración o acepte que aparezca explícitamente como no disponible
  hasta contar con dicha fuente.
- Daniel autorizó el 2026-09-13 ejecutar el lote inicial de Balance y ampliar
  después la cobertura a todas las clases y especializaciones existentes. El
  primer lote conserva exactamente los parámetros de arriba y escribe solo en
  una carpeta nueva fuera de resultados históricos. Cada spec posterior debe
  tener su propio perfil fuente, hash y resultado antes de convertirse en
  default; no se rellenan huecos con datos de otra spec.

### Resultado comprobado del lote (2026-09-13)

- Se ejecutaron corridas reales con el binario y parámetros del manifiesto en
  directorios locales nuevos e ignorados. Se incorporaron 31 perfiles genéricos
  trazables al addon, uno para cada fuente compatible hallada en el registro.
- Quedan explícitamente sin default, sin reutilizar pesos de otra spec:
  Druida Restauración (105), Paladín Sagrado (65), Sacerdote Disciplina (256),
  Sacerdote Sagrado (257), Chamán Restauración (264), Monje Tejedor de niebla
  (270), Evocador Preservación (1468) y Evocador Aumentación (1473). La
  distribución local no aportó un perfil genérico válido para esas fuentes.
- También fallaron por cadenas de talentos no válidas tres fuentes MID1 de
  Cazador, Arcano y Devastación iniciales; fueron sustituidas únicamente cuando
  existía una fuente MID2 independiente y válida para la misma spec.

## Rutas y responsabilidades

Terra al activar: lectura de repositorio, perfiles de referencia seleccionados
y distribución SimC autorizada. Escritura en módulos funcionales relacionados
bajo desktop-app/src/dpslab/, desktop-app/tests/, addon/DpsLab/ (excluidos
Synthetic), herramientas focales nuevas tools/generate_default_weights.py y
sus pruebas tools/tests/, installer/, y datos nuevos versionados bajo
desktop-app/src/dpslab/data/ y addon/DpsLab/Default*.lua.
Artefactos nuevos en build/, dist/ y .dpslab/; nunca reescribir runs previos.
Documentación de ejecución en docs/DEFAULT_WEIGHTS_EXECUTION.md.
Principal: Scope, AGENTS, NEXT_TASK, este plan y compatibilidad del quality gate.
No tocar CI, seguridad, módulos synthetic, perfiles canónicos, escenarios,
variantes ni resultados históricos. No reparar Python global.
Despliegue real, SimC, publicación y commit requieren autoridad aplicable
comprobada al ejecutar. No borrar datos reales para simular primera instalación.
Usar directorio limpio aislado para esa prueba.

## Pruebas, entrega y cierre

Focales con comportamiento, no solo cadenas buscadas en Lua: default disponible,
prioridad personal compatible, edición persistente, importación cancelada,
reemplazo/creación idempotentes, aislamiento, selección no ganadora, dos specs,
apagado total, umbrales y slots, Unicode y copia exacta, perfiles offline con
imports, candidatos guardados, migración, colisiones y actualización de contexto.
Ejecutar suites completas de app y tools; distinguir ejecutadas, aprobadas,
omitidas, fallos y código de salida. Antecedente dd61f94: 1345 ejecutadas,
1344 aprobadas y una omitida; tools 157 aprobadas. No convertir eso en
evidencia actual. No ejecutar SimC accidentalmente durante unit tests.

La conciliación documental reemplaza la allowlist obsoleta por una limitada
a esta preparación. Antes de implementar, alinear el gate con el código autorizado; no eximir
el gate ni modificar pruebas para ocultar fallos. AGENTS permite registro
breve bajo Scope, pero la validación técnica debe reportar su resultado real.
Comprobar hashes protegidos antes/después y diff sin rutas privadas/secretos.
Entrega: diff, evidencia por cada fila de la matriz, pesos reales y fuente,
paquete reducido verificable, instrucciones visuales y limitaciones concretas.
Prueba humana: instalación sin datos -> tooltip generic -> copiar build ->
editar pesos -> simular -> elegir resultado no ganador -> exportar -> cancelar,
crear y reemplazar -> tooltip personalizado -> reload/reinicio -> aislamiento
de otro personaje -> perfil offline con nueva importación.
Cierre solo tras matriz completa, evidencia real de defaults y aprobación
visual de Daniel. La delegación termina al entregar o cambiar el objetivo.
No iniciar otro objetivo.

## Revisión de precisión y correcciones del addon — 2026-09-13

Petición de Daniel: corregir los scores comparativos, mostrar el icono de spec
en cada fila, usar solo `(b)` para la referencia beginner, consultar los pesos
y determinar qué falta para equiparar una simulación completa de SimC.

Hechos comprobados en el código actual:

- `loadout_recommendation.py` llama al motor real con
  `calculate_scale_factors=1`, 1.000 iteraciones, 300 segundos, Patchwerk,
  cuatro threads y sin objetivo explícito de error. El timeout es 600 segundos.
  Esto sí solicita simulaciones perturbadas por stat; no son pesos inventados.
- `loadout_profiles.py` emite `role=attack` incluso para tanks/healers. Por ello
  los resultados de Blood son pesos de DPS, no una evaluación de supervivencia.
- El equipo se reconstruye como `id` e `ilevel`; no se transfieren desde el
  enlace los bonus IDs, gemas ni encantamientos. La duración y el escenario
  tampoco representan automáticamente combate de mazmorra por llamar M+ al loadout.
- El lector de factores conserva valores positivos, pero no guarda sus errores
  ni distingue un cero/negativo medido de un peso ausente. Se descartan los
  informes temporales al terminar. No hay comprobación de convergencia.
- Un score es una suma ponderada de stats visibles. No modela por sí solo
  procs, efectos de abalorios, conjuntos, armas ni viabilidad del tipo de armadura.
  No es una predicción de mejora porcentual de DPS ni debe presentarse como tal.

Procedimiento de precisión propuesto (todavía no implementado):

1. Fidelidad de entrada: conservar equipo completo, bonus IDs, gemas y
   encantamientos; contrastar las estadísticas resultantes con una exportación
   oficial SimC del mismo personaje, talentos y equipo. Fijar versión del motor,
   APL, buffs, escenario, número de objetivos y métrica. Si faltan datos,
   mostrar que la simulación es aproximada antes de llamarla personalizada precisa.
2. Calcular pesos locales con el escalado nativo de SimC. Un peso estima
   `(DPS(stats + delta) - DPS(stats)) / delta`; no es un optimizador que cambie
   pesos hasta encontrar un máximo global. Los pesos se vuelven a calcular
   cuando cambian equipo/talentos/escenario. Evaluar diferencias centradas y
   varios deltas solo cuando ayuden a estudiar sensibilidad o no linealidad.
3. Sustituir el límite fijo de 1.000 por ejecución adaptativa acotada. Punto de
   partida propuesto: `target_error=0.1`, máximo 1.000.000 iteraciones y presupuesto
   de tiempo visible/cancelable. El umbral debe verificarse en el informe;
   alcanzar timeout o límite de iteraciones no acredita haberlo alcanzado.
4. Guardar informe, error de DPS, error y delta de cada factor, versión y
   configuración. El error del DPS medio no garantiza por sí solo pesos precisos:
   una diferencia pequeña entre dos DPS puede tener mucha incertidumbre relativa.
   Repetir con semillas independientes para comprobar estabilidad cuando la
   decisión sea estrecha. No usar un seed fijo como prueba de precisión.
5. Para decidir equipamiento real, simular las alternativas completas con
   presupuesto equivalente, incluidos sus efectos. Si la diferencia no es
   resoluble con la incertidumbre observada, mostrar resultado inconcluso.
   Para optimizar distribuciones, explorar candidatos acotados y validar
   finalistas; una pendiente local no garantiza el óptimo global.
6. Validación de equivalencia: mismo binario, entrada efectiva y opciones en
   DpsLab y SimC; resultados compatibles con el error reportado. DpsLab puede
   mejorar la configuración, trazabilidad y elección de candidatos frente a una
   ejecución rápida, pero no superar la fidelidad del motor que está utilizando.

Fuentes primarias consultadas (algunas páginas incluyen ejemplos antiguos;
los valores/opciones concretos se validarán contra el binario empaquetado):

- https://github.com/simulationcraft/simc/wiki/StatsScaling
- https://github.com/simulationcraft/simc/wiki/StatisticalBehaviour
- https://github.com/simulationcraft/simc/wiki/Equipment

Corrección implementada del addon: el renderizador ya no exige `GetItem`
cuando recibe el enlace por `TooltipUtil`; mantiene una sola sección tras
PostCall/ProcessInfo y reconstrucciones. Icono de spec por fila, sin icono en
el título ni palabra sugerida. `/dpslab scores` abre pesos editables por build,
con copia nombrada y activación persistida; config ofrece acceso directo.
Reimportar un mismo loadout compara contenido y respeta aceptar/cancelar.
Prueba Lua 5.1 cubre tooltips sin GetItem, reconstrucción, ventana, copias,
activación tras recarga y cambio de pesos conservando ID. La verificación en
WoW sigue pendiente de Daniel: el entorno simulado no acredita el resultado visual.

## Prompt para Terra

Continúa desde dd61f94 y la preparación documental verificada. Implementa
serialmente DEFAULT_WEIGHTS_TERRA_PLAN.md y cada fila de su matriz, respetando
Scope y prueba de valor. Reutiliza módulos existentes; corrige los fallos
identificados que impidan el recorrido. Mantén un registro de hechos comprobados,
pendientes y pruebas. Prepara el lote concreto de SimC antes de ejecutarlo bajo
autorización aplicable. No sustituyas pesos reales por fixtures, no declares
terminado un tooltip sin probarlo en el paquete y WoW, ni publiques por tu cuenta.
