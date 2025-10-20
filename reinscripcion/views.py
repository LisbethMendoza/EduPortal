from django.shortcuts import render,redirect
from grado.models import Grado
from tecnico.models import Tecnico
from inscripcion.models import Inscripcion
from estudiante.models import Estudiante
from django.http import JsonResponse
from reinscripcion.models import Reinscripcion
from cupo.models import cupo
from datetime import date
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.utils import timezone
from django.conf import settings
import os

#-------------------Codigo para generar contrato--------------------------#
def generar_contrato(request, codigo):
    try:
        estudiante = Estudiante.objects.get(codigo=codigo)
    except Estudiante.DoesNotExist:
        return HttpResponse("Estudiante no encontrado", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="contrato_{estudiante.nombre}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'imagenes', 'logo.jpg')
    # Encabezado
    
    c.setFont("Helvetica-Bold", 16)
    c.drawImage(ruta_logo, width / 2 - 50, height - 100, width=100, height=50)
    c.drawCentredString(width / 2, height - 50, "Contrato de Reinscripción Politécnico Ana Silva Jiménez de Castro")

    # Fecha actual
    fecha = timezone.now().strftime("%d/%m/%Y")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Fecha: {fecha}")

    c.drawString(50, height - 130, f"Nombre del estudiante: {estudiante.nombre} {estudiante.apellido}")
    c.drawString(50, height - 160, f"Nombre del tutor: {estudiante.tutor.nombre} {estudiante.tutor.apellido}")

    # Texto del contrato
    texto_contrato = (
    """Por la presente, me dirijo a usted con el fin de formalizar la reinscripción de mi hijo(a) 
en el Politécnico Ana Silva Jiménez de Castro para el próximo período académico. Reconozco la 
importancia de la educación continua y deseo que mi hijo(a) siga recibiendo la formación integral 
que esta institución ofrece, tanto en el ámbito académico como en el desarrollo de valores y 
habilidades sociales.

Asimismo, como tutor(a), me comprometo a cumplir estrictamente con las normas y reglamentos 
establecidos por la institución. Entiendo que la participación activa de mi hijo(a) en todas las 
actividades académicas y extracurriculares, según el calendario escolar, es fundamental para su 
desarrollo y aprovechamiento educativo.

Cualquier incumplimiento de estas normas podrá derivar en medidas disciplinarias, las cuales 
aceptaré y respetaré como parte del compromiso con la formación de mi hijo(a). Confío en que la 
institución continuará proporcionando un ambiente seguro, respetuoso y propicio para el aprendizaje, 
contribuyendo al crecimiento integral de mi hijo(a).

Agradezco de antemano la atención prestada a esta reinscripción y quedo a disposición para cumplir 
con cualquier requisito adicional que sea necesario para completar el proceso formal."""
)


    y = height - 200
    for linea in texto_contrato.split('\n'):
        c.drawString(50, y, linea)
        y -= 20

    # Línea para la firma
    c.drawString(50, y - 50, " Firma del tutor: ___________________________")

    c.showPage()
    c.save()
    return response



#-----------------------Para traer los tecncios activos---------------------------------#
def C_Tecnico(request):
    grados = Grado.objects.filter(estado='activo')
    tecnicos = Tecnico.objects.filter(estado='activo')
    return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos})


    
#-------------------------Para traer los datos del estudiante con codigo------------------------------------#
def buscar_estudiante(request):
    codigo = request.GET.get('codigo', '').strip()

    try:
        estudiante = Estudiante.objects.select_related('grado', 'tecnico').get(codigo=codigo)

        inscripcion = Inscripcion.objects.filter(estudiante=estudiante).order_by('-fecha_inscripcion').first()
        seccion = inscripcion.seccion if inscripcion else ''

        reinscripcion = Reinscripcion.objects.filter(estudiante=estudiante).order_by('-fecha_reinscripcion').first()

        if reinscripcion:
            origen = 'reinscripcion'
            periodo_escolar = reinscripcion.periodo_escolar
            estado = reinscripcion.estado
        else:
            origen = 'inscripcion'
            periodo_escolar = inscripcion.periodo_escolar if inscripcion else ''
            estado = inscripcion.estado if inscripcion else 'Pendiente'

        grado_actual = estudiante.grado
        try:
            siguiente_grado = Grado.objects.get(id_grado=grado_actual.id_grado + 1)
        except Grado.DoesNotExist:
            siguiente_grado = grado_actual

        data = {
            'codigo': estudiante.codigo, 
            'nombre': f"{estudiante.nombre} {estudiante.apellido}",
            'grado_id': siguiente_grado.id_grado,
            'tecnico_id': estudiante.tecnico.id_tecnico if estudiante.tecnico else None,
            'origen': origen,
            'periodo_escolar': periodo_escolar,
            'estado': estado,
            'seccion': seccion,  # Siempre viene de Inscripcion
        }

        return JsonResponse({'success': True, 'data': data})

    except Estudiante.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Estudiante no encontrado'})

