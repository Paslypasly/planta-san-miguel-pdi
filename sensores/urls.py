# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: URLs para la aplicación de sensores y actuadores IoT
# FECHA ÚLTIMA MODIFICACIÓN: 18-11-2025
# ---------------------------------------------------------
from django.urls import path
from .views_api import api_recibir_lectura

urlpatterns = [
    path("api/lectura/", api_recibir_lectura, name="api_recibir_lectura"),
]
