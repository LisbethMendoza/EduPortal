from django.urls import path
from . import views

urlpatterns = [
    path('', views.C_Tecnico, name='reinscripcion'),
]
