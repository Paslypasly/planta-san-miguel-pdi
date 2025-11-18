from django.conf import settings
from django.db import models

from core.models import EntidadConRut


# ─────────────────────────────────────
#  Roles del sistema (definidos en 2.1)
# ─────────────────────────────────────
ROLES_CHOICES = [
    ("ADMIN", "Administrador"),
    ("OPERARIO", "Operario de Planta"),
    ("CONDUCTOR", "Conductor"),
    ("GERENTE", "Gerente"),
    ("TECNICO", "Técnico / Mantención"),
    ("AUDITOR", "Auditor"),
]


class Perfil(EntidadConRut):
    """
    Extiende al usuario de Django con:
    - RUT normalizado (rut_numero, rut_dv)
    - Rol de sistema
    - Datos de contacto
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    rol = models.CharField(max_length=10, choices=ROLES_CHOICES)
    telefono_contacto = models.CharField(max_length=20, blank=True)
    cargo = models.CharField(
        max_length=100,
        blank=True,
        help_text="Cargo o rol dentro de la planta (ej: Operario, Gerente)"
    )

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"

    # ─────────────────────────────
    #   Helpers de rol 
    # ─────────────────────────────
    def es_admin(self) -> bool:
        return self.rol == "ADMIN"

    def es_operario(self) -> bool:
        return self.rol == "OPERARIO"

    def es_conductor(self) -> bool:
        return self.rol == "CONDUCTOR"

    def es_gerente(self) -> bool:
        return self.rol == "GERENTE"

    def es_tecnico(self) -> bool:
        return self.rol == "TECNICO"

    def es_auditor(self) -> bool:
        return self.rol == "AUDITOR"

    @property
    def nombre_mostrable(self) -> str:
        """
        Devuelve un nombre amigable para mostrar en la interfaz.
        Prioriza nombre completo del usuario de Django.
        """
        full_name = self.user.get_full_name()
        if full_name:
            return full_name
        return self.user.username
