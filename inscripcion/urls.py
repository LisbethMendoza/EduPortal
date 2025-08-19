
from django.urls import path
from . import views

urlpatterns = [

    path('inscripcion_p/', views.guardar_tutor, name='inscripcion_p'),
    path('buscar_estudiante/', views.buscar_estudiante_por_codigo, name='buscar_estudiante'),
    path('generar_codigo/', views.generar_codigo_api, name='generar_codigo'),
    path('documentacion/<int:inscripcion_id>/', views.subir_documentos_view, name='subir_documentos_view'),
    

    path('usuario/estudiantes_pendientes/', views.obtener_estudiantes_pendientes, name='estudiantes_pendientes'),
    path('detalle_estudiante', views.detalle_estudiante, name='detalle_estudiante'),

]
