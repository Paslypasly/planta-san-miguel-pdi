# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Mixins para la aplicación Django
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------

from typing import Iterable
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .utils import usuario_tiene_rol


class RolRequiredMixin(LoginRequiredMixin):
    """
    Mixin genérico para vistas basadas en clases.

    Uso:
        class DashboardOperarioView(RolRequiredMixin, TemplateView):
            allowed_roles = ["OPERARIO"]
    """

    allowed_roles: Iterable[str] | None = None

    def dispatch(self, request, *args, **kwargs):
        # Primero exige login (LoginRequiredMixin)
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Superusuario siempre permitido
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if not self.allowed_roles:
            # Si alguien olvidó definir allowed_roles, lo consideramos error de diseño
            raise PermissionDenied("La vista no define roles permitidos.")

        if not usuario_tiene_rol(request.user, list(self.allowed_roles)):
            # Usuario autenticado pero sin rol adecuado
            raise PermissionDenied("No tiene permiso para acceder a esta vista.")

        return super().dispatch(request, *args, **kwargs)


# ───────── Mixins específicos por rol (azúcar sintáctico) ─────────

class AdminRequiredMixin(RolRequiredMixin):
    allowed_roles = ["ADMIN"]


class OperarioRequiredMixin(RolRequiredMixin):
    allowed_roles = ["OPERARIO"]


class ConductorRequiredMixin(RolRequiredMixin):
    allowed_roles = ["CONDUCTOR"]


class GerenteRequiredMixin(RolRequiredMixin):
    allowed_roles = ["GERENTE"]


class TecnicoRequiredMixin(RolRequiredMixin):
    allowed_roles = ["TECNICO"]


class AuditorRequiredMixin(RolRequiredMixin):
    allowed_roles = ["AUDITOR"]
