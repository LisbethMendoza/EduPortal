from django.shortcuts import render, redirect
from usuario.models import Usuario
from .models import Aviso
from django.http import JsonResponse


def aviso_adm(request): #Poner esto en los demas form
    if 'usuario_id' not in request.session:
        return redirect('login')  

    nombre = request.session.get('usuario_nombre', 'Invitado')
    return render(request, 'avisos.html', {'nombre': nombre})


def login_usuario(request): #Poner esto en los demas form
    if request.method == 'POST':
        nombre = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')

        try:
            usuario = Usuario.objects.get(nombre=nombre, contrasena=contrasena)

            request.session['usuario_id'] = usuario.id_usuario
            request.session['usuario_nombre'] = usuario.nombre

            return redirect('pagina_admin')  
        except Usuario.DoesNotExist:
            return render(request, 'Login.html', {'error': 'Usuario o contraseña incorrectos'})

    return render(request, 'Login.html')

#-------------------------------------------------------------------------------------------

def Insertar_aviso(request):
    nombre_usuario = request.session.get('usuario_nombre')

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "publicar":
            id_aviso = request.POST.get("id_aviso")  # Puede venir vacío si es nuevo
            titulo = request.POST.get("titulo")
            descripcion = request.POST.get("descripcion")
            fecha_publi = request.POST.get("fecha_publi")
            usuario_id = request.session.get('usuario_id')


            try:
                usuario = Usuario.objects.get(id_usuario=usuario_id)

                if id_aviso:  # Si viene un id, actualizamos
                    try:
                        aviso = Aviso.objects.get(id_aviso=id_aviso)
                        aviso.titulo = titulo
                        aviso.descripcion = descripcion
                        aviso.fecha_publi = fecha_publi
                        aviso.estado = 'activo'

                        aviso.save()
                    except Aviso.DoesNotExist:
                        return render(request, 'avisos.html', {
                            'nombre': nombre_usuario,
                            'error': 'Aviso no encontrado para actualizar'
                        })
                else:  # Si no hay id, creamos uno nuevo
                    aviso = Aviso(
                        id_usuario=usuario,
                        titulo=titulo,
                        descripcion=descripcion,
                        fecha_publi=fecha_publi,
                        estado='activo'
                    )
                    aviso.save()

                return redirect('avisos')

            except Usuario.DoesNotExist:
                return render(request, 'avisos.html', {
                    'nombre': nombre_usuario,
                    'error': 'Usuario no válido'
                })
    return render(request, 'avisos.html', {'nombre': nombre_usuario})


def obtener_aviso_por_titulo(request):
    titulo = request.GET.get('titulo', '')
    try:
        aviso = Aviso.objects.get(titulo__iexact=titulo)
        return JsonResponse({
            'id_aviso': aviso.id_aviso,
            'titulo': aviso.titulo,
            'descripcion': aviso.descripcion,
            'fecha_publi': aviso.fecha_publi.strftime('%Y-%m-%d'),
        })
    except Aviso.DoesNotExist:
        return JsonResponse({'error': 'Aviso no encontrado'}, status=404)
    
    
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def eliminar_aviso(request):
    if request.method == "POST":
        titulo = request.POST.get('titulo', '').strip()

        try:
            aviso = Aviso.objects.get(titulo__iexact=titulo)

            if (aviso.estado or '').lower() != 'eliminado':
                aviso.estado = 'eliminado'
                aviso.save()
                return JsonResponse({'success': 'Aviso fue eliminado para el publico'})
            
            else:
                return JsonResponse({'limpiar': 'Aviso ya estaba eliminado'}, status=200)

        except Aviso.DoesNotExist:
            return JsonResponse({'limpiar': 'Aviso no encontrado'}, status=200)

    return JsonResponse({'error': 'Método no permitido'}, status=405)