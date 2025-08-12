from django.urls import path
from . import views

urlpatterns = [
    path('', views.C_Tecnico, name='reinscripcion'),
    path ('documentacion_re', views.guarda_redirige, name='documentacion_re'),
    path('buscar-estudiante/', views.buscar_estudiante, name='buscar_estudiante'),
    
]
