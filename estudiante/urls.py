from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_estudiante, name='inicio_estudiante'),
]