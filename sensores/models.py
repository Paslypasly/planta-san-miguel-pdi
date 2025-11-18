# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-11-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Modelos para sensores y actuadores IoT
# FECHA ÚLTIMA MODIFICACIÓN: 18-11-2025
# ---------------------------------------------------------
from django.db import models
from django.utils import timezone
from core.models import BaseModel
from planta.models import Estanque
from inventario.models import Ubicacion


# ───────────────────────────────────────────────
#   Modelo base para dispositivos físicos
# ───────────────────────────────────────────────
class Dispositivo(BaseModel):
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100)
    ubicacion = models.ForeignKey(
        Ubicacion,
        on_delete=models.PROTECT,
        related_name="%(class)s_set",
    )
    descripcion = models.TextField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# ───────────────────────────────────────────────
#   Sensor IoT
# ───────────────────────────────────────────────
class Sensor(Dispositivo):
    TIPO_SENSOR = [
        ("NIVEL", "Nivel estanque (ultrasónico)"),
        ("IR", "Infrarrojo (conteo/presencia)"),
        ("PH", "Sensor de pH"),
        ("OTRO", "Otro"),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_SENSOR)
    unidad = models.CharField(max_length=20)
    modelo = models.CharField(max_length=100, blank=True)
    rango_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rango_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estanque = models.ForeignKey(
        Estanque,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sensores",
    )
    es_critico = models.BooleanField(default=False)

    # Sensor de pH inicialmente desactivado
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.tipo == "PH" and self._state.adding:
            self.activo = False
        super().save(*args, **kwargs)

    def ultima_lectura(self):
        return self.lecturas.order_by("-fecha_hora").first()

    def valor_actual(self):
        ultima = self.ultima_lectura()
        return ultima.valor if ultima else None

    def esta_fuera_de_rango(self) -> bool:
        valor = self.valor_actual()
        if valor is None:
            return False
        if self.rango_min is not None and valor < self.rango_min:
            return True
        if self.rango_max is not None and valor > self.rango_max:
            return True
        return False


# ───────────────────────────────────────────────
#   Actuador físico (bomba, válvula, alarma)
# ───────────────────────────────────────────────
class Actuador(Dispositivo):
    TIPO_ACTUADOR = [
        ("BOMBA", "Bomba de agua"),
        ("VALVULA", "Válvula"),
        ("ALARMA", "Alarma / Sirena"),
        ("OTRO", "Otro"),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_ACTUADOR)
    gpio = models.CharField(max_length=10)
    potencia_w = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    estanque = models.ForeignKey(
        Estanque,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actuadores",
    )

    encendido = models.BooleanField(default=False)

    def es_bomba(self):
        return self.tipo == "BOMBA"

    def encender(self):
        self.encendido = True
        self.save()

    def apagar(self):
        self.encendido = False
        self.save()

    def estado_bomba(self) -> str:
        if not self.es_bomba():
            return "No es una bomba"
        return "Encendida" if self.encendido else "Apagada"


# ───────────────────────────────────────────────
#   Lectura proveniente del sensor
# ───────────────────────────────────────────────
class Lectura(BaseModel):
    ORIGEN_LECTURA = [
        ("ESP32", "Lectura desde ESP32"),
        ("MANUAL", "Registro manual"),
        ("SIMULADA", "Dato simulado"),
    ]

    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name="lecturas")
    valor = models.DecimalField(max_digits=12, decimal_places=4)
    unidad = models.CharField(max_length=20)
    fecha_hora = models.DateTimeField()
    origen = models.CharField(max_length=10, choices=ORIGEN_LECTURA, default="ESP32")
    raw_payload = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_hora"]

    def __str__(self):
        return f"{self.sensor} = {self.valor} {self.unidad} ({self.fecha_hora})"

    def esta_fuera_de_rango(self) -> bool:
        sensor = self.sensor
        if sensor.rango_min is None and sensor.rango_max is None:
            return False
        if sensor.rango_min is not None and self.valor < sensor.rango_min:
            return True
        if sensor.rango_max is not None and self.valor > sensor.rango_max:
            return True
        return False


# ───────────────────────────────────────────────
#   Modelo de alertas
# ───────────────────────────────────────────────
class Alerta(BaseModel):
    ESTADO = [
        ("NUEVA", "Nueva"),
        ("EN_PROCESO", "En proceso"),
        ("RESUELTA", "Resuelta"),
    ]
    SEVERIDAD = [
        ("INFO", "Informativa"),
        ("WARN", "Advertencia"),
        ("CRITICA", "Crítica"),
    ]

    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name="alertas")
    lectura = models.ForeignKey(Lectura, on_delete=models.SET_NULL, null=True, blank=True)
    severidad = models.CharField(max_length=10, choices=SEVERIDAD)
    mensaje = models.CharField(max_length=255)
    estado = models.CharField(max_length=15, choices=ESTADO, default="NUEVA")

    def __str__(self):
        return f"[{self.severidad}] {self.mensaje}"


# ───────────────────────────────────────────────
#   Reglas automáticas de control (IoT)
# ───────────────────────────────────────────────
class ReglaControl(BaseModel):
    """
    Regla simple de automatización:
    - condicion: cómo comparar (MAYOR, MENOR, etc.)
    - umbral: valor de referencia
    - actuador opcional: si se cumple, se enciende (por ahora sólo ENCENDER)
    """
    CONDICION_CHOICES = [
        ("MAYOR", "Mayor que"),
        ("MENOR", "Menor que"),
        ("MAYOR_IGUAL", "Mayor o igual que"),
        ("MENOR_IGUAL", "Menor o igual que"),
        ("IGUAL", "Igual a"),
    ]

    SEVERIDAD_CHOICES = [
        ("INFO", "Informativa"),
        ("WARN", "Advertencia"),
        ("CRITICA", "Crítica"),
    ]

    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name="reglas_control",
    )
    actuador = models.ForeignKey(
        Actuador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reglas_control",
    )
    condicion = models.CharField(max_length=20, choices=CONDICION_CHOICES)
    umbral = models.DecimalField(max_digits=12, decimal_places=4)
    mensaje_accion = models.CharField(max_length=255)
    severidad = models.CharField(max_length=10, choices=SEVERIDAD_CHOICES, default="WARN")
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Regla de control"
        verbose_name_plural = "Reglas de control"

    def __str__(self):
        return f"Regla {self.condicion} {self.umbral} para {self.sensor.codigo}"

    def se_cumple(self, valor) -> bool:
        """
        Evalúa si el valor cumple la condición de la regla.
        Acepta tanto float/Decimal como string convertible.
        """
        try:
            v = float(valor)
            u = float(self.umbral)
        except Exception:
            return False

        if self.condicion in ("MAYOR", ">"):
            return v > u
        if self.condicion in ("MENOR", "<"):
            return v < u
        if self.condicion in ("MAYOR_IGUAL", ">="):
            return v >= u
        if self.condicion in ("MENOR_IGUAL", "<="):
            return v <= u
        if self.condicion in ("IGUAL", "=="):
            return v == u
        return False
