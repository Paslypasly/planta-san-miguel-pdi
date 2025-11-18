# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Pruebas unitarias para la API de sensores y actuadores
# FECHA ÚLTIMA MODIFICACIÓN: 18-11-2025
# ---------------------------------------------------------
from django.test import TestCase
from django.utils.timezone import now
import json

from inventario.models import Ubicacion
from planta.models import Estanque
from sensores.models import Sensor


class APITests(TestCase):

    def setUp(self):
        self.ubic = Ubicacion.objects.create(nombre="Zona B")
        self.estanque = Estanque.objects.create(
            codigo="EST-2",
            nombre="Estanque 2",
            capacidad_litros=500,
            ubicacion=self.ubic,
            altura_cm=120,
        )
        self.sensor = Sensor.objects.create(
            codigo="S-02",
            nombre="IR",
            tipo="IR",
            unidad="uds",
            ubicacion=self.ubic,
            estanque=self.estanque,
        )

    def test_api_ingreso_lectura(self):
        url = "/sensores/api/lectura/"

        payload = {
            # CLAVE CORRECTA SEGÚN procesar_payload_lectura
            "sensor_codigo": self.sensor.codigo,
            "valor": 50.5,
            "unidad": "cm",
            "origen": "ESP32",
            "fecha_hora": "2025-11-18T00:00:00Z",
        }

        resp = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 201)
