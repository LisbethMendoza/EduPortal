from django.shortcuts import render,redirect,get_object_or_404
from grado.models import Grado
from tecnico.models import Tecnico
from inscripcion.models import Inscripcion
from estudiante.models import Estudiante
from django.http import JsonResponse
from reinscripcion.models import Reinscripcion
from datetime import date

def C_Tecnico(request):
    grados = Grado.objects.filter(estado='activo')
    tecnicos = Tecnico.objects.filter(estado='activo')
    return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos})


    
    
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




def reinscripcion_insert(request):
    if request.method == 'POST':
        # Guardar datos en sesión
        request.session['reinscripcion_data'] = {
            'id_estudiante': request.POST['id_estudiante'],
            'id_grado': request.POST['id_grado'],
            'seccion': request.POST.get('seccion', ''),  # para grados que requieren sección
            'id_tecnico': request.POST.get('id_tecnico', None),  # para grados que requieren técnico
            'periodo': request.POST['periodo'],
            'estado': request.POST['estado'],
        }
        # Redirigir al formulario de PDF
        return redirect('documentacion_re')  

    return render(request, 'reinscripcion.html', {
        'grados': Grado.objects.all(),
        'tecnicos': Tecnico.objects.all(),
    })


def reinscripcion_re(request):
    datos = request.session.get('reinscripcion_data')
    if not datos:
        return redirect('reinscripcion_insert')  # Si no hay datos, volvemos al primer formulario

    if request.method == 'POST':
        # Obtener estudiante seguro
        estudiante = Estudiante.objects.get(codigo=datos['id_estudiante'])

        # Asignar técnico solo si viene en los datos
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


        del request.session['reinscripcion_data']

    return render(request, 'documentacion_re.html')