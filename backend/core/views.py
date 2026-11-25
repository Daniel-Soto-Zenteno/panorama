import json
from datetime import date, time
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction, IntegrityError
from django.db.models import F, Q, Prefetch
from django.http import JsonResponse, Http404
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from .models import *
from .forms import RegistroForm, PerfilForm, ComunidadForm, LugarForm, ActividadForm, TextoForm, MotivoForm
from .services import publicas, visible, moderar, asistir, CONTENIDOS


def filtradas(request):
    qs = publicas().select_related('comunidad', 'lugar')
    for param, field in [('zone', 'zona'), ('category', 'categoria')]:
        value = request.GET.get(param)
        if value and value != 'all':
            qs = qs.filter(**{field: value})
    if request.GET.get('q'):
        qs = qs.filter(titulo__icontains=request.GET['q'])
    try:
        if request.GET.get('date'):
            d = date.fromisoformat(request.GET['date'])
            qs = qs.filter(Q(todo_el_ano=True) | Q(fecha_hora__date__lte=d, fin__date__gte=d))
        for param, lookup, habitual in [('from', 'fecha_hora__time__gte', 'hora_inicio__gte'), ('to', 'fecha_hora__time__lte', 'hora_inicio__lte')]:
            if request.GET.get(param):
                t = time.fromisoformat(request.GET[param])
                qs = qs.filter(Q(todo_el_ano=True, **{habitual: t}) | Q(todo_el_ano=False, **{lookup: t}))
        if request.GET.get('from') and request.GET.get('to') and request.GET['from'] > request.GET['to']:
            raise ValueError
    except ValueError:
        raise ValidationError('Fecha u hora de filtro inválida.')
    return qs


def serializar(a):
    return {'id': a.pk, 'title': a.titulo, 'category': a.categoria, 'zone': a.zona, 'lat': a.latitud, 'lng': a.longitud,
            'date': timezone.localtime(a.fecha_hora).isoformat() if a.fecha_hora else '', 'description': a.descripcion,
            'all_year': a.todo_el_ano, 'schedule': a.horario, 'featured': a.destacado, 'url': f'/activity/{a.pk}/'}


def home(request):
    try:
        acts = list(filtradas(request))
    except ValidationError as e:
        messages.error(request, e.messages[0])
        acts = []
    return render(request, 'index.html', {'activities': acts, 'map_data': [serializar(a) for a in acts], 'zones': Actividad.Zona.choices, 'categories': Actividad.Categoria.choices})


@require_GET
def csrf_view(request):
    return JsonResponse({'csrfToken': get_token(request)})


@require_GET
def session_status_view(request):
    return JsonResponse({'authenticated': request.user.is_authenticated, 'username': request.user.username if request.user.is_authenticated else None, 'is_admin': request.user.is_staff})


@require_POST
def login_view(request):
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError
        user = authenticate(request, username=data.get('username'), password=data.get('password'))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'JSON inválido.'}, status=400)
    if user is None:
        return JsonResponse({'error': 'Credenciales inválidas.'}, status=401)
    login(request, user)
    return JsonResponse({'authenticated': True, 'username': user.username, 'is_admin': user.is_staff})


@require_POST
def logout_view(request):
    logout(request)
    if request.path.startswith('/api/'):
        return JsonResponse({'authenticated': False})
    return redirect('home')


@require_GET
def actividades_collection_view(request):
    try:
        return JsonResponse({'activities': [serializar(a) for a in filtradas(request)]})
    except ValidationError as e:
        return JsonResponse({'error': e.messages[0]}, status=400)


