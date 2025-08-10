from django.db import models
from django.db.models import Q, UniqueConstraint
from grado.models import Grado
from tecnico.models import Tecnico
from tutor.models import Tutor

class Estudiante(models.Model):
    codigo = models.CharField(max_length=8, null=True, blank=True)  
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE, null=True, blank=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.codigo})"

    class Meta:
        constraints = [
            UniqueConstraint(fields=['codigo'], name='unique_codigo_not_null', condition=Q(codigo__isnull=False))
        ]

