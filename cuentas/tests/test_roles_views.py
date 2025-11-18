# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Pruebas unitarias para vistas con control de roles
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views.generic import View

from cuentas.models import Perfil
from cuentas.mixins import OperarioRequiredMixin


User = get_user_model()


class DummyOperarioView(OperarioRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("OK")


class RolesViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user_operario = User.objects.create_user(
            username="operario",
            password="test1234",
        )
        self.user_gerente = User.objects.create_user(
            username="gerente",
            password="test1234",
        )
        self.superuser = User.objects.create_superuser(
            username="admin",
            password="test1234",
            email="admin@example.com",
        )

        # Perfiles, TODOS con rut_numero
        self.perfil_operario = Perfil.objects.create(
            user=self.user_operario,
            rol="OPERARIO",
            rut_numero=11111111,
        )
        self.perfil_gerente = Perfil.objects.create(
            user=self.user_gerente,
            rol="GERENTE",
            rut_numero=22222222,
        )

    # ---------- OperarioRequiredMixin ----------

    def test_operario_required_mixin_permite_operario(self):
        request = self.factory.get("/dummy-operario/")
        request.user = self.user_operario

        view = DummyOperarioView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_operario_required_mixin_permite_superusuario(self):
        request = self.factory.get("/dummy-operario/")
        request.user = self.superuser

        view = DummyOperarioView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_operario_required_mixin_lanza_permission_denied_para_rol_incorrecto(self):
        # usuario con perfil GERENTE no debería pasar como OPERARIO
        request = self.factory.get("/dummy-operario/")
        request.user = self.user_gerente

        view = DummyOperarioView.as_view()

        with self.assertRaises(PermissionDenied):
            view(request)
