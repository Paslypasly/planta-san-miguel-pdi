from django.db import models
from core.models import BaseModel


class Producto(BaseModel):
    TIPO_PRODUCTO = [
        ("BIDON", "Bidón de agua"),
        ("INSUMO", "Insumo planta (tapas, sello, filtro, sal, etc.)"),
    ]

    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_PRODUCTO, default="BIDON")
    presentacion_litros = models.DecimalField(
        max_digits=6, decimal_places=2,
        help_text="Capacidad en litros (ej. 20.00)"
    )
    precio_lista = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Precio de lista por unidad"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.nombre} ({self.presentacion_litros} L)"

    def es_bidon(self) -> bool:
        return self.tipo == "BIDON"
