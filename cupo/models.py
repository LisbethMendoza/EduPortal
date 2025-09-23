from django.db import models

from django.db import models

class cupo(models.Model):
    TIPO_CHOICES = [
        ("Inscripcion", "Inscripción"),
        ("Reinscripcion", "Reinscripción")
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha_inicio = models.DateField()
    fecha_limite = models.DateField()

    cupos_1ro = models.PositiveIntegerField(default=0)
    cupos_2do = models.PositiveIntegerField(default=0)
    cupos_3ro = models.PositiveIntegerField(default=0)
    cupos_tecnico = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.tipo} ({self.fecha_inicio} - {self.fecha_limite})"
