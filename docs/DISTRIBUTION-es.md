# DpsLab — Guía de distribución para Windows

## Paquete e instalación

El paquete reducido incluye DpsLab.exe, sus archivos internos, simc.exe, la
carpeta DpsLabAddon y SIMULATIONCRAFT_NOTICE.txt. No hace falta instalar
SimulationCraft por separado ni indicar una ruta externa para simc.exe.

1. Extrae el ZIP completo en una carpeta local con permisos de escritura.
2. Copia DpsLabAddon a World of Warcraft/_retail_/Interface/AddOns/DpsLab.
3. Cierra WoW si había una versión anterior y reemplaza el contenido del addon.
4. Ejecuta DpsLab.exe y selecciona Auto, ES, EN o PT-BR.
5. En WoW usa /dpslab export app y confirma /reload.
6. En la app pulsa Detectar exportación, elige de una a cuatro builds y ejecuta.
7. Guarda el perfil si quieres conservar personaje, equipo, builds y resultados.

Una sola build también se puede simular; no tendrá delta comparativo. Las
cadenas externas representan simulaciones hipotéticas.

## Pesos y scores

Después de una simulación con pesos, importa los pesos en el addon, abre
/dpslab config y elige reemplazar, conservar o guardar una copia antes de
activar los nuevos. Usa /reload si se solicita y activa Mostrar scores de item.
Los scores aparecen en tooltips equipados, de inventario y comparativos cuando
existe un perfil compatible. (b) identifica la referencia genérica beginner.
Un dato ausente se muestra como no disponible; nunca se inventa como cero.

## Idiomas, datos y privacidad

Auto sigue esES/esMX para español y ptBR para portugués brasileño; los demás
idiomas usan inglés. La preferencia se guarda en
%LOCALAPPDATA%/DpsLab/language.json. Rutas y perfiles usan archivos separados.
No se necesita red para detectar exportaciones ni para ejecutar SimC. Las
exportaciones pueden contener nombre, reino, equipo, talentos y builds: no las
compartas sin revisar su contenido.

## Actualización y problemas

Cierra WoW y la app antes de reemplazar el addon o actualizar el paquete.
Para empezar sin preferencias de ruta o idioma elimina únicamente
%LOCALAPPDATA%/DpsLab/workspace_paths.json y language.json; eso no borra los
perfiles de personajes guardados.
Si la app no abre, extrae de nuevo el ZIP completo y conserva _internal. Si no
se detecta la exportación, instala la misma versión del addon, ejecuta /reload y
pulsa Detectar exportación. Si falta un score, verifica el perfil de pesos y
que Mostrar scores de item esté activo. Las builds incompletas y personajes que
no están en nivel máximo no se simulan.

SimulationCraft se distribuye bajo GPL v3. Consulta
SIMULATIONCRAFT_NOTICE.txt para el SHA-256 del binario y su repositorio fuente.
