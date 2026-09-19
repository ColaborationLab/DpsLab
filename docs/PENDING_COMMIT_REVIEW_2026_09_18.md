# Revisión de pendientes de commit — 2026-09-18

## Estado comprobado

Base local: 49d88bbeb081e55bccaee646706912372218167e.
Rama: codex/live-export-balance-package.
Rama remota consultada con GitHub API: 11767d3a94a86de5fc23e1b035a231127c72324d.
Por tanto, el commit Qt 49d88bb sigue pendiente de push.
ColaborationLab/DpsLab es público actualmente (private=false); los documentos
históricos que lo describen privado no reflejan el estado de GitHub.
Git ls-remote falló con SEC_E_NO_CREDENTIALS; la lectura por gh api sí funcionó.
No se comprobó permiso efectivo de push ni se modificó autenticación.

La revisión solicitada no produjo commit, push, publicación ni cambios funcionales.
El cambio de Scope cierra el objetivo anterior por instrucción de Daniel;
ese cierre no convierte en aprobadas técnicamente las carencias detectadas.
El contenido pendiente debe corregirse antes de entregarlo como versión distribuible.

## Inventario completo al iniciar la revisión (21 archivos)

| Grupo | Archivos | Estado |
| --- | --- | --- |
| Addon, 4 | addon/DpsLab/DpsLab.lua; DpsLab.toc; ItemScoreProfiles.lua; Localization.lua | Localización parcial; revisar antes de commit de cierre |
| App, 6 | desktop-app/src/dpslab/qt_loadout_ui.py; i18n.py; locales/__init__.py; locales/en.py; locales/es.py; locales/pt_BR.py | Catálogos y selector presentes, defectos funcionales descritos abajo |
| Pruebas, 2 | desktop-app/tests/test_i18n.py; tools/tests/test_addon_item_score_profiles.py | La primera no es descubierta por unittest; la segunda pasa pero no integra el catálogo Lua |
| Documentación de usuario, 6 | docs/DISTRIBUTION.md; DISTRIBUTION-es.md; DISTRIBUTION-en.md; DISTRIBUTION-pt-BR.md; TRANSLATIONS.md; installer/README-WINDOWS.md | Borradores; necesitan correcciones y ser incluidos en el paquete |
| Dirección y planificación, 3 | SCOPE_CORRECTION_0_1.md; docs/NEXT_TASK.md; docs/LOCALIZATION_LUNA_PLAN.md | Se actualizan en esta preparación; historial anterior conservado |

No había cambios staged. Los nuevos documentos de revisión y plan de publicación
de esta sesión se añaden a ese inventario. No hay nuevas modificaciones de
seguridad, motor, CI ni datos personales en el diff revisado.

## Hallazgos concretos antes de distribuir

1. App: _save_language(..., "auto") normaliza y guarda "en"; al abrir vuelve a
   inglés. _t pasa None para Auto, que también resuelve inglés sin consultar
   el locale de Windows. normalize_locale("esES") y ("ptBR") devuelven "en".
   La documentación atribuye al modo Auto de la suite un comportamiento
   todavía no implementado en Qt.
2. App: selector cambia la preferencia y un mensaje, pero no actualiza todos
   los widgets existentes; hay textos españoles sin catálogo en diálogos,
   tooltips, resultados y comparison_table.py. Tratar la UI como parcialmente
   traducida. Al corregir, conservar ediciones no guardadas.
3. Addon: DpsLab.lua llama export_title/export_help/export_reload, ausentes
   en Localization.lua. En Lua real Get("export_title") devuelve la clave
   literal; T no usa el fallback español porque la clave devuelta es truthy.
   Permanecen botones del popup, estadísticas, ayudas y mensajes sin traducir.
   Las ventanas cacheadas no refrescan todas las etiquetas al reabrirse.
4. Pruebas: test_i18n.py contiene funciones de pytest, pero la suite usa
   unittest: ejecuta CERO pruebas. La supuesta paridad usa messages(), que ya
   aplica fallback, y puede ocultar claves faltantes. Validar los catálogos
   originales, placeholders y recorridos con cambio/persistencia de idioma.
5. Paquete: i18n importa módulos dinámicamente y build_reduced.py no declara
   su recolección explícita; riesgo de ausencia en el ejecutable congelado,
   todavía sin prueba del paquete multilingüe. Las guías tampoco se incluyen.
   build_reduced produce onedir, no un instalador de Windows; no anunciarlo
   como setup ni ejecutable único autosuficiente.
6. Documentación: las guías no especifican la ubicación _internal/DpsLabAddon,
   no tienen desinstalación detallada y sugieren borrar archivos locales para
   quitar preferencias sin distinguir perfiles. TRANSLATIONS solo está en ES,
   no explica registro completo del nuevo módulo en _catalog ni pruebas útiles.
   Índice sin enlaces Markdown; falta validación de enlaces desde el paquete.
   No describir traducción/Auto aún incompletos como prestaciones verificadas.
7. Herramientas: dos tests test_github_automation exigen contrato activo aunque
   su propio objetivo acepta cero o uno. Corregirlos con fixtures de contratos
   para probar estados cero/uno/duplicados/identidades repetidas; no reactivar
   el contrato Qt ni omitir casos para obtener verde.
8. Metadatos/licencias de distribución: TOC sigue en 0.1.0-synthetic; fijar
   versión pública y cliente compatible. El aviso SimC llama "Source SHA-256"
   a un hash del binario y enlaza el repositorio genérico. Vincular versión
   exacta, fuente correspondiente y avisos aplicables al runtime distribuido.
   Esto es preparación del paquete, no un programa nuevo de SBOM/firma.

## Evidencia fresca

- unittest tests.test_i18n -v: 0 tests, NO TESTS RAN (código 0).
- Prueba temporal de preferencias: guardar Auto -> {"locale":"en"}; carga en.
  Solo se escribió en una carpeta temporal, sin alterar preferencias del usuario.
- Lua 5.1 disponible por build/lua-test-runtime/lupa, Python build/installer-py313.
  La afirmación anterior de que faltaba runtime Lua no aplica a este entorno.
- Get("export_title") -> "export_title" confirmado con runtime Lua.
- unittest tools.tests.test_addon_item_score_profiles
  tools.tests.test_github_automation -q: 18 pruebas, 16 aprobadas, 2 fallidas,
  cero omitidas, código 1. Fallos: exigencia de contrato activo.
- Totales de suite completa informados el turno anterior son evidencia histórica,
  no se repitieron ni se presentan como verificación nueva.
- No se ejecutó SimulationCraft ni se probó el cliente WoW en esta revisión.

## Orden de commits propuesto

A. Corregir y verificar el lote multilingüe de app/addon junto con pruebas.
B. Corregir guías ES/EN/PT-BR e inclusión en paquete; sincronizar estado real.
C. Registrar transición de Scope y plan de distribución con SHA vigente.
D. Implementar y registrar distribución/instalador, actualizaciones y donativos
   en lotes siguientes revisables, con pruebas proporcionadas a cada cambio.

Es una secuencia propuesta, no commits ya ejecutados. No presentar el lote
pendiente como release aprobada. Próximo paso: correcciones 1–7 que afectan
directamente la primera distribución, bajo el nuevo objetivo.
