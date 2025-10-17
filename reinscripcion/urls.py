from django.urls import path
from . import views

urlpatterns = [
    path('', views.C_Tecnico, name='reinscripcion'),
    path ('documentacion_re', views.reinscripcion_re, name='documentacion_re'),
    path('buscar-estudiante/', views.buscar_estudiante, name='buscar_estudiante'),
    path('reinscripcion_insert/', views.reinscripcion_insert, name='reinscripcion_insert'),
    path('contrato/<str:codigo>/', views.generar_contrato, name='generar_contrato'),
    

    
]
