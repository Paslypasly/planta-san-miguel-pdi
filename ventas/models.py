from django.db import models
from core.models import BaseModel
from clientes.models import Cliente, SectorEntrega
from productos.models import Producto


class Pedido(BaseModel):
    ESTADOS_PEDIDO = [
        ("PENDIENTE", "Pendiente"),
        ("PREPARACION", "En preparación"),
        ("DESPACHO", "En despacho"),
        ("ENTREGADO", "Entregado"),
        ("ANULADO", "Anulado"),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="pedidos"
    )
    sector_entrega = models.ForeignKey(
        SectorEntrega,
        on_delete=models.PROTECT,
        related_name="pedidos"
    )
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_comprometida = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha comprometida de entrega"
    )
    estado = models.CharField(
        max_length=15,
        choices=ESTADOS_PEDIDO,
        default="PENDIENTE"
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-fecha_pedido"]

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente}"

    def total(self):
        return sum(det.subtotal() for det in self.detalles.all())

    def cantidad_total(self) -> int:
        """Retorna la cantidad total de unidades en el pedido."""
        return sum(det.cantidad for det in self.detalles.all())

    def esta_entregado(self) -> bool:
        """Indica si el pedido ya fue entregado."""
        return self.estado == "ENTREGADO"

    def puede_modificarse(self) -> bool:
        """
        Un pedido puede modificarse mientras no esté entregado ni anulado.
        """
        return self.estado in ("PENDIENTE", "PREPARACION")

class DetallePedido(BaseModel):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="detalles"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="detalles_pedido"
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de pedido"
        verbose_name_plural = "Detalles de pedido"

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto} en {self.pedido}"

    def es_bidon(self) -> bool:
        """Indica si el producto es un bidón (para métricas específicas)."""
        return self.producto.es_bidon()