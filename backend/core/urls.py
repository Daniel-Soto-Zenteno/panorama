from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.home, name='home'),
    path('api/csrf/', v.csrf_view), path('api/session/', v.session_status_view),
    path('api/login/', v.login_view), path('api/logout/', v.logout_view),
    path('api/activities/', v.actividades_collection_view),
    path('account/<str:accion>/', v.cuenta, name='cuenta'),
    path('logout/', v.logout_view, name='logout'), path('profile/', v.perfil, name='perfil'),
    path('communities/', v.comunidades, name='comunidades'), path('community/<int:pk>/', v.foro, name='foro'),
    path('propose/<str:tipo>/', v.proponer, name='proponer'),
    path('activity/<int:pk>/', v.detalle, name='detalle'),
    path('activity/<int:pk>/edit/', v.proponer, {'tipo': 'actividad'}, name='editar'),
    path('activity/<int:pk>/rsvp/', v.rsvp, name='rsvp'), path('activity/<int:pk>/cancel/', v.cancelar, name='cancelar'),
    path('activity/<int:pk>/badge/', v.distintivo, name='distintivo'), path('mine/', v.mis_actividades, name='mis_actividades'),
    path('post/<int:pk>/comment/', v.comentar, name='comentar'), path('report/<str:tipo>/<int:pk>/', v.reportar, name='reportar'),
    path('moderation/', v.moderacion, name='moderacion'), path('moderation/<str:tipo>/<int:pk>/', v.decidir, name='decidir'),
    path('resolve/<int:pk>/', v.resolver, name='resolver'), path('privacy/', v.privacidad, name='privacidad'),
]
