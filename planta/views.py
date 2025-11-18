# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Vistas para la aplicación Django
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------

from django.views.generic import TemplateView
from cuentas.mixins import OperarioRequiredMixin


class DashboardOperarioView(OperarioRequiredMixin, TemplateView):
    template_name = "planta/dashboard_operario.html"

    # Aquí en el futuro se pueden agregar métodos get_context_data con datos de sensores, etc.
