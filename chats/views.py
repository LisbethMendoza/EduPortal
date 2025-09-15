from django.shortcuts import render, redirect
from usuario.models import Usuario
from django.views.decorators.csrf import csrf_exempt


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

# views.py
from django.http import JsonResponse
from .models import Documento
import PyPDF2
from django.shortcuts import get_object_or_404, redirect

def upload_documento(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        archivo = request.FILES.get('archivo')

        if not archivo:
            return JsonResponse({'success': False, 'error': 'No se subió ningún archivo'})

        try:
            # Extraer texto del PDF
            pdf_reader = PyPDF2.PdfReader(archivo)
            texto = ""
            for page in pdf_reader.pages:
                texto += page.extract_text() or ""

            # Guardar en el modelo
            Documento.objects.create(
                titulo=titulo,
                archivo=archivo,
                contenido=texto,
                estado="Activo"
            )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def listar_documentos(request):
    documentos = Documento.objects.all().values("id", "titulo", "archivo", "estado")
    data = list(documentos)
    return JsonResponse({"documentos": data})


