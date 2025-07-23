from django.urls import path
from usuario import views


urlpatterns = [
    path('login/', views.login_usuario, name='login'),
    path('avisos/', views.aviso_adm, name='avisos'),
    
]
 