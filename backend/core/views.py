import io
import json
import uuid
from PIL import Image, ImageOps, UnidentifiedImageError
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import FileResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from .models import Actividad, Comunidad, Conversacion, Perfil, Guardado, Reporte


def error(text, status=400):
    return JsonResponse({'error': text}, status=status)


def admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def visible_posts(user):
    qs = Actividad.objects.select_related('creado_por', 'creado_por__perfil', 'comunidad').prefetch_related('comentarios')
    if admin(user):
        return qs
    public = Q(estado='published') & (Q(comunidad__isnull=True) | Q(comunidad__aprobado=True))
    return qs.filter(public | Q(creado_por=user)) if user.is_authenticated else qs.filter(public)


def body(request):
    data = json.loads(request.body or '{}')
    if not isinstance(data, dict):
        raise ValueError('Solicitud inválida.')
    return data


def home(request):
    assets = [settings.PROJECT_ROOT / 'frontend' / name for name in ('css/panorama.css', 'js/panorama.js')]
    version = max((path.stat().st_mtime_ns for path in assets if path.exists()), default=1)
    return render(request, 'index.html', {'asset_version': version})


@require_GET
def csrf_view(request):
    return JsonResponse({'csrfToken': get_token(request)})


@require_GET
def session_status_view(request):
    return session_response(request)


def session_response(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'authenticated': False, 'username': None, 'is_admin': False})
    profile, _ = Perfil.objects.get_or_create(usuario=user)
    return JsonResponse({'authenticated': True, 'username': user.username, 'user_id': user.id,
                         'display_name': profile.nombre or user.username, 'bio': profile.biografia,
                         'is_admin': bool(admin(user))})


@require_POST
def login_view(request):
    try:
        data = body(request)
        username, password = str(data.get('username', '')).strip(), str(data.get('password', ''))
    except (ValueError, TypeError):
        return error('Solicitud inválida.')
    user = authenticate(request, username=username, password=password)
    if user is None:
        return error('Usuario o contraseña incorrectos.', 401)
    login(request, user)
    return session_response(request)


@require_POST
def registro_view(request):
    try:
        data = body(request)
        username, password = str(data.get('username', '')).strip(), str(data.get('password', ''))
        user = get_user_model()(username=username)
        user.full_clean(exclude=['password'])
        validate_password(password, user)
        user.set_password(password)
        user.save()
    except ValidationError as exc:
        return error(' '.join(exc.messages))
    except IntegrityError:
        return error('Ese nombre de usuario ya existe.')
    except (ValueError, TypeError):
        return error('Solicitud inválida.')
    login(request, user)
    return session_response(request)


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({'authenticated': False})


def display_name(user):
    if not user:
        return 'Cuenta eliminada'
    try:
        return user.perfil.nombre or user.username
    except Perfil.DoesNotExist:
        return user.username


def _serialize_actividad(act, user=None):
    editable = bool(user and user.is_authenticated and (admin(user) or act.creado_por_id == user.id))
    return {'id': act.id, 'title': act.titulo, 'category': act.categoria, 'zone': act.zona,
            'lat': act.latitud, 'lng': act.longitud, 'all_year': act.todo_el_ano, 'schedule': act.horario,
            'date': timezone.localtime(act.fecha_hora).isoformat() if act.fecha_hora else '',
            'description': act.descripcion, 'featured': act.destacado, 'status': act.estado,
            'community_id': act.comunidad_id, 'community_name': act.comunidad.nombre if act.comunidad_id else None,
            'image_url': f'/api/activities/{act.id}/image/?v={int(act.actualizado_en.timestamp() * 1000000)}' if act.imagen else None,
            'author': act.creado_por.username if act.creado_por else None,
            'author_name': display_name(act.creado_por), 'author_id': act.creado_por_id,
            'comments_count': act.comentarios.count(), 'pace': act.ritmo, 'place': act.lugar,
            'kind': act.tipo, 'example': act.es_ejemplo, 'created_at': act.creado_en.isoformat(), 'can_edit': editable}


