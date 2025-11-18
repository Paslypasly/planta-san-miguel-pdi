# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Administración de la aplicación Django
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------
from django.contrib import admin
from .models import Perfil
from .forms import PerfilForm


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    form = PerfilForm
    list_display = ("user", "mostrar_rut", "rol", "activo", "created_at")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "rut_numero",
    )
    list_filter = ("rol", "activo")

    def mostrar_rut(self, obj):
        return obj.rut_con_puntos
    mostrar_rut.short_description = "RUT"
