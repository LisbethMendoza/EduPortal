from django.db import models

# Importamos tus modelos ya existentes
from cupo.models import cupo
from tecnico.models import Tecnico


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
    cantidad = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Cupo por Técnico"
        verbose_name_plural = "Cupos por Técnico"
        unique_together = ('cupo', 'tecnico') 

    def __str__(self):
        return f"{self.tecnico.nombre} ({self.cupo.tipo}) - {self.cantidad}"
