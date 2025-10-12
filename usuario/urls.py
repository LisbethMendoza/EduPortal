from django.urls import path
from . import views
from usuario import views

urlpatterns = [
    path('insertar_usuario/', views.usuario_form, name='insertar_usuario'),
    path('obtener/', views.obtener_usuario, name='obtener_usuario'),
    path('login/', views.login_usuario, name='login'),
    path('pagina_admin', views.pagina_admin, name='pagina_admin'),
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('Revision_E/', views.revision_estudiantes, name='Revision_E'),
    path('avisos/', views.aviso_adm, name='avisos'),
    path('chats/', views.chat, name='chats'),
    path('cantidad_estudiantes/', views.cantidad_estudiantes, name='cantidad_estudiantes'),
    path('logout/', views.logout_usuario, name='logout'),
    path('recuperar/', views.recuperar, name='recuperar'),
    path('enviar-enlace/', views.enviar_enlace, name='enviar_enlace'),
    path('restablecer/', views.restablecer, name='restablecer'),
    path('Buscar_E/', views.Buscar_E, name='Buscar_E'),
    path('Aprobados/', views.Aprobacion, name='Aprobacion'),

]