def update_post(act, data, user):
    title, description, schedule = data.get('title', act.titulo), data.get('description', act.descripcion), data.get('schedule', act.horario)
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 150:
        raise ValueError('El título debe tener entre 1 y 150 caracteres.')
    if not isinstance(description, str) or len(description) > 10000:
        raise ValueError('La descripción debe tener hasta 10000 caracteres.')
    if not isinstance(schedule, str) or len(schedule) > 120:
        raise ValueError('El horario debe tener hasta 120 caracteres.')
    category, zone = data.get('category', act.categoria), data.get('zone', act.zona)
    if category not in Actividad.Categoria.values or zone not in Actividad.Zona.values:
        raise ValueError('Categoría o ciudad no válida.')
    try:
        lat, lng = float(data.get('lat', act.latitud)), float(data.get('lng', act.longitud))
    except (ValueError, TypeError):
        raise ValueError('Elige una ubicación en el mapa.')
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise ValueError('Coordenadas fuera de rango.')
    community_id, community = data.get('community_id', act.comunidad_id), None
    if community_id not in (None, ''):
        try:
            community = Comunidad.objects.get(pk=int(community_id), aprobado=True)
        except (ValueError, TypeError, Comunidad.DoesNotExist):
            raise ValueError('Elige una comunidad publicada.')
        if community.categoria != category:
            raise ValueError('La categoría debe coincidir con la de la comunidad.')
    all_year = data.get('all_year', act.todo_el_ano)
    if not isinstance(all_year, bool):
        raise ValueError('Disponibilidad no válida.')
    kind = data.get('kind', act.tipo)
    if kind not in ('event', 'place') or (kind == 'place' and not all_year):
        raise ValueError('Un lugar de encuentro debe tener disponibilidad habitual.')
    act.tipo = kind
    raw_date = data.get('date', act.fecha_hora.isoformat() if act.fecha_hora else '')
    dt = None if all_year or not raw_date else parse_datetime(str(raw_date))
    if raw_date and not all_year and dt is None:
        raise ValueError('Fecha no válida.')
    if dt and timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    pace, place = data.get('pace', act.ritmo), data.get('place', act.lugar)
    if pace not in ('active', 'calm') or not isinstance(place, str) or len(place) > 150:
        raise ValueError('Ritmo o lugar no válido.')
    act.ritmo, act.lugar = pace, place.strip()
    act.titulo, act.descripcion, act.horario = title.strip(), description.strip(), schedule.strip()
    act.categoria, act.zona, act.latitud, act.longitud = category, zone, lat, lng
    act.comunidad, act.todo_el_ano, act.fecha_hora = community, all_year, dt
    if admin(user):
        if 'featured' in data:
            act.destacado = data['featured'] is True
        state = data.get('status', act.estado or 'published')
        if state not in ('published', 'pending', 'rejected'):
            raise ValueError('Estado no válido.')
        act.estado = state
    else:
        act.destacado, act.estado = False, 'pending'


@require_http_methods(['GET', 'POST'])
def actividades_collection_view(request):
    if request.method == 'GET':
        qs = visible_posts(request.user)
        for param, field in [('zone', 'zona'), ('category', 'categoria')]:
            value = request.GET.get(param)
            if value and value != 'all':
                qs = qs.filter(**{field: value})
        return JsonResponse({'activities': [_serialize_actividad(a, request.user) for a in qs]})
    if not request.user.is_authenticated:
        return error('Inicia sesión para publicar.', 401)
    try:
        act = Actividad(creado_por=request.user)
        update_post(act, body(request), request.user)
        act.save()
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    return JsonResponse({'activity': _serialize_actividad(act, request.user)}, status=201)


@require_http_methods(['PATCH', 'PUT', 'DELETE'])
def actividad_detail_view(request, actividad_id):
    if not request.user.is_authenticated:
        return error('Inicia sesión.', 401)
    try:
        act = Actividad.objects.get(pk=actividad_id)
    except Actividad.DoesNotExist:
        return error('Publicación no encontrada.', 404)
    if not admin(request.user) and act.creado_por_id != request.user.id:
        return error('Solo el autor o un moderador puede modificar esta publicación.', 403)
    if request.method == 'DELETE':
        act.delete()
        return JsonResponse({'deleted': True})
    try:
        data = body(request)
        update_post(act, data, request.user)
        if 'remove_image' in data and not isinstance(data['remove_image'], bool):
            raise ValueError('Solicitud de imagen no válida.')
        if data.get('remove_image'):
            act.imagen = ''
        act.save()
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    return JsonResponse({'activity': _serialize_actividad(act, request.user)})


