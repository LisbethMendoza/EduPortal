from django.shortcuts import render
from .models import Tecnico
from grado.models import Grado
from django.contrib import messages

def Insert_update_delete(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_tecnico').strip().lower()
        accion = request.POST.get('accion')

        # Buscar técnico ignorando mayúsculas/minúsculas
        tecnico_obj = Tecnico.objects.filter(nombre__iexact=nombre).first()

        if accion == 'agregar':
            if tecnico_obj:
                tecnico_obj.estado = 'activo'  # reactiva si estaba eliminado
                tecnico_obj.save()
                messages.success(request, "Técnico actualizado o reactivado.")
            else:
                Tecnico.objects.create(nombre=nombre, estado='activo')
                messages.success(request, "Técnico creado correctamente.")

        elif accion == 'eliminar':
            if tecnico_obj:
                tecnico_obj.estado = 'eliminado'
                tecnico_obj.save()
                messages.warning(request, "Técnico eliminado correctamente.")
            else:
                messages.error(request, "El técnico no existe.")

    return render(request, 'Cant_Estudiantes.html')


# Renderiza el formulario
def configuraciones_formulario(request):
    activos_count = Tecnico.objects.filter(estado='activo').count()
    return render(request, 'usuario/Cant_Estudiantes.html', {
        'activos_count': activos_count
    })
    

