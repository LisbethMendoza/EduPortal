from django.db import models
from cupo.models import cupo
from tecnico.models import Tecnico
from grado.models import Grado  # Asumiendo que tu app se llama 'grado'

class CupoTecnico(models.Model):
    cupo = models.ForeignKey(
        cupo,
        on_delete=models.CASCADE,
        related_name='cupos_tecnicos'
    )
    tecnico = models.ForeignKey(
        Tecnico,
        on_delete=models.CASCADE,
        related_name='cupos_asignados'
    )
    grado = models.ForeignKey(
    Grado,
    on_delete=models.CASCADE,
    related_name='cupos_por_tecnico',
    null=True,  # permite nulos
    blank=True
    )

    cantidad = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Cupo por Técnico"
        verbose_name_plural = "Cupos por Técnico"
        unique_together = ('cupo', 'tecnico', 'grado')  # Ahora único por cupo-tecnico-grado

    def __str__(self):
        return f"{self.tecnico.nombre} ({self.grado.grado}) - {self.cantidad}"
