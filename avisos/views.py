from django.shortcuts import render, redirect
from usuario.models import Usuario
from .models import Aviso


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
            titulo = request.POST.get("titulo")
            descripcion = request.POST.get("descripcion")
            fecha_publi = request.POST.get("fecha_publi")

           
            usuario_id = request.session.get('usuario_id')
            try:
                usuario = Usuario.objects.get(id_usuario=usuario_id)

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

        elif accion == "eliminar":
            return redirect('avisos') 

    return render(request, 'avisos.html', {'nombre': nombre_usuario})