@require_http_methods(['GET', 'POST'])
def imagen_view(request, actividad_id):
    if request.method == 'GET':
        try:
            activity = visible_posts(request.user).get(pk=actividad_id)
            if not activity.imagen:
                return error('Esta publicación no tiene imagen.', 404)
            response = FileResponse(activity.imagen.open('rb'), content_type='image/jpeg')
            response['X-Content-Type-Options'] = 'nosniff'
            response['Cache-Control'] = 'private, no-cache'
            return response
        except (Actividad.DoesNotExist, FileNotFoundError):
            return error('Imagen no encontrada.', 404)
    if not request.user.is_authenticated:
        return error('Inicia sesión.', 401)
    try:
        act = Actividad.objects.get(pk=actividad_id)
    except Actividad.DoesNotExist:
        return error('Publicación no encontrada.', 404)
    if act.creado_por_id != request.user.id and not admin(request.user):
        return error('No puedes modificar esta publicación.', 403)
    upload = request.FILES.get('image')
    if not upload or upload.size > 5 * 1024 * 1024:
        return error('Adjunta una imagen JPG, PNG o WebP de hasta 5 MB.')
    try:
        with Image.open(upload) as source:
            if source.format not in ('JPEG', 'PNG', 'WEBP') or source.width * source.height > 25000000:
                raise ValueError('Formato o tamaño no admitido.')
            source.load()
            normalized = ImageOps.exif_transpose(source)
            normalized.thumbnail((1800, 1800))
            output = io.BytesIO()
            normalized.convert('RGB').save(output, 'JPEG', quality=88)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        return error('La imagen no es válida. Usa JPG, PNG o WebP de hasta 25 megapíxeles.')
    act.imagen.save(uuid.uuid4().hex + '.jpg', ContentFile(output.getvalue()), save=False)
    if not admin(request.user):
        act.estado, act.destacado = 'pending', False
    act.save()
    return JsonResponse({'activity': _serialize_actividad(act, request.user)})


def serialize_community(c, user):
    return {'id': c.id, 'name': c.nombre, 'category': c.categoria, 'description': c.descripcion,
            'approved': c.aprobado, 'rejected': c.rechazada, 'author_id': c.creado_por_id, 'posts_count': visible_posts(user).filter(comunidad=c).count()}


@require_http_methods(['GET', 'POST'])
def comunidades_view(request):
    if request.method == 'GET':
        qs = Comunidad.objects.all() if admin(request.user) else Comunidad.objects.filter(Q(aprobado=True) | Q(creado_por=request.user)) if request.user.is_authenticated else Comunidad.objects.filter(aprobado=True)
        return JsonResponse({'communities': [serialize_community(c, request.user) for c in qs.order_by('nombre')]})
    if not request.user.is_authenticated:
        return error('Inicia sesión para crear una comunidad.', 401)
    try:
        data = body(request)
        name, description, category = data.get('name', ''), data.get('description', ''), data.get('category')
        if not isinstance(name, str) or not 3 <= len(name.strip()) <= 80 or not isinstance(description, str) or len(description) > 1200 or category not in Actividad.Categoria.values:
            return error('Ingresa un nombre de 3 a 80 caracteres, una categoría válida y una descripción de hasta 1200 caracteres.')
        c = Comunidad.objects.create(nombre=name.strip(), descripcion=description.strip(), categoria=category, creado_por=request.user, aprobado=bool(admin(request.user)))
    except IntegrityError:
        return error('Ya existe una comunidad con ese nombre.')
    except (ValueError, TypeError):
        return error('Solicitud inválida.')
    return JsonResponse({'community': serialize_community(c, request.user)}, status=201)


@require_POST
def moderar_comunidad_view(request, comunidad_id):
    if not admin(request.user):
        return error('Solo los moderadores pueden aprobar comunidades.', 403)
    try:
        c = Comunidad.objects.get(pk=comunidad_id)
        data = body(request)
        if not isinstance(data.get('approved'), bool):
            return error('Estado no válido.')
        if not isinstance(data.get('rejected', False), bool):
            return error('Estado no válido.')
        c.aprobado = data['approved']
        c.rechazada = data.get('rejected', False) if not c.aprobado else False
        c.save()
    except Comunidad.DoesNotExist:
        return error('Comunidad no encontrada.', 404)
    except (ValueError, TypeError):
        return error('Solicitud inválida.')
    return JsonResponse({'community': serialize_community(c, request.user)})


@require_http_methods(['GET', 'POST'])
def conversacion_view(request, actividad_id):
    try:
        actividad = visible_posts(request.user).get(pk=actividad_id)
    except Actividad.DoesNotExist:
        return error('Publicación no encontrada.', 404)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return error('Inicia sesión para comentar.', 401)
        try:
            data = body(request)
            text = data.get('text')
            if not isinstance(text, str) or not 1 <= len(text.strip()) <= 2000:
                return error('El comentario debe tener entre 1 y 2000 caracteres.')
        except (ValueError, TypeError):
            return error('Solicitud inválida.')
        Conversacion.objects.create(actividad=actividad, autor=request.user, texto=text.strip())
    comments = actividad.comentarios.select_related('autor')
    return JsonResponse({'comments': [{'id': c.id, 'author': c.autor.username if c.autor else 'Cuenta eliminada', 'text': c.texto, 'created_at': c.creado_en.isoformat(), 'display_name': display_name(c.autor), 'can_delete': request.user.is_authenticated and (admin(request.user) or c.autor_id == request.user.id)} for c in comments]}, status=201 if request.method == 'POST' else 200)


