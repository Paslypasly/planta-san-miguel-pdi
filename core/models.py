# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Modelos base para la aplicación Django
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------

from django.db import models
from django.core.exceptions import ValidationError

# Utilidades de RUT centralizadas
from core.utils.rut import (
    calcular_dv,
    formatear_rut_sin_puntos,
    formatear_rut_con_puntos,
)

# ───────────────────────────────────────────────
#   Modelo base 1: timestamps automáticos
# ───────────────────────────────────────────────
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ───────────────────────────────────────────────
#   Modelo base 2: entidad con estado activo/inactivo
# ───────────────────────────────────────────────
class BaseModel(TimeStampedModel):
    activo = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def desactivar(self):
        """Desactiva la entidad (soft delete)."""
        self.activo = False
        self.save()

    def activar(self):
        """Activa la entidad nuevamente."""
        self.activo = True
        self.save()


# ───────────────────────────────────────────────
#   Modelo base 3: Entidades con RUT chileno
#   (Clientes, proveedores, conductores, usuarios con RUT)
# ───────────────────────────────────────────────
class EntidadConRut(BaseModel):
    rut_numero = models.PositiveIntegerField(
        help_text="RUT sin puntos y sin dígito verificador"
    )
    rut_dv = models.CharField(
        max_length=1,
        help_text="Dígito verificador calculado automáticamente",
        editable=False,
    )

    class Meta:
        abstract = True
        verbose_name = "Entidad con RUT"

    def clean(self):
        """
        Calcula SIEMPRE el DV en base a rut_numero.
        Sobrescribe el DV previo para asegurar consistencia.
        """
        super().clean()
        if self.rut_numero:
            self.rut_dv = calcular_dv(self.rut_numero)

    # ──────────────────────────────
    #   Representaciones de RUT
    # ──────────────────────────────
    @property
    def rut_sin_puntos(self) -> str:
        """Ej: 12345678-5"""
        return formatear_rut_sin_puntos(self.rut_numero, self.rut_dv)

    @property
    def rut_con_puntos(self) -> str:
        """Ej: 12.345.678-5"""
        return formatear_rut_con_puntos(self.rut_numero, self.rut_dv)

    def rut_completo(self) -> str:
        """Alias para rut_sin_puntos (compatibilidad con admin)."""
        return self.rut_sin_puntos

    def __str__(self):
        # Para logs y admin, sin puntos es más claro
        return self.rut_sin_puntos
