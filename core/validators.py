# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Validadores personalizados para la aplicación Django
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------
from django.core.exceptions import ValidationError

from core.utils.rut import rut_es_valido


def validar_rut_string(value: str):
    """
    Valida un RUT en formato libre (12.345.678-5, 12345678-5, etc.).
    Se usa en formularios que reciben el RUT como un único string.
    """
    if not rut_es_valido(value):
        raise ValidationError("El RUT ingresado no es válido.")
