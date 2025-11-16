from django.db import models
from django.core.exceptions import ValidationError

# ───────────────────────────────────────────────
#   Modelo base 1: trae timestamps automáticos
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
        """Desactiva la entidad sin borrarla físicamente."""
        self.activo = False
        self.save()

    def activar(self):
        """Activa nuevamente la entidad."""
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
        help_text="Dígito verificador (0-9 o K)"
    )

    class Meta:
        abstract = True
        verbose_name = "Entidad con RUT"

    # ───────────────────────────────────────────────
    #   Método de dominio: calcular DV oficial
    # ───────────────────────────────────────────────
    @staticmethod
    def calcular_dv(rut_numero: int) -> str:
        """
        Calcula el dígito verificador según el algoritmo oficial.
        """
        reversed_digits = map(int, reversed(str(rut_numero)))
        factors = [2, 3, 4, 5, 6, 7]
        s = 0
        for i, d in enumerate(reversed_digits):
            s += d * factors[i % 6]
        dv = 11 - (s % 11)
        if dv == 11:
            return "0"
        if dv == 10:
            return "K"
        return str(dv)

    # ───────────────────────────────────────────────
    #   Validación automática del RUT
    # ───────────────────────────────────────────────
    def clean(self):
        dv_calculado = self.calcular_dv(self.rut_numero)
        if dv_calculado.upper() != self.rut_dv.upper():
            raise ValidationError(
                {
                    "rut_dv": f"DV incorrecto. Debería ser {dv_calculado}"
                }
            )

    # ───────────────────────────────────────────────
    #   Representación amigable
    # ───────────────────────────────────────────────
    def rut_completo(self) -> str:
        """
        Devuelve el RUT formateado sin puntos: 12345678-9
        """
        return f"{self.rut_numero}-{self.rut_dv.upper()}"

    def __str__(self):
        return self.rut_completo()
