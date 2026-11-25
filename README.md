# Panorama

Prototipo web de comunidades y actividades locales en Puerto Montt y Puerto Varas.
Evaluación 3 de Ingeniería de Software TI3043. Equipo: Daniel Soto, Diego Villota y Mauro Sotomayor.

## Ejecutar en Windows

Requiere Python 3.12 o 3.13, Git e internet para instalar dependencias y ver la cartografía.
Desde esta carpeta, en PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
Copy-Item .env.example .env
# Cambia SECRET_KEY en .env por una clave aleatoria local.
.\.venv\Scripts\python.exe backend/manage.py migrate
.\.venv\Scripts\python.exe backend/manage.py seed_demo
.\.venv\Scripts\python.exe backend/manage.py runserver 127.0.0.1:8000
```

Abrir http://127.0.0.1:8000/. `seed_demo` imprime claves aleatorias para
`demo_vecina` y `demo_moderador` una sola vez; guardarlas localmente. Nunca subirlas.
En esta copia de trabajo las claves generadas están en `.demo-credentials.txt`, excluido de Git.
Para cambiar una clave perdida: `python backend/manage.py changepassword demo_vecina`.
No ejecutar el servidor de desarrollo como servicio público.

SQLite es el motor predeterminado. PostgreSQL es opcional: instalar
`backend/requirements-postgres.txt`, configurar `DB_ENGINE=postgres` y las variables
`DB_*` de `.env`, y ejecutar las migraciones. Esa variante no fue probada aquí.
Las migraciones conservan actividades anteriores como PENDIENTE; completar comunidad,
lugar y fin antes de aprobarlas. El índice único de correo requiere resolver posibles
duplicados históricos antes de migrar una base externa.

## Recorrido completo

1. Explorar mapa y lista, combinar filtros y abrir una ficha y su comunidad.
2. Crear cuenta o entrar como `demo_vecina`. Proponer comunidad, lugar o actividad.
3. Entrar como `demo_moderador`, abrir Moderación y aprobar con motivo.
4. Confirmar o cancelar asistencia desde la ficha. Es intención, sin reserva de cupo.
5. Publicar y comentar en una comunidad; reportar contenido para revisión.
6. Moderar el contenido o resolver un reporte; consultar el registro de auditoría.
7. Consultar métricas propias en Mis propuestas. Los distintivos son simulados.

## Pruebas y evidencia

```powershell
.\.venv\Scripts\python.exe backend/manage.py check
.\.venv\Scripts\python.exe backend/manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe backend/manage.py test core --verbosity 2
.\.venv\Scripts\python.exe tools/verify_quality.py
```

La última orden usa una base aislada `.local/quality.sqlite3` y se detiene si ya existe:
renombrarla junto con `.local/backup.sqlite3` antes de repetir. Comprueba 100 consultas,
20 sesiones, 200 eventos y 20 comunidades; el tiempo es de cliente Django en proceso,
sin red ni teselas. Comprueba restauración con una copia SQLite independiente.
Las herramientas de navegador comparten `tools/browser-runtime.cjs`. Requieren Node.js,
las cuentas de demostración y un servidor local en el puerto 8011:

```powershell
npm install --no-save --package-lock=false playwright
npx playwright install chromium
node tools/browser-check.cjs
node tools/browser-access.cjs
```

Para usar un navegador ya instalado, definir `BROWSER_EXECUTABLE` con la ruta de su
ejecutable. `tools/capture-details.cjs` actualiza los recortes del informe usando los
registros de demostración creados durante el recorrido inicial.

Evidencias reales en `docs/evidencias/`; informe en `docs/Informe_Evaluacion_3_Panorama.pdf`.
La versión editable adaptada a la plantilla INACAP está en
`docs/Informe_Evaluacion_3_Panorama_Formato_INACAP.docx` (29 páginas, con contraportada).
La primera ejecución tuvo un fallo en CP07, corregido y repetido. El informe separa
pruebas funcionales, medición local y validación externa pendiente.

## Archivos de entrega

`docs/` concentra el informe final, el contexto de la evaluación y las evidencias.
Los entornos virtuales, bases locales, credenciales, cachés y archivos de revisión
están excluidos de Git. No se necesita el ZIP para clonar ni ejecutar el proyecto.

Para reconstruir el Word en Windows se requiere la plantilla original facilitada por
el equipo, Python con `python-docx`, `reportlab` y `Pillow`, y Poppler en el PATH:

```powershell
python tools/adapt_report_template.py --template "C:\ruta\Carta-1-vert(1).docx"
```

`tools/build_report.py` conserva el contenido estructurado y genera una versión de
revisión en `docs/qa/`; no sobrescribe el PDF final. Tras editar el Word hay que
exportarlo a PDF y comprobar la paginación e índice antes de reemplazar la entrega.
`python tools/package_delivery.py` actualiza el manifiesto SHA-256 y genera un ZIP
local opcional con los archivos de entrega, sin bases ni claves locales.

## Operación y límites

`python backend/manage.py finalizar_eventos` cambia los vencidos a FINALIZADO; la
consulta pública los excluye por fecha aunque no se haya ejecutado el comando.
Programarlo diariamente en un despliegue real. Retirar y cancelar conservan registros.
Los horarios habituales se limitan a un intervalo diario en el mismo día. Filtros
Desde/Hasta seleccionan la hora de inicio, en America/Santiago.

Para producción: configurar SECRET_KEY real, DEBUG=False, ALLOWED_HOSTS y PRODUCTION=1;
usar HTTPS, servidor WSGI/ASGI, archivos estáticos, PostgreSQL y respaldos restringidos.
Quedan pendientes despliegue público, revisión de concurrencia de escrituras en
PostgreSQL, límites de intentos de acceso, recuperación de contraseña y validación con
usuarios. Los avisos de `check --deploy` del entorno local no equivalen a una auditoría.
La política de conservación y el canal formal de derechos deben definirse antes de
tratar datos reales. No hay pagos, chat, seguimiento personal ni garantías de seguridad.
