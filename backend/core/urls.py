from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/csrf/", views.csrf_view, name="api_csrf"),
    path("api/session/", views.session_status_view, name="api_session"),
    path("api/login/", views.login_view, name="api_login"),
    path("api/logout/", views.logout_view, name="api_logout"),
    path("api/activities/", views.actividades_collection_view, name="api_activities"),
    path("api/activities/<int:actividad_id>/", views.actividad_detail_view, name="api_activity_detail"),
]