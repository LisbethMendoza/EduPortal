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
    
    path('B_estudiantes', views.estudiantes_rechazados_todos_json, name='estudiantes_rechazados_todos_json'),
    path('actualizar_estado/inscripcion/<str:codigo>/', views.actualizar_estado_inscripcion, name='actualizar_estado_inscripcion'),
    path('actualizar_estado/reinscripcion/<str:codigo>/', views.actualizar_estado_reinscripcion, name='actualizar_estado_reinscripcion'),
    
    
    
    #------------ESTO ES PARA EL CHAT DE LOS ESTUDIANTES-----------------------
    path('api/chat-documentos/', views.chat_documentos, name='chat_documentos'),
]