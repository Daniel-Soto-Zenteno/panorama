from django.core.management.base import BaseCommand
from core.models import Actividad, Comunidad


class Command(BaseCommand):
    help = 'Carga ejemplos ficticios para revisar el diseño local, sin crear cuentas.'

    def handle(self, *args, **options):
        rows = [
            ('Paseo por la costanera', 'Aire libre', 'puerto-varas', -41.318, -72.98, 'Un recorrido junto al lago para disfrutar el paisaje. Actividad ficticia de demostración.', 'Horario de ejemplo · 09:00 a 19:00', True),
            ('Básquetbol en el barrio', 'Deportes', 'puerto-montt', -41.472, -72.936, 'Una propuesta de actividad física al aire libre. Ejemplo ficticio para revisar el diseño.', 'Horario de ejemplo · Sábados 11:00', False),
            ('Encuentro de arte y oficios', 'Cultura', 'puerto-varas', -41.319, -72.984, 'Un espacio para conocer distintas expresiones creativas. Actividad ficticia de demostración.', 'Horario de ejemplo · 10:00 a 17:00', True),
            ('Feria de productores locales', 'Ferias y Comunidad', 'puerto-montt', -41.48, -72.96, 'Una propuesta de encuentro de la comunidad. Este ejemplo no anuncia una feria real.', 'Horario de ejemplo · Domingos 10:00', False),
            ('Una tarde entre libros', 'Cultura', 'puerto-montt', -41.466, -72.93, 'Una propuesta tranquila para compartir lecturas. Actividad ficticia de demostración.', 'Horario de ejemplo · Viernes 16:00', False),
            ('Pedalea junto al lago', 'Deportes', 'puerto-varas', -41.325, -72.97, 'Un recorrido de ejemplo para explorar el borde del lago. No corresponde a una convocatoria real.', 'Horario de ejemplo · 09:30 a 12:00', False),
            ('Explora los senderos', 'Aire libre', 'puerto-montt', -41.454, -72.91, 'Una propuesta para caminar y conocer el entorno. Ejemplo ficticio de diseño.', 'Horario de ejemplo · 09:00 a 18:00', False),
        ]
        for title, category, zone, lat, lng, description, schedule, featured in rows:
            Actividad.objects.get_or_create(titulo=title, defaults=dict(categoria=category,zona=zone,latitud=lat,longitud=lng,descripcion=description,horario=schedule,todo_el_ano=True,destacado=featured,es_ejemplo=True))
        Actividad.objects.filter(titulo__in=[r[0] for r in rows], creado_por__isnull=True).update(es_ejemplo=True)
        groups = [
            ('Deportes', 'Deportes', 'Encuentra con quién practicar, comparte encuentros deportivos y conversa sobre actividades en Puerto Montt y Puerto Varas.'),
            ('Arte y cultura', 'Cultura', 'Lectura, arte, talleres y encuentros para compartir lo que nos gusta.'),
            ('Aire libre', 'Aire libre', 'Caminatas, paseos y lugares para disfrutar el entorno de nuestras ciudades.'),
            ('Ferias y barrio', 'Ferias y Comunidad', 'Ferias, iniciativas locales y actividades para encontrarnos como comunidad.'),
        ]
        for name, category, description in groups:
            group, _ = Comunidad.objects.get_or_create(nombre=name, defaults=dict(categoria=category, descripcion=description, aprobado=True))
            # Solo los ejemplos identificados: no mover publicaciones reales ni independientes del usuario.
            titles = {'Deportes': ['Básquetbol en el barrio', 'Pedalea junto al lago'], 'Cultura': ['Una tarde entre libros'], 'Aire libre': ['Explora los senderos'], 'Ferias y Comunidad': ['Feria de productores locales']}[category]
            Actividad.objects.filter(titulo__in=titles, creado_por__isnull=True, comunidad__isnull=True).update(comunidad=group)
        self.stdout.write(self.style.SUCCESS('Ejemplos y comunidades de diseño preparados. No son eventos reales.'))
