# ---------------------------------------------------------
# AUTORES: Paula Ortiz, Benjamin Nuñez, Khrismery Gallardo
# FECHA DE CREACIÓN: 01-10-2025
# LICENCIA: Uso Educacional-No Comercial
# PROPÓSITO: Pruebas unitarias para utilidades de roles
# FECHA ÚLTIMA MODIFICACIÓN: 17-11-2025
# ---------------------------------------------------------
from django.contrib.auth import get_user_model
from django.test import TestCase

from cuentas.models import Perfil
from cuentas.utils import obtener_rol_usuario, usuario_tiene_rol  



User = get_user_model()


class RolesUtilsTests(TestCase):
    def setUp(self):
        # Usuario sin perfil asociado
        self.user_sin_perfil = User.objects.create_user(
            username="sin_perfil",
            password="test1234",
        )

        # Usuario OPERARIO
        self.user_operario = User.objects.create_user(
            username="operario",
            password="test1234",
        )

        # Usuario GERENTE
        self.user_gerente = User.objects.create_user(
            username="gerente",
            password="test1234",
        )

        # Superusuario
        self.superuser = User.objects.create_superuser(
            username="admin",
            password="test1234",
            email="admin@example.com",
        )

        # Perfiles: ahora SIEMPRE con rut_numero
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

    # ----------------- obtener_rol_usuario -----------------

    def test_obtener_rol_usuario_retorna_none_si_no_tiene_perfil(self):
        rol = obtener_rol_usuario(self.user_sin_perfil)
        self.assertIsNone(rol)

    def test_obtener_rol_usuario_retorna_rol_correcto(self):
        rol_operario = obtener_rol_usuario(self.user_operario)
        rol_gerente = obtener_rol_usuario(self.user_gerente)

        self.assertEqual(rol_operario, "OPERARIO")
        self.assertEqual(rol_gerente, "GERENTE")

    # ----------------- usuario_tiene_rol -------------------

    def test_usuario_tiene_rol_false_para_rol_incorrecto(self):
        self.assertFalse(usuario_tiene_rol(self.user_operario, "GERENTE"))
        self.assertFalse(usuario_tiene_rol(self.user_gerente, "OPERARIO"))

    def test_usuario_tiene_rol_true_para_rol_correcto(self):
        self.assertTrue(usuario_tiene_rol(self.user_operario, "OPERARIO"))
        self.assertTrue(usuario_tiene_rol(self.user_gerente, "GERENTE"))

    def test_usuario_tiene_rol_true_para_superusuario_siempre(self):
        # el superusuario debería pasar aunque no tenga Perfil explícito
        self.assertTrue(usuario_tiene_rol(self.superuser, "OPERARIO"))
        self.assertTrue(usuario_tiene_rol(self.superuser, "GERENTE"))
