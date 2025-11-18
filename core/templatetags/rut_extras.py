from django import template

from core.utils.rut import (
    formatear_rut_con_puntos,
    formatear_rut_sin_puntos,
    limpiar_rut,
    separar_rut,
)

register = template.Library()


@register.filter
def rut_con_puntos(obj):
    """
    Uso:
      {{ cliente|rut_con_puntos }}
      {{ perfil|rut_con_puntos }}

    El objeto debe tener rut_numero y rut_dv.
    """
    rut_numero = getattr(obj, "rut_numero", None)
    rut_dv = getattr(obj, "rut_dv", None)
    if rut_numero is None or rut_dv is None:
        return ""
    return formatear_rut_con_puntos(rut_numero, rut_dv)


@register.filter
def rut_sin_puntos(obj):
    """
    Mismo uso que rut_con_puntos, pero sin puntos:
      {{ cliente|rut_sin_puntos }}
    """
    rut_numero = getattr(obj, "rut_numero", None)
    rut_dv = getattr(obj, "rut_dv", None)
    if rut_numero is None or rut_dv is None:
        return ""
    return formatear_rut_sin_puntos(rut_numero, rut_dv)


@register.filter
def rut_normalizado(value: str):
    """
    Recibe un string y devuelve solo dígitos y DV (sin puntos ni guiones).
    Ej: "12.345.678-5" -> "123456785"
    Útil para debug/logs.
    """
    try:
        return limpiar_rut(value)
    except Exception:
        return value
