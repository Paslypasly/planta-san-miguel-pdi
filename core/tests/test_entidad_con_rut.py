# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Pruebas unitarias para el modelo EntidadConRut
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from core.models import EntidadConRut


class DummyEntidadConRut(EntidadConRut):
    """
    Modelo de prueba para verificar el comportamiento genérico de EntidadConRut.
    """
    nombre = models.CharField(max_length=50)

    class Meta:
        app_label = "core"  


class EntidadConRutModelTests(TestCase):
    def test_calcula_dv_automaticamente_en_clean(self):
        obj = DummyEntidadConRut(
            rut_numero=12345678,
            nombre="Prueba",
        )
        obj.full_clean()  # dispara clean()
        self.assertEqual(obj.rut_dv, "5")

    def test_repr_sin_puntos(self):
        obj = DummyEntidadConRut(
            rut_numero=12345678,
            nombre="Prueba",
        )
        obj.full_clean()
        self.assertEqual(obj.rut_sin_puntos, "12345678-5")

    def test_repr_con_puntos(self):
        obj = DummyEntidadConRut(
            rut_numero=12345678,
            nombre="Prueba",
        )
        obj.full_clean()
        self.assertEqual(obj.rut_con_puntos, "12.345.678-5")

    def test_str_usa_rut_sin_puntos(self):
        obj = DummyEntidadConRut(
            rut_numero=12345678,
            nombre="Prueba",
        )
        obj.full_clean()
        self.assertEqual(str(obj), "12345678-5")

    def test_rut_numero_obligatorio(self):
        obj = DummyEntidadConRut(
            nombre="Sin RUT",
        )
        with self.assertRaises(ValidationError):
            obj.full_clean()
