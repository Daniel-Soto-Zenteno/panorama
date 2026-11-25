import secrets
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from core.models import Actividad, Comunidad, Lugar, Perfil, Publicacion, Comentario, Auditoria


class Command(BaseCommand):
    help = 'Crea datos ficticios. No modifica cuentas existentes. Las contraseñas se generan al ejecutar.'

    @transaction.atomic
    def handle(self, *args, **options):
        if User.objects.filter(username='demo_moderador').exists():
            self.stdout.write('Los datos demo ya existen; no se modificaron contraseñas.')
            return
        accounts = []
        for name, staff in [('demo_moderador', True), ('demo_vecina', False)]:
            if User.objects.filter(username=name).exists():
                raise CommandError(f'Ya existe {name}; no se alteró la cuenta.')
            password = secrets.token_urlsafe(14)
            user = User.objects.create_user(name, f'{name}@example.invalid', password, is_staff=staff)
            Perfil.objects.create(usuario=user, nombre='Moderación demo' if staff else 'Vecina demo')
            accounts.append((user, password))
        mod, author = accounts[0][0], accounts[1][0]
        c = Comunidad.objects.create(nombre='Encuentros del sur', descripcion='Comunidad de demostración para compartir cultura y vida al aire libre.', estado='APROBADO', autor=author)
        places = []
        for name, zone, lat, lng in [('Costanera de Puerto Montt', 'puerto-montt', -41.4717, -72.9369), ('Costanera de Puerto Varas', 'puerto-varas', -41.3195, -72.9811)]:
            places.append(Lugar.objects.create(nombre=name, descripcion='Punto de encuentro ficticio para la evaluación.', zona=zone, latitud=lat, longitud=lng, estado='APROBADO', autor=author))
        for i, (title, category, description) in enumerate([
            ('Caminata junto al lago', 'Aire libre', 'Recorrido comunitario de demostración por la costanera. Lleva agua y ropa para la lluvia.'),
            ('Taller de fotografía local', 'Cultura', 'Un encuentro ficticio para compartir miradas de nuestra ciudad.'),
            ('Feria de intercambio vecinal', 'Ferias y Comunidad', 'Actividad ficticia para intercambiar libros, plantas e ideas.'),
            ('Encuentro de trote comunitario', 'Deportes', 'Recorrido de demostración a ritmo tranquilo, sin competición.')]):
            p = places[i % 2]
            start = (timezone.now() + timedelta(days=i+5)).replace(hour=17, minute=0, second=0, microsecond=0)
            a = Actividad.objects.create(titulo=title, descripcion=description, categoria=category, zona=p.zona, latitud=p.latitud + i*.002, longitud=p.longitud, fecha_hora=start, fin=start+timedelta(hours=2), estado='APROBADO', comunidad=c, lugar=p, creado_por=author)
            Auditoria.objects.create(tipo='actividad', objeto_id=a.pk, responsable=mod, decision='APROBADO', motivo='Datos ficticios preparados para evaluación')
        Publicacion.objects.create(comunidad=c, autor=author, texto='¿Qué actividad les gustaría compartir este mes? Este foro contiene únicamente datos de demostración.')
        Comunidad.objects.create(nombre='Talleres del barrio', descripcion='Propuesta ficticia pendiente de revisión.', autor=author)
        for user, password in accounts:
            self.stdout.write(f'{user.username}: {password}')
        self.stdout.write(self.style.SUCCESS('Datos demo creados. Guarda las claves localmente; no las publiques.'))
