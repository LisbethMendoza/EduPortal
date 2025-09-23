from django.urls import path
from . import views

urlpatterns = [
    path("configurar_cupos/", views.configurar_cupos, name="configurar_cupos"),
    
]
