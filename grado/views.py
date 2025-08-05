from django.shortcuts import render
from .models import Grado
from django.contrib import messages

def Insert_update_delete(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_grado').strip().lower()
        accion = request.POST.get('accion')

        # Buscar grado ignorando mayúsculas/minúsculas
        grado_obj = Grado.objects.filter(grado__iexact=nombre).first()

        if accion == 'agregar':
            if grado_obj:
                grado_obj.estado = 'activo'  # reactiva si estaba eliminado
                grado_obj.save()
                messages.success(request, "Grado actualizado o reactivado.")
            else:
                Grado.objects.create(grado=nombre, estado='activo')
                messages.success(request, "Grado creado correctamente.")

        elif accion == 'eliminar':
            if grado_obj:
                grado_obj.estado = 'eliminado'
                grado_obj.save()
                messages.warning(request, "Grado eliminado correctamente.")
        else:
                messages.error(request, "El grado no existe.")

    return render(request, 'Cant_Estudiantes.html')
