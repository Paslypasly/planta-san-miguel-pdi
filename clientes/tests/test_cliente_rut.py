# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Pruebas unitarias para el modelo Cliente
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------
from django.core.exceptions import ValidationError
from django.test import TestCase

from clientes.models import Cliente


class ClienteRutTests(TestCase):
    def test_rut_dv_se_calcula_automaticamente_al_validar(self):
        c = Cliente(
            rut_numero=12345678,
            nombre_razon_social="Cliente de prueba",
            direccion_cobranza="Calle X 123",
            telefono="987654321",
            email="cliente@prueba.cl",
        )
        c.full_clean()
        c.save()

        self.assertEqual(c.rut_dv, "5")
        self.assertEqual(c.rut_sin_puntos, "12345678-5")
        self.assertEqual(c.rut_con_puntos, "12.345.678-5")

    def test_rut_numero_es_obligatorio(self):
        c = Cliente(
            nombre_razon_social="Sin RUT",
            direccion_cobranza="Calle X 123",
            telefono="987654321",
            email="cliente@prueba.cl",
        )
        with self.assertRaises(ValidationError):
            c.full_clean()

    def test_str_de_cliente_muestra_rut_y_nombre(self):
        c = Cliente(
            rut_numero=12345678,
            nombre_razon_social="Cliente de prueba",
            direccion_cobranza="Calle X 123",
            telefono="987654321",
            email="cliente@prueba.cl",
        )
        c.full_clean()
        c.save()
        # adapta esto si tu __str__ es distinto,
        # pero al menos que contenga el rut sin puntos.
        self.assertIn("12345678-5", str(c))
