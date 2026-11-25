# Panorama

Aplicación web comunitaria para Puerto Montt y Puerto Varas. El diseño aprobado de la maqueta HTML está integrado con el backend Django del proyecto: mapa, publicaciones independientes o en comunidades, cuentas, perfiles, comentarios, guardados e imágenes opcionales, con revisión del equipo moderador.

## Ejecutar en Windows

Desde la carpeta del repositorio, en PowerShell:

```powershell
.\iniciar.ps1
```

Abrir http://127.0.0.1:8011. Se necesita Python 3.10 o superior e internet para instalar dependencias y cargar el mapa. El entorno local usa SQLite y conserva los datos entre reinicios. No crea cuentas ni publicaciones por defecto.

Para cargar ejemplos ficticios opcionales:

```powershell
.\iniciar.ps1 -ConEjemplos
```

Si prefieres ejecutar los pasos manualmente:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-local.txt
.\.venv\Scripts\python.exe backend/manage.py migrate --settings=config.settings_local
.\.venv\Scripts\python.exe backend/manage.py runserver 127.0.0.1:8011 --settings=config.settings_local
```

## Cuentas y moderación

Crear cuenta desde el botón de perfil o al intentar publicar, comentar o guardar. El acceso usa usuario y contraseña. La definición de autenticación con RUT sigue pendiente.

Para crear una cuenta moderadora propia:

```powershell
.\.venv\Scripts\python.exe backend/manage.py createsuperuser --settings=config.settings_local
```

Después inicia sesión en la web. En Tu perfil → Revisar contenido puedes aprobar, destacar o rechazar propuestas, aprobar comunidades y resolver reportes. Los usuarios normales no tienen acceso a estas operaciones, aunque modifiquen el navegador o llamen directamente a la API.

## Funciones

- Mapa de fondo y panel flotante, recogible y adaptable a teléfono.
- Destacadas visibles desde lejos; publicaciones normales desde zoom 15.
- Comunidades por intereses y publicaciones independientes.
- Eventos con fecha, actividades recurrentes por horario y lugares de encuentro.
- Filtros de ciudad, interés, fecha, ritmo activo/tranquilo, distancia y tipo de publicación.
- Perfil, comentarios y guardados persistentes por cuenta.
- Imagen opcional del autor; no hay fotos automáticas. Validación, reducción y conversión a JPEG en el servidor.
- Reportes y revisión con permisos de moderador.

No hay confirmación de asistencia ni votos simulados. Los ejemplos se identifican en la interfaz.

## PostgreSQL del equipo

La configuración original sigue en config.settings. Copia .env.example a .env y configura tu SECRET_KEY y las credenciales de PostgreSQL. Instala backend/requirements.txt y aplica las migraciones usando ese entorno:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe backend/manage.py migrate --settings=config.settings
.\.venv\Scripts\python.exe backend/manage.py runserver 127.0.0.1:8011 --settings=config.settings
```

Las dependencias se unificaron en Django 5.2, la versión probada para esta integración. Las migraciones añaden campos y tablas; conservan Actividad, sus datos originales y el modo recurrente por horario. La ejecución se verificó con SQLite; no se dispuso de una instancia PostgreSQL para validarla aquí.

## Validar

```powershell
.\.venv\Scripts\python.exe backend/manage.py test core --settings=config.settings_local
.\.venv\Scripts\python.exe backend/manage.py check --settings=config.settings_local
```

17 pruebas de integración. Véase [VALIDACION.md](VALIDACION.md).

## Para continuar y elaborar el informe

- [INFORME_IMPLEMENTACION.md](INFORME_IMPLEMENTACION.md): arquitectura, funciones, permisos, decisiones y límites verificados.
- [API.md](API.md): rutas y contratos principales.
- [DESIGN.md](DESIGN.md): diseño activo y archivos que lo implementan.

El frontend activo es frontend/index.html, frontend/css/panorama.css y frontend/js/panorama.js. Los archivos originales styles.css, map.js y main.js se conservan como referencia; la nueva página no los carga.

Los datos de SQLite, las imágenes subidas, el entorno virtual, .env y la clave local están excluidos de Git. En otro equipo se crean la base y las cuentas mediante los pasos anteriores. No se comparten contraseñas en el repositorio.

## Créditos

Diseño inspirado en los patrones de exploración observados en AllTrails y organización comunitaria de Reddit; no se copian sus marcas, código o fotografías. Revisión visual con Unslop de Damir Sokolovsky (@heydamir), https://github.com/heydamir/unslop, CC BY 4.0. Mapa con Leaflet y OpenStreetMap; tipografía DM Sans. El backend continúa el trabajo original del repositorio Panorama.
