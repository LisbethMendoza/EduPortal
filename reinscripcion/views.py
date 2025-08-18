from django.shortcuts import render,redirect
from grado.models import Grado
from tecnico.models import Tecnico
from inscripcion.models import Inscripcion
from estudiante.models import Estudiante
from django.http import JsonResponse
from reinscripcion.models import Reinscripcion
from datetime import date
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.utils import timezone
from django.conf import settings
import os


def generar_contrato(request, codigo):
    try:
        estudiante = Estudiante.objects.get(codigo=codigo)
    except Estudiante.DoesNotExist:
        return HttpResponse("Estudiante no encontrado", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="contrato_{estudiante.nombre}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'imagenes', 'logo.jpg')
    # Encabezado
    
    c.setFont("Helvetica-Bold", 16)
    c.drawImage(ruta_logo, width / 2 - 50, height - 100, width=100, height=50)
    c.drawCentredString(width / 2, height - 50, "Contrato de Reinscripción Politécnico Ana Silva Jiménez de Castro")

    # Fecha actual
    fecha = timezone.now().strftime("%d/%m/%Y")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Fecha: {fecha}")

    c.drawString(50, height - 130, f"Nombre del estudiante: {estudiante.nombre} {estudiante.apellido}")
    c.drawString(50, height - 160, f"Nombre del tutor: {estudiante.tutor.nombre} {estudiante.tutor.apellido}")

    # Texto del contrato
    texto_contrato = (
    """Por la presente, me dirijo a usted con el fin de formalizar la reinscripción de mi hijo(a) 
en el Politécnico Ana Silva Jiménez de Castro para el próximo período académico. Reconozco la 
importancia de la educación continua y deseo que mi hijo(a) siga recibiendo la formación integral 
que esta institución ofrece, tanto en el ámbito académico como en el desarrollo de valores y 
habilidades sociales.

Asimismo, como tutor(a), me comprometo a cumplir estrictamente con las normas y reglamentos 
establecidos por la institución. Entiendo que la participación activa de mi hijo(a) en todas las 
actividades académicas y extracurriculares, según el calendario escolar, es fundamental para su 
desarrollo y aprovechamiento educativo.

Cualquier incumplimiento de estas normas podrá derivar en medidas disciplinarias, las cuales 
aceptaré y respetaré como parte del compromiso con la formación de mi hijo(a). Confío en que la 
institución continuará proporcionando un ambiente seguro, respetuoso y propicio para el aprendizaje, 
contribuyendo al crecimiento integral de mi hijo(a).

Agradezco de antemano la atención prestada a esta reinscripción y quedo a disposición para cumplir 
con cualquier requisito adicional que sea necesario para completar el proceso formal."""
)


    y = height - 200
    for linea in texto_contrato.split('\n'):
        c.drawString(50, y, linea)
        y -= 20

    # Línea para la firma
    c.drawString(50, y - 50, " Firma del tutor: ___________________________")

    c.showPage()
    c.save()
    return response




def C_Tecnico(request):
    grados = Grado.objects.filter(estado='activo')
    tecnicos = Tecnico.objects.filter(estado='activo')
    return render(request, 'reinscripcion.html', {'grados': grados, 'tecnicos': tecnicos})


    
    
def buscar_estudiante(request):
    codigo = request.GET.get('codigo', '').strip()

    try:
        estudiante = Estudiante.objects.select_related('grado', 'tecnico').get(codigo=codigo)

        inscripcion = Inscripcion.objects.filter(estudiante=estudiante).order_by('-fecha_inscripcion').first()
        seccion = inscripcion.seccion if inscripcion else ''

        reinscripcion = Reinscripcion.objects.filter(estudiante=estudiante).order_by('-fecha_reinscripcion').first()

        if reinscripcion:
            origen = 'reinscripcion'
            periodo_escolar = reinscripcion.periodo_escolar
            estado = reinscripcion.estado
        else:
            origen = 'inscripcion'
            periodo_escolar = inscripcion.periodo_escolar if inscripcion else ''
            estado = inscripcion.estado if inscripcion else 'Pendiente'

        grado_actual = estudiante.grado
        try:
            siguiente_grado = Grado.objects.get(id_grado=grado_actual.id_grado + 1)
        except Grado.DoesNotExist:
            siguiente_grado = grado_actual

        data = {
            'codigo': estudiante.codigo, 
            'nombre': f"{estudiante.nombre} {estudiante.apellido}",
            'grado_id': siguiente_grado.id_grado,
            'tecnico_id': estudiante.tecnico.id_tecnico if estudiante.tecnico else None,
            'origen': origen,
            'periodo_escolar': periodo_escolar,
            'estado': estado,
            'seccion': seccion,  # Siempre viene de Inscripcion
        }

        return JsonResponse({'success': True, 'data': data})

    except Estudiante.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Estudiante no encontrado'})




def reinscripcion_insert(request):
    if request.method == 'POST':
        # Guardar datos en sesión
        request.session['reinscripcion_data'] = {
            'id_estudiante': request.POST['id_estudiante'],
            'id_grado': request.POST['id_grado'],
            'seccion': request.POST.get('seccion', ''),  # para grados que requieren sección
            'id_tecnico': request.POST.get('id_tecnico', None),  # para grados que requieren técnico
            'periodo': request.POST['periodo'],
            'estado': request.POST['estado'],
        }
        # Redirigir al formulario de PDF
        return redirect('documentacion_re')  

    return render(request, 'reinscripcion.html', {
        'grados': Grado.objects.all(),
        'tecnicos': Tecnico.objects.all(),
    })


def reinscripcion_re(request):
    datos = request.session.get('reinscripcion_data')
    if not datos:
        return redirect('reinscripcion_insert')  # Si no hay datos, volvemos al primer formulario

    if request.method == 'POST':
        # Obtener estudiante seguro
        estudiante = Estudiante.objects.get(codigo=datos['id_estudiante'])

        # Asignar técnico solo si viene en los datos
        if datos.get('id_tecnico'):
            estudiante.tecnico_id = datos['id_tecnico']
            estudiante.save()

        # Crear la reinscripción
        Reinscripcion.objects.create(
            estudiante=estudiante,
            periodo_escolar=datos['periodo'],
            estado=datos['estado'],
            documento_pdf=request.FILES['archivo_pdf'],  
        )


        del request.session['reinscripcion_data']

    return render(request, 'documentacion_re.html')