# Diseño integrado vigente

El diseño del HTML independiente se integra en Django manteniendo la composición elegida: mapa al fondo, panel flotante recogible, búsqueda en cabecera, filtros sobre el mapa y conversación dentro de cada publicación.

## Archivos activos

- frontend/index.html: plantilla, estructura y diálogos.
- frontend/css/panorama.css: estilos de escritorio y móvil.
- frontend/js/panorama.js: componentes de interfaz, mapa y consumo de API.
- frontend/assets/icon.svg: icono.
- backend/core/views.py: autenticación, perfiles, contenido y permisos.
- backend/core/models.py y migrations: persistencia.

Las versiones previas de estilos y scripts no se cargan. Los archivos originales del compañero se conservan; no se sustituyen por una segunda aplicación de datos locales. La maqueta original sigue separada fuera de este repositorio.

## Comportamiento

Comunidades por intereses y posts independientes. Se distinguen eventos con fecha, actividades recurrentes por horario y lugares de encuentro. La lista conserva resultados a cualquier zoom. En el mapa, las destacadas se muestran desde lejos y las demás desde zoom 15; los marcadores próximos se agrupan. Ver lugar centra y acerca. Buscar en esta zona limita al encuadre visible.

Las imágenes son opcionales y se muestran solo cuando el autor adjunta una. Los comentarios, perfiles, guardados y propuestas vienen del servidor. El acceso a la revisión es exclusivo de moderadores y se comprueba también en la API. RUT pendiente, sin asistencia ni votos.

## Criterios visuales

DM Sans y fallback del sistema; superficies neutras, verde #356348, texto #243029 y secundario #5c685f. Metadatos de 12/13 px y cuerpo de 14/16 px. Margen de escritorio de 24 px y panel de 416 px, ajustado al ancho. En móvil una hoja deja visible parte del mapa y hay navegación inferior. Diálogos nativos, foco visible, teclado y movimiento reducido.

Se aplicó la revisión Unslop de Damir Sokolovsky (@heydamir), https://github.com/heydamir/unslop, CC BY 4.0. El mapa y el contenido comunitario aportan la riqueza visual; no se añaden portadas promocionales, fotos automáticas o decoración sin función.
