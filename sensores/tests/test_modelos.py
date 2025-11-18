# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-11-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Pruebas unitarias para modelos de sensores y actuadores Io
# FECHA ÚLTIMA MODIFICACIÓN: 18-11-2025
# ---------------------------------------------------------
from django.test import TestCase
from django.utils import timezone

from sensores.models import Sensor, Actuador, Lectura, Alerta, ReglaControl
from inventario.models import Ubicacion
from planta.models import Estanque


class SensorLecturaTests(TestCase):

    def setUp(self):
        self.ubic = Ubicacion.objects.create(
            codigo="UB-1",
            nombre="Sala 1"
        )

        self.estanque = Estanque.objects.create(
            codigo="EST-1",
            nombre="Estanque 1000L",
            capacidad_litros=1000,
            ubicacion=self.ubic,
            altura_cm=150
        )

        self.sensor = Sensor.objects.create(
            codigo="SEN-1",
            nombre="Sensor Nivel",
            tipo="NIVEL",
            unidad="cm",
            ubicacion=self.ubic,
            estanque=self.estanque,
            rango_min=10,
            rango_max=90,
        )

    def test_crear_lectura(self):
        lectura = Lectura.objects.create(
            sensor=self.sensor,
            valor=50,
            unidad="cm",
            fecha_hora=timezone.now(),
            origen="ESP32"
        )
        self.assertEqual(lectura.valor, 50)
        self.assertFalse(lectura.esta_fuera_de_rango())

    def test_fuera_de_rango(self):
        lectura = Lectura.objects.create(
            sensor=self.sensor,
            valor=200,
            unidad="cm",
            fecha_hora=timezone.now(),
        )
        self.assertTrue(lectura.esta_fuera_de_rango())

