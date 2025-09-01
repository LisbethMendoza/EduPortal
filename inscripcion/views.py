from django.shortcuts import render, redirect,get_object_or_404
from .models import Tutor
from estudiante.models import Estudiante
from grado.models import Grado
from tecnico.models import Tecnico
from estudiante.models import Grado, Tecnico
from inscripcion.models import Inscripcion
from reinscripcion.models import Reinscripcion
import random
import string
from django.http import JsonResponse
import os
from django.http import FileResponse, Http404
from django.conf import settings
from datetime import datetime
from django.core.exceptions import ValidationError

def generar_codigo():
    while True:
        codigo = 'EST' + ''.join(random.choices(string.digits, k=5))  
        if not Estudiante.objects.filter(codigo=codigo).exists():
            return codigo
        



def generar_codigo_api(request):
    codigo = generar_codigo()
    return JsonResponse({'codigo': codigo})

def inscripcion_view(request):
    codigo = generar_codigo()
    return render(request, 'inscripcion.html', {'codigo': codigo})


def guardar_tutor(request):
    grados = Grado.objects.all()
    tecnicos = Tecnico.objects.all()

    if request.method == 'POST':
        data = request.POST

        if not data.get("id_grado"):
            print("No se seleccionó grado")
            return render(request, 'inscripcion.html', {
                'grados': grados,
                'tecnicos': tecnicos,
                'error': "Por favor seleccione un grado."
            })

        tutor = crear_tutor(data)  
        estudiante = crear_estudiante(data, tutor)
        inscripcion = crear_inscripcion(data, estudiante, tutor)  

        print("Inscripción creada/actualizada:", inscripcion)

        return redirect('subir_documentos_view', inscripcion_id=inscripcion.id_inscripcion)

    # MÉTODO GET: cargar datos del estudiante si se recibe
    id_est = request.GET.get("id_estudiante")
    estudiante = None
    codigo = None

    if id_est:
        try:
            estudiante = Estudiante.objects.get(id=id_est)
        except Estudiante.DoesNotExist:
            pass

    return render(request, 'inscripcion.html', {
        'grados': grados,
        'tecnicos': tecnicos,
        'estudiante': estudiante,
        'codigo': codigo   
    })


def subir_documentos_view(request, inscripcion_id):
    inscripcion = Inscripcion.objects.get(id_inscripcion=inscripcion_id)
    mensaje = None 
    if request.method == 'POST':
        cedula_tutor = request.FILES.get('cedula_tutor')
        foto_estudiante = request.FILES.get('foto_estudiante')
        record_notas = request.FILES.get('record_notas')
        acta_nacimiento = request.FILES.get('acta_nacimiento')
        certificado_medico = request.FILES.get('certificado_medico')

        # Función auxiliar para eliminar archivo existente
        def reemplazar_archivo(campo, nuevo_archivo):
            archivo_antiguo = getattr(inscripcion, campo)
            if archivo_antiguo:
                ruta = os.path.join(settings.MEDIA_ROOT, archivo_antiguo.name)
                if os.path.isfile(ruta):
                    os.remove(ruta) 
            setattr(inscripcion, campo, nuevo_archivo) 

        if cedula_tutor:
            reemplazar_archivo('cedula_tutor', cedula_tutor)
        if foto_estudiante:
            reemplazar_archivo('foto_estudiante', foto_estudiante)
        if record_notas:
            reemplazar_archivo('record_notas', record_notas)
        if acta_nacimiento:
            reemplazar_archivo('acta_nacimiento', acta_nacimiento)
        if certificado_medico:
            reemplazar_archivo('certificado_medico', certificado_medico)

        inscripcion.save()

        mensaje = f"SU INSCRIPCIÓN FUE HECHA EXITOSAMENTE. Nota: anota '{inscripcion.estudiante.codigo}' para futuras consultas."
        return render(request, 'documentacion.html', {
            'inscripcion': inscripcion,
            'mensaje': mensaje,
        })

    return render(request, 'documentacion.html', {'inscripcion': inscripcion})



