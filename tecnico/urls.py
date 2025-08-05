from django.urls import path
from . import views

urlpatterns = [
    path('manejar_tecnico/', views.Insert_update_delete, name='manejar_tecnico'),
    
]
