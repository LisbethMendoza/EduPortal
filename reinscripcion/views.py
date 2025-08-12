from django.shortcuts import render
from grado.models import Grado
from tecnico.models import Tecnico
from inscripcion.models import Inscripcion
from estudiante.models import Estudiante
from django.http import JsonResponse

def C_Tecnico(request):
    grados = Grado.objects.filter(estado='activo')
    tecnicos = Tecnico.objects.filter(estado='activo')
    return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos})


def guarda_redirige (request):
        return render(request, 'documentacion_re.html')
    
    
def buscar_estudiante(request):
    codigo = request.GET.get('codigo', '').strip()

    try:
        estudiante = Estudiante.objects.select_related('grado', 'tecnico').get(codigo=codigo)
        inscripcion = Inscripcion.objects.filter(estudiante=estudiante).order_by('-fecha_inscripcion').first()

        grado_actual = estudiante.grado
        # Aquí defines tu lógica para obtener el siguiente grado
        try:
            siguiente_grado = Grado.objects.get(id_grado=grado_actual.id_grado + 1)
        except Grado.DoesNotExist:
            siguiente_grado = grado_actual  # si no hay siguiente, se queda igual

        data = {
            'nombre': f"{estudiante.nombre} {estudiante.apellido}",
            'grado_id': siguiente_grado.id_grado,  # en vez del actual, devuelves el siguiente
            'tecnico_id': estudiante.tecnico.id_tecnico if estudiante.tecnico else None,
            'inscripcion': {
                'periodo_escolar': inscripcion.periodo_escolar if inscripcion else '',
                'estado': inscripcion.estado if inscripcion else 'Pendiente',
                'seccion': inscripcion.seccion if inscripcion else '',
            }
        }

        return JsonResponse({'success': True, 'data': data})

    except Estudiante.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Estudiante no encontrado'})
