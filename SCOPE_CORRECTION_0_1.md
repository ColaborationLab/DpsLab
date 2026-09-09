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

La cadena de Restauración ya está cerrada. Balance de Druida queda autorizado
como la segunda especialización para replicar exactamente esta misma cadena.
Ninguna otra clase, rol o especialización queda incluida.

### 1.1 Decisión de dirección (2026-09-08): empaquetar, no reconstruir

Daniel evaluó construir un motor de simulación propio (para lograr un
ejecutable único sin dependencias externas) y decidió **no hacerlo**. La vía
elegida para lograr ese mismo objetivo de accesibilidad es empaquetar el
binario real de SimulationCraft dentro del instalador de la app, para que el
usuario final descargue una sola cosa y nunca necesite instalar `simc.exe`
por separado.

- **Motor de simulación propio: descartado.** No se retoma esta idea salvo
  una autorización nueva y explícita de Daniel, aunque haya sido mencionada
  en conversaciones de diseño previas a esta corrección.
- **Siguiente objetivo del roadmap, una vez cerrado el objetivo de la
  sección 1:** empaquetar `simc.exe` dentro del instalador de la app
  (vía PyInstaller o equivalente), incluyendo el aviso de licencia GPL v3 de
  SimulationCraft y la disponibilidad de su código fuente, tal como exige su
  licencia. Esto es papeleo de empaquetado, no ingeniería de simulación —
  no requiere ni justifica firma criptográfica de releases, SBOM, ni modelo
  de amenazas formal (esos siguen congelados según la sección 3).

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

- Firma criptográfica de releases / ceremonia de custodia de claves. (No
  confundir con empaquetar el binario de `simc.exe` dentro del instalador,
  que sí está en el roadmap — ver sección 1.1. Empaquetar no es firmar.)
- Programa formal de SBOM, modelo de amenazas, y auditoría de
  vulnerabilidades más allá del escaneo básico ya integrado.
- Pipeline automático de adquisición de fuentes oficiales / notas de parche.
  Se reemplaza por: Daniel actualiza a mano un archivo de datos cuando haga
  falta.
- Cualquier nuevo esquema de "conocimiento gobernado", catálogo, propuesta,
  revisión o candidato que no sea parte directa del objetivo de la sección 1.
- Cualquier addon/funcionalidad adicional marcada como "synthetic".
- Cualquier expansión a otra clase, especialización o rol fuera de Balance de Druida.

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
esté funcionando de extremo a extremo con datos reales para Restauración y
Balance de Druida. Solo Daniel puede cerrarla, extenderla o modificarla.

## 6. Coordinación entre dos cuentas del agente

Este proyecto usa dos cuentas del mismo agente sobre el mismo repositorio:
una principal (dueña de la organización de GitHub) y una colaboradora (con
permiso de escritura). Reglas para que avancen en paralelo sin pisarse:

1. Los documentos de gobierno (`AGENTS.md`, este archivo, y cualquier
   contrato de datos vigente) los edita solo la cuenta principal, o la
   colaboradora únicamente cuando Daniel lo pida explícitamente ese día.
   Ambas cuentas los leen siempre.
2. Nunca las dos cuentas sobre el mismo objetivo sin una frontera técnica
   escrita que las separe. Trabajar en paralelo sobre el mismo objetivo SÍ
   está permitido cuando existe un contrato de datos fijo entre las dos
   mitades (ver punto 4).
3. Por defecto, la colaboradora audita: no propone tareas nuevas, solo
   verifica que el código cumple el objetivo vigente y que nada toca la
   lista de congelados de la sección 3. Este rol cambia a implementación
   activa solo cuando Daniel asigna explícitamente una mitad del trabajo
   bajo el protocolo del punto 4.
4. Protocolo de contrato de datos para trabajo en paralelo: antes de
   dividir una tarea entre las dos cuentas, una sola cuenta escribe primero
   el contrato de datos entre las dos mitades (formatos de entrada/salida
   compartidos) en un archivo aparte, sin implementar nada. Daniel lo
   aprueba. Recién entonces cada cuenta implementa su mitad, en su propia
   rama, tocando solo sus propios archivos, construyendo contra ese
   contrato — sin coordinarse en tiempo real entre ellas.
5. Rama protegida: `main` requiere Pull Request y aprobación de Daniel
   antes de fusionar cualquier cambio de cualquiera de las dos cuentas.
6. Cada cuenta usa su propio `git config user.name`/`user.email`, para que
   el historial identifique quién hizo cada cosa sin ambigüedad.
7. Cada cuenta entrega su propio reporte de cierre de sesión (formato de la
   sección 4) por separado — ninguna resume el trabajo de la otra.
