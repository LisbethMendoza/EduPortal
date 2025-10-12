
from django.shortcuts import render
from avisos.models import Aviso
from django.http import JsonResponse
from .models import Estudiante
from inscripcion.models import Inscripcion
from reinscripcion.models import Reinscripcion
from chats.models import Documento
from django.views.decorators.csrf import csrf_exempt
import json

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

#-------------------RECHAZADOS ----------------------------------------#
def estudiantes_rechazados_todos_json(request):
    codigo = request.GET.get('codigo', '').strip()  # Obtenemos el código si viene

    # Inscripciones rechazadas
    inscripciones_queryset = Inscripcion.objects.filter(estado='Rechazado').select_related('estudiante')
    if codigo:
        inscripciones_queryset = inscripciones_queryset.filter(estudiante__codigo=codigo)

    inscripciones = []
    for insc in inscripciones_queryset:
        inscripciones.append({
            'estudiante__codigo': insc.estudiante.codigo,
            'estudiante__nombre': insc.estudiante.nombre,
            'estudiante__apellido': insc.estudiante.apellido,
            'estado': insc.estado,
            'comentario': insc.comentario,
            'documentos': {
                'cedula_tutor': insc.cedula_tutor.url if insc.cedula_tutor else None,
                'foto_estudiante': insc.foto_estudiante.url if insc.foto_estudiante else None,
                'record_notas': insc.record_notas.url if insc.record_notas else None,
                'acta_nacimiento': insc.acta_nacimiento.url if insc.acta_nacimiento else None,
                'certificado_medico': insc.certificado_medico.url if insc.certificado_medico else None,
            }
        })

    # Reinscripciones rechazadas
    reinscripciones_queryset = Reinscripcion.objects.filter(estado='Rechazado').select_related('estudiante')
    if codigo:
        reinscripciones_queryset = reinscripciones_queryset.filter(estudiante__codigo=codigo)

    reinscripciones = []
    for reins in reinscripciones_queryset:
        reinscripciones.append({
            'estudiante__codigo': reins.estudiante.codigo,
            'estudiante__nombre': reins.estudiante.nombre,
            'estudiante__apellido': reins.estudiante.apellido,
            'estado': reins.estado,
            'comentario': reins.comentario,
            'documento_pdf': reins.documento_pdf.url if reins.documento_pdf else None,
        })

    return JsonResponse({
        'inscripciones': inscripciones,
        'reinscripciones': reinscripciones
    })


@csrf_exempt
def actualizar_estado_inscripcion(request, codigo):
    if request.method == 'POST':
        data = json.loads(request.body)
        estado = data.get('estado')
        try:
            insc = Inscripcion.objects.get(estudiante__codigo=codigo)
            insc.estado = estado
            insc.save()
            return JsonResponse({'success': True})
        except Inscripcion.DoesNotExist:
            return JsonResponse({'error': 'No encontrado'}, status=404)

@csrf_exempt
def actualizar_estado_reinscripcion(request, codigo):
    if request.method == 'POST':
        data = json.loads(request.body)
        estado = data.get('estado')
        try:
            reins = Reinscripcion.objects.get(estudiante__codigo=codigo)
            reins.estado = estado
            reins.save()
            return JsonResponse({'success': True})
        except Reinscripcion.DoesNotExist:
            return JsonResponse({'error': 'No encontrado'}, status=404)




#----------------------------------CHAT INTELUGENTE NE FUNCION-------------------------------------------
from django.http import JsonResponse
from .utils import responder_con_gemini

def chat_documentos(request):
    pregunta = request.POST.get('pregunta')
    if pregunta:
        respuesta = responder_con_gemini(pregunta)
        return JsonResponse({"respuesta": respuesta})
    else:
        return JsonResponse({"error": "No se proporcionó una pregunta."}, status=400)

#------------------------------APROBADOS----------------------------------------------------------------------------#
def estudiantes_aprobados_todos_json(request):
    codigo = request.GET.get('codigo', '').strip()  
    periodo = request.GET.get('periodo', '').strip()  

    # Inscripciones aprobadas
    inscripciones_queryset = Inscripcion.objects.filter(estado='Aprobado').select_related('estudiante')
    if codigo:
        inscripciones_queryset = inscripciones_queryset.filter(estudiante__codigo=codigo)
    if periodo:
        inscripciones_queryset = inscripciones_queryset.filter(periodo_escolar=periodo)

    inscripciones = []
    for insc in inscripciones_queryset:
        inscripciones.append({
            'numero_solicitud': insc.id_inscripcion,
            'estudiante__codigo': insc.estudiante.codigo,
            'estudiante__nombre': insc.estudiante.nombre,
            'estudiante__apellido': insc.estudiante.apellido,
            'periodo_escolar': insc.periodo_escolar,
            'tipo': 'Inscripción',
            'documentos': {
                'cedula_tutor': insc.cedula_tutor.url if insc.cedula_tutor else None,
                'foto_estudiante': insc.foto_estudiante.url if insc.foto_estudiante else None,
                'record_notas': insc.record_notas.url if insc.record_notas else None,
                'acta_nacimiento': insc.acta_nacimiento.url if insc.acta_nacimiento else None,
                'certificado_medico': insc.certificado_medico.url if insc.certificado_medico else None,
            }
        })

    # Reinscripciones aprobadas
    reinscripciones_queryset = Reinscripcion.objects.filter(estado='Aprobado').select_related('estudiante')
    if codigo:
        reinscripciones_queryset = reinscripciones_queryset.filter(estudiante__codigo=codigo)
    if periodo:
        reinscripciones_queryset = reinscripciones_queryset.filter(periodo_escolar=periodo)

    reinscripciones = []
    for reins in reinscripciones_queryset:
        reinscripciones.append({
            'numero_solicitud': reins.id_reinscripcion,
            'estudiante__codigo': reins.estudiante.codigo,
            'estudiante__nombre': reins.estudiante.nombre,
            'estudiante__apellido': reins.estudiante.apellido,
            'periodo_escolar': reins.periodo_escolar,
            'tipo': 'Reinscripción',
            'documento_pdf': reins.documento_pdf.url if reins.documento_pdf else None,
        })

    return JsonResponse({
        'inscripciones': inscripciones,
        'reinscripciones': reinscripciones
    })