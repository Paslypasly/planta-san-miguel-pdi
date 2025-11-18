# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: URLs para la aplicación Django
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------
from django.urls import path
from .views import dashboard_gerencia

app_name = "reportes"

urlpatterns = [
    path("dashboard/gerencia/", dashboard_gerencia, name="dashboard_gerencia"),
]
