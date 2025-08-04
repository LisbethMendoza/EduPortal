from django.db import models
from usuario.models import Usuario

class Aviso(models.Model):
    id_aviso = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_publi = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, blank=True, null=True) 

    def __str__(self):
        return self.titulo



