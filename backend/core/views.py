import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import Actividad


def _validar_coordenadas(lat, lng):
    try:
        lat_val = float(lat)
        lng_val = float(lng)
    except (TypeError, ValueError):
        return None, None, "Latitud y longitud deben ser números válidos."

    if not (-90.0 <= lat_val <= 90.0) or not (-180.0 <= lng_val <= 180.0):
        return None, None, "Coordenadas fuera de rango geográfico válido."

    return lat_val, lng_val, None


def _parsear_fecha_opcional(fecha_raw):
    if not fecha_raw:
        return None, None
    parsed = parse_datetime(str(fecha_raw))
    if parsed is None:
        return None, "Formato de fecha y hora inválido."
    return parsed, None


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
        "all_year": act.todo_el_ano,
        "schedule": act.horario,
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

    lat, lng, coord_err = _validar_coordenadas(data.get("lat"), data.get("lng"))
    if coord_err:
        return JsonResponse({"error": coord_err}, status=400)

    categoria = data.get("category") or Actividad.Categoria.FERIAS
    if categoria not in Actividad.Categoria.values:
        return JsonResponse({"error": "Categoría no válida."}, status=400)

    zona = data.get("zone") or Actividad.Zona.PUERTO_MONTT
    if zona not in Actividad.Zona.values:
        return JsonResponse({"error": "Zona no válida."}, status=400)

    todo_el_ano = bool(data.get("all_year", False))
    horario = (data.get("schedule") or "").strip()

    if todo_el_ano:
        fecha_dt = None
    else:
        fecha_dt, date_err = _parsear_fecha_opcional(data.get("date"))
        if date_err:
            return JsonResponse({"error": date_err}, status=400)

    act = Actividad.objects.create(
        titulo=titulo,
        categoria=categoria,
        zona=zona,
        latitud=lat,
        longitud=lng,
        todo_el_ano=todo_el_ano,
        horario=horario,
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
        if data["category"] not in Actividad.Categoria.values:
            return JsonResponse({"error": "Categoría no válida."}, status=400)
        act.categoria = data["category"]

    if "zone" in data and data["zone"]:
        if data["zone"] not in Actividad.Zona.values:
            return JsonResponse({"error": "Zona no válida."}, status=400)
        act.zona = data["zone"]

    if "lat" in data or "lng" in data:
        lat_input = data["lat"] if "lat" in data else act.latitud
        lng_input = data["lng"] if "lng" in data else act.longitud
        lat, lng, coord_err = _validar_coordenadas(lat_input, lng_input)
        if coord_err:
            return JsonResponse({"error": coord_err}, status=400)
        act.latitud = lat
        act.longitud = lng

    if "description" in data:
        act.descripcion = (data.get("description") or "").strip()

    if "featured" in data:
        act.destacado = bool(data["featured"])

    if "all_year" in data:
        act.todo_el_ano = bool(data["all_year"])
        if act.todo_el_ano:
            act.fecha_hora = None

    if "schedule" in data:
        act.horario = (data.get("schedule") or "").strip()

    if "date" in data and not act.todo_el_ano:
        fecha_dt, date_err = _parsear_fecha_opcional(data.get("date"))
        if date_err:
            return JsonResponse({"error": date_err}, status=400)
        act.fecha_hora = fecha_dt

    act.save()
    return JsonResponse({"activity": _serialize_actividad(act)})