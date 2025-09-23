from django.shortcuts import render, redirect
from .models import cupo

def configurar_cupos(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo")  
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_limite = request.POST.get("fecha_limite")
        cupos_1ro = request.POST.get("cupos_1ro") or 0
        cupos_2do = request.POST.get("cupos_2do") or 0
        cupos_3ro = request.POST.get("cupos_3ro") or 0
        cupos_tecnico = request.POST.get("cupos_tecnico") or 0

        # Crear el registro en la base de datos
        cupo.objects.create(
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_limite=fecha_limite,
            cupos_1ro=cupos_1ro,
            cupos_2do=cupos_2do,
            cupos_3ro=cupos_3ro,
            cupos_tecnico=cupos_tecnico
        )
        return render(request, "Cant_Estudiantes.html")  
    

