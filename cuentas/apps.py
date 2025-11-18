from django.apps import AppConfig


class CuentasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cuentas"
    verbose_name = "Gestión de cuentas y roles"

    def ready(self):
        # Importa señales para registrar grupos y permisos
        from . import signals  # noqa
