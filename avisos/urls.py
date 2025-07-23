from django.urls import path #Poner esto en los demas form
from usuario import views #Poner esto en los demas form
from avisos import views


urlpatterns = [
    path('login/', views.login_usuario, name='login'), #Poner esto en los demas form
    path('avisos/', views.aviso_adm, name='avisos'), #Poner esto en los demas form
    path('Insertar_aviso/', views.Insertar_aviso, name='Insertar_aviso'),
    path('obtener_aviso/', views.obtener_aviso_por_titulo, name='obtener_aviso'),
    path('eliminar_aviso/', views.eliminar_aviso, name='eliminar_aviso'),
     
]
 