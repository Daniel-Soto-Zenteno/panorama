from django.urls import path
from . import views

urlpatterns = [
    path('api/profile/', views.perfil_view),
    path('api/saved/', views.guardados_view),
    path('api/saved/<int:actividad_id>/', views.guardado_detail_view),
    path('api/reports/', views.reportes_view),
    path('api/reports/<int:reporte_id>/', views.reporte_detail_view),
    path('api/register/', views.registro_view),
    path('api/communities/', views.comunidades_view),
    path('api/communities/<int:comunidad_id>/moderate/', views.moderar_comunidad_view),
    path('api/activities/<int:actividad_id>/image/', views.imagen_view),
    path('api/comments/<int:comentario_id>/', views.eliminar_comentario_view, name='api_comment_delete'),
    path('api/activities/<int:actividad_id>/comments/', views.conversacion_view, name='api_comments'),
    path("", views.home, name="home"),
    path("api/csrf/", views.csrf_view, name="api_csrf"),
    path("api/session/", views.session_status_view, name="api_session"),
    path("api/login/", views.login_view, name="api_login"),
    path("api/logout/", views.logout_view, name="api_logout"),
    path("api/activities/", views.actividades_collection_view, name="api_activities"),
    path("api/activities/<int:actividad_id>/", views.actividad_detail_view, name="api_activity_detail"),
]
