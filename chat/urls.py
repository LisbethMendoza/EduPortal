from django.urls import path #Poner esto en los demas form
from usuario import views
from . import views

urlpatterns = [
    path('login/', views.login_usuario, name='login'), #Poner esto en los demas form
    path('avisos/', views.aviso_adm, name='avisos'), #Poner esto en los demas form
    path('chat/', views.agregar_pregunta, name='agregar_pregunta'),
    path('obtener_pregunta/<int:id_chat>/', views.obtener_pregunta, name='obtener_pregunta'),
    path('chat/cargar_tbody/', views.cargar_tbody, name='cargar_tbody'),

]




 
 