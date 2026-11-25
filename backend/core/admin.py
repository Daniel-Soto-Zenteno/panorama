from django.contrib import admin
from .models import Actividad, Comunidad, Conversacion, Perfil, Guardado, Reporte

@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'zona', 'estado', 'destacado', 'creado_por']
    list_filter = ['estado', 'destacado', 'categoria', 'zona']
    search_fields = ['titulo', 'descripcion']

@admin.register(Comunidad)
class ComunidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'aprobado', 'rechazada']
    list_filter = ['aprobado', 'rechazada', 'categoria']

admin.site.register([Conversacion, Perfil, Guardado, Reporte])
