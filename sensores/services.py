# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Servicios para la aplicación de sensores y actuadores IoT
# FECHA ÚLTIMA MODIFICACIÓN: 18-11-2025
# ---------------------------------------------------------
from __future__ import annotations

from datetime import datetime
from django.utils.timezone import now
from django.db import transaction

from sensores.models import Sensor, Lectura, Alerta, ReglaControl, Actuador


# ================================================================
# 1) REGISTRO DE LECTURAS (acepta dict o argumentos sueltos)
# ================================================================
def _payload_json_safe(payload: dict | None) -> dict | None:
    """
    Convierte objetos no serializables (ej: datetime) a strings ISO para guardar en raw_payload.
    """
    if payload is None:
        return None

    def fix(o):
        if isinstance(o, datetime):
            return o.isoformat()
        return o

    return {k: fix(v) for k, v in payload.items()}


def registrar_lectura(
    sensor=None,
    valor=None,
    unidad=None,
    fecha_hora=None,
    raw_payload=None,
) -> Lectura:
    """
    Modo 1: registrar_lectura({
                "sensor_codigo": "S-01",
                "valor": 55,
                "unidad": "cm",
                "fecha_hora": "2025-11-18T00:00:00Z",
                "raw": {...}
            })

    Modo 2: registrar_lectura(sensor_obj, 55, "cm", now(), {...})
    """

    # ---- MODO DICCIONARIO (payload desde API/ESP32) ----
    if isinstance(sensor, dict):
        data = sensor
        sensor = Sensor.objects.get(codigo=data["sensor_codigo"])
        valor = float(data["valor"])
        unidad = data.get("unidad", "")

        fecha_raw = data.get("fecha_hora")
        if isinstance(fecha_raw, datetime):
            fecha_hora = fecha_raw
        elif isinstance(fecha_raw, str):
            # Maneja formato ISO con o sin 'Z'
            fecha_hora = datetime.fromisoformat(fecha_raw.replace("Z", "+00:00"))
        else:
            fecha_hora = now()

        raw_payload = _payload_json_safe(data)

    # ---- MODO ARGUMENTOS SUELTOS ----
    if fecha_hora is None:
        fecha_hora = now()

    with transaction.atomic():
        lectura = Lectura.objects.create(
            sensor=sensor,
            valor=valor,
            unidad=unidad,
            fecha_hora=fecha_hora,
            origen="ESP32",
            raw_payload=_payload_json_safe(raw_payload),
        )

        # Evaluar reglas asociadas a este sensor
        evaluar_reglas_sensor(sensor, lectura)

        return lectura


# ================================================================
# 2) MOTOR DE REGLAS
# ================================================================
def evaluar_reglas_sensor(sensor: Sensor, lectura: Lectura) -> None:
    """
    Busca reglas activas para el sensor y ejecuta acciones si se cumplen.
    """
    reglas = ReglaControl.objects.filter(sensor=sensor, activo=True)

    for regla in reglas:
        if regla.se_cumple(lectura.valor):
            ejecutar_accion_regla(regla, sensor, lectura)


def ejecutar_accion_regla(regla: ReglaControl, sensor: Sensor, lectura: Lectura) -> None:
    """
    Crea una alerta y ejecuta la acción asociada (por ahora: encender bomba).
    """
    # Registrar alerta
    Alerta.objects.create(
        sensor=sensor,
        lectura=lectura,
        severidad=regla.severidad,
        mensaje=regla.mensaje_accion,
    )

    # Accion sobre actuador: por simplicidad, siempre ENCENDER si hay actuador
    actuador: Actuador | None = regla.actuador
    if actuador:
        actuador.encender()


# ================================================================
# 3) PROCESAMIENTO DE PAYLOAD JSON DE LA API
# ================================================================
def procesar_payload_lectura(payload: dict) -> dict:
    """
    Valida y normaliza el JSON recibido desde el ESP32 / cliente HTTP.

    Retorna:
      - {"ok": False, "error": "..."} si hay error
      - {"ok": True, "sensor": <Sensor>, "valor": float, "unidad": str, "fecha_hora": datetime}
    """
    required = ["sensor_codigo", "valor", "unidad"]
    for campo in required:
        if campo not in payload:
            return {"ok": False, "error": f"Falta el campo '{campo}'"}

    # Resolver fecha
    fecha_txt = payload.get("fecha_hora")
    if not fecha_txt:
        fecha = now()
    else:
        try:
            fecha = datetime.fromisoformat(fecha_txt.replace("Z", "+00:00"))
        except Exception:
            return {"ok": False, "error": "Formato de fecha inválido"}

    # Buscar sensor
    try:
        sensor = Sensor.objects.get(codigo=payload["sensor_codigo"])
    except Sensor.DoesNotExist:
        return {"ok": False, "error": "Sensor no encontrado"}

    try:
        valor = float(payload["valor"])
    except Exception:
        return {"ok": False, "error": "Valor numérico inválido"}

    return {
        "ok": True,
        "sensor": sensor,
        "valor": valor,
        "unidad": payload["unidad"],
        "fecha_hora": fecha,
    }
