# Publicación, instaladores, actualizaciones y donativos

Fecha: 2026-09-18. Estado: preparación terminada; nueva implementación no iniciada.
Base: 49d88bbeb081e55bccaee646706912372218167e, rama codex/live-export-balance-package.
Scope remoto: 9929bfc58cd0878987a4266b65f7718e83c74092, texto íntegro incorporado
con historial local; SHA-256 real en protected_files de NEXT_TASK.
Responsable: agente principal. No se activa automáticamente otro agente.
Si se retoma Luna, entregar un lote acotado y una única frontera de escritura.

## Prueba de valor y resultado esperado

Sí: permite que un jugador obtenga la suite desde CurseForge y GitHub,
la mantenga actualizada y apoye voluntariamente la continuidad del proyecto.

| Requerimiento del Scope | Entrega verificable | Condición para considerarlo cumplido |
| --- | --- | --- |
| 1. Addon en CurseForge | ZIP instalable, ficha ES/EN/PT-BR, versión/interface y página del proyecto | Publicado/aprobado por la plataforma, descargable e instalable desde su cliente |
| 2. App e instaladores en GitHub público | Setup de Windows, opción portable, SimC incluido, guías/avisos | Descarga pública y arranque en entorno limpio sin Python ni SimC externos |
| 3. Actualizaciones y donativos | Mecanismo de actualización app/addon, historial de versiones, enlace de apoyo verificado | Actualizar conserva perfiles; enlace llega al destinatario real sin condicionar funciones |

Un borrador de publicación no equivale a disponibilidad pública. La preparación
actual no cierra esas tres condiciones.

## Base que hay que sanear

Ver PENDING_COMMIT_REVIEW_2026_09_18.md: 21 archivos previos sin commit,
traducción parcial, Auto incorrecto, catálogo Lua incompleto y pruebas omitidas
por diseño. El cierre del objetivo anterior se registra por cambio de Scope,
pero se corrigen estos defectos como requisitos de la entrega pública.
No descartar ningún cambio existente ni adoptar guías históricas como prueba.

GitHub confirma repositorio público actualmente. No convertir visibilidad ni
crear repositorio por suposición. Revisar contenido a publicar, no copiar
perfiles/exportaciones/research interno al ZIP o repositorio del addon.
PUBLIC_ADDON_REPOSITORY_SEPARATION.md y
INTELLECTUAL_PROPERTY_AND_MONETIZATION.md son diseños históricos: sus
presunciones de repositorio privado, prohibición de distribuir app y ceremonia
de firma no se reactivan frente al nuevo Scope. Conservar su historia y
conciliar las instrucciones operativas que contradigan este objetivo.
La licencia de la app no se deduce de que GitHub sea público.

## Lote 0 — Candidato coherente para distribución

Corregir los hallazgos del informe: Auto persistente/sistema, claves faltantes,
cobertura de textos y refresco seguro, pruebas unittest y catálogo Lua integrado.
Corregir las dos pruebas que exigen contrato activo usando fixtures; verificar
casos cero/uno/dos y replay sin reducir cobertura.
Reconciliar estado de NEXT_TASK/plan previo y el control de alcance vigente.
Probar catálogos originales, fallback, caracteres y placeholders; recorridos
guardar/abrir/importar/limpiar y tabla 1–4 con runner falso en tres idiomas.
Ejecutar suite completa app/tools y gate aplicable sin simular realmente.
Resultado: candidato corregido para commit, con resultados y limitaciones.

## Lote 1 — Identidad y paquete público

Fijar una versión coherente para app, addon, instalador y changelog.
Documentar compatibilidad de formato de intercambio, versión WoW y Windows
realmente probados; no adivinar el Interface de Retail.
Producir ZIP solo de addon con raíz DpsLab/DpsLab.toc; excluir exports reales,
recomendaciones de personajes, SavedVariables, capturas y archivos de desarrollo.
Verificar específicamente DpsLabRealRecommendation.lua antes de exportar:
solo placeholder vacío o fixture explícitamente pública, nunca datos reales.
Preparar descripción, icono con derechos disponibles, soporte y changelog
ES/EN/PT-BR. No iniciar un diseño gráfico nuevo innecesario.
Corregir guías y crear variantes de contribución/traducción; incluirlas en paquete.
Registrar hash del binario SimC como binario y vincular su revisión/fuentes
correspondientes, texto de licencia y avisos runtime. Revisar PySide6/Qt conforme
a lo realmente incluido; resolver ruta de licencia aplicable antes de publicar.
No generar programa de SBOM, firma ni ceremonia nueva.

## Lote 2 — Instalador Windows y GitHub Releases

Conservar onedir como portable; añadir setup reducido con herramienta estándar
(por ejemplo Inno Setup, decisión a confirmar al revisar herramientas instaladas).
Instalación por usuario, accesos directos y desinstalación sin borrar perfiles
por defecto. Instalación del addon opcional, con selección de carpeta real;
detectar WoW abierto y explicar cuándo cerrar/reiniciar.
El instalador contiene SimC y catálogos; no depende de directorios de desarrollo,
Python del usuario ni simuladores ajenos.
Revisar generación de fuente/datos de PyInstaller para asegurar locales
dinámicos y guías. Verificar arranque de paquete, primera instalación, reparación,
actualización y desinstalación usando carpeta/cuenta limpia con datos de prueba.
Preparar assets, notas trilingües, hashes y enlace a avisos; el usuario descarga
el setup/portable, no el archivo Source code automático de GitHub.
Usar el repositorio público existente si es el destino confirmado; preparar
destino alternativo solo si Daniel lo elige. No cambiar visibilidad histórica.

