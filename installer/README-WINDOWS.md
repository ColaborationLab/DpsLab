# DpsLab para Windows

Construcción local con íconos (2026-09-27): preparar primero el lector descrito
en [LOCAL_ITEM_ICONS](../docs/LOCAL_ITEM_ICONS.md). El empaquetador requiere
`CascLib.dll`, incluye sus licencias y nunca incorpora texturas de WoW.
Core y Link deben actualizarse juntos para leer las nuevas exportaciones 0.10.
La beta pública se entrega mediante el instalador `DpsFoundry-Core-*-Setup.exe`.
No instala ni modifica World of Warcraft ni otros addons.

Guías completas de distribución:

- `docs/DISTRIBUTION-es.md` — español.
- `docs/DISTRIBUTION-en.md` — English.
- `docs/DISTRIBUTION-pt-BR.md` — português do Brasil.

Estas guías incluyen instalación, selección de idioma, perfiles, pesos,
privacidad, actualización y solución de problemas.

1. Ejecuta el instalador y acepta la carpeta de usuario propuesta.
2. Copia `DpsLabAddon` de la carpeta instalada a `Interface\AddOns\DpsLab` de tu instalación de WoW.
3. Abre DpsFoundry Core desde el menú Inicio o el acceso directo elegido.
4. En WoW ejecuta `/dpslab export app`, confirma la recarga y vuelve a la app.
5. Confirma que la app identifica la clase y especialización exportadas, elige de una a cuatro builds del mismo personaje y especialización, o añade cadenas de talentos manuales con nombre, y ejecuta la comparación.
6. La app compara únicamente DPS entre esas builds y conserva el contexto de clase/especialización al guardar un caso. No presenta DPS como curación o supervivencia, ni reutiliza pesos de Balance fuera de Balance.
7. Para scores, abre el perfil guardado, ejecuta una simulación que entregue pesos, luego en WoW usa `/reload`, `/dpslab config` y pasa el cursor sobre un item. Sin pesos compatibles, el addon informa que el score no está disponible.

La distribución contiene `simc.exe`; no se necesita una instalación separada de SimulationCraft.
