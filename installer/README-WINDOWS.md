# DpsLab para Windows

Guías completas de distribución:

- `docs/DISTRIBUTION-es.md` — español.
- `docs/DISTRIBUTION-en.md` — English.
- `docs/DISTRIBUTION-pt-BR.md` — português do Brasil.

Estas guías incluyen instalación, selección de idioma, perfiles, pesos,
privacidad, actualización y solución de problemas.

1. Extrae por completo el archivo ZIP en una carpeta con permisos de escritura.
2. Copia `DpsLab\_internal\DpsLabAddon` a `Interface\AddOns\DpsLab` de tu instalación de WoW.
3. Abre `DpsLab\DpsLab.exe`.
4. En WoW ejecuta `/dpslab export app`, confirma la recarga y vuelve a la app.
5. Confirma que la app identifica la clase y especialización exportadas, elige de una a cuatro builds del mismo personaje y especialización, o añade cadenas de talentos manuales con nombre, y ejecuta la comparación.
6. La app compara únicamente DPS entre esas builds y conserva el contexto de clase/especialización al guardar un caso. No presenta DPS como curación o supervivencia, ni reutiliza pesos de Balance fuera de Balance.
7. Para scores, abre el perfil guardado, ejecuta una simulación que entregue pesos, luego en WoW usa `/reload`, `/dpslab config` y pasa el cursor sobre un item. Sin pesos compatibles, el addon informa que el score no está disponible.

La distribución contiene `simc.exe`; no se necesita una instalación separada de SimulationCraft.
