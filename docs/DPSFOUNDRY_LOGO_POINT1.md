# Punto 1 — logotipo forjado

Daniel aprobó el logotipo y pidió integrar cabecera/cuerpo (2026-09-20).
El recurso aprobado se conserva byte a byte. El fondo existente se dibuja
ahora en coordenadas de ventana compartidas por cabecera, lateral y página;
no se reinicia el encuadre en cada superficie. La cabecera aplica un
oscurecimiento gradual para la marca y controles, sin línea de corte ni
nueva imagen. Las variantes siguen a cada sección. Otros temas mantienen
sus superficies originales. Esta integración adicional requiere revisión;
no constituye aprobación de puntos 2–6 ni autoriza avanzar al addon.

2026-09-20. Solo identidad de Core; no avanzar a puntos 2–6 ni Link sin
revisión visual de Daniel. Sin cambios funcionales ni GitHub.

Recurso: desktop-app/src/dpslab/assets/foundry-brand-forged-v1.png.
Generado con la herramienta integrada image_gen, sin CLI ni API propia.
Referencia: dpsfoundry_core_sistema_forjado.png, paquete elegido por Daniel.
Roca agrietada, lava contenida, chispas y magma en borde del yunque; nombre
de acero forjado y módulo cobre. Texto accesible conservado en Qt; los otros
temas conservan su presentación vectorial. Asset estático, sin animación.

## Prompt final

Create a production-ready single horizontal DpsFoundry Core logo banner,
faithfully reproducing the PRIMARY HORIZONTAL LOGO and header branding of
the supplied design sheet. This is not a UI mockup: output ONLY the logo
banner, no sheet, no panels, no extra labels. Very wide composition. At left
the exact hollow anvil silhouette with broad flat face, pinched angular
stem, flared foot, three upright sparks, incandescent orange-gold edge and
a molten chipped magma patch on upper right edge. Sparse fine flying sparks.
Behind logo dark cracked volcanic rock with restrained lava glow in a few
fissures, fading to near-black #080e12 at ALL image edges for seamless header
use. To right exact uppercase text 'DPSFOUNDRY / CORE', DPSFOUNDRY in chunky
angular forged silver steel lettering with sharp chamfer bevels, dark cut
edges and fine hammered texture, / CORE in hot copper-gold. Beneath exact
small tracked readable text 'SIMULATION · ANALYSIS · OPTIMIZATION'. Match
reference lettering and symbol nearly exactly, not generic sans serif, not
redesigned. Logo occupies most of width with modest safe margin, vertically
compact header proportions. No border. No extra text, no watermarks. Static
asset with detailed materials, preserve clear legibility at 520 pixels wide.

## Valor y límite

El cambio aporta el material gráfico que faltaba en la identidad; 100% del
cambio de producto de este incremento es presentación. Código, empaquetado,
documentación y pruebas son soporte. No se afirma equivalencia pixel-perfect:
la aceptación del punto 1 permanece pendiente de la revisión en la app.
