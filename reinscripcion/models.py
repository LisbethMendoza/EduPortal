from django.db import models
from estudiante.models import Estudiante

class Reinscripcion(models.Model):
    id_reinscripcion = models.AutoField(primary_key=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    periodo_escolar = models.CharField(max_length=20)
    estado = models.CharField(max_length=50, default='Pendiente')
    documento_pdf = models.FileField(upload_to='documentos/reinscripciones/')
    fecha_reinscripcion = models.DateField(auto_now_add=True)
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Reinscripción de {self.estudiante} - {self.periodo_escolar}"
    