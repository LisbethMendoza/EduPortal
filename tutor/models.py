from django.db import models

class Tutor(models.Model):
    id_tutor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    parentesco = models.CharField(max_length=50)
    cedula = models.CharField(max_length=20)
    documento_pdf = models.FileField(upload_to='documentos/tutores/')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"