## Lote 3 — Actualizaciones

Addon: usar el cliente de CurseForge como canal de actualización, con alternativa
ZIP manual. Versiones release/beta visibles; no red ni autoescritura desde Lua.
App: comprobación opcional de nueva versión en GitHub Releases por HTTPS,
botón Buscar actualizaciones y preferencia recordada; funcionamiento offline.
Modo automático opt-in: consultar/descargar y ofrecer instalación al cerrar,
sin interrumpir simulación o perder datos. El instalador sustituye binarios
solo cuando app/SimC hayan terminado y conserva datos locales.
Validar versión y asset esperado, tamaño/hash publicado para detectar corrupción;
ese hash no se anuncia como firma. No ejecutar binarios de URLs arbitrarias.
Manejar red ausente, rate limit, descarga parcial/corrupta, versión incompatible,
aplicación ocupada, cancelación y recuperación a versión anterior.
Separar versión de app/addon de esquema de intercambio; advertir incompatibilidad
sin sobrescribir perfiles ni resultados. SimC cambia con el paquete validado.
Probar upgrade N -> N+1 y recuperación; escribir pasos de actualización manual
en ES/EN/PT-BR. Un enlace a descargar no basta para llamar a esto autoactualización.

## Lote 4 — Donativos voluntarios

Preparar texto ES/EN/PT-BR en páginas externas con enlace aportado/confirmado
por Daniel. No inventar cuenta, URL, destinatario, país o disponibilidad regional.
Mantener todas las funciones gratuitas del addon y sin beneficio funcional
condicionado a pago. No mostrar solicitudes de donativos dentro de WoW.
GitHub admite FUNDING.yml/enlaces de apoyo; CurseForge permite configurar un
método disponible en su página de proyecto. Elegir servicio según la cuenta
real, no imponer Patreon por una recomendación histórica.
Verificar destino y nombre públicamente mostrado sin realizar cargo ni pago
de prueba. La creación/autenticación de cuenta de cobro queda con el titular.
Texto de apoyo opcional en app externa y web; sin datos financieros en el repo.

## Lote 5 — Publicación y prueba de valor completa

Preparar primero paquetes y páginas revisables, luego la publicación solicitada
con cuenta/destino concretos. Si falta acceso a CurseForge, continuar candidato
y documentación mientras se obtiene. Nunca presentar moderación pendiente como
addon disponible.
Prueba real: descargar de CurseForge, instalar/actualizar addon; descargar setup
público de GitHub y abrir app sin dependencias externas; usar ES/EN/PT-BR,
exportar -> detectar -> elegir 1–4 -> simular con autorización concreta ->
importar pesos -> scores mouseover/comparativos.
Probar actualización conservando perfil con equipo y preferencias; visitar
enlace de apoyo para confirmar destinatario, sin efectuar transacción.
Registrar URLs públicas, versión, assets/hashes, resultados y confirmación visual
de Daniel. Cada fila de la matriz inicial necesita su propia evidencia.

## Fronteras y decisiones necesarias

Preparación actual: Scope, NEXT_TASK, plan e informe; sin alterar producto.
Implementación prevista: UI/catalogos/pruebas del lote previo,
installer/**, docs de usuario/publicación, módulo de actualizaciones y pruebas
en desktop-app, metadatos TOC/versiones, empaquetado del addon y pruebas tools.
.github/FUNDING.yml solo al configurar el destino real de apoyo; automatización
de publicación únicamente si necesaria y activada para el canal definido.
No tocar datos personales, runs, escenarios históricos, algoritmos de SimC,
Synthetic* ni expandir clases/specs. Mantener lo ya funcional.

Resolver antes de publicar, no bloquean el lote 0:
- cuenta/ID/proyecto CurseForge y acceso de publicación;
- destino GitHub final (el repositorio existente ya es público);
- versión inicial y derechos/avisos de app, addon y dependencias;
- proveedor y enlace real de donativos;
- acceso a entorno Windows limpio y a WoW para aceptación visual.

Primer trabajo concreto: lote 0 y sus pruebas, después commits temáticos y
paquetes. Esta sesión revisa y prepara; no ha realizado commit/push/Release.
No trasladar automáticamente permisos de publicación de objetivos anteriores.

## Fuentes primarias consultadas el 2026-09-18

- [CurseForge: envío de proyectos y campo de donativos](https://support.curseforge.com/support/solutions/articles/9000199552)
- [GitHub: releases y binarios](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [GitHub: enlaces de apoyo](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository)
- [Blizzard: addon gratuito y sin peticiones de donativos en el juego](https://us.forums.blizzard.com/en/wow/t/ui-add-on-development-policy/24534)
- [Qt for Python: licencias](https://doc.qt.io/qtforpython-6/licenses.html)
- [SimulationCraft: COPYING, referencia; fijar revisión exacta del binario antes de distribuir](https://github.com/simulationcraft/simc/blob/thewarwithin/COPYING)
