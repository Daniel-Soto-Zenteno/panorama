"""Build the evaluation report with the bundled artifact Python runtime."""
import ast
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, Circle
from PIL import Image as PILImage

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/qa/Informe_Evaluacion_3_Panorama_Fuente.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
E=ROOT/'docs/evidencias'
quality=json.loads((E/'calidad.json').read_text(encoding='utf-8'))
browser=json.loads((E/'navegador.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
styles=getSampleStyleSheet()
for n in ['Normal','BodyText','Heading1','Heading2','Heading3','Title']:
    styles[n].fontName='Arial-Bold' if n.startswith('Heading') or n=='Title' else 'Arial'
    styles[n].textColor=colors.black
styles['BodyText'].fontSize=10.5;styles['BodyText'].leading=15;styles['BodyText'].spaceAfter=9
styles['Heading1'].fontSize=19;styles['Heading1'].leading=24;styles['Heading1'].spaceAfter=15
styles['Heading2'].fontSize=12.5;styles['Heading2'].leading=17;styles['Heading2'].spaceBefore=12;styles['Heading2'].spaceAfter=7
styles['Title'].fontSize=29;styles['Title'].leading=35
styles.add(ParagraphStyle(name='Small',fontName='Arial',fontSize=8.7,leading=12,spaceAfter=7))
styles.add(ParagraphStyle(name='Cell',fontName='Arial',fontSize=8.5,leading=11.5))
styles.add(ParagraphStyle(name='Caption',fontName='Arial',fontSize=9,leading=12,spaceBefore=7,spaceAfter=12))
styles.add(ParagraphStyle(name='CodeBlock',fontName='Courier',fontSize=8.2,leading=11,spaceBefore=8,spaceAfter=12,backColor=colors.HexColor('#F2F3F2'),borderPadding=10))
story=[]; sections=[]
W=495
def p(text,style='BodyText'):
    story.append(Paragraph(text,styles[style]))
def h(text):p(text,'Heading2')
def page(title):
    if story:story.append(PageBreak())
    sections.append((title,len(sections)+3))
    p(title,'Heading1')
def table(headers,rows,widths=None,pad=8):
    data=[[Paragraph(escape(str(x)),styles['Cell']) for x in row] for row in [headers]+rows]
    t=Table(data,colWidths=widths or [W/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EFEFEF')),('GRID',(0,0),(-1,-1),.45,colors.HexColor('#D9D9D9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad)]))
    story.append(t);story.append(Spacer(1,10))
def pic(name,caption,maxh=370,width=W):
    path=E/name
    with PILImage.open(path) as im:iw,ih=im.size
    scale=min(width/iw,maxh/ih)
    story.append(Image(str(path),width=iw*scale,height=ih*scale,hAlign='CENTER'));p(caption,'Caption')
def code(file,function,limit=18):
    source=(ROOT/file).read_text(encoding='utf-8-sig');tree=ast.parse(source)
    node=next(n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==function)
    lines=source.splitlines()[node.lineno-1:min(node.end_lineno,node.lineno+limit-1)]
    p(f'Código · {file}, línea {node.lineno}. Función {function}.','Caption')
    story.append(Preformatted('\n'.join(lines),styles['CodeBlock'],maxLineLength=88))
def arrow(d,x1,y1,x2,y2,label='',dashed=False):
    d.add(Line(x1,y1,x2,y2,strokeColor=colors.black,strokeWidth=.8,strokeDashArray=[4,3] if dashed else None))
    import math
    a=math.atan2(y2-y1,x2-x1);s=6
    d.add(Polygon([x2,y2,x2-s*math.cos(a-.45),y2-s*math.sin(a-.45),x2-s*math.cos(a+.45),y2-s*math.sin(a+.45)],fillColor=colors.black))
    if label:d.add(String((x1+x2)/2,(y1+y2)/2+7,label,fontName='Arial',fontSize=8,textAnchor='middle'))
def box(d,x,y,w,h,title,lines=(),rounded=0):
    d.add(Rect(x,y,w,h,rx=rounded,ry=rounded,strokeColor=colors.black,fillColor=colors.white,strokeWidth=.8))
    d.add(String(x+w/2,y+h-17,title,fontName='Arial-Bold',fontSize=9,textAnchor='middle'))
    if lines:
        d.add(Line(x,y+h-25,x+w,y+h-25,strokeWidth=.6))
        for i,line in enumerate(lines):d.add(String(x+7,y+h-40-13*i,line,fontName='Arial',fontSize=8))

# Front matter
p('INACAP','Heading2');story.append(Spacer(1,55))
p('Panorama','Title');p('Informe técnico de implementación seguridad y pruebas','Heading1')
p('Evaluación 3 · Ingeniería de Software TI3043','Heading2')
p('Comunidades y actividades locales en Puerto Montt y Puerto Varas')
story.append(Spacer(1,38))
table(['Antecedente','Detalle'],[['Integrantes','Daniel Soto\nDiego Villota\nMauro Sotomayor'],['Carrera','Analista Programador'],['Docente','José Jara'],['Fecha','25 de noviembre de 2026'],['Entrega','Prototipo web ejecutable, código y evidencias verificables']], [120,375])
story.append(Spacer(1,25));p('El informe documenta la construcción y las pruebas del prototipo. La demostración presencial y defensa corresponden a la Evaluación 4 y se preparan por separado.','Small')
story.append(PageBreak());p('Índice','Heading1')
toc_index=len(story);story.append(Spacer(1,1))

page('1 Introducción y estado del proyecto')
p('Panorama reúne actividades, lugares y conversaciones comunitarias de Puerto Montt y Puerto Varas. El prototipo permite descubrir un evento, revisar su comunidad y expresar intención de asistir. También permite que una persona registrada proponga actividades y que un moderador decida su publicación con un motivo registrado.')
p('La implementación completa el recorrido principal previsto en la Evaluación 2: propuesta, aprobación, consulta pública y asistencia. La primera ejecución de 28 pruebas automatizadas detectó un defecto de respuesta en el inicio de sesión de la API; después de corregirlo, las 28 aprobaron. Se agregaron seis comprobaciones en navegador y dos comprobaciones de calidad, para 36 casos identificados. Estos resultados corresponden al entorno local descrito en este informe.')
h('1.1 Continuidad e insumos')
p('Utilizamos los 16 requerimientos funcionales RF01 a RF16, los ocho no funcionales RNF01 a RNF08, las reglas RN01 a RN10 y los casos de uso CU01 a CU10 del informe anterior [1]. Conservamos las dos ciudades, el mapa público, los foros moderados y la asistencia simbólica. Los distintivos siguen siendo simulados y no generan cobros ni privilegios de seguridad.')
p('El Informe 2 indicaba que las entrevistas y la validación externa estaban pendientes. La construcción no modifica ese antecedente: las pruebas de software no constituyen entrevistas ni aceptación del producto por parte de usuarios. Tampoco se atribuyen convenios a municipalidades o a espacios comunitarios.')
h('1.2 Punto de partida y cambios')
p('La carpeta ya tenía origin apuntando a Daniel-Soto-Zenteno/panorama. Se ejecutó git pull --ff-only sobre main y Git informó que estaba actualizada. La base recibida fue 285313ebf0d1291bee86606d75940cf05121f1b0. Contenía el mapa, autenticación y CRUD de actividades para administradores; core/tests.py aún no tenía casos implementados.')
p('Se incorporaron cuentas, perfiles, propuestas de comunidad y lugar, moderación, foro, reportes, asistencia y métricas propias. Se mantuvo el modelo Actividad para preservar las migraciones existentes. Se eligió SQLite como entorno de reproducción y se dejó PostgreSQL como alternativa configurable, sin atribuirle pruebas que no se ejecutaron.')
h('1.3 Alcance de esta entrega')
p('La entrega incluye los archivos fuente locales, migraciones, dependencias fijadas, instrucciones, datos ficticios regenerables, capturas y registros de pruebas. No incluye publicación del sitio ni envío de cambios a GitHub. El repositorio remoto identifica el punto de partida; el paquete local y el manifiesto de huellas identifican los archivos implementados en esta evaluación.')

page('2 Tecnologías y entorno de desarrollo')
p('La solución mantiene la tecnología presente en el repositorio para evitar una reescritura sin necesidad funcional. Python concentra las reglas del servidor; Django aporta formularios, autenticación, sesiones, ORM y migraciones. La interfaz usa plantillas HTML, CSS adaptable y JavaScript limitado a la cartografía.')
table(['Tecnología o herramienta','Versión comprobada','Función real'],[['Python','3.12.14','Servidor, comandos y pruebas'],['Django','5.2.17','Rutas, formularios, seguridad, ORM y plantillas'],['SQLite','Incluido con Python','Persistencia relacional local y respaldo'],['Leaflet','1.9.4','Marcadores y navegación cartográfica'],['OpenStreetMap','Servicio externo','Teselas del mapa; sin almacenamiento del dominio'],['python-dotenv','1.2.1','Lectura de configuración externa'],['Git y GitHub','Repositorio main','Historial y actualización de la base'],['Edge y Playwright','Edge '+browser['browser'],'Pruebas de interfaz y capturas']], [140,110,245])
h('2.1 Dependencias y decisión de versión')
p('Se fijó Django 5.2.17 de la línea LTS para el entorno académico. El repositorio base declaraba Django 6.1.3; la transición a la línea LTS se verificó ejecutando todas las migraciones, las comprobaciones de Django y la suite. Esta decisión reduce cambios de plataforma durante la evaluación, pero requiere revisar actualizaciones de seguridad antes de un despliegue posterior [3].')
p('backend/requirements.txt fija también asgiref 3.13.0, sqlparse 0.6.1 y tzdata 2026.6. No se requiere un proceso de compilación del frontend. La cartografía externa se descarga en el navegador; los eventos y las conversaciones permanecen en la base propia.')
h('2.2 Entorno medido')
p('Las pruebas se ejecutaron en Windows 11, versión 10.0.26300, con Python de 64 bits y 12 procesadores lógicos. El motor fue SQLite. El cliente de pruebas de Django ejecutó las comprobaciones de servidor; Edge ejecutó las comprobaciones de interfaz. Los datos son ficticios y no contienen correos operativos de personas.')

page('2.3 Tendencias y reproducción del entorno')
p('Cloud Computing permite utilizar recursos compartidos provisionados como servicios. SaaS entrega una aplicación utilizable por sus consumidores; IaaS entrega capacidad de cómputo, almacenamiento y red que el equipo administra. Estas categorías no son equivalentes ni se deducen simplemente de usar internet [4].')
table(['Opción','Pertinencia para Panorama','Decisión de esta entrega'],[['SaaS','La aplicación podría ofrecerse como servicio web a vecinos y organizadores. GitHub se consume como servicio de colaboración.','Panorama se ejecutó localmente; no se declara servicio SaaS de producción.'],['IaaS','Una máquina virtual podría alojar Django y el motor relacional; exige parches, TLS, respaldos y supervisión.','No contratada ni utilizada para ejecutar las pruebas.'],['Nube administrada','Un servicio de aplicaciones y una base administrada podrían reducir tareas de operación.','Alternativa futura, sujeta a recursos y prueba técnica.']], [95,215,185])
h('2.4 Instalación reproducible')
p('Se requiere Python 3.12, Git y acceso a internet para instalar las dependencias. En PowerShell, desde la raíz del proyecto, se ejecutan las siguientes órdenes. La variable SECRET_KEY de .env debe sustituirse por un valor aleatorio local antes del uso fuera de desarrollo.')
story.append(Preformatted('py -3.12 -m venv .venv\n.\\.venv\\Scripts\\python.exe -m pip install -r backend/requirements.txt\nCopy-Item .env.example .env\n.\\.venv\\Scripts\\python.exe backend/manage.py migrate\n.\\.venv\\Scripts\\python.exe backend/manage.py seed_demo\n.\\.venv\\Scripts\\python.exe backend/manage.py runserver 127.0.0.1:8000',styles['CodeBlock'],maxLineLength=85))
p('El comando seed_demo crea demo_vecina y demo_moderador con claves aleatorias que imprime una sola vez. Si los datos ya existen, no cambia las contraseñas. La copia de trabajo conserva las claves en un archivo local excluido de Git; no se incluyen en el informe ni en el paquete de entrega.')
p('Para PostgreSQL se instala requirements-postgres.txt y se configura DB_ENGINE=postgres con DB_NAME, DB_USER, DB_PASSWORD, DB_HOST y DB_PORT. Esta variante exige un servicio disponible y queda fuera de los resultados medidos. La guía completa y el recorrido de uso están en README.md.')

page('3 Arquitectura y estructura de la implementación')
p('Se implementó un monolito modular. Django sirve las páginas y las operaciones de negocio desde el mismo origen. El mapa recibe los mismos resultados que la lista mediante JSON incorporado con json_script; la API de consulta pública mantiene /api/activities/. Los cambios de estado se realizan mediante formularios POST protegidos por CSRF.')
table(['Ubicación','Responsabilidad'],[['backend/config/','Configuración, middleware y rutas raíz'],['backend/core/models.py','Entidades, relaciones y validaciones de dominio'],['backend/core/forms.py','Campos permitidos y errores de entrada'],['backend/core/services.py','Visibilidad, moderación transaccional y RSVP'],['backend/core/views.py y urls.py','Autorización, navegación y coordinación'],['backend/core/management/commands/','Datos demo y finalización de eventos'],['frontend/','Plantillas, CSS y adaptador de mapa'],['tools/ y docs/evidencias/','Pruebas adicionales, informe y resultados']], [205,290])
h('3.1 Componentes actualizados')
d=Drawing(W,220)
box(d,15,140,150,65,'Navegador',['HTML, CSS y Leaflet'])
box(d,260,140,215,65,'«component» Django',['views + forms + services'])
box(d,260,20,215,65,'«database» SQLite',['ORM y migraciones'])
box(d,15,20,150,65,'«external» OSM',['Teselas por HTTPS'])
arrow(d,165,172,260,172,'HTTP local')
arrow(d,368,140,368,85,'ORM')
arrow(d,90,140,90,85,'HTTPS')
story.append(d);p('Figura 1. Diagrama de componentes actualizado. Los componentes lógicos del Informe 2 se concretan dentro de una aplicación Django.','Caption')
p('El diseño previo no fijaba marcas ni lenguajes. La implementación concentra identidad, comunidad y moderación en core y aísla las reglas compartidas en services.py. Se adoptó renderizado en servidor para que lista, ficha y foro sigan funcionando sin JavaScript. Este cambio afecta el diagrama de componentes; no altera los actores ni los objetivos de los casos de uso.')

page('3.2 Modelo de clases y relaciones persistentes')
p('Evento se concretó como Actividad para conservar el historial de migraciones del repositorio. Usuario corresponde a auth.User y el rol de moderador se representa con is_staff. Perfil amplía la identidad sin sustituir el mecanismo de autenticación de Django. Se añadieron horarios habituales para mantener las actividades recurrentes del código base.')
d=Drawing(W,360)
box(d,5,260,140,85,'User',['username, email, password','is_staff'])
box(d,330,260,155,85,'Perfil',['nombre, intereses','verificado simulado'])
box(d,5,140,140,80,'Comunidad',['nombre, descripcion','estado, autor'])
box(d,177,140,140,95,'Actividad',['inicio, fin, estado','creado_por, aperturas','destacado simulado'])
box(d,345,140,140,80,'Lugar',['zona, latitud, longitud','estado, autor'])
box(d,5,15,140,80,'Publicacion',['texto, autor, estado'])
box(d,177,15,140,80,'Asistencia',['usuario, actividad','UNIQUE ambos'])
box(d,345,15,140,80,'Comentario',['texto, autor, estado'])
arrow(d,145,300,330,300,'1                           0..1')
arrow(d,177,180,145,180,'* : 1')
arrow(d,317,180,345,180,'* : 1')
arrow(d,75,95,75,140,'* : 1')
arrow(d,247,95,247,140,'* : 1')
d.add(Line(415,15,415,0,strokeWidth=.8));d.add(Line(415,0,75,0,strokeWidth=.8));arrow(d,75,0,75,15)
d.add(String(245,4,'Comentario * : 1 Publicacion',fontName='Arial',fontSize=8,textAnchor='middle'))
arrow(d,75,260,75,220,'1 autor : *')
story.append(d);p('Figura 2. Clases principales y multiplicidades. Las flechas apuntan a la referencia única; se omiten asociaciones de autoría repetidas para evitar cruces.','Caption')
p('Reporte y Auditoria conservan tipo y objeto_id, además de responsable o autor. El servicio comprueba el tipo permitido y la existencia del contenido antes de operar; esa referencia polimórfica no es una clave foránea a cinco tablas. Reporte agrega resolución y fecha de cierre. Auditoria conserva decisión, motivo y fecha.')
p('Las relaciones del dominio usan PROTECT para evitar eliminar accidentalmente contexto comunitario. Retirar contenido modifica su estado y no borra sus referencias. Asistencia usa una restricción única por usuario y actividad; el correo tiene un índice único sin distinguir mayúsculas para los valores no vacíos. CP26 y CP27 comprueban estas garantías en la base.')

page('3.3 Estados y despliegue actualizados')
p('Las propuestas se guardan directamente como PENDIENTE: el borrador reside en el formulario y no crea una fila. APROBADO es el nombre persistido equivalente al evento publicado del Informe 2. Corregir un rechazo o cambiar inicio, fin, lugar o recurrencia de un evento exige revisión nuevamente. Los estados terminales no se reabren desde la interfaz.')
d=Drawing(W,200)
box(d,5,110,120,45,'PENDIENTE',rounded=12);box(d,185,110,120,45,'APROBADO',rounded=12);box(d,370,110,120,45,'FINALIZADO',rounded=12)
box(d,5,10,120,45,'RECHAZADO',rounded=12);box(d,185,10,120,45,'CANCELADO',rounded=12);box(d,370,10,120,45,'RETIRADO',rounded=12)
arrow(d,125,140,185,140,'aprobar');arrow(d,305,140,370,140,'fin alcanzado')
arrow(d,65,110,65,55,'rechazar');arrow(d,245,110,245,55,'cancelar')
arrow(d,305,110,400,55,'retirar');arrow(d,185,167,125,167,'editar fechas o lugar')
story.append(d);p('Figura 3. Estados principales de Actividad. La edición de un rechazo vuelve a PENDIENTE; también se admite cancelación desde propuesta.','Caption')
h('3.4 Despliegue verificado')
p('El navegador y el servidor de desarrollo se ejecutaron en el mismo computador. Las pruebas visuales usaron 127.0.0.1:8011; la guía de instalación utiliza el puerto 8000. SQLite almacena la base en backend/db.sqlite3. La medición de calidad utilizó otra base en .local/quality.sqlite3. No se expuso el prototipo a internet.')
d=Drawing(W,125)
box(d,5,35,140,70,'«device» PC local',['Edge / navegador'])
box(d,220,15,265,105,'«executionEnvironment» Python',['Django en 127.0.0.1:8011','SQLite en archivo local','Mismo computador de evaluación'])
arrow(d,145,70,220,70,'HTTP')
story.append(d);p('Figura 4. Despliegue real de pruebas. La cartografía externa usa HTTPS; el acceso local a Django usó HTTP.','Caption')
p('El diagrama de despliegue anterior mostraba HTTPS y un motor relacional lógico. Aquí se documenta el entorno efectivamente usado; HTTPS público, servidor WSGI/ASGI y respaldo operativo corresponden al siguiente entorno. Las secuencias de consulta, aprobación y RSVP conservan su lógica y no se redibujan como requisito nuevo.')

page('4 Construcción del prototipo y propuestas')
p('El visitante puede explorar sin autenticarse. Crear propuestas, publicar, comentar, reportar y asistir exige sesión. Organizador no es un rol privilegiado: cualquier usuario registrado puede proponer una actividad y mantener sus propios eventos. Moderador es una cuenta is_staff, cuyo permiso se comprueba en el servidor.')
h('4.1 Entradas y validación de propuestas')
p('Comunidad recibe nombre y descripción de temática. Lugar agrega ciudad y coordenadas; el formulario limita la ciudad a las dos opciones del alcance y valida los rangos geográficos. Actividad recibe título, descripción, categoría, comunidad, lugar, inicio y fin, o un horario habitual si está disponible todo el año. Comunidad y lugar deben estar aprobados.')
p('El formulario excluye estado, autor, métricas y distintivos de los campos editables. El servidor asigna autor y estado y copia la ciudad y coordenadas del lugar. Una fecha de fin anterior al inicio se rechaza antes de guardar. Los campos válidos se conservan al mostrar el error, de modo que la persona puede corregir el dato sin reconstruir toda la propuesta.')
pic('C17-propuesta-extracto.png','Captura C17. Campo de título con un valor ficticio, sin envío. RF07; frontend/form.html y core/forms.py. La captura completa del recorrido CP32 es C06.',maxh=95)
code('backend/core/models.py','clean',12)
p('En CP10 se envió una propuesta válida, se comprobó que quedó PENDIENTE y fuera de la consulta pública y luego se aprobó con otra cuenta. En CP11 se ensayaron fin anterior al inicio y referencia inexistente: la respuesta mantuvo el formulario y no creó una actividad adicional. En navegador, CP32 repitió el recorrido sobre el servidor local.')

page('4.2 Moderación y flujo completo')
p('El moderador revisa la propuesta y registra una decisión con motivo obligatorio. Aprobar una actividad vuelve a validar sus referencias y vigencia. Una transición que no corresponde al estado actual se rechaza. La actualización de estado y la auditoría se ejecutan dentro de la misma transacción.')
code('backend/core/services.py','moderar',16)
p('Código 1. Inicio de la operación de moderación. El resto de la función guarda el nuevo estado y crea Auditoria dentro del mismo bloque atómico. CP17 prueba la denegación al usuario común y CP18 fuerza un fallo de auditoría para comprobar la reversión completa.','Caption')
pic('C14-auditoria.png','Captura C14. Decisiones persistidas con contenido, motivo, responsable y fecha. RF12; frontend/moderacion.html; CP10, CP18 y CP32.',maxh=205)
h('4.3 Resultado observable')
p('La propuesta de lectura vecinal creada en CP32 recibió el identificador 5. Después de aprobarla, su ficha informó APROBADO y admitió una intención de asistencia. La cuenta que propone y la que modera son diferentes. La auditoría conserva la explicación de la decisión y puede consultarse desde Moderación.')
p('Los reportes siguen otro ciclo: reportar crea una fila ABIERTO y no retira el contenido. Resolver registra motivo, responsable y fecha. Si se decide retirar, esa es otra operación auditada sobre el contenido. CP16 y CP19 comprueban que abrir y cerrar el reporte no alteran por sí solos la visibilidad del evento.')

page('4.4 Descubrimiento y participación')
p('El mapa y la lista se alimentan de una sola consulta. publicas() exige actividad aprobada, comunidad aprobada, lugar aprobado y fin futuro, salvo actividad habitual. Esto impide mostrar propuestas pendientes o eventos retirados, cancelados o vencidos. La lista permite continuar aunque falle Leaflet o el proveedor de teselas.')
p('Los filtros combinan búsqueda de título, ciudad, categoría, fecha y rango horario. Desde/Hasta se aplica a la hora de inicio en America/Santiago; las actividades habituales utilizan hora_inicio. Limpiar vuelve a la consulta sin parámetros. Una consulta sin coincidencias muestra un mensaje y no se trata como fallo de servidor.')
pic('C12-ficha-detalle.png','Captura C12. Ficha del evento aprobado durante CP32, con comunidad, lugar, horario y asistencia. RF03 y RF08; frontend/detalle.html.',maxh=340)
p('La asistencia es idempotente: get_or_create y la restricción única evitan una segunda fila para el mismo usuario y evento. Cancelar elimina la asistencia activa. No se aceptan nuevas confirmaciones si el evento ya inició o no es público. CP12 y CP13 verifican estos resultados; CP26 comprueba la restricción de integridad directamente.')
p('Las aperturas se incrementan con una expresión F del ORM y cuentan accesos, sin identificar personas únicas. La lista Mis propuestas limita sus métricas al creador autenticado. Los distintivos de evento destacado y organizador verificado se administran por separado y muestran su condición simulada.')

page('4.5 Comunidades foro y reportes')
p('La comunidad aprobada tiene un foro público. Una persona con sesión puede publicar texto y responder a publicaciones visibles. Se preservan autor, comunidad, publicación de origen y fecha. Los comentarios de una publicación retirada no reciben nuevas respuestas y el contenido retirado deja de aparecer en la consulta pública del foro.')
pic('C13-foro-detalle.png','Captura C13. Publicación y comentario guardados durante CP33. Los datos son ficticios. RF09 y RF10; frontend/foro.html y core/views.py.',maxh=320)
p('Los textos se muestran con el escape automático de las plantillas; no se aceptan fragmentos HTML como contenido ejecutable. CP25 almacenó una cadena con etiquetas de script y comprobó que la respuesta contenía las etiquetas escapadas, sin ejecutarlas como código. Los marcadores del mapa también construyen sus enlaces mediante textContent.')
h('4.6 Manejo de errores y límites')
p('El texto vacío se rechaza y la interfaz informa el dato que requiere corrección. Las publicaciones se limitan a 3000 caracteres y los comentarios a 1500. Reportar exige un motivo y un objeto visible de uno de los cinco tipos admitidos. Un identificador inexistente o un contenido no consultable devuelve 404; el permiso insuficiente devuelve 403.')
p('La moderación conserva los registros internos. Este comportamiento responde a la necesidad de contexto y auditoría; no reemplaza una política de conservación de datos personales. El prototipo no incorpora mensajes privados, chat instantáneo, venta de entradas, correos transaccionales ni notificaciones push.')

page('5 Datos e interfaces desarrolladas')
table(['Entidad','Operaciones desarrolladas','Relación o integridad principal'],[['User y Perfil','Registro, inicio y cierre; edición propia de perfil','User 1 a 0..1 Perfil; correo único'],['Comunidad y Lugar','Propuesta, consulta aprobada y moderación','Autor protegido; coordenadas y ciudad válidas'],['Actividad','Propuesta, consulta, edición propia, cancelación y fin','Comunidad y lugar aprobados; fin posterior'],['Asistencia','Confirmación, consulta de total y cancelación','Usuario + actividad únicos'],['Publicacion y Comentario','Alta, consulta y retiro por moderación','Autor y contexto protegidos'],['Reporte','Alta y cierre con resolución','Tipo e identificador validados por servicio'],['Auditoria','Alta transaccional y consulta de moderador','Motivo, responsable y fecha obligatorios']], [110,200,185])
p('La eliminación física se limita a la asistencia que la persona cancela. El contenido del dominio utiliza retiro o cancelación lógica para conservar referencias. Las migraciones nuevas mantienen las actividades históricas como propuestas pendientes; deben completarse con comunidad, lugar y fin antes de aprobarse.')
h('5.1 Navegación y contratos')
table(['Interfaz','Entrada y salida'],[['/ y /api/activities/','GET de consulta y filtros; página o JSON público'],['/activity/id/ y /community/id/','Ficha y foro; enlaces entre contexto y evento'],['/account/register/ y /account/login/','Formularios de cuenta y sesión'],['/propose/tipo/ y /mine/','Propuestas y métricas propias'],['/moderation/ y /resolve/id/','Revisión y resolución, solo moderador'],['/profile/ y /privacy/','Perfil propio y aviso de uso de datos']], [220,275])
p('La persistencia se verifica volviendo a consultar el ORM después de cada operación en las pruebas. Las capturas C07, C09 y C10 muestran resultados que ya proceden del almacenamiento. CP35 compara usuarios, eventos, comentarios y auditoría en un respaldo independiente. No se sustituye la base por datos estáticos incrustados en JavaScript.')

page('5.2 Adaptabilidad y continuidad sin mapa')
p('La interfaz reorganiza las columnas a una sola columna en pantallas pequeñas. Los formularios tienen etiquetas visibles y los controles admiten foco por teclado. Se evita el desbordamiento del documento y se permite que descripciones largas envuelvan sus líneas. La ficha y el foro siguen siendo enlaces HTML utilizables sin el adaptador cartográfico.')
imgs=[]
for name in ['C16-explorar-viewport.png','C15-propuesta-viewport.png']:
    imgs.append(Image(str(E/name),width=216,height=480))
t=Table([imgs],colWidths=[247.5,247.5]);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]));story.append(t)
p('Capturas C16 y C15. Vista inicial de exploración y propuesta a 360 × 800. Son recortes de ventana; el formulario continúa mediante desplazamiento vertical. CP30 y CP36 comprobaron ancho del documento de 360 px, sin desplazamiento horizontal.','Caption')
p('CP31 bloqueó unpkg.com y tile.openstreetmap.org. El aviso indicó que el mapa no estaba disponible y mantuvo la lista con cuatro actividades. CP36 comprobó el acceso al enlace Saltar al contenido y el paso por teclado de título a descripción. Estas comprobaciones no constituyen una auditoría completa WCAG ni una prueba en teléfono físico.')

page('6 Confidencialidad normativa y seguridad')
p('El sistema trata correo privado, credenciales derivadas, identificador de usuario, perfil, textos públicos, intenciones de asistir y decisiones de moderación. Los riesgos relevantes son exposición del correo, edición de contenido ajeno, suplantación de sesión, ejecución de texto malicioso y pérdida de contexto por cambios parciales.')
table(['Dato','Acceso previsto','Medida y límite'],[['Correo y credencial','Cuenta propia y operación del sistema','Ausentes de API pública; hash de contraseña'],['Usuario y mensajes','Visibles en el foro','Aviso de publicación; escape de texto'],['Asistencia','Total público y relación interna','No publica lista de correos; unicidad'],['Reportes y auditoría','Moderadores','is_staff comprobado en servidor'],['Ubicación','Lugares de actividad','No se rastrea la ubicación de personas']], [115,170,210])
h('6.1 Marco chileno aplicable')
p('Al corte de 25 de noviembre de 2026, el tratamiento de datos personales exige analizar la Ley 19.628. Sus reglas de autorización, finalidad y derechos de los titulares son pertinentes a las cuentas y al contenido vinculado con personas [5]. El carácter académico no convierte automáticamente toda información personal en información de uso libre.')
p('La Ley 21.719 modifica este régimen. El texto consolidado de BCN consultado incorpora la Ley 21.855 publicada el 23 de noviembre de 2026 y fija la vigencia de las modificaciones para el 15 de octubre de 2027 [6]. Por eso no se afirma que sus nuevas obligaciones ya estén íntegramente vigentes en esta evaluación.')
p('El formulario de registro exige aceptación del aviso y se usan datos ficticios en las pruebas. Antes de abrir cuentas reales deben definirse responsable operativo, conservación, eliminación, respaldo restringido y canal verificable para ejercer derechos. No se declara cumplimiento jurídico integral por haber implementado un checkbox o una página informativa.')
h('6.2 Proporcionalidad')
p('No se realizan pagos ni se almacenan tarjetas; por ello no se atribuye al prototipo cumplimiento PCI DSS. Tampoco se afirma aplicación automática del RGPD europeo sin analizar su ámbito. La cartografía recibe solicitudes del navegador y su IP; la aplicación no le envía correos, contraseñas ni las relaciones de asistencia.')

page('6.3 Controles realizados y relación con OWASP')
table(['Riesgo OWASP 2025','Control implementado','Evidencia y pendiente'],[['A01 Control de acceso roto','Sesión, propiedad e is_staff; CSRF en POST','CP08, CP17, CP20 y CP24'],['A02 Configuración insegura','Secretos por entorno; cabeceras; modo PRODUCTION exige clave','check --deploy detecta cuatro avisos locales de TLS'],['A05 Inyección','ORM parametrizado; formularios y texto escapado','CP11 y CP25; no se usan consultas SQL con texto de usuario'],['A07 Fallos de autenticación','Autenticación y validadores de Django; hash con sal; cierre POST','CP06, CP07 y CP25; limitación de intentos pendiente'],['A09 Fallos de registro y alertas','Auditoría de decisiones con motivo, fecha y responsable','CP18 y CP19; monitoreo de seguridad operativo pendiente']], [125,210,160])
p('La relación con OWASP describe controles concretos y no una certificación ni una prueba de penetración completa [7]. Las sesiones usan cookie HttpOnly, SameSite=Lax y duración de una hora. Las rutas de escritura verifican permisos en servidor, incluso si una persona manipula los campos del formulario [8].')
code('backend/core/services.py','asistir',16)
p('Código 2. Validación de vigencia e idempotencia de asistencia. La restricción única permanece en la base incluso si una operación no pasa por el servicio.','Caption')
p('Django almacena contraseñas con su mecanismo PBKDF2 predeterminado [9]; CP25 comprueba que el valor persistido es diferente de la clave y que su verificación funciona. El informe no muestra hashes, cookies ni claves de las cuentas demo. El archivo .env y la base local están excluidos de Git.')
p('check --deploy informó W004, W008, W012 y W016 en el modo local: HSTS, redirección HTTPS y cookies Secure no están activos en HTTP. PRODUCTION=1 configura esos controles, pero debe probarse detrás del servicio HTTPS real. La entrega no se declara lista para exposición pública.')

page('7 Plan de pruebas y condiciones de ejecución')
p('El alcance comprende recorridos funcionales y negativos de los RF, restricciones de integridad, visibilidad, protección de datos y continuidad de la interfaz. Se distinguen tres grupos: CP01 a CP28 con Django TestCase; CP29 a CP33 y CP36 con navegador; CP34 y CP35 con una base aislada y medición de calidad.')
table(['Aspecto','Definición usada'],[['Entrada','Dependencias instaladas, migraciones aplicables y comprobación de Django sin errores'],['Datos unitarios','Tres cuentas ficticias: autor, otro usuario y moderador; comunidad y lugar aprobados; evento futuro'],['Aislamiento','Base temporal de Django por suite; transacciones restauradas entre casos'],['Salida funcional','Cada aserción cumple resultado esperado; ninguna prueba fallida se cuenta como aprobada'],['Salida de rendimiento','P95 de 100 consultas con 20 sesiones ≤ 2000 ms; cero respuestas erróneas'],['Salida de restauración','Mismos conteos de usuarios, eventos, comentarios y auditoría en archivo independiente'],['Evidencias','Logs, JSON y capturas rotulados en docs/evidencias/']], [130,365])
h('7.1 Reproducción')
story.append(Preformatted('.\\.venv\\Scripts\\python.exe backend/manage.py check\n.\\.venv\\Scripts\\python.exe backend/manage.py test core --verbosity 2\n.\\.venv\\Scripts\\python.exe tools/verify_quality.py',styles['CodeBlock'],maxLineLength=84))
p('Las tablas siguientes comparten la precondición de datos ficticios indicada arriba, salvo que una fila diga anónimo o sin CSRF. Los pasos se ejecutan en el método test_CPxx correspondiente de core/tests.py. Cada resultado observado de CP01 a CP28 se comprueba con aserciones y se conserva en pruebas-finales.txt.')
h('7.2 Alcance de la evidencia')
p('Una aprobación de un caso significa que pasaron sus comprobaciones específicas, no que el sistema esté libre de defectos. Las solicitudes del cliente de Django ejercitan URLs, middleware, formularios, vistas y base de datos sin un navegador. Los casos de navegador complementan esas pruebas con navegación y captura real sobre HTTP local.')
p('La carga de CP34 mide respuestas de aplicación en proceso, con 20 clientes autenticados y cinco consultas por cliente. No mide latencia de internet ni del proveedor cartográfico. La comprobación de restauración usa SQLite; no demuestra recuperación de un servicio PostgreSQL ni recuperación completa de infraestructura.')

# Detailed executed test cases. Shared preconditions are on the prior page.
cases=[
('01','RF01','Anónimo: abrir / y GET API','Evento publicado en ambos','Visible; API devuelve 1'),
('02','RF01 RF14','Variar estado; fijar fin anterior a ahora','Pendientes y vencidos ausentes','Lista vacía en cada estado'),
('03','RF02','Ciudad Montt + Cultura; Varas; búsqueda inexistente; limpiar','AND, vacío y restauración','1, 0, aviso y 1 resultado'),
('04','RF02','Fecha del evento; fecha inválida; hora xx; 19:00 a 10:00','Coincide o error 400','1 coincidencia; tres 400'),
('05','RF03 RNF02','Abrir ficha y leer JSON','Comunidad correcta; sin privados','Nombre correcto; sin correo/clave'),
('06','RF04','Registrar nueva cuenta; repetir correo con otro usuario','Cuenta y rechazo de duplicado','Nueva persiste; duplicada no'),
('07','RF04','Clave inválida; login válido; logout; proponer','401, 200 y escritura bloqueada','401, 200; no crea propuesta'),
('08','RF05','Editar perfil enviando además ID de otro usuario','Solo perfil de la sesión cambia','Perfil ajeno conserva nombre'),
('09','RF06','Proponer comunidad; lugar con latitud 99','Pendiente; coordenada rechazada','Comunidad creada; lugar no'),
('10','RF07 RF08 RF12','Crear evento, consultar, aprobar como mod, asistir como otro','Oculto, visible, RSVP y auditoría','Todos los registros comprobados'),
('11','RF07 RNF06','Evento con fin en 2000; comunidad 999999','Formulario con error; sin alta','200 con formulario; una fila previa'),
('12','RF08','Confirmar dos veces; cancelar','Una asistencia y luego cero','Conteos 1, 1 y 0'),
('13','RF08 RF14','Inicio anterior a ahora; luego estado cancelado','Ambos rechazan asistencia','ValidationError en ambos'),
('14','RF09 RF10','Publicar Hola comunidad; comentar Nos vemos','Texto con autor y origen','Relaciones y textos persistidos'),
('15','RF09 RF10','Publicar espacios; responder a publicación retirada','Sin publicación; 404 al comentar','Cero nuevas filas'),
('16','RF11','Reportar evento con motivo','ABIERTO sin ocultar','Reporte abierto; evento público'),
('17','RF12 RNF01','Usuario común intenta moderar y cambiar distintivo','403; sin cambio de estado','Tres 403; sigue APROBADO'),
('18','RF12 RNF06','Simular excepción al insertar Auditoria durante retiro','Reversión de estado y auditoría','APROBADO; cero auditorías'),
('19','RF13','Moderador cierra reporte con resolución','Responsable, fecha y contenido visible','CERRADO con datos; evento público'),
('20','RF14','Editar ajeno; luego autor cambia fecha','Ajeno denegado; vuelve a pendiente','404 y PENDIENTE'),
('21','RF14','Cancelar evento propio; ejecutar finalización sobre vencido','Oculto y FINALIZADO','Fuera del mapa; estado final'),
('22','RF15','Moderador alterna destacado y verificado por separado','Banderas independientes y aviso','Persisten independientes; simulado'),
('23','RF16','Abrir ficha; consultar Mis propuestas de otro usuario','Suma acceso; sin métricas ajenas','Una apertura; título ajeno ausente'),
('24','RNF01','Cliente estricto POST sin CSRF; GET logout','403 y 405','Ambos códigos coinciden'),
('25','RNF02','Verificar hash; publicar etiqueta script','Clave derivada y texto escapado','Verificación válida; HTML escapado'),
('26','RNF06','Insertar RSVP duplicado directamente en base','Restricción única impide fila','IntegrityError; no duplica'),
('27','RF04 RNF06','Crear correo repetido en mayúsculas desde ORM','Índice único rechaza duplicado','IntegrityError'),
('28','RF12','Retirar comunidad aprobada con moderador','Hijos fuera del mapa; foro no público','Cero eventos; foro 404'),
]
for title,chunk in [('7.3 Casos ejecutados del 01 al 10',cases[:10]),('7.4 Casos ejecutados del 11 al 20',cases[10:20]),('7.5 Casos ejecutados del 21 al 28',cases[20:])]:
    page(title)
    p('Precondiciones: conjunto aislado de CP01 a CP28 descrito en 7. Todos los casos se ejecutaron el 25 de noviembre de 2026. Evidencia de cada fila: método test_CPxx de backend/core/tests.py y docs/evidencias/pruebas-finales.txt.','Small')
    table(['Caso y requisito','Pasos y datos','Esperado','Observado y estado'],[[f'CP{n}\n{rf}',steps,expected,observed+'\nAPROBADO'] for n,rf,steps,expected,observed in chunk],[90,145,120,140])
    if chunk is cases[20:]:pass
    p('La ejecución usa autenticación del rol indicado y vuelve a consultar el almacenamiento después de cada mutación. Un estado APROBADO en esta tabla corresponde al caso de prueba y no al estado de moderación del contenido.','Small')

page('7.6 Navegador rendimiento y recuperación')
table(['Caso y requisito','Procedimiento y esperado','Observado y estado'],[['CP29 / RF01','Abrir mapa y lista a 1366 × 768; al menos cuatro eventos.','4 actividades y mapa. APROBADO. C01; navegador.json.'],['CP30 / RNF04','Abrir mapa, ficha, foro y registro a 360 × 800; sin desbordamiento.','Ancho 360 en las cuatro rutas. APROBADO. C04.'],['CP31 / RNF08','Bloquear CDN y teselas; conservar aviso, lista y acceso a fichas.','Aviso de mapa no disponible y 4 actividades. APROBADO. C05.'],['CP32 / RF07 RF08 RF12','Proponer, aprobar con otra cuenta y asistir desde interfaz.','Evento 5 APROBADO; 1 intención. APROBADO. C06 a C09.'],['CP33 / RF09 RF10','Publicar y comentar en foro desde navegador.','Ambos textos visibles. APROBADO. C10.'],['CP36 / RNF04 RNF05','Propuesta, perfil y métricas móviles; Tab al acceso y entre campos.','Sin desbordamiento; foco correcto. APROBADO. acceso.json.']], [100,210,185])
h('7.7 CP34 Medición de consulta')
perf=quality['CP34']
p(f"Se crearon 200 eventos aprobados, 20 comunidades y 20 cuentas ficticias. Se autenticaron 20 clientes y se enviaron cinco consultas de filtros por cliente con un máximo de 20 trabajadores concurrentes. Tras una consulta de calentamiento, las 100 muestras obtuvieron 200 registros por respuesta, sin errores. P95 por rango más próximo: <b>{perf['p95_ms']:.3f} ms</b>; máximo: {perf['maximum_ms']:.3f} ms. El umbral propuesto de 2000 ms se cumple en este entorno. APROBADO; evidencia calidad.json y tools/verify_quality.py.")
h('7.8 CP35 Respaldo y restauración')
p('Se generó una copia mediante SQLite online backup y se abrió como archivo independiente. Se compararon 20 usuarios, 200 actividades, un comentario y una auditoría: los cuatro conteos coincidieron. APROBADO; calidad.json registra cada valor. La prueba no contiene datos personales reales ni declara que ya exista un calendario operativo de respaldos por Sprint.')

page('8 Defectos correcciones y nuevas pruebas')
p('Se conservó la primera ejecución para que la evaluación no dependa solo del resultado final. pruebas-iniciales.txt registra 28 casos, 27 aprobados y un fallo. pruebas-finales.txt registra la ejecución posterior de los 28 casos con resultado OK. Las incidencias de revisión de código se distinguen del fallo reproducido.')
table(['ID y prioridad','Defecto y evidencia','Corrección y reprueba','Situación'],[['I01 / Alta','CP07: login válido devolvía 405. login_view invocaba una vista decorada solo para GET dentro de POST.','Se devuelve JsonResponse directamente. CP07: 200 y sesión válida; suite completa OK.','Cerrado'],['I02 / Alta','Inspección de la base 285313e: API consultaba todas las actividades, sin estados ni vigencia.','Consulta publicas() con estado, referencias y fin. CP02 y CP28.','Cerrado'],['I03 / Alta','Inspección de la base: faltaban autoría de propuestas, revisión y auditoría de decisiones.','Modelos y servicios transaccionales; CP10, CP17 y CP18.','Cerrado'],['I04 / Media','Revisión de implementación: distintivos de evento y organizador estaban acoplados.','Acciones independientes y prueba de persistencia separada en CP22.','Cerrado'],['I05 / Media','check --deploy local: cuatro avisos de TLS y cookies Secure.','Configuración PRODUCTION disponible; requiere comprobar HTTPS y servidor real.','Abierto para despliegue'],['I06 / Media','La validación externa y las carreras de escritura en PostgreSQL no tienen evidencia.','Aplicar sesiones con usuarios y pruebas concurrentes en el motor de destino.','Abierto']], [70,160,180,85])
h('8.1 Análisis de causa y repetición')
p('I01 fue un fallo de integración entre vistas: autenticar funcionaba, pero el contrato HTTP de la respuesta reutilizada era incompatible con la solicitud original. La corrección se verificó en el mismo caso negativo y positivo y luego en toda la suite, evitando declarar solucionado el defecto solo por cambiar el código.')
p('I02 e I03 son brechas encontradas al comparar el código recibido con el Informe 2; no se presentan como fallos ejecutados antes de esta intervención. La prioridad refleja el efecto sobre publicación indebida y control de acceso. I05 e I06 permanecen abiertos y limitan el uso fuera de la evaluación local.')

page('9 Trazabilidad y evaluación de cumplimiento')
p('La matriz relaciona los 16 RF y los ocho RNF del Informe 2. I significa implementado con evidencia en el entorno descrito; P significa parcial por una verificación o condición operativa pendiente. El estado se refiere al requerimiento completo y no únicamente a disponer de una ruta o una pantalla.')
trace=[
('RF01','views.publicas / index','I','01,02,29','C01'),('RF02','views.filtradas','I','03,04','API y C01'),('RF03','views.detalle','I','05,32','C12'),('RF04','RegistroForm / cuenta','I','06,07,27','Log final'),('RF05','PerfilForm / perfil','I','08','Log final'),('RF06','proponer / formularios','I','09','Log final'),('RF07','ActividadForm / proponer','I','10,11,32','C06'),('RF08','services.asistir','I','12,13,26,32','C09'),('RF09','views.foro','I','14,15,33','C10'),('RF10','views.comentar','I','14,15,33','C13'),('RF11','views.reportar','I','16','Log final'),('RF12','services.moderar','I','17,18,28,32','C14'),('RF13','views.resolver','I','19','Log final'),('RF14','proponer / finalizar','I','02,20,21','Log final'),('RF15','views.distintivo','I','17,22','Log final'),('RF16','detalle / mine','I','23','C07'),('RNF01','Vistas / middleware','I','17,20,24','Log final'),('RNF02','auth / serializar','I','05,25','Log final'),('RNF03','filtradas / carga','I','34','calidad.json'),('RNF04','styles.css / plantillas','I','29,30,36','C15,C16'),('RNF05','Formularios / foco','P','11,36','Revisión parcial'),('RNF06','Restricciones / atomic','P','18,26,27','Falta carrera PG'),('RNF07','verify_quality / backup','P','35','Falta calendario'),('RNF08','map.js / HTML base','I','31','C05')]
table(['RF/RNF','Módulo o archivo','Estado','CP','Evidencia'],trace,[62,170,43,75,145],pad=4)
p('Resultado del criterio binario declarado: 21 de 24 requerimientos tienen estado I (87,5 %); 3 de 24 son P (12,5 %). Cada identificador pesa igual y los parciales no suman como completos. Los 16 RF tienen sus criterios centrales ejecutados. Este porcentaje no mide calificación, cobertura de líneas ni validación externa.','Small')

page('10 Limitaciones y trabajo pendiente')
p('La entrega es un prototipo local con funcionalidades persistentes y verificadas. Sus límites se organizan por condición de uso y no se ocultan detrás del número de pruebas aprobadas. La Evaluación 4 requiere preparar demostración y defensa con el equipo, además de conservar una copia estable del entorno.')
table(['Pendiente','Impacto','Acción necesaria antes de uso público'],[['Validación con usuarios','No hay evidencia de comprensión ni utilidad fuera del equipo.','Aplicar instrumentos del Informe 2 y registrar cambios.'],['Escrituras concurrentes','SQLite no reproduce el bloqueo de filas de PostgreSQL.','Ensayar RSVP simultáneo, moderación y edición sobre PostgreSQL.'],['Despliegue y HTTPS','La prueba local no protege tráfico público.','Servidor WSGI/ASGI, TLS, host, estáticos y check --deploy.'],['Operación y recuperación','Un respaldo probado no garantiza periodicidad ni recuperación de servidor.','Programar respaldos restringidos y ensayo de recuperación integral.'],['Privacidad operativa','No existe canal público formal ni plazos aprobados de conservación.','Definir responsable, atención de derechos y eliminación.'],['Autenticación robusta','No hay recuperación por correo ni limitación de intentos.','Añadir controles al preparar cuentas reales.'],['Accesibilidad completa','Se verificó foco y adaptación; no lector de pantalla ni WCAG integral.','Recorrer tareas con teclado, lector y teléfono real.']], [115,180,200])
h('10.1 Decisiones de alcance')
p('Los horarios habituales representan un intervalo diario dentro del mismo día. No se modelan calendarios semanales, feriados ni intervalos que crucen medianoche. La búsqueda horaria selecciona la hora de inicio; este significado debe contrastarse con usuarios. El diseño no incorpora pagos, reservas de cupo, chat ni seguimiento personal.')
h('10.2 Preparación de la Evaluación 4')
p('El equipo debe ejecutar la instalación desde una copia limpia, guardar las credenciales demo localmente, recorrer propuesta y aprobación con dos cuentas, comprobar las fechas de demostración y conservar respaldo de la base. Conviene preparar la explicación de permisos, estados, auditoría y de la diferencia entre el resultado de CP34 y una medición desde internet.')

page('11 Conclusiones')
p('Panorama pasó de un mapa con administración restringida a un prototipo que integra descubrimiento, cuentas, propuestas, revisión, participación y conversación comunitaria. El flujo de propuesta, aprobación y asistencia se ejecutó tanto mediante pruebas de servidor como desde un navegador real y dejó datos persistidos y auditoría consultable.')
p('La evidencia final incluye 28 pruebas automatizadas de servidor aprobadas, seis comprobaciones de navegador aprobadas y dos comprobaciones de calidad aprobadas. La primera ejecución detectó un defecto real de respuesta HTTP que se corrigió y volvió a comprobar. Los resultados permiten afirmar que los recorridos evaluados funcionan en el entorno local; no demuestran ausencia de defectos ni aceptación de usuarios.')
h('11.1 Decisiones técnicas verificables')
p('Mantener Django permitió concentrar el esfuerzo en los requerimientos del dominio. Los formularios restringen qué datos puede enviar cada rol; el servidor asigna autoría y estado. La moderación transaccional evita que una decisión se guarde sin auditoría, y la base impide asistencia duplicada y correo repetido. La cartografía se desacopló de la lista para conservar el acceso a la información cuando falla el proveedor.')
p(f"El uso de SQLite redujo los pasos de instalación. Con el conjunto de 200 eventos y 20 sesiones, CP34 registró un P95 de {perf['p95_ms']:.3f} ms frente al objetivo de 2000 ms. La restauración comprobó conteos coincidentes en cuatro entidades. Estas decisiones facilitan la reproducción académica, aunque no reemplazan las verificaciones del motor y alojamiento de destino.")
h('11.2 Balance respecto de lo comprometido')
p('Los 16 requerimientos funcionales tienen implementación y prueba identificadas. Cinco no funcionales tienen evidencia suficiente para el entorno declarado y tres se mantienen parciales por revisión de accesibilidad, concurrencia de escrituras y operación de respaldos. La validación con usuarios continúa pendiente, tal como se reconocía en el Informe 2.')
p('El principal aprendizaje de integración fue que un control correcto por separado puede producir un contrato incorrecto al reutilizarse desde otra operación, como ocurrió en el login de la API. Conservar el fallo y la reprueba hace auditable la corrección. El siguiente paso del equipo es contrastar los recorridos con usuarios y preparar la defensa sobre esta misma versión del prototipo.')

page('Referencias')
refs=[
('[1]','Soto, D., Villota, D. y Sotomayor, M. (2026). Comunidades y actividades locales. Evaluación 2. Informe entregado el 28 de octubre de 2026.'),
('[2]','Guía Evaluación 3 Ingeniería de Software TI3043. Documento de evaluación proporcionado para esta entrega.'),
('[3]','Django Software Foundation. Download Django y versiones soportadas. https://www.djangoproject.com/download/'),
('[4]','Mell, P. y Grance, T. (2011). The NIST Definition of Cloud Computing. SP 800-145. https://csrc.nist.gov/pubs/sp/800/145/final'),
('[5]','Biblioteca del Congreso Nacional de Chile. Ley 19.628 sobre protección de la vida privada. Texto de referencia al corte de esta evaluación. https://www.bcn.cl/leychile/navegar?idNorma=141599&amp;idVersion=2026-10-21'),
('[6]','Biblioteca del Congreso Nacional de Chile. Ley 21.719, texto consolidado con modificación de Ley 21.855 de 23 de noviembre de 2026. Artículo primero transitorio. https://www.bcn.cl/leychile/navegar?idNorma=1209272'),
('[7]','OWASP Foundation. OWASP Top 10 2025. https://top10.owasp.org/2025/'),
('[8]','Django Software Foundation. Security in Django 5.2. https://docs.djangoproject.com/en/5.2/topics/security/'),
('[9]','Django Software Foundation. Password management in Django 5.2. https://docs.djangoproject.com/en/5.2/topics/auth/passwords/'),
('[10]','Leaflet. Documentación 1.9.4. https://leafletjs.com/reference.html'),
('[11]','OpenStreetMap Foundation. Tile Usage Policy. https://operations.osmfoundation.org/policies/tiles/')]
for key,text in refs:p(f'<b>{key}</b> {text}')
p('Consulta de fuentes técnicas y normativas: 25 de noviembre de 2026. Los resultados de pruebas proceden de los archivos locales identificados en los anexos; no se atribuyen a las fuentes de documentación.','Small')

page('Anexo A Índice de evidencias y acceso al código')
p('Repositorio de origen: <link href="https://github.com/Daniel-Soto-Zenteno/panorama">https://github.com/Daniel-Soto-Zenteno/panorama</link>. Rama main actualizada al inicio desde el commit 285313e. Los cambios de esta entrega se encuentran en el código local y en el paquete Panorama_Entrega_Evaluacion_3.zip; no se afirma que ya estén publicados en el remoto.')
table(['Evidencia','Ubicación en docs/evidencias','Uso'],[['E01','pruebas-iniciales.txt','Primera ejecución: 27/28; fallo CP07'],['E02','pruebas-finales.txt','Reprueba: 28/28 OK'],['E03','navegador.json','CP29 a CP33 y versión de Edge'],['E04','calidad.json','CP34 y CP35; entorno y 100 muestras'],['E05','acceso.json','CP36; anchos móviles y foco'],['E06','revision-despliegue.txt','Cuatro avisos locales de TLS'],['E07','interfaz-audit.json','Detector mecánico: sin hallazgos; resolución CSS parcial'],['C01 a C05','Capturas de explorar, ficha, foro, móvil y sin mapa','Descubrimiento, interfaz y contingencia'],['C06 a C10','Propuesta, propias, moderación, asistencia y foro','Flujos de escritura persistente'],['C11 a C16','Capturas móviles y de detalle','Legibilidad de formulario, ficha y auditoría']], [80,220,195])
p('El detector mecánico informó una dificultad para resolver la ruta estática de CSS desde el HTML. El resultado sin hallazgos no se interpreta como validación exhaustiva. La revisión principal de interfaz procede de las capturas y las comprobaciones de navegador.')
h('A.1 Ubicaciones de código representativo')
table(['Requisito','Archivo y punto de entrada'],[['RF01 y RF02','backend/core/views.py · filtradas, serializar y home'],['RF04 a RF07','backend/core/forms.py · RegistroForm y ActividadForm'],['RF08 y RF12','backend/core/services.py · asistir y moderar'],['RF09 a RF16','backend/core/views.py · foro, comentar, reportar, resolver, distintivo y mis_actividades'],['Integridad','backend/core/models.py y migraciones 0003 a 0005'],['Reproducción','README.md y backend/requirements.txt']], [100,395])

page('Anexo B Revisión de la rúbrica y versión entregada')
table(['Criterio de la guía','Puntaje máximo','Secciones y evidencia'],[['Continuidad, alcance y trazabilidad','10','1, 9 y 10; matriz de 24 requerimientos'],['Tecnologías, tendencias y entorno','10','2; dependencias, nube y reproducción'],['Arquitectura, interfaces y datos','12','3 y 5; cuatro UML actualizados'],['Programación y funcionalidades','23','4; flujo completo, código y capturas'],['Confidencialidad, normativa y OWASP','15','6; pruebas de permisos, privacidad y límites'],['Diseño y ejecución de pruebas','15','7; 36 casos y evidencias'],['Defectos, correcciones y validación','10','8; fallo inicial, corrección y pendientes'],['Calidad del informe y evidencias','5','Índice, referencias y anexos A y B']], [220,70,205])
p('Esta tabla permite localizar la evidencia por criterio. No asigna una nota al trabajo ni reemplaza la revisión del docente. La sección del curso se omite en portada por indicación de los integrantes.')
h('B.1 Identificación de archivos')
p('docs/evidencias/manifiesto-sha256.json contiene las huellas SHA-256 de los archivos fuente y las evidencias del paquete. La base SQLite, .env, credenciales demo, entornos virtuales, metadatos Git y archivos temporales se excluyen del paquete. El conjunto de demostración se reconstruye con migrate y seed_demo.')
h('B.2 Comprobaciones de cierre')
p('La comprobación de Django terminó sin errores y makemigrations --check --dry-run informó No changes detected. La suite final registró 28 pruebas OK. Las dos bases de calidad se mantuvieron separadas de la base de demostración. No se utilizaron datos personales reales en las capturas ni se incluyeron secretos operativos en las evidencias compartidas.')
p('El informe contiene 23 páginas de desarrollo, además de portada, índice, referencias y anexos. El equipo puede repetir los comandos y contrastar cada resultado con las ubicaciones indicadas. La demostración presencial y la defensa no forman parte de la calificación de este informe [2].')

# Fill TOC after all headings are known. The report uses one explicit page per section.
toc_rows=[]
for title,num in sections:
    if title.startswith(('1 ','2 ','3 ','4 ','5 ','6 ','7 ','8 ','9 ','10 ','11 ','Referencias','Anexo')):
        toc_rows.append([title,str(num)])
toc=Table([[Paragraph(escape(a),styles['Small']),Paragraph(b,styles['Small'])] for a,b in toc_rows],colWidths=[455,40])
toc.setStyle(TableStyle([('BOTTOMPADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP')]))
story[toc_index]=toc
def footer(c,doc):
    c.setFont('Arial',8);c.setFillColor(colors.HexColor('#555555'))
    c.drawString(50,27,'Panorama · Ingeniería de Software TI3043 · Evaluación 3')
    c.drawRightString(545,27,str(doc.page))
doc=SimpleDocTemplate(str(OUT),pagesize=(595.28,841.89),rightMargin=50,leftMargin=50,topMargin=45,bottomMargin=45,title='Panorama Informe técnico de implementación seguridad y pruebas',author='Daniel Soto, Diego Villota y Mauro Sotomayor')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
(ROOT/'docs/qa/estructura.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2),encoding='utf-8')
