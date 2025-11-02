from django.shortcuts import render, redirect,get_object_or_404
from .models import Tutor
from estudiante.models import Estudiante
from grado.models import Grado
from tecnico.models import Tecnico
from estudiante.models import Grado, Tecnico
from inscripcion.models import Inscripcion
from reinscripcion.models import Reinscripcion
from cupo.models import cupo
import random
import string
from django.http import JsonResponse
import os
from django.http import FileResponse, Http404
from django.conf import settings
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_date


def fecha_hoy(request):
    today = timezone.now().date()
    return render(request, 'inscripcion.html', {"today": today})


def generar_codigo():
    while True:
        codigo = 'S' + ''.join(random.choices(string.digits, k=5))  
        if not Estudiante.objects.filter(codigo=codigo).exists():
            return codigo
        


def generar_codigo_api(request):
    codigo = generar_codigo()
    return JsonResponse({'codigo': codigo})

def inscripcion_view(request):
    codigo = generar_codigo()
    return render(request, 'inscripcion.html', {'codigo': codigo})


#------------------------------------DESCONTAR LOS CUPOS----------------------------------------------#

def descontar_cupo(cupo_actual, grado, seccion=None):
    """
    Resta un cupo del grado/sección indicado en el objeto cupo_actual.
    Retorna True si se pudo descontar, False si no hay cupos.
    """
    campo_cupo = None

    if grado == "1ro" and seccion:
        campo_cupo = f"cupos_1ro_{seccion}"
    elif grado == "2do" and seccion:
        campo_cupo = f"cupos_2do_{seccion}"
    elif grado == "3ro" and seccion:
        campo_cupo = f"cupos_3ro_{seccion}"
    elif grado in ["4to", "5to", "6to"]:  # Técnicos
        campo_cupo = "cupos_tecnico"

    if not campo_cupo:
        return False  # No corresponde a ningún campo válido

    valor_actual = getattr(cupo_actual, campo_cupo)

    if valor_actual <= 0:
        return False  # No hay cupos disponibles

    setattr(cupo_actual, campo_cupo, valor_actual - 1)
    cupo_actual.save()
    return True

#----------------------PARA SABER LOS CUPOS-------------------------------------------#
def descontar_cupo(cupo_actual, grado_str, seccion=None):  #Poner en Reinscripcion
    campo = None
    if grado_str == "1ro" and seccion:
        campo = f"cupos_1ro_{seccion}"
    elif grado_str == "2do" and seccion:
        campo = f"cupos_2do_{seccion}"
    elif grado_str == "3ro" and seccion:
        campo = f"cupos_3ro_{seccion}"
  

    cupos_disponibles = getattr(cupo_actual, campo, 0)


    if cupos_disponibles <= 0:
        return False

    setattr(cupo_actual, campo, cupos_disponibles - 1)
    cupo_actual.save(update_fields=[campo])

    return True

#-------------------------CUPO POR TECNICO--------------------------------------#
def descontar_cupo_tecnico(cupo_actual, tecnico_id, grado_str):

    try:
        tecnico = Tecnico.objects.get(id_tecnico=tecnico_id, estado__iexact="activo")
    except Tecnico.DoesNotExist:
        return False  # Técnico no encontrado o inactivo

    # Buscamos el cupo de este técnico para el grado específico
    try:
        ct = CupoTecnico.objects.get(
            cupo=cupo_actual,
            tecnico=tecnico,
            grado__grado=grado_str   # Filtramos por el grado
        )
    except CupoTecnico.DoesNotExist:
        return False  # No hay registro para este técnico y grado
    except CupoTecnico.MultipleObjectsReturned:
        # Esto no debería pasar si tu modelo tiene unique_together = (cupo, tecnico, grado)
        ct = CupoTecnico.objects.filter(
            cupo=cupo_actual,
            tecnico=tecnico,
            grado__grado=grado_str
        ).first()

    if ct.cantidad > 0:
        ct.cantidad -= 1
        ct.save()
        return True
    else:
        return False



#-----------------------------NO INSCRIBE SI NO ESTA EN FECHA------------------------------------------#
# tus funciones existentes

