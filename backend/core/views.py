import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import Actividad


def home(request):
    return render(request, "index.html")


@require_GET
def csrf_view(request):
    return JsonResponse({"csrfToken": get_token(request)})


@require_GET
def session_status_view(request):
    user = request.user
    if user.is_authenticated:
        return JsonResponse({
            "authenticated": True,
            "username": user.username,
            "is_admin": bool(user.is_staff or user.is_superuser),
        })
    return JsonResponse({
        "authenticated": False,
        "username": None,
        "is_admin": False,
    })


@require_POST
def login_view(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return JsonResponse({"error": "Debes ingresar usuario y contraseña."}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Credenciales inválidas."}, status=401)

    login(request, user)
    return JsonResponse({
        "authenticated": True,
        "username": user.username,
        "is_admin": bool(user.is_staff or user.is_superuser),
    })


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"authenticated": False})


def _serialize_actividad(act):
    return {
        "id": act.id,
        "title": act.titulo,
        "category": act.categoria,
        "zone": act.zona,
        "lat": act.latitud,
        "lng": act.longitud,
        "date": act.fecha_hora.strftime("%Y-%m-%dT%H:%M") if act.fecha_hora else "",
        "description": act.descripcion,
        "featured": act.destacado,
    }


@require_http_methods(["GET", "POST"])
def actividades_collection_view(request):
    if request.method == "GET":
        qs = Actividad.objects.all()
        zona = request.GET.get("zone")
        categoria = request.GET.get("category")

        if zona and zona != "all":
            qs = qs.filter(zona=zona)
        if categoria and categoria != "all":
            qs = qs.filter(categoria=categoria)

        return JsonResponse({
            "activities": [_serialize_actividad(a) for a in qs]
        })

    # POST: solo usuarios admin (staff o superuser)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Debes iniciar sesión."}, status=401)
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({"error": "Solo un administrador puede añadir actividades."}, status=403)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    titulo = (data.get("title") or "").strip()
    if not titulo:
        return JsonResponse({"error": "El título es obligatorio."}, status=400)

    try:
        lat = float(data.get("lat"))
        lng = float(data.get("lng"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Latitud y longitud deben ser números válidos."}, status=400)

    fecha_raw = data.get("date")
    fecha_dt = parse_datetime(fecha_raw) if fecha_raw else None

    act = Actividad.objects.create(
        titulo=titulo,
        categoria=data.get("category") or Actividad.Categoria.FERIAS,
        zona=data.get("zone") or Actividad.Zona.PUERTO_MONTT,
        latitud=lat,
        longitud=lng,
        fecha_hora=fecha_dt,
        descripcion=(data.get("description") or "").strip(),
        destacado=bool(data.get("featured", False)),
        creado_por=request.user,
    )

    return JsonResponse({"activity": _serialize_actividad(act)}, status=201)


@require_http_methods(["PUT", "PATCH", "DELETE"])
def actividad_detail_view(request, actividad_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Debes iniciar sesión."}, status=401)
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({"error": "Solo un administrador puede modificar o eliminar actividades."}, status=403)

    try:
        act = Actividad.objects.get(pk=actividad_id)
    except Actividad.DoesNotExist:
        return JsonResponse({"error": "Actividad no encontrada."}, status=404)

    if request.method == "DELETE":
        act.delete()
        return JsonResponse({"deleted": True, "id": actividad_id})

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    if "title" in data:
        titulo = (data.get("title") or "").strip()
        if not titulo:
            return JsonResponse({"error": "El título no puede estar vacío."}, status=400)
        act.titulo = titulo

    if "category" in data and data["category"]:
        act.categoria = data["category"]

    if "zone" in data and data["zone"]:
        act.zona = data["zone"]

    if "lat" in data and "lng" in data:
        try:
            act.latitud = float(data["lat"])
            act.longitud = float(data["lng"])
        except (TypeError, ValueError):
            return JsonResponse({"error": "Coordenadas inválidas."}, status=400)

    if "date" in data:
        act.fecha_hora = parse_datetime(data["date"]) if data["date"] else None

    if "description" in data:
        act.descripcion = (data.get("description") or "").strip()

    if "featured" in data:
        act.destacado = bool(data["featured"])

    act.save()
    return JsonResponse({"activity": _serialize_actividad(act)})