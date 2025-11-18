import re
from typing import Tuple


RUT_CLEAN_REGEX = re.compile(r"[^0-9kK]")


class RutInvalidoError(ValueError):
    """Excepción específica para errores de RUT."""
    pass


def limpiar_rut(rut_str: str) -> str:
    """
    Elimina puntos, guiones y cualquier carácter no permitido.
    Deja solo dígitos y 'K'/'k'.
    """
    if rut_str is None:
        raise RutInvalidoError("El RUT no puede ser None.")
    rut_limpio = RUT_CLEAN_REGEX.sub("", rut_str)
    if not rut_limpio:
        raise RutInvalidoError("El RUT está vacío después de limpiarlo.")
    return rut_limpio


def separar_rut(rut_str: str) -> Tuple[int, str]:
    """
    Recibe un RUT en cualquier formato (12.345.678-5, 12345678-5, 123456785)
    y retorna (rut_numero, dv) normalizados.

    - rut_numero: int (solo los dígitos sin DV)
    - dv: str (un solo carácter, 0-9 o K)
    """
    rut_limpio = limpiar_rut(rut_str)

    if len(rut_limpio) < 2:
        raise RutInvalidoError("El RUT debe tener al menos 2 caracteres (número + DV).")

    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1].upper()

    if not cuerpo.isdigit():
        raise RutInvalidoError("La parte numérica del RUT contiene caracteres no válidos.")

    rut_numero = int(cuerpo)
    if rut_numero <= 0:
        raise RutInvalidoError("El número de RUT debe ser mayor que cero.")

    if not (dv.isdigit() or dv == "K"):
        raise RutInvalidoError("El dígito verificador debe ser 0-9 o K.")

    return rut_numero, dv


def calcular_dv(rut_numero: int) -> str:
    """
    Calcula el dígito verificador de un RUT chileno según el algoritmo oficial.
    """
    if rut_numero <= 0:
        raise RutInvalidoError("El número de RUT debe ser mayor que cero.")

    reversed_digits = map(int, reversed(str(rut_numero)))
    factors = [2, 3, 4, 5, 6, 7]
    s = 0
    for i, d in enumerate(reversed_digits):
        s += d * factors[i % len(factors)]
    dv = 11 - (s % 11)
    if dv == 11:
        return "0"
    if dv == 10:
        return "K"
    return str(dv)


def validar_rut_coincide(rut_numero: int, dv: str) -> bool:
    """
    Valida que el DV entregado coincide con el DV calculado para rut_numero.
    """
    dv = dv.upper()
    dv_calculado = calcular_dv(rut_numero)
    return dv_calculado == dv


def rut_es_valido(rut_str: str) -> bool:
    """
    Valida un RUT en formato libre.
    Retorna True si el RUT es válido (estructura + DV correcto).
    """
    try:
        rut_numero, dv = separar_rut(rut_str)
        return validar_rut_coincide(rut_numero, dv)
    except RutInvalidoError:
        return False


def formatear_rut_sin_puntos(rut_numero: int, dv: str) -> str:
    """
    Devuelve el RUT formateado como '12345678-9' (sin puntos).
    """
    return f"{rut_numero}-{dv.upper()}"


def formatear_rut_con_puntos(rut_numero: int, dv: str) -> str:
    """
    Devuelve el RUT formateado como '12.345.678-9'.
    Solo efecto visual, no para guardar en BD.
    """
    cuerpo = f"{rut_numero}"
    partes = []
    while len(cuerpo) > 3:
        partes.insert(0, cuerpo[-3:])
        cuerpo = cuerpo[:-3]
    partes.insert(0, cuerpo)
    cuerpo_con_puntos = ".".join(partes)
    return f"{cuerpo_con_puntos}-{dv.upper()}"
