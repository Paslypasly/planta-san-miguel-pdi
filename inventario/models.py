from django.db import models
from core.models import BaseModel
from productos.models import Producto


class Ubicacion(BaseModel):
    TIPO_UBICACION = [
        ("PLANTA", "Planta"),
        ("BODEGA", "Bodega"),
        ("VEHICULO", "Vehículo"),
        ("OTRO", "Otro"),
    ]

    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_UBICACION)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class StockUbicacion(BaseModel):
    ubicacion = models.ForeignKey(
        Ubicacion,
        on_delete=models.CASCADE,
        related_name="stocks"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="stocks"
    )
    cantidad = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=0)
    stock_maximo = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Stock por ubicación"
        verbose_name_plural = "Stocks por ubicación"
        unique_together = ("ubicacion", "producto")

    def __str__(self):
        return f"{self.producto} en {self.ubicacion}: {self.cantidad} ud."

    def stock_disponible(self) -> int:
        return self.cantidad

    def incrementar(self, cantidad: int):
        """
        Incrementa el stock en 'cantidad' unidades.
        Uso típico: recepción de compra, retorno de bidones.
        """
        if cantidad <= 0:
            raise ValueError("La cantidad a incrementar debe ser positiva.")
        self.cantidad += cantidad
        self.save()

    def decrementar(self, cantidad: int):
        """
        Decrementa el stock en 'cantidad' unidades.
        Valida que exista stock suficiente.
        """
        if cantidad <= 0:
            raise ValueError("La cantidad a decrementar debe ser positiva.")
        if cantidad > self.cantidad:
            raise ValueError("No hay stock suficiente para realizar la salida.")
        self.cantidad -= cantidad
        self.save()

    def esta_bajo_minimo(self) -> bool:
        """
        Retorna True si el stock actual está por debajo del mínimo configurado.
        """
        if self.stock_minimo is None:
            return False
        return self.cantidad < self.stock_minimo

class MovimientoInventario(BaseModel):
    TIPO_MOVIMIENTO = [
        ("ENTRADA", "Entrada"),
        ("SALIDA", "Salida"),
        ("TRASLADO", "Traslado"),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    ubicacion_origen = models.ForeignKey(
        Ubicacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_salida"
    )
    ubicacion_destino = models.ForeignKey(
        Ubicacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_entrada"
    )
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.PositiveIntegerField()
    referencia = models.CharField(
        max_length=100,
        blank=True,
        help_text="Referencia a pedido, compra, producción, etc."
    )

    class Meta:
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"

    def __str__(self):
        return f"{self.tipo} {self.cantidad} {self.producto}"
