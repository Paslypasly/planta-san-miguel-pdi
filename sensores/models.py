from django.db import models
from core.models import BaseModel
from planta.models import Estanque
from inventario.models import Ubicacion


class Dispositivo(BaseModel):
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100)
    ubicacion = models.ForeignKey(
        Ubicacion,
        on_delete=models.PROTECT,
        # Evitar colisión entre Sensor y Actuador
        related_name="%(class)s_set",
    )
    descripcion = models.TextField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Sensor(Dispositivo):
    TIPO_SENSOR = [
        ("NIVEL", "Nivel estanque (ultrasónico)"),
        ("IR", "Infrarrojo (conteo/presencia)"),
        ("PH", "Sensor de pH"),
        ("OTRO", "Otro"),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_SENSOR)
    unidad = models.CharField(max_length=20, help_text="Ej: %, cm, pH, uds")
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

    # sensor de pH definido pero inicialmente desactivado
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.tipo == "PH" and self._state.adding:
            self.activo = False
        super().save(*args, **kwargs)

    def ultima_lectura(self):
        return self.lecturas.order_by("-fecha_hora").first()

    def valor_actual(self):
        """
        Retorna el valor numérico de la última lectura, o None si no hay lecturas.
        """
        ultima = self.ultima_lectura()
        return ultima.valor if ultima else None

    def esta_fuera_de_rango(self) -> bool:
        """
        Indica si el último valor está fuera del rango definido (min/max).
        Si no hay rango configurado, retorna False.
        """
        valor = self.valor_actual()
        if valor is None:
            return False

        if self.rango_min is not None and valor < self.rango_min:
            return True
        if self.rango_max is not None and valor > self.rango_max:
            return True
        return False

class Actuador(Dispositivo):
    TIPO_ACTUADOR = [
        ("BOMBA", "Bomba de agua"),
        ("VALVULA", "Válvula"),
        ("ALARMA", "Alarma / Sirena"),
        ("OTRO", "Otro"),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_ACTUADOR)
    gpio = models.CharField(
        max_length=10,
        help_text="Etiqueta de GPIO en ESP32 (ej: GPIO23)",
    )
    potencia_w = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Potencia asociada al actuador si aplica",
    )
    estanque = models.ForeignKey(
        Estanque,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actuadores",
    )

     # ───────── Estado lógico del actuador (ej. Bomba encendida/apagada) ─────────
    encendido = models.BooleanField(
        default=False,
        help_text="Estado actual del actuador (True = encendido / False = apagado)"
    )

    # ───────── Métodos de dominio ─────────
    def es_bomba(self) -> bool:
        """Indica si este actuador representa una bomba de agua."""
        return self.tipo == "BOMBA"

    def encender(self):
        """Marca el actuador como encendido (no envía señal física aún)."""
        self.encendido = True
        self.save()

    def apagar(self):
        """Marca el actuador como apagado."""
        self.encendido = False
        self.save()

    def estado_bomba(self) -> str:
        """
        Retorna una descripción amigable del estado de la bomba.
        """
        if not self.es_bomba():
            return "No es una bomba"
        return "Encendida" if self.encendido else "Apagada"

class Lectura(BaseModel):
    ORIGEN_LECTURA = [
        ("ESP32", "Lectura desde ESP32"),
        ("MANUAL", "Registro manual"),
        ("SIMULADA", "Dato simulado para pruebas"),
    ]

    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name="lecturas",
    )
    valor = models.DecimalField(max_digits=12, decimal_places=4)
    unidad = models.CharField(max_length=20)
    fecha_hora = models.DateTimeField()
    origen = models.CharField(max_length=10, choices=ORIGEN_LECTURA, default="ESP32")
    raw_payload = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON original recibido desde el dispositivo o API",
    )

    class Meta:
        verbose_name = "Lectura de sensor"
        verbose_name_plural = "Lecturas de sensores"
        ordering = ["-fecha_hora"]

    def __str__(self):
        return f"{self.sensor} = {self.valor} {self.unidad} en {self.fecha_hora}"
    
       # ───────── Métodos de dominio ─────────
    def esta_fuera_de_rango(self) -> bool:
        """
        Reutiliza la configuración de rango del sensor para evaluar esta lectura puntual.
        """
        sensor = self.sensor
        if sensor.rango_min is None and sensor.rango_max is None:
            return False

        if sensor.rango_min is not None and self.valor < sensor.rango_min:
            return True
        if sensor.rango_max is not None and self.valor > sensor.rango_max:
            return True
        return False


class Alerta(BaseModel):
    ESTADO_ALERTA = [
        ("NUEVA", "Nueva"),
        ("EN_PROCESO", "En proceso"),
        ("RESUELTA", "Resuelta"),
    ]
    SEVERIDAD = [
        ("INFO", "Informativa"),
        ("WARN", "Advertencia"),
        ("CRITICA", "Crítica"),
    ]

    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name="alertas",
    )
    lectura = models.ForeignKey(
        Lectura,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alertas",
    )
    severidad = models.CharField(max_length=10, choices=SEVERIDAD)
    mensaje = models.CharField(max_length=255)
    estado = models.CharField(max_length=15, choices=ESTADO_ALERTA, default="NUEVA")

    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"

    def __str__(self):
        return f"[{self.severidad}] {self.mensaje}"