def Siguiente_inscripcion(request):
    grados = Grado.objects.all()
    tecnicos = Tecnico.objects.all()

    if request.method == 'POST':
        data = request.POST

        # ------------------- Validar grado -------------------
        id_grado = data.get("id_grado")
        if not id_grado:
            messages.error(request, "Por favor seleccione un grado.")
            return render(request, 'inscripcion.html', {'grados': grados, 'tecnicos': tecnicos})

        grado_obj = Grado.objects.get(id_grado=id_grado)
        grado_str = grado_obj.grado  # "1ro", "2do", etc.

        # ------------------- Validar fecha -------------------
        fecha_str = data.get("fecha_inscrip")
        fecha = parse_date(fecha_str)

        cupo_actual = cupo.objects.filter(tipo="Inscripcion").last()
        if not cupo_actual:
            messages.error(request, "No hay cupos activos para inscripciones.")
            return render(request, 'inscripcion.html', {'grados': grados, 'tecnicos': tecnicos})

        if fecha < cupo_actual.fecha_inicio or fecha > cupo_actual.fecha_limite:
            messages.error(request, "Lo siento, usted está fuera de la fecha pautada para inscribirse.")
            return render(request, 'inscripcion.html', {'grados': grados, 'tecnicos': tecnicos})

        # ------------------- Validar sección -------------------
        seccion = data.get("seccion") if grado_str in ["1ro", "2do", "3ro"] else None
        if grado_str in ["1ro", "2do", "3ro"] and not seccion:
            messages.error(request, "Debe seleccionar una sección para este grado.")
            return render(request, 'inscripcion.html', {'grados': grados, 'tecnicos': tecnicos})

        # ------------------- Descontar cupo ------------------- # Poner en Reinscripcion
        if grado_str in ["4to", "5to", "6to"]:
            tecnico_id = data.get("id_tecnico")  # El técnico seleccionado en el formulario
            if not tecnico_id:
                messages.error(request, "Debe seleccionar un técnico para este grado.")
                return render(request, 'inscripcion.html', {'grados': grados, 'tecnicos': tecnicos})

            if not descontar_cupo_tecnico(cupo_actual, tecnico_id, grado_str):
                messages.error(request, f"No hay cupos disponibles para el técnico seleccionado en {grado_str}.")
                return render(request, 'inscripcion.html', {'grados': grados, 'tecnicos': tecnicos})

        else:
            # Para 1ro,2do,3ro usamos tu función de secciones existente
            if not descontar_cupo(cupo_actual, grado_str, seccion):
                messages.error(request, f"No hay cupos disponibles para {grado_str} {seccion}.")
                return render(request, 'inscripcion.html', {'grados': grados, 'tecnicos': tecnicos})



        # ------------------- Crear inscripción -------------------
        tutor = crear_tutor(data)
        estudiante = crear_estudiante(data, tutor)
        inscripcion = crear_inscripcion(data, estudiante, tutor)

        messages.success(request, "")
        return redirect('subir_documentos_view', inscripcion_id=inscripcion.id_inscripcion)

    # ------------------- GET -------------------
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


#----------------------SUBIDA DE LOS DOCUMENTOS----------------------------------------#

