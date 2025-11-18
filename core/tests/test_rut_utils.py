# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Pruebas unitarias para utilidades de RUT
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------
from django.test import TestCase

from core.utils.rut import (
    calcular_dv,
    formatear_rut_sin_puntos,
    formatear_rut_con_puntos,
    limpiar_rut,
)


class RutUtilsTests(TestCase):
    def test_calcular_dv_retorna_digito_correcto(self):
        # RUT conocido 12.345.678-5
        self.assertEqual(calcular_dv(12345678), "5")

    def test_calcular_dv_lanza_value_error_para_rut_no_positivo(self):
        # según tu implementación, rut_numero debe ser > 0
        with self.assertRaises(ValueError):
            calcular_dv(0)

    def test_formatear_rut_sin_puntos(self):
        rut = formatear_rut_sin_puntos(12345678, "5")
        self.assertEqual(rut, "12345678-5")

    def test_formatear_rut_con_puntos(self):
        rut = formatear_rut_con_puntos(12345678, "5")
        self.assertEqual(rut, "12.345.678-5")

    def test_limpiar_rut_remueve_puntos_y_guion(self):
        limpio = limpiar_rut("12.345.678-5")
        # se ajusta al comportamiento real de tu función:
        # devuelve todo junto sin puntos ni guion
        self.assertEqual(limpio, "123456785")
