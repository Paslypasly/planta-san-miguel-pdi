from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import ROLES_CHOICES


@receiver(post_migrate)
def crear_grupos_y_permisos_basicos(sender, app_config, **kwargs):
    """
    Crea (si no existen) los grupos de roles y les asigna
    permisos base. Se ejecuta después de migrate.
    """
    # Solo ejecutarse cuando la app 'cuentas' haya sido migrada
    if app_config.name != "cuentas":
        return

    # ───────── 1) Crear grupos para cada rol ─────────
    grupos = {}
    for rol, _label in ROLES_CHOICES:
        grupo, _created = Group.objects.get_or_create(name=rol)
        grupos[rol] = grupo

    # ───────── 2) Helper para asignar permisos ─────────
    def add_perms(group: Group, specs: list[tuple[str, str, list[str]]]):
        """
        specs: lista de tuplas (app_label, model_name, [acciones])
        acciones = ["view", "add", "change", "delete"]
        """
        for app_label, model_name, actions in specs:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model_name)
            except ContentType.DoesNotExist:
                # Modelo aún no existe (por cambios futuros) → se ignora silenciosamente
                continue

            for action in actions:
                codename = f"{action}_{model_name}"
                try:
                    perm = Permission.objects.get(content_type=ct, codename=codename)
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    # Si no existe ese permiso en particular, se omite
                    continue

    # ───────── 3) Definición de permisos base por rol ─────────

    # Operario de planta → opera producción, inventario básico y pedidos
    operario_specs = [
        ("planta", "estanque", ["view"]),
        ("sensores", "sensor", ["view"]),
        ("sensores", "actuador", ["view"]),
        ("sensores", "lectura", ["view", "add"]),
        ("sensores", "alerta", ["view", "change"]),
        ("inventario", "stockubicacion", ["view", "change"]),
        ("inventario", "movimientoinventario", ["view", "add"]),
        ("ventas", "pedido", ["view", "change"]),
        ("ventas", "detallepedido", ["view", "add"]),
    ]
    add_perms(grupos["OPERARIO"], operario_specs)

    # Conductor → rutas y estado de entrega
    conductor_specs = [
        ("logistica", "ruta", ["view"]),
        ("logistica", "detalleruta", ["view", "change"]),
        ("ventas", "pedido", ["view", "change"]),
    ]
    add_perms(grupos["CONDUCTOR"], conductor_specs)

    # Técnico → configuración de sensores, actuadores y estanques
    tecnico_specs = [
        ("planta", "estanque", ["view", "change"]),
        ("sensores", "sensor", ["view", "add", "change"]),
        ("sensores", "actuador", ["view", "add", "change"]),
        ("sensores", "lectura", ["view"]),
        ("sensores", "alerta", ["view", "change"]),
    ]
    add_perms(grupos["TECNICO"], tecnico_specs)

    # Gerente → acceso lectura amplia (usamos todos los 'view_')
    view_all = Permission.objects.filter(codename__startswith="view_")
    grupos["GERENTE"].permissions.add(*view_all)

    # Auditor → solo lectura de todo el sistema
    grupos["AUDITOR"].permissions.add(*view_all)

    # Admin → se espera usar usuarios con is_superuser=True
    # El grupo ADMIN existe por orden, pero la gestión de permisos
    # se controla principalmente vía superuser.
    # No se asignan permisos específicos aquí.
    