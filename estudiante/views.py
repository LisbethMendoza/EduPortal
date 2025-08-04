
from django.shortcuts import render
from avisos.models import Aviso
from django.http import JsonResponse


def pagina_estudiante(request):
    return render(request, 'P_Estudiante.html')

def Link_resgistro(request):
    return render(request, 'registro.html')

def Consulta_Solicitud(request):
    return render(request, 'C_solicitud_E.html')

def Link_inscripcion(request):
    return render(request, 'inscripcion.html')

def Link_reinscripcion(request):
    return render(request, 'reinscripcion.html')


def Consulta_avisos(request):
    avisos = Aviso.objects.filter(estado="activo").values('titulo', 'descripcion', 'fecha_publi', 'fecha_fin')
    return JsonResponse(list(avisos), safe=False)