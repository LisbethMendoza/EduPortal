from django.shortcuts import render
from .models import cupo
from tecnico.models import Tecnico
from cupotecnico.models import CupoTecnico
from grado.models import Grado  # Importa tu modelo Grado

def configurar_cupos(request):
    if request.method == "POST":
        # ------------------- Datos generales -------------------
        tipo = request.POST.get("tipo")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_limite = request.POST.get("fecha_limite")

        # ------------------- Cupos por sección (1ro a 3ro) -------------------
        cupos_1ro_A = int(request.POST.get("cupos_1ro_A") or 0)
        cupos_1ro_B = int(request.POST.get("cupos_1ro_B") or 0)
        cupos_1ro_C = int(request.POST.get("cupos_1ro_C") or 0)

        cupos_2do_A = int(request.POST.get("cupos_2do_A") or 0)
        cupos_2do_B = int(request.POST.get("cupos_2do_B") or 0)
        cupos_2do_C = int(request.POST.get("cupos_2do_C") or 0)

        cupos_3ro_A = int(request.POST.get("cupos_3ro_A") or 0)
        cupos_3ro_B = int(request.POST.get("cupos_3ro_B") or 0)
        cupos_3ro_C = int(request.POST.get("cupos_3ro_C") or 0)

        # ------------------- Cupos globales para técnicos -------------------
        cupos_tecnicos_valor = int(request.POST.get("cupos_tecnicos") or 0)

        # ------------------- Buscar o crear registro principal de cupo -------------------
        registro, created = cupo.objects.get_or_create(tipo=tipo)
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
        registro.save()

        # ------------------- Asignar el cupo a todos los técnicos activos por grado (4to, 5to, 6to) -------------------
        tecnicos = Tecnico.objects.filter(estado__iexact="activo")
        grados_tecnicos = Grado.objects.filter(grado__in=["4to", "5to", "6to"])

        for tecnico in tecnicos:
            for grado in grados_tecnicos:
                CupoTecnico.objects.update_or_create(
                    cupo=registro,
                    tecnico=tecnico,
                    grado=grado,
                    defaults={'cantidad': cupos_tecnicos_valor}
                )

        # ------------------- Retornar página con datos actualizados -------------------
        return render(request, "Cant_Estudiantes.html", {
            "tecnicos": tecnicos,
            "registro": registro
        })

    # ------------------- GET: Mostrar técnicos activos y cupos existentes -------------------
    tecnicos = Tecnico.objects.filter(estado__iexact="activo")
    return render(request, "Cant_Estudiantes.html", {"tecnicos": tecnicos})
