# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Formularios para la aplicación Django
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------
from django import forms
from core.utils.rut import separar_rut, formatear_rut_con_puntos
from core.validators import validar_rut_string
from .models import Cliente


class ClienteForm(forms.ModelForm):
    rut = forms.CharField(
        label="RUT",
        max_length=20,
        help_text="Ingrese el RUT con o sin puntos, por ejemplo 12.345.678-5",
        validators=[validar_rut_string],
    )

    class Meta:
        model = Cliente
        fields = [
            "rut",
            "nombre_razon_social",
            "telefono",
            "email",
            "direccion_cobranza",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["rut"].initial = formatear_rut_con_puntos(
                self.instance.rut_numero,
                self.instance.rut_dv,
            )

    def clean_rut(self):
        rut_str = self.cleaned_data["rut"]
        rut_numero, dv = separar_rut(rut_str)
        self.cleaned_data["rut_numero"] = rut_numero
        self.cleaned_data["rut_dv"] = dv
        return rut_str

    def save(self, commit=True):
        cliente = super().save(commit=False)
        rut_numero = self.cleaned_data.get("rut_numero")
        dv = self.cleaned_data.get("rut_dv")

        if rut_numero is not None and dv is not None:
            cliente.rut_numero = rut_numero
            cliente.rut_dv = dv

        if commit:
            cliente.save()
            self.save_m2m()
        return cliente
