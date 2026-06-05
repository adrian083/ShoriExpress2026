from django.test import TestCase

from rol.models import Rol


class RolModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol = Rol.objects.create(nombre_rol='Administrador')

    def test_rol_creation_and_str(self):
        self.assertEqual(self.rol.nombre_rol, 'Administrador')
        self.assertEqual(str(self.rol), 'Administrador')
