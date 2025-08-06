from django.urls import path
from . import views

urlpatterns = [
    path('manejar_grado', views.Insert_update_delete, name='manejar_grado'),
    path('inscripcion/', views.C_Grado, name='inscripcion'),
]
