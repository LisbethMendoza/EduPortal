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

def agregar_pregunta(request):
    if request.method == "POST":
        accion = request.POST.get("accion")
        id_input = request.POST.get("id_input")
        pregunta = request.POST.get("pregunta")
        respuesta = request.POST.get("respuesta")

        if accion == "guardar":
            if id_input:  
                try:
                    obj = ChatBotMensaje.objects.get(id_chat=id_input)
                    obj.pregunta = pregunta
                    obj.respuesta = respuesta
                    obj.estado = 'activo'
                    obj.save()
                    print("🔄 Pregunta actualizada:", pregunta)
                except ChatBotMensaje.DoesNotExist:
                    print("❌ No se encontró el ID para actualizar. Se creará nuevo.")
                    ChatBotMensaje.objects.create(
                        pregunta=pregunta, respuesta=respuesta, estado='activo'
                    )
            else:  
                ChatBotMensaje.objects.create(
                    pregunta=pregunta, respuesta=respuesta, estado='activo'
                )
                print("✅ Pregunta nueva guardada:", pregunta)

        elif accion == "eliminar":
            try:
                obj = ChatBotMensaje.objects.get(pregunta=pregunta)
                obj.estado = "eliminado"
                obj.save()
                print("🗑️ Pregunta eliminada:", pregunta)
            except ChatBotMensaje.DoesNotExist:
                print("❌ No se encontró la pregunta para eliminar:", pregunta)
            return redirect("agregar_pregunta")

        return redirect("agregar_pregunta")
    mensajes_activos = ChatBotMensaje.objects.filter(estado='activo').order_by('id_chat')
    return render(request, 'Chat.html', {'mensajes': mensajes_activos})



def obtener_pregunta(request, id_chat):
    try:
        mensaje = ChatBotMensaje.objects.get(id_chat=id_chat)
        data = {
            'pregunta': mensaje.pregunta,
            'respuesta': mensaje.respuesta,
        }
        return JsonResponse(data)
    except ChatBotMensaje.DoesNotExist:
        return JsonResponse({'error': 'No se encontró la pregunta'}, status=404)


from django.http import JsonResponse
from django.template import Context, Template

def cargar_tbody(request):
    mensajes = ChatBotMensaje.objects.filter(estado='activo').order_by('id_chat')
    
    # Simular un fragmento con Template en lugar de archivo
    html = """
    {% for mensaje in mensajes %}
    <tr>
      <td>{{ forloop.counter }}</td>
      <td>{{ mensaje.pregunta }}</td>
      <td>{{ mensaje.respuesta }}</td>
    </tr>
    {% empty %}
    <tr>
      <td colspan="3" style="text-align:center;">No hay preguntas registradas.</td>
    </tr>
    {% endfor %}
    """

    template = Template(html)
    context = Context({'mensajes': mensajes})
    tbody_html = template.render(context)

    return JsonResponse({'tbody': tbody_html})
