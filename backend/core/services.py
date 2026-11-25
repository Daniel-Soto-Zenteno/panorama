from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from .models import Actividad, Comunidad, Lugar, Publicacion, Comentario, Reporte, Auditoria, Asistencia

CONTENIDOS = {'actividad': Actividad, 'comunidad': Comunidad, 'lugar': Lugar, 'publicacion': Publicacion, 'comentario': Comentario}


def publicas():
    return Actividad.objects.filter(estado='APROBADO', comunidad__estado='APROBADO', lugar__estado='APROBADO').filter(Q(todo_el_ano=True) | Q(fin__gt=timezone.now()))


def visible(obj):
    if isinstance(obj, Actividad):
        return publicas().filter(pk=obj.pk).exists()
    if isinstance(obj, Publicacion):
        return obj.estado == 'APROBADO' and obj.comunidad.estado == 'APROBADO'
    if isinstance(obj, Comentario):
        return obj.estado == 'APROBADO' and visible(obj.publicacion)
    return obj.estado == 'APROBADO'


@transaction.atomic
def moderar(usuario, tipo, pk, decision, motivo):
    if not usuario.is_staff:
        raise PermissionDenied
    if not motivo.strip():
        raise ValidationError('Debes explicar el motivo.')
    obj = CONTENIDOS[tipo].objects.select_for_update().get(pk=pk)
    allowed = {'PENDIENTE': ['APROBADO', 'RECHAZADO'], 'APROBADO': ['RETIRADO']}
    if decision not in allowed.get(obj.estado, []):
        raise ValidationError('Transición de estado no permitida.')
    if decision == 'APROBADO' and isinstance(obj, Actividad):
        obj.full_clean()
        if not obj.todo_el_ano and obj.fin <= timezone.now():
            raise ValidationError('El evento ya finalizó.')
    obj.estado = decision
    obj.save()
    Auditoria.objects.create(
        tipo=tipo, objeto_id=pk, responsable=usuario,
        decision=decision, motivo=motivo,
    )
    return obj


@transaction.atomic
def asistir(usuario, pk, cancelar=False):
    if not usuario.is_authenticated:
        raise PermissionDenied
    obj = Actividad.objects.select_for_update().get(pk=pk)
    if cancelar:
        Asistencia.objects.filter(usuario=usuario, actividad=obj).delete()
    else:
        if not visible(obj) or (
            not obj.todo_el_ano and obj.fecha_hora <= timezone.now()
        ):
            raise ValidationError('El evento no admite nuevas asistencias.')
        Asistencia.objects.get_or_create(usuario=usuario, actividad=obj)
    return obj.asistencias.count()