def crear_estudiante(data, tutor):
    id_estudiante = data.get("id_estudiante")
    codigo = data.get("codigo") or generar_codigo()

    try:
        if id_estudiante:
            estudiante = Estudiante.objects.get(id=id_estudiante)
        else:
            estudiante = Estudiante.objects.get(codigo=codigo)

        estudiante.nombre = data.get("nombre_e")
        estudiante.apellido = data.get("apellido_e")
        estudiante.fecha_nacimiento = data.get("fecha_naci")
        estudiante.grado_id = data.get("id_grado")
        estudiante.tecnico_id = data.get("id_tecnico")
        estudiante.tutor = tutor
        estudiante.codigo = codigo
        estudiante.save()
        return estudiante

    except Estudiante.DoesNotExist:
        return Estudiante.objects.create(
            codigo=codigo,
            nombre=data.get("nombre_e"),
            apellido=data.get("apellido_e"),
            fecha_nacimiento=data.get("fecha_naci"),
            grado_id=data.get("id_grado"),
            tecnico_id=data.get("id_tecnico"),
            tutor=tutor
        )
    


def crear_tutor(data):
    cedula = data.get("cedula")
    telefono = data.get("num")
    try:
        tutor = Tutor.objects.get(cedula=cedula)
        tutor.nombre = data.get("nombre_p")
        tutor.apellido = data.get("apellido_p")
        tutor.parentesco = data.get("parentesco")
        tutor.telefono = telefono   
        tutor.save()
        return tutor

    except Tutor.DoesNotExist:
        # Si no existe, crea uno nuevo
        return Tutor.objects.create(
            nombre=data.get("nombre_p"),
            apellido=data.get("apellido_p"),
            parentesco=data.get("parentesco"),
            cedula=cedula,
            telefono=telefono
        )

        
        


def buscar_estudiante_por_codigo(request):
    codigo = request.GET.get('codigo')

    try:
        estudiante = Estudiante.objects.get(codigo=codigo)
        tutor = estudiante.tutor

        
        inscripcion = Inscripcion.objects.filter(estudiante=estudiante).order_by('-fecha_inscripcion').first()

        data = {
            'nombre': estudiante.nombre,
            'apellido': estudiante.apellido,
            'fecha_nacimiento': estudiante.fecha_nacimiento.strftime('%Y-%m-%d'),
            'id_grado': estudiante.grado_id,
            'id_tecnico': estudiante.tecnico_id,
            'tutor': {
                'nombre': tutor.nombre if tutor else '',
                'apellido': tutor.apellido if tutor else '',
                'parentesco': tutor.parentesco if tutor else '',
                'cedula': tutor.cedula if tutor else '',
                'telefono': tutor.telefono if tutor else '',
            },
            'inscripcion': {
                'periodo_escolar': inscripcion.periodo_escolar if inscripcion else '',
                'fecha_inscripcion': inscripcion.fecha_inscripcion.strftime('%Y-%m-%d') if inscripcion else '',
                'estado': inscripcion.estado if inscripcion else '',
                'seccion': inscripcion.seccion if inscripcion else '',
                
                'cedula_tutor': inscripcion.cedula_tutor.url if inscripcion and inscripcion.cedula_tutor else '',
                'foto_estudiante': inscripcion.foto_estudiante.url if inscripcion and inscripcion.foto_estudiante else '',
                'record_notas': inscripcion.record_notas.url if inscripcion and inscripcion.record_notas else '',
                'acta_nacimiento': inscripcion.acta_nacimiento.url if inscripcion and inscripcion.acta_nacimiento else '',
                'certificado_medico': inscripcion.certificado_medico.url if inscripcion and inscripcion.certificado_medico else '', 
            }
        }

        return JsonResponse({'success': True, 'data': data})
    
    except Estudiante.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Estudiante no encontrado'})


