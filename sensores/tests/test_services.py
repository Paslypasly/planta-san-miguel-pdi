# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Pruebas unitarias para servicios IoT
# FECHA ÚLTIMA MODIFICACIÓN: 18-11-2025
# ---------------------------------------------------------

from django.test import TestCase
from django.utils.timezone import now

from planta.models import Estanque
from inventario.models import Ubicacion
from sensores.models import Sensor, Actuador, ReglaControl, Lectura
from sensores.services import (
    procesar_payload_lectura,
    registrar_lectura,
    evaluar_reglas_sensor,
)


class ServiciosTests(TestCase):

    def setUp(self):
        # Ubicación
        self.ubic = Ubicacion.objects.create(nombre="Zona A")

        # Estanque
        self.estanque = Estanque.objects.create(
            codigo="EST-1000",
            nombre="Estanque 1000L",
            capacidad_litros=1000,
            ubicacion=self.ubic,
            altura_cm=150,
        )

        # Sensor
        self.sensor = Sensor.objects.create(
            codigo="S-01",
            nombre="Ultrasonico",
            tipo="NIVEL",
            unidad="cm",
            ubicacion=self.ubic,
            estanque=self.estanque,
        )

        # Actuador (bomba)
        self.act = Actuador.objects.create(
            codigo="A-01",
            nombre="Bomba",
            tipo="BOMBA",
            gpio="GPIO23",
            ubicacion=self.ubic,
            estanque=self.estanque,
        )

        # Regla de control
        self.regla = ReglaControl.objects.create(
            sensor=self.sensor,
            actuador=self.act,
            condicion="MAYOR",
            umbral=50,
            mensaje_accion="Nivel alto",
            severidad="WARN",
            activo=True,
        )

    # -------------------------------------------------------------
    # TEST 1: Registrar lectura desde un payload
    # -------------------------------------------------------------
    def test_registrar_lectura(self):
        datos = {
            "sensor_codigo": "S-01",
            "valor": 55,
            "unidad": "cm",
            "fecha_hora": now().isoformat(),
            "raw": {"sensor_codigo": "S-01", "valor": 55},
        }

        lectura = registrar_lectura(datos)

        self.assertEqual(lectura.sensor.codigo, "S-01")
        self.assertEqual(float(lectura.valor), 55)

    # -------------------------------------------------------------
    # TEST 2: Regla que enciende la bomba
    # -------------------------------------------------------------
    def test_evaluar_reglas_dispara_actuador(self):
        lectura = Lectura.objects.create(
            sensor=self.sensor,
            valor=60,     # supera el umbral
            unidad="cm",
            fecha_hora=now(),
            origen="TEST",
        )

        evaluar_reglas_sensor(self.sensor, lectura)

        # Recargar el actuador para ver el estado actualizado
        self.act.refresh_from_db()
        self.assertTrue(self.act.encendido)
