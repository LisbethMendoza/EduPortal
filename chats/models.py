from django.db import models

class Documento(models.Model):
    titulo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to="documentos/", null=True, blank=True)
    contenido = models.TextField()
    estado = models.CharField(max_length=20)

    def __str__(self):
        return self.titulo