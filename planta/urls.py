# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: URLs para la aplicación Django
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------
from django.urls import path
from .views import DashboardOperarioView

app_name = "planta"

urlpatterns = [
    path("dashboard/operario/", DashboardOperarioView.as_view(), name="dashboard_operario"),
]

