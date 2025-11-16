from django.db import models
from core.models import EntidadConRut, BaseModel


class SectorEntrega(BaseModel):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    direccion_referencia = models.CharField(
        max_length=255,
        help_text="Referencia general (calle, villa, sector)"
    )
    enlace_maps = models.URLField(
        blank=True,
        help_text="URL opcional a Google Maps"
    )

    class Meta:
        verbose_name = "Sector de entrega"
        verbose_name_plural = "Sectores de entrega"

    def __str__(self):
        return self.nombre


class Cliente(EntidadConRut):
    nombre_razon_social = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion_cobranza = models.CharField(
        max_length=255,
        help_text="Dirección para facturación o cobranza"
    )
    sector_entrega_principal = models.ForeignKey(
        SectorEntrega,
        on_delete=models.PROTECT,
        related_name="clientes",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.nombre_razon_social} ({self.rut_completo()})"