def subir_documentos_view(request, inscripcion_id):
    inscripcion = Inscripcion.objects.get(id_inscripcion=inscripcion_id)

    if request.method == 'POST':
        cedula_tutor = request.FILES.get('cedula_tutor')
        foto_estudiante = request.FILES.get('foto_estudiante')
        record_notas = request.FILES.get('record_notas')
        acta_nacimiento = request.FILES.get('acta_nacimiento')
        certificado_medico = request.FILES.get('certificado_medico')

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

        mensaje = f"SU Solicitud fue realizada exitosamente. Nota: anota '{inscripcion.estudiante.codigo}' para futuras consultas."

        # Si es AJAX, devuelve JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'mensaje': mensaje})

        # Si no, renderiza normal
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
    telefono2 = data.get("num2")
    try:
        tutor = Tutor.objects.get(cedula=cedula)
        tutor.nombre = data.get("nombre_p")
        tutor.apellido = data.get("apellido_p")
        tutor.parentesco = data.get("parentesco")
        tutor.telefono = telefono   
        tutor.telefono2 = telefono2   
        tutor.save()
        return tutor

    except Tutor.DoesNotExist:
        # Si no existe, crea uno nuevo
        return Tutor.objects.create(
            nombre=data.get("nombre_p"),
            apellido=data.get("apellido_p"),
            parentesco=data.get("parentesco"),
            cedula=cedula,
            telefono=telefono,
            telefono2=telefono2
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
                'telefono2': tutor.telefono2 if tutor else '',
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

#---------------------DETALLE DEL ESTUDIANTE USADO EN ADM------------------------------------# 
from django.shortcuts import render, get_object_or_404

from django.shortcuts import render, get_object_or_404

def detalle_estudiante(request):
    estudiante_id = request.GET.get("estudiante")
    estudiante = None
    mostrar = None
    inscripciones = None
    reinscripciones = None
    seccion_ultima = None

    inscripciones_pendientes = Inscripcion.objects.filter(estado="Pendiente").order_by('id_inscripcion')
    reinscripciones_pendientes = Reinscripcion.objects.filter(estado="Pendiente").order_by('id_reinscripcion')

    # Definir listas vacías por defecto
    estudiantes_reinscripcion = []
    estudiantes_inscripcion = []

    if estudiante_id:
        estudiante = Estudiante.objects.get(id=estudiante_id)

        reinscripciones = reinscripciones_pendientes.filter(estudiante=estudiante)
        inscripciones = inscripciones_pendientes.filter(estudiante=estudiante)

        # Traer la sección de la última inscripción (si existe)
        ultima_insc = Inscripcion.objects.filter(estudiante=estudiante).order_by('-fecha_inscripcion').first()
        seccion_ultima = ultima_insc.seccion if ultima_insc else None

        # Decidir qué mostrar
        if estudiante.grado.grado in ["1ro", "2do", "3ro"]:
            mostrar = "seccion"
        else:
            mostrar = "tecnico"

    # Obtener todos los estudiantes pendientes
    estudiantes_reinscripcion = [r.estudiante for r in reinscripciones_pendientes]
    estudiantes_inscripcion = [i.estudiante for i in inscripciones_pendientes]

    # Combinar: primero reinscripciones, luego inscripciones
    estudiantes_pendientes = estudiantes_reinscripcion + estudiantes_inscripcion

    return render(request, "Revision_E.html", {
        "estudiante": estudiante,
        "inscripciones": inscripciones,
        "reinscripciones": reinscripciones,
        "mostrar": mostrar,
        "seccion_ultima": seccion_ultima,
        "estudiantes_pendientes": estudiantes_pendientes,
    })

    
#---------------------CAMBIAR EL ESTADO DE LA INSCRIPCION O REINSCRIPCION------------------------#
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

def cupo_seccion_inscripcion(request):
    cupo_actual = cupo.objects.filter(tipo="Inscripcion").last()
    if not cupo_actual:
        return JsonResponse({"error": "No hay cupos disponibles."}, status=404)
    cupos_por_grado = {
        "1ro": {
            "A": cupo_actual.cupos_1ro_A,
            "B": cupo_actual.cupos_1ro_B,
            "C": cupo_actual.cupos_1ro_C,
        },
        "2do": {
            "A": cupo_actual.cupos_2do_A,
            "B": cupo_actual.cupos_2do_B,
            "C": cupo_actual.cupos_2do_C,
        },
        "3ro": {
            "A": cupo_actual.cupos_3ro_A,
            "B": cupo_actual.cupos_3ro_B,
            "C": cupo_actual.cupos_3ro_C,
        }
    }
    return JsonResponse(cupos_por_grado)



#-----------------------------Listado d elos tecncios----------------------------------------#
from django.http import JsonResponse
from cupotecnico.models import CupoTecnico
from cupo.models import cupo

def cupo_tecnicos_inscripcion(request):
    # Tomamos el último cupo de inscripción
    cupo_actual = cupo.objects.filter(tipo="Inscripcion").last()
    if not cupo_actual:
        return JsonResponse({"error": "No hay cupos disponibles."}, status=404)

    # Filtramos solo los técnicos activos
    cupos_tecnicos = CupoTecnico.objects.filter(
        cupo=cupo_actual,
        tecnico__estado="activo"  
    )

    cupos_por_tecnico = {}

    for ct in cupos_tecnicos:
        nombre_tecnico = ct.tecnico.nombre
        grado_str = ct.grado.grado if ct.grado else "Sin grado"

        if nombre_tecnico not in cupos_por_tecnico:
            cupos_por_tecnico[nombre_tecnico] = {}

        cupos_por_tecnico[nombre_tecnico][grado_str] = ct.cantidad

    return JsonResponse(cupos_por_tecnico)



