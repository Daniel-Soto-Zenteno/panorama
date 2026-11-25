# API de Panorama

Rutas del mismo origen que la página. Respuestas JSON salvo GET de una imagen. Las operaciones de escritura usan una sesión de Django y el encabezado X-CSRFToken obtenido desde GET /api/csrf/. El token debe renovarse después de iniciar o cerrar sesión.

| Ruta | Método | Acceso y función |
| --- | --- | --- |
| /api/csrf/ | GET | Token CSRF |
| /api/session/ | GET | Estado de sesión, nombre visible y rol |
| /api/register/ | POST | Crear cuenta e iniciar sesión |
| /api/login/ | POST | Iniciar sesión con username y password |
| /api/logout/ | POST | Cerrar sesión |
| /api/profile/ | GET, PATCH | Perfil de la cuenta actual; name y bio |
| /api/activities/ | GET | Publicaciones visibles para quien consulta |
| /api/activities/ | POST | Proponer publicación; requiere cuenta |
| /api/activities/{id}/ | PATCH, PUT, DELETE | Autor o moderador |
| /api/activities/{id}/image/ | GET | Imagen con la misma visibilidad que el post |
| /api/activities/{id}/image/ | POST | Adjunto multipart con campo image; autor o moderador |
| /api/activities/{id}/comments/ | GET, POST | Leer si el post es visible; comentar con cuenta |
| /api/comments/{id}/ | DELETE | Autor del comentario o moderador |
| /api/communities/ | GET, POST | Leer aprobadas y propuestas propias; proponer con cuenta |
| /api/communities/{id}/moderate/ | POST | Moderador: approved y rejected |
| /api/saved/ | GET | IDs guardados de la cuenta actual |
| /api/saved/{id}/ | POST, DELETE | Añadir o quitar guardado de la cuenta actual |
| /api/reports/ | POST | Enviar post_id, reason y text con cuenta |
| /api/reports/ | GET | Moderador: reportes sin resolver |
| /api/reports/{id}/ | PATCH | Moderador: resolved=true |

## Publicaciones

Se mantiene el contrato original: title, category, zone, lat, lng, all_year, schedule, date, description y featured. Se agregan community_id (nulo para independiente), kind (event/place), pace (active/calm), place, status y remove_image. El contenido devuelto incluye autor, nombre visible, permisos de edición, número de comentarios, fecha de creación e image_url cuando existe una imagen.

Categorías del backend: Deportes, Cultura, Ferias y Comunidad, Aire libre. Ciudades: puerto-montt y puerto-varas. El frontend adapta esos valores a sus nombres visuales. Un evento puede usar fecha o ser recurrente mediante all_year y schedule. Un lugar de encuentro usa kind=place y all_year=true.

Los estados son pending, published y rejected. Un usuario normal no puede controlar status ni featured: sus propuestas quedan pending y editar una propia retira el destacado y vuelve a revisión. Solo staff o superuser puede aprobar, destacar o rechazar. Los moderadores no se crean desde el registro web.

## Imágenes y privacidad

JPEG, PNG y WebP, hasta 5 MB y 25 megapíxeles. La imagen se normaliza y convierte a JPEG; nunca se devuelve una imagen por defecto. image_url apunta a la API protegida, no a un directorio público. No configurar MEDIA_ROOT como carpeta pública en un despliegue: las imágenes pendientes deben seguir comprobando permisos.

## Errores

400: datos inválidos. 401: falta sesión. 403: falta permiso o token CSRF. 404: contenido inexistente o no visible. Los errores de las vistas de la API incluyen error con un texto explicativo.
