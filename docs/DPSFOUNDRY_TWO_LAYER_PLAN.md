# Navegación y simulación en dos capas — 2026-09-20

Estado: arquitectura de navegación del ciclo UI implementada; ampliaciones
funcionales de este documento solo planificadas por instrucción de Daniel.
No autoriza ejecutar SimC ni captar datos adicionales.

## Ahora: organizar las capacidades existentes

Simulación → Comparar → Personaje → Inicio → Recomendaciones → Link → Ajustes.
Setup se conserva al final, reservado para redefinición; no concentra acciones.
Simulación contiene detectar/pegar exportación, acceso a perfiles guardados,
selección de 1–4 builds, importaciones y ejecución existente. Ajustes contiene
ruta de Link, recordar rutas, estado del motor incluido, idioma y tema.
Comparar presenta resultados; Personaje conserva y muestra equipo/perfiles.
Un solo estado de perfil y comparación: la navegación no duplica datos ni runners.

Arte por contexto: exterior de fortaleza en Inicio/Ajustes/Setup; forja en
Simulación/Comparar; interior/arsenal en Personaje/Recomendaciones/Link. Menú
lateral acompaña la variante activa. Metal rústico exclusivo de Foundry.
Equipo compacto en dos columnas; nombre, slot y nivel visibles, stats en tooltip
y texto accesible; retrato neutro hasta disponer de imagen local autorizada.

## Después: capa 1 — decidir talentos

Usar el equipo del perfil como referencia fija, mismo escenario y configuración
para las builds elegidas. Conservar resultados, error e identidad de ejecución.
Elegir una build para continuar; por defecto la de mayor DPS entre las simuladas.
Permitir elegir otra expresamente. Pesos de esa build o selección explícita;
optimizar qué pesos calcular requiere un lote funcional posterior, no este UI.

## Después: capa 2 — optimizar equipo de una sola build

Entrada: snapshot inmutable de personaje/equipo, build seleccionada, escenario,
motor y referencia a la ejecución de capa 1. Fijar talentos; no cruzar todas las
builds con todos los equipos. Crear ejecuciones nuevas, nunca reescribir capa 1.

Fuentes pendientes, separadas y etiquetadas:

- Objetos realmente disponibles en inventario: captación pendiente de autorización.
- Objetos externos/sugeridos por slot: catálogo aplicable a clase/spec, versión,
  temporada y escenario, con fuente/fecha; no confundir sugerido con poseído.
- Gemas y encantamientos: selección y compatibilidad de slots pendientes de
  autorización. No aplicarlos al juego; solo simulaciones hipotéticas futuras.

Preparación futura visible: revisar candidatos, excluir piezas, limitar variantes
y confirmar presupuesto antes de ejecutar. Enumeración acotada; sin producto
cartesiano indiscriminado. Pesos sirven de orientación local, no sustituyen la
simulación de procs, abalorios, sets ni interacciones.

Salida: alternativas completas de equipo con DPS total, delta contra referencia,
error, cambios por slot y límites. Nunca sumar impactos individuales para
inventar el total ni etiquetar una orientación meta como mejora medida.
Recomendaciones numeradas de objetos, gemas y encantamientos solo tras contar con
evidencia aplicable; mantener separadas orientación genérica y mejora simulada.

## Tiempo, precisión y límites

Proponer presupuesto total y reparto entre capas, número máximo de candidatos y
precisión deseada. Estimar tiempo a partir de runs medidos en el equipo; no prometer
duración universal. Una reducción de candidatos limita cobertura, no prueba óptimo
global. Parada/cancelación segura conserva resultados completos y marca incompletos.
No bajar silenciosamente precisión para cumplir un reloj. No ordenar como ganador
concluyente una diferencia compatible con el ruido de simulación.

La mejor build con el equipo inicial puede dejar de serlo al cambiar piezas:
dos capas no garantizan un óptimo conjunto de talentos/equipo. Ofrecer posteriormente
una validación final opcional y acotada de finalistas, con coste explicado y
confirmación; no ejecutarla automáticamente ni reabrir matrices masivas.

## Secuencia futura y aceptación

1. Aprobar fuentes/captación, catálogo meta y compatibilidad por slot.
2. Implementar persistencia separada de candidatos y vínculo a capa 1.
3. Implementar runner acotado de capa 2, cancelación y presupuesto.
4. Conectar controles y recomendaciones con límites visibles.
5. Probar perfil guardado sin WoW, cambios de equipo, gemas/encantamientos,
   candidatos inválidos, cancelación, diferencias pequeñas y restauración de runs.

Nada de lo propuesto queda descartado. Hasta autorización funcional específica,
no hay nuevos botones que aparenten poder ejecutar la capa 2, captura de mochila,
adquisición de catálogo, gemas/encantamientos ni DPS individual por objeto.

## Iluminación: decisión pendiente

No se amplía el brillo en esta entrega. Se mide el efecto existente sin SimC,
con/sin efectos, en la misma ventana y resolución. Una prueba offscreen de grab()
no mide FPS del juego ni consumo GPU de una sesión real. El brillo estático en
pocas superficies es la opción propuesta; evitar desenfoque global y animación
continua. Antes de extenderlo, validar también en sesión real con WoW y escalado
Windows alto. Referencia técnica: https://doc.qt.io/qt-6/qgraphicsdropshadoweffect.html

Medición local del 2026-09-20: 3 calentamientos y 15 capturas completas por
condición, orden on/off/off/on, sin tests ni build concurrentes en la segunda
pasada. A 1240×800, medianas de Simulación: 30.24/31.10 ms con efecto,
29.77/29.51 sin efecto; Inicio: 31.27/30.11 con efecto, 29.98/30.04 sin efecto.
A 1920×1080: Simulación 42.54/42.95 vs 42.16/42.09; Inicio 43.54/43.58 vs
44.53/44.82 (ruido mayor que la diferencia). No evidencia de impacto severo
del efecto estático actual; no es evidencia para generalizar blur a todos los
textos. No mide CPU en reposo, GPU, FPS in-game ni equipos de gama baja.
