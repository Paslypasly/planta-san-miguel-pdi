# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Vistas para la aplicación Django
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------
from django.shortcuts import render
from cuentas.decorators import role_required


@role_required("GERENTE", "ADMIN")
def dashboard_gerencia(request):
    contexto = {
        # Aquí irán KPIs de producción, alertas, etc.
    }
    return render(request, "reportes/dashboard_gerencia.html", contexto)
