from django.db import models
from core.models import BaseModel
from inventario.models import Ubicacion


class Estanque(BaseModel):
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100)
    capacidad_litros = models.DecimalField(max_digits=10, decimal_places=2)
    ubicacion = models.ForeignKey(
        Ubicacion,
        on_delete=models.PROTECT,
        related_name="estanques"
    )
    altura_cm = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Altura física aproximada del estanque (para cálculo de nivel)"
    )

    class Meta:
        verbose_name = "Estanque"
        verbose_name_plural = "Estanques"

    def __str__(self):
        return f"{self.nombre} ({self.capacidad_litros} L)"

    def nivel_porcentaje(self, volumen_actual_litros: float) -> float:
        if self.capacidad_litros <= 0:
            return 0
        return float((volumen_actual_litros / float(self.capacidad_litros)) * 100)

    def capacidad_disponible(self, volumen_actual_litros: float) -> float:
        """
        Litros que aún caben en el estanque antes de llegar a su capacidad máxima.
        """
        disponible = float(self.capacidad_litros) - float(volumen_actual_litros)
        return max(disponible, 0.0)

    def esta_sobre_capacidad(self, volumen_actual_litros: float) -> bool:
        """
        Indica si el volumen actual supera la capacidad nominal del estanque.
        """
        return float(volumen_actual_litros) > float(self.capacidad_litros)