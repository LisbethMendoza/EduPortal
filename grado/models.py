from django.db import models

class Grado(models.Model):
    id_grado = models.AutoField(primary_key=True)
    grado = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return self.grado