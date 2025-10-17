from django.shortcuts import render
from .models import Grado
from django.contrib import messages
from tecnico.models import Tecnico
from django.http import JsonResponse

def Insert_update_delete(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_grado').strip().lower()
        accion = request.POST.get('accion')

        niveles_existentes = set(
            Grado.objects.filter(estado='activo')
            .values_list('grado', flat=True)
        )
        niveles_existentes = {n.strip().lower() for n in niveles_existentes}
        niveles_necesarios = {'1ro','2do','3ro','4to','5to','6to'}
        niveles_completos = niveles_necesarios.issubset(niveles_existentes)

        # Buscar grado ignorando mayúsculas/minúsculas
        grado_obj = Grado.objects.filter(grado__iexact=nombre).first()

        if accion == 'agregar':
            if niveles_completos:
                messages.error(request, "Ya existen todos los niveles del 1ro al 6to. No se puede agregar más.")
            else:
                if grado_obj:
                    grado_obj.estado = 'activo'
                    grado_obj.save()
                    messages.success(request, "Grado actualizado o reactivado.")
                else:
                    Grado.objects.create(grado=nombre, estado='activo')
                    messages.success(request, "Grado creado correctamente.")

        elif accion == 'eliminar':
            if niveles_completos:
                messages.error(request, "Ya existen todos los niveles del 1ro al 6to. No se puede eliminar.")
            else:
                if grado_obj:
                    grado_obj.estado = 'eliminado'
                    grado_obj.save()
                    messages.warning(request, "Grado eliminado correctamente.")
                else:
                    messages.error(request, "El grado no existe.")

    return render(request, 'Cant_Estudiantes.html')


def C_Grado(request):
    grados = Grado.objects.filter(estado='activo')
    tecnicos = Tecnico.objects.filter(estado='activo')
    return render(request, 'inscripcion.html', {'grados': grados, 'tecnicos': tecnicos})


def manejar_grado_view(request):
    niveles_existentes = set(
        Grado.objects.filter(estado='activo')
        .values_list('grado', flat=True)
    )
    niveles_existentes = {n.strip().lower() for n in niveles_existentes}
    niveles_necesarios = {'1ro','2do','3ro','4to','5to','6to'}
    niveles_completos = niveles_necesarios.issubset(niveles_existentes)

    return JsonResponse({'niveles_completos': niveles_completos})
