"""Run with the project's venv. All generated datasets stay in .local/."""
import json
import os
import sys
import time
import platform
import sqlite3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings
from django.core.management import call_command
from django.db import connections
from django.contrib.auth.models import User
from django.test import Client
from django.utils import timezone
from core.models import Comunidad, Lugar, Actividad, Publicacion, Comentario, Auditoria

local = ROOT / '.local'
local.mkdir(exist_ok=True)
db = local / 'quality.sqlite3'
if db.exists():
    raise SystemExit('quality.sqlite3 ya existe. Conserva o renombra el resultado antes de repetir.')
connections.close_all()
settings.DATABASES['default']['NAME'] = db
settings.ALLOWED_HOSTS += ['testserver']
call_command('migrate', verbosity=0)
users = [User.objects.create_user(f'carga{i}', f'carga{i}@example.invalid') for i in range(20)]
communities = [Comunidad.objects.create(nombre=f'Comunidad {i}', descripcion='Carga ficticia', autor=users[i], estado='APROBADO') for i in range(20)]
place = Lugar.objects.create(nombre='Lugar de prueba', descripcion='Ficticio', zona='puerto-montt', latitud=-41.47, longitud=-72.93, autor=users[0], estado='APROBADO')
now=timezone.now()
for i in range(200):
    Actividad.objects.create(titulo=f'Evento {i}', descripcion='Carga ficticia', categoria='Cultura', zona=place.zona, latitud=place.latitud, longitud=place.longitud, fecha_hora=now+timedelta(days=2), fin=now+timedelta(days=2,hours=2), estado='APROBADO', comunidad=communities[i%20], lugar=place, creado_por=users[i%20])
p=Publicacion.objects.create(comunidad=communities[0], autor=users[0], texto='Publicación de respaldo')
Comentario.objects.create(publicacion=p,autor=users[1],texto='Comentario de respaldo')
Auditoria.objects.create(tipo='actividad',objeto_id=1,responsable=users[0],decision='APROBADO',motivo='Datos de prueba')
clients=[]
for user in users:
    c=Client();c.force_login(user);clients.append(c)
# Warm caches before measuring. Five sequential requests per concurrent session.
clients[0].get('/api/activities/?category=Cultura&zone=puerto-montt')
def worker(client):
    rows=[]
    for _ in range(5):
        start=time.perf_counter()
        r=client.get('/api/activities/?category=Cultura&zone=puerto-montt')
        rows.append({'ms':round((time.perf_counter()-start)*1000,3),'status':r.status_code,'count':len(r.json()['activities'])})
    connections.close_all()
    return rows
with ThreadPoolExecutor(max_workers=20) as pool:
    samples=[r for rows in pool.map(worker,clients) for r in rows]
times=sorted(r['ms'] for r in samples)
source=sqlite3.connect(db); backup=sqlite3.connect(local/'backup.sqlite3');source.backup(backup);backup.close();source.close()
original=sqlite3.connect(db);restored=sqlite3.connect(local/'backup.sqlite3')
counts={}
for table in ['auth_user','core_actividad','core_comentario','core_auditoria']:
    before=original.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    after=restored.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    counts[table]={'original':before,'restaurado':after}
original.close();restored.close()
result={'environment':{'python':sys.version,'django':django.get_version(),'os':platform.platform(),'cpu':platform.processor(),'logical_cpus':os.cpu_count(),'engine':'SQLite','measurement':'Cliente de pruebas Django en proceso; sin HTTP de red ni teselas'},'CP34':{'events':200,'communities':20,'sessions':20,'requests':100,'p95_ms':times[94],'maximum_ms':max(times),'errors':sum(r['status']!=200 for r in samples),'passed':times[94]<=2000 and all(r['status']==200 and r['count']==200 for r in samples)},'CP35':{'counts':counts,'passed':all(c['original']==c['restaurado'] for c in counts.values()),'method':'SQLite online backup; reapertura en archivo independiente'},'samples':samples}
(ROOT/'docs/evidencias/calidad.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='samples'},ensure_ascii=False,indent=2))
