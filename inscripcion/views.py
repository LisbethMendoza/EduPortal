from django.shortcuts import render, redirect
from .models import Tutor
from estudiante.models import Estudiante
from grado.models import Grado
from tecnico.models import Tecnico
from estudiante.models import Grado, Tecnico
from inscripcion.models import Inscripcion
import random
import string
from django.http import JsonResponse
import os
from django.http import FileResponse, Http404
from django.conf import settings


def generar_codigo():
    while True:
        codigo = 'EST' + ''.join(random.choices(string.digits, k=5))  
        if not Estudiante.objects.filter(codigo=codigo).exists():
            return codigo
        
def documentacion_view(request, inscripcion_id):
    
    inscripcion = Inscripcion.objects.get(id_inscripcion=inscripcion_id)

    if request.method == 'POST':
        archivo_pdf = request.FILES.get('pdf_file')
        if archivo_pdf:
            inscripcion.documento_pdf = archivo_pdf
            inscripcion.save()
            mensaje = "PDF subido correctamente."

    return render(request, 'documentacion.html', {'inscripcion': inscripcion})


def descargar_formulario(request):
    ruta_archivo = os.path.join(settings.MEDIA_ROOT, 'documentos', 'Formulario_de_Inscripcion.docx')
    print("Buscando archivo en:", ruta_archivo)
    print("¿Existe archivo?:", os.path.exists(ruta_archivo))

    if os.path.exists(ruta_archivo):
        return FileResponse(
            open(ruta_archivo, 'rb'),
            as_attachment=True,
            filename='Formulario_de_Inscripcion.docx'
        )
    else:
        print("Archivo NO encontrado en la ruta anterior")
        raise Http404("El archivo no existe")



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

        tutor = crear_tutor(data)  # ya no pasamos files porque no hay pdf aquí
        estudiante = crear_estudiante(data, tutor)
        inscripcion = crear_inscripcion(data, estudiante, tutor)  # Sin files

        print("Inscripción creada/actualizada:", inscripcion)

        # Redirige a la vista de subir PDF, pasando el id de la inscripción
        return redirect('documentacion_view', inscripcion_id=inscripcion.id_inscripcion)

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


def subir_pdf_view(request, inscripcion_id):
    inscripcion = Inscripcion.objects.get(id_inscripcion=inscripcion_id)

    if request.method == 'POST':
        archivo_pdf = request.FILES.get('pdf_file')
        if archivo_pdf:
            inscripcion.documento_pdf = archivo_pdf
            inscripcion.save()
            # Redirigir a página de éxito o detalle
            return redirect('inscripcion_exitosa')

    return render(request, 'documentacion.html', {'inscripcion': inscripcion})


def crear_estudiante(data, tutor):
    id_estudiante = data.get("id_estudiante")
    codigo = data.get("codigo") or generar_codigo()

    try:
        if id_estudiante:
            estudiante = Estudiante.objects.get(id=id_estudiante)
        else:
            estudiante = Estudiante.objects.get(codigo=codigo)

        # Si existe, actualiza
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
        # Si no existe, lo crea
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
    try:
        tutor = Tutor.objects.get(cedula=cedula)
        tutor.nombre = data.get("nombre_p")
        tutor.apellido = data.get("apellido_p")
        tutor.parentesco = data.get("parentesco")
        tutor.save()
        return tutor

    except Tutor.DoesNotExist:
        # Si no existe, crea uno nuevo
        return Tutor.objects.create(
            nombre=data.get("nombre_p"),
            apellido=data.get("apellido_p"),
            parentesco=data.get("parentesco"),
            cedula=cedula
        )

        
        


def buscar_estudiante_por_codigo(request):
    codigo = request.GET.get('codigo')

    try:
        estudiante = Estudiante.objects.get(codigo=codigo)
        tutor = estudiante.tutor

        # Buscar la inscripción más reciente del estudiante (si existe)
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
            },
            'inscripcion': {
                'periodo_escolar': inscripcion.periodo_escolar if inscripcion else '',
                'fecha_inscripcion': inscripcion.fecha_inscripcion.strftime('%Y-%m-%d') if inscripcion else '',
                'estado': inscripcion.estado if inscripcion else '',
                'documento_pdf': inscripcion.documento_pdf.url if inscripcion and inscripcion.documento_pdf else '',
                'seccion': inscripcion.seccion if inscripcion else '' 
            }
        }

        return JsonResponse({'success': True, 'data': data})
    
    except Estudiante.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Estudiante no encontrado'})



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
        
