from django.urls import path #Poner esto en los demas form
from usuario import views
from . import views
from django.urls import path

urlpatterns = [
    path('login/', views.login_usuario, name='login'), #Poner esto en los demas form
    path('avisos/', views.aviso_adm, name='avisos'), #Poner esto en los demas form
    path('upload_documento/', views.upload_documento, name='upload_documento'),
    path('listar_documentos/', views.listar_documentos, name='listar_documentos'),

]





