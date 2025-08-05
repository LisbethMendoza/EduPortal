from django.db import models

class Tecnico(models.Model):
    id_tecnico = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
