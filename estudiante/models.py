from django.db import models
from grado.models import Grado
from tecnico.models import Tecnico
from tutor.models import Tutor

class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"