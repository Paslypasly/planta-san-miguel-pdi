from __future__ import annotations

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .services import procesar_payload_lectura, registrar_lectura


@csrf_exempt
def api_recibir_lectura(request):
    """
    Endpoint para recibir lecturas desde el ESP32.

    URL: /sensores/api/lectura/
    Método: POST
    Body (JSON):
    {
        "sensor_codigo": "NIVEL_TK1",
        "valor": 123.4,
        "unidad": "cm",
        "fecha_hora": "2025-11-18T04:30:00Z"  # opcional
    }

    Respuestas:
      - 201: {"ok": true, "id": <id_lectura>, "sensor": "<codigo>"}
      - 400: {"ok": false, "error": "..."}
    """
    if request.method != "POST":
        return JsonResponse(
            {"detail": "Método no permitido"},
            status=405,
        )

    # Intentar parsear JSON del cuerpo
    try:
        if request.body:
            data = json.loads(request.body.decode("utf-8"))
        else:
            # Fallback por si el cliente envía form-data
            data = request.POST.dict()
    except json.JSONDecodeError:
        return JsonResponse(
            {"ok": False, "error": "JSON inválido"},
            status=400,
        )

    # Validar y transformar payload
    resultado = procesar_payload_lectura(data)
    if not resultado.get("ok"):
        return JsonResponse(resultado, status=400)

    # Registrar lectura usando los datos ya validados
    lectura = registrar_lectura(
        sensor=resultado["sensor"],
        valor=resultado["valor"],
        unidad=resultado["unidad"],
        fecha_hora=resultado["fecha_hora"],
        raw_payload=data,  # solo tipos simples, serializable
    )

    return JsonResponse(
        {
            "ok": True,
            "id": lectura.id,
            "sensor": lectura.sensor.codigo,
        },
        status=201,
    )