#-----------------------CREA LA INSCRIPCION Y LA ACTUALIZACION------------------------------------
def crear_inscripcion(data, estudiante, tutor):
    periodo = data.get("periodo")
    fecha = data.get("fecha_inscrip")
    seccion = data.get("seccion") 


    try:
        inscripcion = Inscripcion.objects.get(estudiante=estudiante, periodo_escolar=periodo)
        inscripcion.tutor = tutor
        inscripcion.fecha_inscripcion = fecha
        inscripcion.estado = data.get("estado", "Pendiente")
        inscripcion.seccion = seccion 
        inscripcion.save()
        return inscripcion

    except Inscripcion.DoesNotExist:
        return Inscripcion.objects.create(
            estudiante=estudiante,
            tutor=tutor,
            periodo_escolar=periodo,
            fecha_inscripcion=fecha,
            estado=data.get("estado", "Pendiente"),
            seccion=seccion
)
#--------------------------------PARTE ADMINISTRATIVA REVISION DE LOS ESTUDIANTES-----------------------------------------------------------------------------


def obtener_estudiantes_pendientes(request):
    estudiantes = []
    seen_ids = set()

    # Inscripciones pendientes
    inscripciones = Inscripcion.objects.filter(estado="Pendiente").select_related("estudiante")
    for insc in inscripciones:
        e = insc.estudiante
        if e.id not in seen_ids:
            estudiantes.append({"id": e.id, "codigo": e.codigo, "tipo": "Inscripción"})
            seen_ids.add(e.id)

    # Reinscripciones pendientes
    reinscripciones = Reinscripcion.objects.filter(estado="Pendiente").select_related("estudiante")
    for reinsc in reinscripciones:
        e = reinsc.estudiante
        if e.id not in seen_ids:
            estudiantes.append({"id": e.id, "codigo": e.codigo, "tipo": "Reinscripción"})
            seen_ids.add(e.id)

    return JsonResponse({"estudiantes": estudiantes})


def detalle_estudiante(request):
    estudiante_id = request.GET.get("estudiante")
    estudiante = None
    mostrar = None
    inscripciones = None
    reinscripciones = None
    seccion_ultima = None

    # Filtrar solo pendientes
    inscripciones_pendientes = Inscripcion.objects.filter(estado="Pendiente")
    reinscripciones_pendientes = Reinscripcion.objects.filter(estado="Pendiente")

    # Obtener lista de estudiantes pendientes
    estudiantes = set()
    for insc in inscripciones_pendientes:
        estudiantes.add(insc.estudiante)
    for reinsc in reinscripciones_pendientes:
        estudiantes.add(reinsc.estudiante)

    if estudiante_id:
        estudiante = Estudiante.objects.get(id=estudiante_id)

        # Filtrar solo las inscripciones/reinscripciones del estudiante seleccionado
        inscripciones = inscripciones_pendientes.filter(estudiante=estudiante)
        reinscripciones = reinscripciones_pendientes.filter(estudiante=estudiante)

        # Traer la sección de la última inscripción (si existe)
        ultima_insc = Inscripcion.objects.filter(estudiante=estudiante).order_by('-fecha_inscripcion').first()
        seccion_ultima = ultima_insc.seccion if ultima_insc else None

        # Decidir qué mostrar
        if estudiante.grado.grado in ["1ro", "2do", "3ro"]:
            mostrar = "seccion"
        else:
            mostrar = "tecnico"

    return render(request, "Revision_E.html", {
        "estudiante": estudiante,
        "estudiantes": estudiantes,
        "inscripciones": inscripciones,
        "reinscripciones": reinscripciones,
        "mostrar": mostrar,
        "seccion_ultima": seccion_ultima,
    })
    
    
from django.contrib import messages
def cambiar_estado(request, tipo, id, nuevo_estado):
    if tipo == "inscripcion":
        registro = get_object_or_404(Inscripcion, id_inscripcion=id)
    elif tipo == "reinscripcion":
        registro = get_object_or_404(Reinscripcion, id_reinscripcion=id)
    else:
        messages.error(request, "Tipo inválido")
        return redirect('detalle_estudiante')


    comentario = request.POST.get("comentario", "")
    if comentario:
        registro.comentario = comentario  

    registro.estado = nuevo_estado
    registro.save()

    messages.success(request, f"El estado se actualizó a {nuevo_estado}")
    return redirect(f'/usuario/Revision_E/?estudiante={registro.estudiante.id}')



#--------------------------VISUALIZAR CANTIDAD-----------------------------------------
