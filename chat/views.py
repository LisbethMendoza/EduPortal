from django.shortcuts import render, redirect
from usuario.models import Usuario
from django.http import JsonResponse
from .models import ChatBotMensaje

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

#------------------------------------------------------------------------------------------------------

