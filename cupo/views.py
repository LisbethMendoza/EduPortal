from django.shortcuts import render, redirect
from .models import cupo

def configurar_cupos(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_limite = request.POST.get("fecha_limite")

        # Cupos por sección (si no ponen nada, queda 0)
        cupos_1ro_A = request.POST.get("cupos_1ro_A") or 0
        cupos_1ro_B = request.POST.get("cupos_1ro_B") or 0
        cupos_1ro_C = request.POST.get("cupos_1ro_C") or 0

        cupos_2do_A = request.POST.get("cupos_2do_A") or 0
        cupos_2do_B = request.POST.get("cupos_2do_B") or 0
        cupos_2do_C = request.POST.get("cupos_2do_C") or 0

        cupos_3ro_A = request.POST.get("cupos_3ro_A") or 0
        cupos_3ro_B = request.POST.get("cupos_3ro_B") or 0
        cupos_3ro_C = request.POST.get("cupos_3ro_C") or 0

        cupos_tecnico = request.POST.get("cupos_tecnico") or 0

        # Buscar si ya existe un registro con ese tipo
        registro = cupo.objects.filter(tipo=tipo).first()

        if registro:
            # Si existe, actualizamos
            registro.fecha_inicio = fecha_inicio
            registro.fecha_limite = fecha_limite
            registro.cupos_1ro_A = cupos_1ro_A
            registro.cupos_1ro_B = cupos_1ro_B
            registro.cupos_1ro_C = cupos_1ro_C
            registro.cupos_2do_A = cupos_2do_A
            registro.cupos_2do_B = cupos_2do_B
            registro.cupos_2do_C = cupos_2do_C
            registro.cupos_3ro_A = cupos_3ro_A
            registro.cupos_3ro_B = cupos_3ro_B
            registro.cupos_3ro_C = cupos_3ro_C
            registro.cupos_tecnico = cupos_tecnico
            registro.save()
        else:
    
            cupo.objects.create(
                tipo=tipo,
                fecha_inicio=fecha_inicio,
                fecha_limite=fecha_limite,
                cupos_1ro_A=cupos_1ro_A,
                cupos_1ro_B=cupos_1ro_B,
                cupos_1ro_C=cupos_1ro_C,
                cupos_2do_A=cupos_2do_A,
                cupos_2do_B=cupos_2do_B,
                cupos_2do_C=cupos_2do_C,
                cupos_3ro_A=cupos_3ro_A,
                cupos_3ro_B=cupos_3ro_B,
                cupos_3ro_C=cupos_3ro_C,
                cupos_tecnico=cupos_tecnico
            )

        return render(request, "Cant_Estudiantes.html")