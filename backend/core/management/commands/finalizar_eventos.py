from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Actividad


class Command(BaseCommand):
    help = 'Finaliza eventos vencidos; la consulta pública ya los excluye aunque no se ejecute esta tarea.'

    def handle(self, *args, **kwargs):
        total = Actividad.objects.filter(estado='APROBADO', todo_el_ano=False, fin__lte=timezone.now()).update(estado='FINALIZADO')
        self.stdout.write(f'{total} eventos finalizados')
