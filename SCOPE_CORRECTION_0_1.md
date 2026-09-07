# SCOPE_CORRECTION_0_1.md

## Autorización de Daniel — corrección de alcance obligatoria

Este documento tiene prioridad sobre cualquier tarea, contrato o autorización
previa en `docs/NEXT_TASK.md` o `AGENTS.md` que no esté directamente
relacionada con el objetivo único definido en la sección 1. Ninguna tarea
nueva puede aprobarse ni implementarse sin pasar primero la prueba de la
sección 2. Esta corrección permanece vigente hasta que Daniel la levante
explícitamente por escrito.

## 1. Objetivo único vigente (todo lo demás queda congelado)

El único trabajo autorizado a partir de ahora es completar, de punta a punta,
con datos reales (no sintéticos), una sola cadena de valor:

1. El addon lee el equipo, talentos y especialización reales del personaje
   (no un fixture sintético).
2. La app de escritorio usa esos datos reales para correr o comparar
   simulaciones ya existentes (parser, runner, comparador — componentes ya
   implementados y reutilizables).
3. El addon muestra al jugador, dentro del juego, una recomendación concreta
   basada en ese resultado real (aunque sea texto simple, sin interfaz
   elaborada).

Se aplica a una sola especialización (la más avanzada actualmente: Druida).
Ninguna otra clase, rol o especialización se toca hasta que esta cadena
funcione de extremo a extremo.

## 2. Prueba de valor obligatoria

Antes de proponer, diseñar o implementar cualquier tarea, Codex debe
responder explícitamente, en una sola frase y en lenguaje simple:

> "¿Esta tarea hace que un jugador reciba hoy una recomendación real
> (no sintética, no de diseño, no de gobernanza) que no tenía antes?"

- Si la respuesta es **no**, la tarea queda congelada. No se diseña, no se
  implementa, no se documenta como "next task" — se descarta o se pospone.
- Ninguna tarea puede justificarse por "seguridad", "auditoría",
  "gobernanza", "procedencia" o "preparación para release" a menos que
  Daniel la autorice mencionando esa característica por su nombre exacto,
  en un mensaje aparte, fuera de este flujo de corrección.

## 3. Trabajo congelado explícitamente

No se continúa, expande ni "mejora" ninguno de estos frentes salvo
autorización nueva y explícita de Daniel:

- Firma criptográfica de releases / ceremonia de custodia de claves.
- Programa formal de SBOM, modelo de amenazas, y auditoría de
  vulnerabilidades más allá del escaneo básico ya integrado.
- Pipeline automático de adquisición de fuentes oficiales / notas de parche.
  Se reemplaza por: Daniel actualiza a mano un archivo de datos cuando haga
  falta.
- Cualquier nuevo esquema de "conocimiento gobernado", catálogo, propuesta,
  revisión o candidato que no sea parte directa del objetivo de la sección 1.
- Cualquier addon/funcionalidad adicional marcada como "synthetic".
- Cualquier expansión a otra clase, especialización o rol.

Nada de esto se borra — se archiva. Puede retomarse más adelante si alguna
vez el proyecto se distribuye a terceros, que hoy no es el caso.

## 4. Formato de reporte obligatorio

Al final de cada sesión de trabajo, Codex reporta a Daniel en lenguaje llano,
sin JSON, sin terminología de contrato:

1. Qué puede hacer un jugador hoy que no podía hacer antes de esta sesión.
2. Si se tocó algo fuera del objetivo de la sección 1, y por qué, en una
   frase.
3. Cuánto de la sesión fue directamente hacia el objetivo de la sección 1.

Si el punto 1 queda vacío dos sesiones seguidas, la sesión siguiente se
dedica exclusivamente a explicar el bloqueo concreto, sin nueva
infraestructura.

## 5. Vigencia

Esta corrección se mantiene activa hasta que el objetivo de la sección 1
esté funcionando de extremo a extremo con datos reales para la
especialización Druida. Solo Daniel puede cerrarla, extenderla o modificarla.
