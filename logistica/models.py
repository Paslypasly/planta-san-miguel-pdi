from django.db import models
from django.conf import settings
from core.models import BaseModel
from ventas.models import Pedido


class Vehiculo(BaseModel):
    patente = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50, blank=True)
    modelo = models.CharField(max_length=50, blank=True)
    capacidad_litros = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

    def __str__(self):
        return self.patente


class Ruta(BaseModel):
    nombre = models.CharField(max_length=100)
    fecha = models.DateField()
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.PROTECT,
        related_name="rutas"
    )
    conductor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rutas_asignadas"
    )

    class Meta:
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas"

    def __str__(self):
        return f"{self.nombre} - {self.fecha}"


class DetalleRuta(BaseModel):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name="detalles")
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT, related_name="rutas")
    orden = models.PositiveIntegerField(
        help_text="Orden sugerido de visita dentro de la ruta"
    )
    entregado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Detalle de ruta"
        verbose_name_plural = "Detalles de ruta"
        ordering = ["orden"]

    def __str__(self):
        return f"{self.pedido} en {self.ruta} (orden {self.orden})"
