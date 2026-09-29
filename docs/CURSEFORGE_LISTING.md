# DpsFoundry Link — ficha de beta abierta para CurseForge

Idiomas: [English](CURSEFORGE_LISTING-en.md) ·
[Português do Brasil](CURSEFORGE_LISTING-pt-BR.md)

## Datos de proyecto

- Nombre: **DpsFoundry Link**
- Categoría propuesta: **Utilities**
- Juego: World of Warcraft Retail
- Tipo: addon
- Estado: beta abierta

## Descripción corta

DpsFoundry Link observa tu personaje localmente, exporta el perfil hacia
DpsFoundry Core y muestra scores de equipo a partir de pesos compatibles.

## Descripción

DpsFoundry Link acompaña a DpsFoundry Core en el flujo **analizar → decidir →
sincronizar → jugar → refinar**. Desde el juego puedes exportar tu personaje y
loadouts a Core, importar pesos calculados y consultar scores en tooltips de
equipo compatibles.

No es una conexión en tiempo real ni automatiza acciones del juego. Tus datos
se intercambian localmente entre el addon y la aplicación. La beta admite
clases y especializaciones soportadas por el flujo existente de Core.

## Inicio rápido

1. Instala Link en `World of Warcraft/_retail_/Interface/AddOns/DpsLab`.
2. En el juego usa `/dpslab export app` y confirma `/reload`.
3. Abre DpsFoundry Core, importa la exportación y ejecuta la simulación de las
   builds seleccionadas.
4. Exporta los pesos elegidos desde Core e impórtalos en Link para ver scores.

## Feedback de beta

Reporta errores o sugiere mejoras en
[GitHub Issues](https://github.com/ColaborationLab/DpsLab/issues/new?title=Beta+feedback%3A+).
No publiques nombres, reinos ni exportaciones completas si no son necesarios
para explicar el problema.

## Changelog inicial

- Primera beta abierta de DpsFoundry Link.
- Exportación local de personaje y loadouts hacia Core.
- Importación de pesos estadísticos y scores en tooltips compatibles.
- Selector de perfiles, interfaz Foundry y acceso por minimapa.

## Capturas requeridas antes de enviar

1. Ventana principal de Link con un perfil activo.
2. Ventana de pesos con una build seleccionada.
3. Tooltip con score de un objeto compatible.
4. Menú de minimapa y flujo de exportación local.

Las capturas beta actuales están en [`curseforge-captures`](curseforge-captures/)
y se reemplazarán por una sesión de juego actual antes de una publicación estable.
