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
from .models import Perfil


class PerfilForm(forms.ModelForm):
    # Campo visible para el usuario
    rut = forms.CharField(
        label="RUT",
        max_length=20,
        help_text="Ingrese el RUT con o sin puntos, por ejemplo 12.345.678-5",
        validators=[validar_rut_string],
    )

    class Meta:
        model = Perfil
        fields = [
            "user",
            "rut",
            "rol",
            "telefono_contacto",
            "cargo",
            "activo",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando un perfil existente, mostrar el RUT formateado
        if self.instance.pk:
            self.fields["rut"].initial = formatear_rut_con_puntos(
                self.instance.rut_numero,
                self.instance.rut_dv,
            )

    def clean_rut(self):
        """
        El usuario puede escribir 12.345.678-5 o 12345678.
        Nosotros nos quedamos con el número. El DV lo calcula el modelo.
        """
        rut_str = self.cleaned_data["rut"]
        rut_numero, _dv_ignorado = separar_rut(rut_str)
        self.cleaned_data["rut_numero"] = rut_numero
        return rut_str

    def save(self, commit=True):
        perfil = super().save(commit=False)
        rut_numero = self.cleaned_data.get("rut_numero")

        if rut_numero is not None:
            perfil.rut_numero = rut_numero
            # NO seteamos rut_dv aquí: lo calculará EntidadConRut.clean()

        # Disparar clean() para que calcule el DV
        perfil.full_clean(exclude=None)

        if commit:
            perfil.save()
            self.save_m2m()
        return perfil
