from django.db import models

class Tutor(models.Model):
    id_tutor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    parentesco = models.CharField(max_length=50)
    cedula = models.CharField(max_length=20)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    telefono2 = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

