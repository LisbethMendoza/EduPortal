from django.db import models

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)  
    rol = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre} ({self.rol})"

