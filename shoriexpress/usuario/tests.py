from django.core.exceptions import ValidationError
from django.test import TestCase

from rol.models import Rol
from usuario.models import Usuario


class UsuarioModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol = Rol.objects.create(nombre_rol='Cliente')
        cls.usuario = Usuario.objects.create(
            tipo_documento='CC',
            documento='12345678',
            primer_nombre='Juan',
            apellido='Pérez',
            correo='juan@example.com',
            telefono='3001234567',
            direccion='Calle 123',
            nombre_usuario='juanp',
            contrasena='password123',
            rol=cls.rol,
        )

    def test_usuario_creation(self):
        self.assertEqual(self.usuario.primer_nombre, 'Juan')
        self.assertEqual(self.usuario.rol.nombre_rol, 'Cliente')

    def test_full_clean_accepts_valid_data(self):
        self.usuario.full_clean()

    def test_full_clean_rejects_short_document(self):
        self.usuario.documento = '12'

        with self.assertRaises(ValidationError):
            self.usuario.full_clean()

    def test_full_clean_rejects_invalid_phone(self):
        self.usuario.telefono = '123'

        with self.assertRaises(ValidationError):
            self.usuario.full_clean()