#-------------------------CUPO POR SECCIÓN--------------------------------------#
def descontar_cupo(cupo_actual, grado_str, seccion=None):
    campo = None
    if grado_str == "1ro" and seccion:
        campo = f"cupos_1ro_{seccion}"
    elif grado_str == "2do" and seccion:
        campo = f"cupos_2do_{seccion}"
    elif grado_str == "3ro" and seccion:
        campo = f"cupos_3ro_{seccion}"

    if not campo:
        return False

    cupos_disponibles = getattr(cupo_actual, campo, 0)
    if cupos_disponibles <= 0:
        return False

    setattr(cupo_actual, campo, cupos_disponibles - 1)
    cupo_actual.save(update_fields=[campo])
    return True


#-------------------------CUPO POR TÉCNICO--------------------------------------#
def descontar_cupo_tecnico(cupo_actual, tecnico_id, grado_str):
    try:
        tecnico = Tecnico.objects.get(id_tecnico=tecnico_id, estado__iexact="activo")
    except Tecnico.DoesNotExist:
        return False

    try:
        ct = CupoTecnico.objects.get(
            cupo=cupo_actual,
            tecnico=tecnico,
            grado__grado=grado_str
        )
    except CupoTecnico.DoesNotExist:
        return False
    except CupoTecnico.MultipleObjectsReturned:
        ct = CupoTecnico.objects.filter(
            cupo=cupo_actual,
            tecnico=tecnico,
            grado__grado=grado_str
        ).first()

    if ct.cantidad > 0:
        ct.cantidad -= 1
        ct.save(update_fields=["cantidad"])
        return True

    return False


#----------------------------Dato de la reinscripcion insertar--------------------------------------------#
def reinscripcion_insert(request):
    grados = Grado.objects.all()
    tecnicos = Tecnico.objects.all()
    mensaje = None  # Variable para enviar al template

    if request.method == 'POST':
        data = request.POST

        # ------------------- Buscar estudiante -------------------
        try:
            estudiante = Estudiante.objects.get(codigo=data.get("id_estudiante"))
        except Estudiante.DoesNotExist:
            mensaje = "Estudiante no encontrado."
            return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos, 'mensaje': mensaje})

        # ------------------- Reinscripción pendiente -------------------
        if Reinscripcion.objects.filter(estudiante=estudiante, estado="Pendiente").exists():
            mensaje = "Usted tiene una reinscripción pendiente. Comuníquese con el Politecnico al 000-000-000."
            return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos, 'mensaje': mensaje})

        # ------------------- Inscripción pendiente -------------------
        if Inscripcion.objects.filter(estudiante=estudiante, estado="Pendiente").exists():
            mensaje = "Usted tiene una inscripción pendiente. Comuníquese con el Politecnico al 000-000-000."
            return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos, 'mensaje': mensaje})

        # ------------------- Inscripción aprobada -------------------
        if not Inscripcion.objects.filter(estudiante=estudiante, estado="Aprobado").exists():
            mensaje = "Usted no ha estado inscrito en este Politécnico."
            return redirect('inscripcion')

        # ------------------- Verificar periodo activo -------------------
        hoy = timezone.now().date()
        cupo_actual = cupo.objects.filter(tipo="Reinscripcion").last()
        if not cupo_actual:
            mensaje = "No hay periodos de reinscripción activos."
            return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos, 'mensaje': mensaje})

        if hoy < cupo_actual.fecha_inicio or hoy > cupo_actual.fecha_limite:
            mensaje = "Actualmente no está dentro del periodo de reinscripción."
            return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos, 'mensaje': mensaje})

        # ------------------- Validar grado y sección -------------------
        id_grado = data.get("id_grado")
        if not id_grado:
            mensaje = "Debe seleccionar un grado."
            return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos, 'mensaje': mensaje})

        grado_obj = Grado.objects.get(id_grado=id_grado)
        grado_str = grado_obj.grado
        seccion = data.get("seccion") if grado_str in ["1ro", "2do", "3ro"] else None

        if grado_str in ["1ro", "2do", "3ro"] and not seccion:
            mensaje = "Debe seleccionar una sección para este grado."
            return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos, 'mensaje': mensaje})

        # ------------------- Descontar cupo -------------------
        if grado_str in ["4to", "5to", "6to"]:
            tecnico_id = data.get("id_tecnico")
            if not tecnico_id:
                mensaje = "Debe seleccionar un técnico para este grado."
                return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos, 'mensaje': mensaje})

            if not descontar_cupo_tecnico(cupo_actual, tecnico_id, grado_str):
                mensaje = f"No hay cupos disponibles para el técnico seleccionado en {grado_str}."
                return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos, 'mensaje': mensaje})

        else:
            if not descontar_cupo(cupo_actual, grado_str, seccion):
                mensaje = f"No hay cupos disponibles para {grado_str} {seccion or ''}."
                return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos, 'mensaje': mensaje})

        # ------------------- Guardar datos en sesión -------------------
        request.session['reinscripcion_data'] = {
            'id_estudiante': estudiante.codigo,
            'id_grado': id_grado,
            'seccion': seccion,
            'id_tecnico': data.get("id_tecnico"),
            'periodo': data.get("periodo"),
            'estado': data.get("estado", "Pendiente")
        }
        request.session.modified = True  

        return redirect('documentacion_re')

    # ------------------- GET -------------------
    return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos, 'mensaje': None})



