
from django.shortcuts import render
from avisos.models import Aviso
from django.http import JsonResponse
from .models import Estudiante
from inscripcion.models import Inscripcion
from reinscripcion.models import Reinscripcion

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


def consultar_estado(request):
    codigo = request.GET.get("codigo", "").strip()

    try:
        estudiante = Estudiante.objects.get(codigo=codigo)
    except Estudiante.DoesNotExist:
        return JsonResponse({"error": "No se encontró el estudiante."}, status=404)

    # Buscar en Reinscripción primero
    reinscripcion = Reinscripcion.objects.filter(estudiante=estudiante).order_by("-fecha_reinscripcion").first()
    if reinscripcion:
        return JsonResponse({
            "estado": reinscripcion.estado,
            "tipo": "Reinscripción",
            "periodo": reinscripcion.periodo_escolar,
            "comentario": reinscripcion.comentario or ""
            
        })

    # Si no existe, buscar en Inscripción
    inscripcion = Inscripcion.objects.filter(estudiante=estudiante).order_by("-fecha_inscripcion").first()
    if inscripcion:
        return JsonResponse({
            "estado": inscripcion.estado,
            "tipo": "Inscripción",
            "periodo": inscripcion.periodo_escolar,
            "comentario": inscripcion.comentario or "" 
        })

    return JsonResponse({"error": "El estudiante no tiene inscripción registrada."}, status=404)