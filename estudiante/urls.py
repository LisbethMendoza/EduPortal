from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_estudiante, name='inicio_estudiante'),
    path('registro', views.Link_resgistro, name='registro'),
    path('Csolicitud', views.Consulta_Solicitud, name='Csolicitud'),
    path('inscripcion', views.Link_inscripcion, name='inscripcion'),
    path('reinscripcion', views.Link_reinscripcion, name='reinscripcion'),
    path('Consulta_avisos', views.Consulta_avisos, name='Consulta_avisos'),
    path("consultar_estado", views.consultar_estado, name="consultar_estado"),
]