def cuenta(request, accion):
    if accion not in ['register', 'login']:
        raise Http404
    cls = RegistroForm if accion == 'register' else AuthenticationForm
    form = cls(data=request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                user = form.save() if accion == 'register' else form.get_user()
                if accion == 'register':
                    Perfil.objects.create(usuario=user, nombre=user.username)
                login(request, user)
            return redirect('home')
        except IntegrityError:
            form.add_error('email', 'Este correo ya está registrado.')
    return render(request, 'form.html', {'form': form, 'title': 'Crear cuenta' if accion == 'register' else 'Iniciar sesión', 'submit': 'Continuar'})


@login_required
def perfil(request):
    obj, _ = Perfil.objects.get_or_create(usuario=request.user, defaults={'nombre': request.user.username})
    form = PerfilForm(request.POST if request.method == 'POST' else None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Perfil actualizado.')
        return redirect('perfil')
    return render(request, 'form.html', {'form': form, 'title': 'Mi perfil', 'submit': 'Guardar cambios'})


def comunidades(request):
    return render(request, 'comunidades.html', {'comunidades': Comunidad.objects.filter(estado='APROBADO'), 'lugares': Lugar.objects.filter(estado='APROBADO')})


@login_required
def proponer(request, tipo, pk=None):
    cls = {'actividad': ActividadForm, 'comunidad': ComunidadForm, 'lugar': LugarForm}.get(tipo)
    if not cls:
        raise Http404
    obj = None
    if pk:
        obj = get_object_or_404(Actividad, pk=pk, creado_por=request.user)
        if obj.estado in ['CANCELADO', 'FINALIZADO', 'RETIRADO'] or (obj.fin and obj.fin <= timezone.now()):
            raise PermissionDenied('El evento ya no puede editarse.')
    old_date, old_place, old_end, old_year = (obj.fecha_hora, obj.lugar_id, obj.fin, obj.todo_el_ano) if obj else (None, None, None, None)
    form = cls(request.POST if request.method == 'POST' else None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        if tipo == 'actividad':
            item.creado_por = request.user
            item.zona, item.latitud, item.longitud = item.lugar.zona, item.lugar.latitud, item.lugar.longitud
            if not obj or (old_date, old_place, old_end, old_year) != (item.fecha_hora, item.lugar_id, item.fin, item.todo_el_ano) or item.estado == 'RECHAZADO':
                item.estado = 'PENDIENTE'
        else:
            item.autor = request.user
        item.save()
        messages.success(request, 'Propuesta guardada. Los cambios de fecha o lugar requieren aprobación.')
        return redirect('mis_actividades')
    return render(request, 'form.html', {'form': form, 'title': ('Editar evento' if pk else f'Proponer {tipo}'), 'submit': 'Guardar propuesta'})


def detalle(request, pk):
    obj = get_object_or_404(Actividad.objects.select_related('comunidad', 'lugar', 'creado_por'), pk=pk)
    if not visible(obj) and not (request.user.is_staff or request.user == obj.creado_por):
        raise Http404
    Actividad.objects.filter(pk=pk).update(aperturas=F('aperturas') + 1)
    joined = request.user.is_authenticated and obj.asistencias.filter(usuario=request.user).exists()
    return render(request, 'detalle.html', {'activity': obj, 'joined': joined, 'total': obj.asistencias.count(), 'public': visible(obj)})


@login_required
@require_POST
def rsvp(request, pk):
    try:
        asistir(request.user, pk, request.POST.get('cancelar') == '1')
        messages.success(request, 'Tu intención de asistencia se actualizó. No reserva cupo.')
    except (ValidationError, Actividad.DoesNotExist) as e:
        messages.error(request, e.messages[0] if isinstance(e, ValidationError) else 'Evento inexistente.')
    return redirect('detalle', pk=pk)


@login_required
def mis_actividades(request):
    return render(request, 'mis_actividades.html', {'activities': Actividad.objects.filter(creado_por=request.user), 'propuestas': list(Comunidad.objects.filter(autor=request.user)) + list(Lugar.objects.filter(autor=request.user))})


@login_required
@require_POST
def cancelar(request, pk):
    obj = get_object_or_404(Actividad, pk=pk, creado_por=request.user)
    if obj.estado not in ['CANCELADO', 'RETIRADO', 'FINALIZADO']:
        obj.estado = 'CANCELADO'
        obj.save(update_fields=['estado'])
    return redirect('mis_actividades')


def foro(request, pk):
    comunidad = get_object_or_404(Comunidad, pk=pk, estado='APROBADO')
    form = TextoForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            raise PermissionDenied
        if form.is_valid():
            Publicacion.objects.create(comunidad=comunidad, autor=request.user, texto=form.cleaned_data['texto'])
            return redirect('foro', pk=pk)
    posts = comunidad.publicaciones.filter(estado='APROBADO').select_related('autor').prefetch_related(Prefetch('comentarios', queryset=Comentario.objects.filter(estado='APROBADO').select_related('autor'))).order_by('-fecha')
    return render(request, 'foro.html', {'comunidad': comunidad, 'posts': posts, 'form': form})


@login_required
@require_POST
def comentar(request, pk):
    obj = get_object_or_404(Publicacion, pk=pk)
    if not visible(obj):
        raise Http404
    form = TextoForm(request.POST)
    if form.is_valid() and len(form.cleaned_data['texto']) <= 1500:
        Comentario.objects.create(publicacion=obj, autor=request.user, texto=form.cleaned_data['texto'])
    else:
        messages.error(request, 'El comentario debe contener entre 1 y 1500 caracteres.')
    return redirect('foro', pk=obj.comunidad_id)


@login_required
def reportar(request, tipo, pk):
    model = CONTENIDOS.get(tipo)
    if not model:
        raise Http404
    obj = get_object_or_404(model, pk=pk)
    if not visible(obj):
        raise Http404
    form = MotivoForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        Reporte.objects.create(tipo=tipo, objeto_id=pk, autor=request.user, motivo=form.cleaned_data['motivo'])
        messages.success(request, 'Reporte enviado. El contenido permanece visible hasta la decisión de moderación.')
        return redirect('home')
    return render(request, 'form.html', {'title': 'Reportar contenido', 'form': form, 'submit': 'Enviar reporte'})


@login_required
def moderacion(request):
    if not request.user.is_staff:
        raise PermissionDenied
    pendientes = [(tipo, obj) for tipo, model in CONTENIDOS.items() for obj in model.objects.filter(estado='PENDIENTE')]
    return render(request, 'moderacion.html', {'pendientes': pendientes, 'reportes': Reporte.objects.filter(estado='ABIERTO'), 'audit': Auditoria.objects.select_related('responsable').order_by('-fecha')[:30]})


@login_required
def decidir(request, tipo, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    if tipo not in CONTENIDOS:
        raise Http404
    obj = get_object_or_404(CONTENIDOS[tipo], pk=pk)
    form = MotivoForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            moderar(request.user, tipo, pk, request.POST.get('decision'), form.cleaned_data['motivo'])
            messages.success(request, 'Decisión registrada con auditoría.')
            return redirect('moderacion')
        except ValidationError as e:
            form.add_error(None, e)
    return render(request, 'decision.html', {'form': form, 'obj': obj, 'tipo': tipo})


@login_required
def resolver(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    obj = get_object_or_404(Reporte, pk=pk)
    form = MotivoForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            obj = Reporte.objects.select_for_update().get(pk=pk)
            if obj.estado != 'ABIERTO':
                raise PermissionDenied('El reporte ya está cerrado.')
            obj.estado, obj.resolucion = 'CERRADO', form.cleaned_data['motivo']
            obj.responsable, obj.resuelto_en = request.user, timezone.now()
            obj.save()
            Auditoria.objects.create(tipo='reporte', objeto_id=pk, responsable=request.user, decision='CERRADO', motivo=obj.resolucion)
        return redirect('moderacion')
    return render(request, 'form.html', {'title': 'Resolver reporte sin retiro automático', 'form': form, 'submit': 'Cerrar reporte'})


@login_required
@require_POST
def distintivo(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied
    with transaction.atomic():
        obj = get_object_or_404(Actividad.objects.select_for_update(), pk=pk)
        target = request.POST.get('target', 'evento')
        if target not in ['evento', 'organizador']:
            raise PermissionDenied
        if target == 'evento':
            obj.destacado = not obj.destacado
            obj.save(update_fields=['destacado'])
        elif obj.creado_por:
            perfil, _ = Perfil.objects.get_or_create(usuario=obj.creado_por, defaults={'nombre': obj.creado_por.username})
            perfil.verificado = not perfil.verificado
            perfil.save()
        Auditoria.objects.create(tipo='actividad', objeto_id=pk, responsable=request.user, decision='DISTINTIVO', motivo=f'Cambio de distintivo simulado de {target}')
    return redirect('detalle', pk=pk)


def privacidad(request):
    return render(request, 'privacidad.html')
