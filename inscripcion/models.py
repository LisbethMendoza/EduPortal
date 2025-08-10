from django.db import models
from tutor.models import Tutor
from estudiante.models import Estudiante

class Inscripcion(models.Model):
    id_inscripcion = models.AutoField(primary_key=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    periodo_escolar = models.CharField(max_length=20)
    fecha_inscripcion = models.DateField()
    estado = models.CharField(max_length=50, default='Pendiente')
    documento_pdf = models.FileField(upload_to='documentos/inscripciones/')
    seccion = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self):
        return f"Inscripción de {self.estudiante} - {self.periodo_escolar}"
    
    
    