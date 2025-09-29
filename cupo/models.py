from django.db import models
class cupo(models.Model):
    TIPO_CHOICES = [
        ("Inscripcion", "Inscripción"),
        ("Reinscripcion", "Reinscripción")
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha_inicio = models.DateField()
    fecha_limite = models.DateField()

    # Cupos por sección
    cupos_1ro_A = models.PositiveIntegerField(default=0)
    cupos_1ro_B = models.PositiveIntegerField(default=0)
    cupos_1ro_C = models.PositiveIntegerField(default=0)

    cupos_2do_A = models.PositiveIntegerField(default=0)
    cupos_2do_B = models.PositiveIntegerField(default=0)
    cupos_2do_C = models.PositiveIntegerField(default=0)

    cupos_3ro_A = models.PositiveIntegerField(default=0)
    cupos_3ro_B = models.PositiveIntegerField(default=0)
    cupos_3ro_C = models.PositiveIntegerField(default=0)

    cupos_tecnico = models.PositiveIntegerField(default=0)  # técnico sigue global

    def __str__(self):
        return f"{self.tipo} ({self.fecha_inicio} - {self.fecha_limite})"
