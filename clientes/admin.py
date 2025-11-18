# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Administración de la aplicación Django
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------
from django.contrib import admin
from .models import Cliente, SectorEntrega
from .forms import ClienteForm

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_razon_social",
        "mostrar_rut",
        "telefono",
        "email",
        "activo",
    )
    search_fields = ("nombre_razon_social", "rut_numero", "email")
    list_filter = ("activo",)

    def mostrar_rut(self, obj):
        return obj.rut_con_puntos  
    mostrar_rut.short_description = "RUT"



@admin.register(SectorEntrega)
class SectorEntregaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "activo")   
    search_fields = ("nombre",)
    list_filter = ("activo",)
