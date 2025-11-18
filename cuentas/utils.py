# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Utilidades para la aplicación Django
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------

from typing import Optional

from django.contrib.auth.models import AbstractUser

from .models import Perfil


def obtener_rol_usuario(user: AbstractUser) -> Optional[str]:
    """
    Devuelve el código de rol del usuario (ej: 'ADMIN', 'OPERARIO').

    - Si el usuario no está autenticado → None
    - Si no tiene Perfil asociado → None
    """
    if user is None or not user.is_authenticated:
        return None

    try:
        return user.perfil.rol
    except Perfil.DoesNotExist:
        return None


def usuario_tiene_rol(user: AbstractUser, roles_permitidos: list[str]) -> bool:
    """
    True si el usuario tiene alguno de los roles en roles_permitidos.
    Los superusuarios tienen siempre acceso.
    """
    if user is None or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    rol = obtener_rol_usuario(user)
    if rol is None:
        return False

    return rol in roles_permitidos
