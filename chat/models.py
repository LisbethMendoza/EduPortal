from django.db import models

class ChatBotMensaje(models.Model):
    id_chat = models.AutoField(primary_key=True)
    pregunta = models.CharField(max_length=100, unique=True)
    respuesta = models.TextField()
    estado = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.pregunta} ({self.estado})"
