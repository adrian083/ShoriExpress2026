from django.test import TestCase
from django.urls import reverse

from rol.models import Rol
from usuario.models import Usuario


class RolModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol = Rol.objects.create(nombre_rol='Administrador')
        cls.admin_user = Usuario.objects.create(
            tipo_documento='CC',
            documento='1234567890',
            primer_nombre='Admin',
            apellido='Sistema',
            correo='admin@example.com',
            telefono='3001234567',
            direccion='Calle 1',
            nombre_usuario='adminrol',
            contrasena='secret',
            rol=cls.rol,
        )

    def test_rol_creation_and_str(self):
        self.assertEqual(self.rol.nombre_rol, 'Administrador')
        self.assertEqual(str(self.rol), 'Administrador')

    def test_crear_rol_rechaza_nombres_mayores_a_30_caracteres(self):
        session = self.client.session
        session['usuario_id'] = self.admin_user.pk
        session['usuario_rol'] = 'Administrador'
        session.save()

        response = self.client.post(
            reverse('crear_rol'),
            {'nombre_rol': 'A' * 31},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '30 caracteres')

    def test_editar_rol_rechaza_nombres_mayores_a_30_caracteres(self):
        session = self.client.session
        session['usuario_id'] = self.admin_user.pk
        session['usuario_rol'] = 'Administrador'
        session.save()

        rol = Rol.objects.create(nombre_rol='Cajero')

        response = self.client.post(
            reverse('editar_rol', args=[rol.id]),
            {'nombre_rol': 'B' * 31},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '30 caracteres')
