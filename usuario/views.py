from django.shortcuts import render,redirect
from .models import Usuario
from tecnico.models import Tecnico
from django.db import DatabaseError
from django.http import JsonResponse
from django.contrib import messages

#-------------Crear y actualizar Usuarios------------------------------
def usuario_form(request):
    mensaje = ""
    error = ""
    usuario_data = {}

    if request.method == 'POST':
        accion = request.POST.get('accion')
        correo = request.POST.get('correo')
        nombre = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')

        if accion == 'crear':
            try:
                nuevo_usuario = Usuario(
                    nombre=nombre,
                    correo=correo,
                    contrasena=contrasena,
                    rol='Docente' 
                )
                nuevo_usuario.save()
                mensaje = "Usuario creado correctamente."
            except DatabaseError as e:
                error = f"Error de base de datos: {str(e)}"
        
        elif accion == 'actualizar':
            try:
                usuario = Usuario.objects.get(correo=correo)
                if usuario.nombre == nombre and usuario.contrasena == contrasena:
                    mensaje = "Datos cargados para edición."
                else:
                    usuario.nombre = nombre
                    usuario.contrasena = contrasena
                    usuario.save()
                    mensaje = "Usuario actualizado correctamente."
                usuario_data = {
                    'correo': usuario.correo,
                    'usuario': usuario.nombre,
                    'contrasena': usuario.contrasena
                }
            except Usuario.DoesNotExist:
                error = "Usuario no encontrado para actualizar."
            except DatabaseError:
                error = "Error de base de datos."

    return render(request, 'crear_usuario.html', {
        'mensaje': mensaje,
        'error': error,
        'usuario_data': usuario_data
    })

#----------------Obtener los datos de ----------------------------------
def obtener_usuario(request):
    if request.method == 'GET':
        correo = request.GET.get('correo')
        nombre = request.GET.get('usuario')

        try:
            if correo:
                usuario = Usuario.objects.get(correo=correo)
            elif nombre:
                usuario = Usuario.objects.get(nombre=nombre)
            else:
                return JsonResponse({'error': 'No se proporcionó correo ni usuario'}, status=400)

            return JsonResponse({
                'correo': usuario.correo,
                'usuario': usuario.nombre,
                'contrasena': usuario.contrasena
            })

        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

    return JsonResponse({'error': 'Método no permitido'}, status=405)



def login_usuario(request):
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



def pagina_admin(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    nombre = request.session.get('usuario_nombre', 'Invitado')
    return render(request, 'P_ADM.html', {'nombre': nombre})



def aviso_adm(request):
    if 'usuario_id' not in request.session:
        return redirect('login')  

    nombre = request.session.get('usuario_nombre', 'Invitado')
    return render(request, 'avisos.html', {'nombre': nombre})



def revision_estudiantes(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    nombre = request.session.get('usuario_nombre', 'Invitado')
    return render(request, 'Revision_E.html', {'nombre': nombre})




def crear_usuario(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    nombre = request.session.get('usuario_nombre', 'Invitado')
    return render(request, 'crear_usuario.html', {'nombre': nombre})



def chat(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    nombre = request.session.get('usuario_nombre', 'Invitado')
    return render(request, 'Chat.html', {'nombre': nombre})


def Buscar_E(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    nombre = request.session.get('usuario_nombre', 'Invitado')
    return render(request, 'Buscar_E.html', {'nombre': nombre})

def Aprobacion(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    nombre = request.session.get('usuario_nombre', 'Invitado')
    return render(request, 'Aprobados.html', {'nombre': nombre})


def cantidad_estudiantes(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    nombre = request.session.get('usuario_nombre', 'Invitado')
    activos_count = Tecnico.objects.filter(estado='activo').count()  # ✅ Conteo de técnicos activos

    return render(request, 'Cant_Estudiantes.html', {
        'nombre': nombre,
        'activos_count': activos_count,  # ✅ Pasamos al template
    })

#--------------Cierra sesion----------------------------
def logout_usuario(request):
    request.session.flush()  
    return redirect('login') 


def recuperar(request):
    return render(request, 'recuperar.html') 

#--------------Restablece la contrasena----------------------------
def restablecer(request):
    if request.method == 'POST':
        nueva_clave = request.POST.get('nueva_contrasena')
        correo = request.session.get('correo_recuperacion')

        if correo and nueva_clave:
            try:
                usuario = Usuario.objects.get(correo=correo)
                usuario.contrasena = nueva_clave
                usuario.save()

                del request.session['correo_recuperacion']
                messages.success(request, 'Contraseña actualizada correctamente')
                return redirect('login')  # ← Redirige correctamente
            except Usuario.DoesNotExist:
                return render(request, 'restablecer.html', {'error': 'Usuario no encontrado'})
        else:
            return render(request, 'restablecer.html', {'error': 'No se pudo validar el usuario'})
    
    return render(request, 'restablecer.html')







#----------------CORREO ELECTRONICO INFIGURACION---------------------
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse

def enviar_enlace(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')

        request.session['correo_recuperacion'] = correo

        enlace = request.build_absolute_uri(reverse('restablecer'))

        asunto = 'Recuperación de contraseña'
        mensaje = f"Hola,\n\nHaz clic en este enlace para restablecer tu contraseña:\n{enlace}\n\nSi no fuiste tú, ignora este mensaje."

 
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[correo],
            fail_silently=False,
        )

        messages.success(request, '')
        return redirect('login')
    
    return redirect('login')



