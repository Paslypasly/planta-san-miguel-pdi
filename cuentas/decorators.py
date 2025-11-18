# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Decoradores para la aplicación Django
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from .utils import usuario_tiene_rol


def role_required(*roles_permitidos: str):
    """
    Decorador para vistas basadas en funciones.

    Uso:
        @role_required("GERENTE", "ADMIN")
        def dashboard_gerencia(request):
            ...

    - Exige usuario autenticado.
    - Superusuario siempre tiene acceso.
    - Si el usuario no tiene Perfil o el rol no está permitido → 403.
    """

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user = request.user

            # Superusuario siempre puede
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            if not usuario_tiene_rol(user, list(roles_permitidos)):
                raise PermissionDenied("No tiene permiso para acceder a esta vista.")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