#----------------------------Dato de la subida de doc de la reinscripcion--------------------------------------------#
from django.contrib import messages

def reinscripcion_re(request):
    datos = request.session.get('reinscripcion_data')
    if not datos:
        return redirect('reinscripcion_insert')  # Si no hay datos, volvemos al primer formulario

    if request.method == 'POST':
        # Obtener estudiante seguro
        estudiante = Estudiante.objects.get(codigo=datos['id_estudiante'])
        

        # Asignar técnico solo si viene en los datos
        estudiante.grado_id = datos['id_grado']
        if datos.get('id_tecnico'):
            estudiante.tecnico_id = datos['id_tecnico']
        estudiante.save()

        # Crear la reinscripción
        Reinscripcion.objects.create(
            estudiante=estudiante,
            periodo_escolar=datos['periodo'],
            estado=datos['estado'],
            documento_pdf=request.FILES['archivo_pdf'],  
        )
        
        # Actualizar inscripción existente
        inscripcion = Inscripcion.objects.filter(estudiante=estudiante).first()
        if inscripcion:
            inscripcion.seccion = datos.get('seccion', '')
            inscripcion.save()

        # Limpiar sesión
        del request.session['reinscripcion_data']

        # Mensaje de éxito
        messages.success(request, "Reinscripción realizada")

    # Renderizar siempre, fuera del POST
    return render(request, 'documentacion_re.html')





# ----------------------------- CUPOS POR SECCIÓN (1ro, 2do, 3ro) ----------------------------- #
from django.http import JsonResponse
from cupo.models import cupo
from cupotecnico.models import CupoTecnico


def cupo_seccion_reinscripcion(request):
    cupo_actual = cupo.objects.filter(tipo="Reinscripcion").last()
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
        },
    }

    return JsonResponse(cupos_por_grado)


# ----------------------------- CUPOS POR TÉCNICO (4to, 5to, 6to) ----------------------------- #
def cupo_tecnicos_reinscripcion(request):
    cupo_actual = cupo.objects.filter(tipo="Reinscripcion").last()
    if not cupo_actual:
        return JsonResponse({"error": "No hay cupos técnicos disponibles."}, status=404)

    cupos_tecnicos = CupoTecnico.objects.filter(cupo=cupo_actual).select_related("tecnico", "grado")

    cupos_por_tecnico = {}

    for ct in cupos_tecnicos:
        nombre_tecnico = ct.tecnico.nombre if ct.tecnico else "Sin técnico"
        grado_str = ct.grado.grado if ct.grado else "Sin grado"

        if nombre_tecnico not in cupos_por_tecnico:
            cupos_por_tecnico[nombre_tecnico] = {}

        cupos_por_tecnico[nombre_tecnico][grado_str] = ct.cantidad

    return JsonResponse(cupos_por_tecnico)
