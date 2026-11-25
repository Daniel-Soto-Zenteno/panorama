# Implementación de Panorama: base técnica para el informe

Este documento describe el código integrado y comprobado. Sirve de apoyo al equipo; no sustituye la rúbrica ni inventa sprints, entrevistas, métricas o pruebas con usuarios que no se hayan realizado.

## Propósito y alcance

Aplicación de comunidades y actividades de Puerto Montt y Puerto Varas. Permite descubrir qué se hace en el territorio y conversar sobre ello. Las publicaciones pueden ser independientes o pertenecer a una comunidad. La plataforma informa y permite conversar, sin confirmar asistencia.

## Arquitectura

Cliente web con HTML, CSS y JavaScript, servido como plantilla por Django. Leaflet presenta el mapa usando teselas de OpenStreetMap. La interfaz consume rutas JSON del mismo servidor y envía imágenes por multipart/form-data. Los datos están en modelos de Django; se conserva la configuración PostgreSQL original y existe un entorno SQLite para desarrollo local.

La maqueta HTML anterior usaba datos del navegador. Esa simulación fue reemplazada: cuentas, perfil, propuestas, conversaciones, guardados y reportes se consultan y modifican mediante la API y la base de datos. El navegador mantiene temporalmente el estado de la pantalla y los filtros, no una segunda base de publicaciones.

## Modelo de datos

| Modelo | Responsabilidad |
| --- | --- |
| User de Django | Cuenta, contraseña almacenada con hash y rol staff/superuser |
| Perfil | Nombre visible y biografía, asociado a la cuenta |
| Comunidad | Nombre, interés, descripción, creador y resultado de revisión |
| Actividad | Publicación, categoría, ciudad, ubicación, tipo, ritmo, fecha/horario, comunidad opcional, imagen opcional y estado |
| Conversacion | Comentarios asociados a una publicación y a su autor |
| Guardado | Relación única entre usuario y publicación |
| Reporte | Motivo, detalle, autor, publicación y resolución del equipo |

Las migraciones 0003 a 0006 añaden los modelos y campos de esta integración. No eliminan las tablas ni los campos iniciales de Actividad. La disponibilidad todo_el_ano se conserva para actividades recurrentes y no se confunde con el nuevo tipo de lugar de encuentro.

## Recorridos implementados

1. Una persona explora el mapa y las publicaciones sin iniciar sesión. Puede filtrar por ciudad, interés, fecha, ritmo y distancia.
2. Elige una comunidad para ver sus publicaciones o explora las independientes.
3. Crea una cuenta o inicia sesión para publicar, comentar, guardar y reportar.
4. Propone un evento con fecha, una actividad recurrente con horario o un lugar de encuentro; elige ubicación y puede adjuntar una imagen.
5. Una propuesta de usuario queda pendiente, visible solo para el autor y los moderadores. No aparece públicamente en el mapa.
6. Un moderador aprueba, destaca o rechaza el contenido. Las publicaciones normales aparecen al acercarse; las destacadas también desde lejos.
7. La conversación queda asociada al post. Su autor y los moderadores pueden eliminar comentarios.
8. Los guardados permanecen en la cuenta y se recuperan desde otra sesión.
9. Los reportes llegan a una bandeja visible solo para moderadores y pueden resolverse u originar la ocultación del contenido.

## Permisos y validaciones

La lectura de contenido aprobado es pública. La escritura requiere sesión y protección CSRF. El servidor verifica autoría y rol; ocultar botones en el cliente no es el control de acceso. Un usuario no puede aprobarse, destacarse, ver propuestas privadas ajenas, consultar guardados de otro usuario ni resolver reportes.

Títulos, descripciones, perfiles, comentarios, categorías, ciudades, coordenadas, ritmo y estados se validan en el servidor. Las imágenes admiten JPG, PNG y WebP de hasta 5 MB y 25 megapíxeles; se normaliza la orientación, se reducen hasta 1800 px y se guardan como JPEG. Se sirven por una ruta que comprueba la visibilidad de la publicación, también cuando está pendiente. Editar contenido propio vuelve a enviarlo a revisión.

Se utilizan las funciones de autenticación, contraseña y sesión de Django, no una implementación casera. Referencias técnicas: https://docs.djangoproject.com/en/5.2/topics/auth/default/ y https://docs.djangoproject.com/en/5.2/topics/http/file-uploads/.

## Diseño y tecnología

Se integra la composición elegida por el usuario: mapa de fondo, panel flotante, búsqueda en cabecera, filtros sobre el mapa, comunidades y conversación. El detalle conserva el contexto del mapa. No se colocan fotos de stock ni imágenes por defecto. El diseño se adapta a móvil y admite navegación con teclado y foco visible.

El equipo indicó Scrum como metodología. No se agregan aquí duraciones, sprints terminados, roles asignados o ceremonias como hechos, porque no se entregó evidencia para describirlos.

## Verificación y límites

17 pruebas automatizadas pasaron con SQLite, junto con la comprobación de Django y la revisión de migraciones. Se probaron además registro, perfil, publicaciones, comentarios, guardados entre sesiones, moderación, comunidad nueva y reportes desde el navegador, en escritorio y móvil. Detalles en VALIDACION.md.

La autenticación por RUT sigue sin definición y no se implementó. No se incluyeron asistencia a eventos, pagos, chat privado ni votos. No se probó la conexión real a PostgreSQL ni se realizó despliegue público. Antes de desplegar se deben configurar dominio, HTTPS, SECRET_KEY, base, estáticos, almacenamiento, copias y parámetros de producción propios del entorno. El servidor de desarrollo no sustituye un despliegue.