@require_http_methods(['DELETE'])
def eliminar_comentario_view(request, comentario_id):
    if not request.user.is_authenticated:
        return error('Inicia sesión.', 401)
    try:
        c = Conversacion.objects.get(pk=comentario_id)
    except Conversacion.DoesNotExist:
        return error('Comentario no encontrado.', 404)
    if c.autor_id != request.user.id and not admin(request.user):
        return error('No tienes permiso para eliminar este comentario.', 403)
    c.delete()
    return JsonResponse({'deleted': True})


@require_http_methods(['GET', 'PATCH'])
def perfil_view(request):
    if not request.user.is_authenticated:
        return error('Inicia sesión para ver tu perfil.', 401)
    profile, _ = Perfil.objects.get_or_create(usuario=request.user)
    if request.method == 'PATCH':
        try:
            data = body(request)
            name, bio = data.get('name', profile.nombre or request.user.username), data.get('bio', profile.biografia)
            if not isinstance(name, str) or not 2 <= len(name.strip()) <= 40 or not isinstance(bio, str) or len(bio) > 180:
                return error('El nombre debe tener de 2 a 40 caracteres y la biografía hasta 180.')
            profile.nombre, profile.biografia = name.strip(), bio.strip()
            profile.save()
        except (ValueError, TypeError):
            return error('Solicitud inválida.')
    return session_response(request)


@require_GET
def guardados_view(request):
    if not request.user.is_authenticated:
        return error('Inicia sesión para ver tus guardados.', 401)
    ids = visible_posts(request.user).filter(guardados__usuario=request.user).values_list('id', flat=True)
    return JsonResponse({'saved': list(ids)})


@require_http_methods(['POST', 'DELETE'])
def guardado_detail_view(request, actividad_id):
    if not request.user.is_authenticated:
        return error('Inicia sesión para guardar publicaciones.', 401)
    try:
        activity = visible_posts(request.user).get(pk=actividad_id)
    except Actividad.DoesNotExist:
        return error('Publicación no encontrada.', 404)
    if request.method == 'POST':
        Guardado.objects.get_or_create(usuario=request.user, actividad=activity)
    else:
        Guardado.objects.filter(usuario=request.user, actividad=activity).delete()
    return JsonResponse({'saved': request.method == 'POST'})


REPORT_REASONS = ('Contenido inapropiado', 'Datos personales', 'Información engañosa', 'Fuera de tema')


@require_http_methods(['GET', 'POST'])
def reportes_view(request):
    if not request.user.is_authenticated:
        return error('Inicia sesión para reportar contenido.', 401)
    if request.method == 'GET':
        if not admin(request.user):
            return error('Solo los moderadores pueden revisar reportes.', 403)
        reports = Reporte.objects.filter(resuelto=False).select_related('actividad', 'autor')
        return JsonResponse({'reports': [{'id': r.id, 'post_id': r.actividad_id, 'title': r.actividad.titulo,
            'reason': r.motivo, 'text': r.detalle, 'author': display_name(r.autor), 'created_at': r.creado_en.isoformat()} for r in reports]})
    try:
        data = body(request)
        post_id = int(data.get('post_id'))
        activity = visible_posts(request.user).get(pk=post_id)
        reason, text = data.get('reason'), data.get('text', '')
        if reason not in REPORT_REASONS or not isinstance(text, str) or len(text) > 500:
            return error('Elige un motivo e información adicional de hasta 500 caracteres.')
        report = Reporte.objects.filter(actividad=activity, autor=request.user, resuelto=False).first()
        if report is None:
            report = Reporte.objects.create(actividad=activity, autor=request.user, motivo=reason, detalle=text.strip())
    except (ValueError, TypeError):
        return error('Solicitud inválida.')
    except Actividad.DoesNotExist:
        return error('Publicación no encontrada.', 404)
    return JsonResponse({'id': report.id, 'received': True}, status=201)


@require_http_methods(['PATCH'])
def reporte_detail_view(request, reporte_id):
    if not admin(request.user):
        return error('Solo los moderadores pueden resolver reportes.', 403)
    try:
        report = Reporte.objects.get(pk=reporte_id)
        data = body(request)
        if data.get('resolved') is not True:
            return error('Estado de reporte no válido.')
        report.resuelto = True
        report.save(update_fields=['resuelto'])
    except Reporte.DoesNotExist:
        return error('Reporte no encontrado.', 404)
    except (ValueError, TypeError):
        return error('Solicitud inválida.')
    return JsonResponse({'resolved': True})
