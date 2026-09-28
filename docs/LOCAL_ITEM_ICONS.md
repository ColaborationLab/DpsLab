# Íconos locales de Core — 2026-09-27

Fuente: `<instalación WoW>/.build.info` y `Data`, derivados exclusivamente
de la carpeta `_retail_/Interface/AddOns/DpsLab` seleccionada. Lectura CASC
offline por FileDataID, decodificación BLP2 en memoria y presentación Qt.
No se descargan texturas, no se persisten imágenes ni se redistribuye arte de WoW.

Link exporta `icon_file_data_id` usando `C_Item.GetItemIconByID` sobre el enlace
de la pieza ya observada. Introducido en 0.10; 0.11 añade raza, clase y facción
para la cabecera de identidad, sin fotografía ni captura de pantalla. El retrato
es una silueta genérica discreta y los distintivos de facción son gráficos
vectoriales propios. Ausencia de icono es `null`. Core conserva
lectura de 0.1–0.10 y perfiles antiguos. Es necesario actualizar Core junto con
Link y exportar nuevamente para obtener IDs; no se inventan para perfiles viejos.
Los perfiles nuevos conservan el ID al guardarse y al reabrirse.

La carga ocurre fuera del hilo de interfaz, máximo 19 identificadores por
perfil, una lectura activa a la vez. Se descartan resultados de una selección
anterior. Cambiar instalación o `.build.info` invalida la selección. Solo se
decodifica BLP2 hasta 4 MiB y 512×512. Archivos ausentes, inválidos o cifrados
sin clave conservan un marcador explícito; no activan descargas alternativas.
La comprobación real del 2026-09-27 leyó FileDataID 134400: BLP de 3916 bytes,
64×64, sin archivo de imagen generado. Esto no acredita cada pieza del usuario.

## Dependencias y construcción local

- CascLib 3.0, revisión `4971d363e665551ac4142f541e5f2d71f1cda653`,
  [fuente MIT](https://github.com/ladislav-zezula/CascLib/tree/4971d363e665551ac4142f541e5f2d71f1cda653).
  Solo se invoca la apertura local, con `.build.info` exacto y producto `wow`;
  se pasa `bOnlineStorage=false`, se cancelan los callbacks de descarga antes
  de adquirir archivos y se rechaza el indicador online. No hay fallback CDN.
- Pillow 12.3.0 para BLP2; rueda fijada en el lock existente y registrada en
  el inventario existente. No hay un pipeline nuevo de seguridad ni distribución.
- El DLL es un artefacto de build ignorado, no una textura ni un binario de WoW.
  `CascLib-LICENSE.txt` acompaña al lector.

Preparar un checkout limpio de esa revisión en `build/CascLib-3.0`. El helper
verifica la revisión y que no existan modificaciones; no descarga dependencias.
Con Visual Studio C++ y los paquetes oficiales NuGet
`Microsoft.Windows.SDK.CPP` y `Microsoft.Windows.SDK.CPP.x64` 10.0.28000.2705
extraídos respectivamente en `build/windows-sdk/common` y `build/windows-sdk/x64`:

```powershell
python tools/build_casc_reader.py --source build/CascLib-3.0 --visual-studio '<Visual Studio>' --sdk-common build/windows-sdk/common --sdk-x64 build/windows-sdk/x64
```

El helper usa CMake/Ninja de Visual Studio, normaliza el entorno solo del proceso
y genera `desktop-app/src/dpslab/native/CascLib.dll`. No instala el SDK globalmente.
SHA-256 de los paquetes SDK usados:

- common: `a74ca8f9af98bd61925d9e2932ad98f746306123167b8f0bba99cd9ea9f03807`.
- x64: `bf892c1048059984850a1ed79bb81c0243478c6d7472d637c90565ab5c836013`.

`installer/build_reduced.py` requiere el DLL y empaqueta lector/licencia, plugin
BLP y licencia de Pillow. No copia archivos de WoW. Sigue siendo el paquete local de
revisión existente; no es la distribución pública de la sección 1.10.

## Revisión personal pendiente

Con Core y Link actualizados, exportar desde el juego y comprobar los íconos en
Personaje, Simulación y Comparar; guardar/reabrir el perfil sin nueva exportación.
Después ejecutar el recorrido de simulación y retorno de pesos autorizado por
Daniel. No declarar completada la sección 1.9 por el smoke técnico de un ícono.
