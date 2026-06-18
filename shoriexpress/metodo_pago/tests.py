from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from pedido.models import Pedido
from recibo.models import Recibo
from rol.models import Rol
from usuario.models import Usuario

from metodo_pago.models import MetodoPago


class MetodoPagoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.metodo = MetodoPago.objects.create(
            nombre_metodo='Efectivo Test',
            descripcion='Pago en efectivo',
            esta_activo=True,
        )

    def test_metodo_pago_str_and_status(self):
        self.assertEqual(str(self.metodo), 'Efectivo Test')
        self.assertTrue(self.metodo.esta_activo)

    def test_eliminar_metodo_referenciado_muestra_warning(self):
        rol = Rol.objects.create(nombre_rol='Administrador')
        usuario = Usuario.objects.create(
            tipo_documento='CC',
            documento='1234567890',
            primer_nombre='Admin',
            apellido='Test',
            correo='admin@test.com',
            telefono='3001234567',
            direccion='Calle 123',
            nombre_usuario='admin_test',
            contrasena='123456',
            rol=rol,
        )
        pedido = Pedido.objects.create(usuario=usuario, total_pedido=100.00)
        Recibo.objects.create(
            pedido=pedido,
            metodo_pago=self.metodo,
            subtotal=100.00,
            iva_total=19.00,
            total_pagado=119.00,
        )

        session = self.client.session
        session['usuario_id'] = usuario.pk
        session['usuario_rol'] = rol.nombre_rol
        session.save()

        response = self.client.post(reverse('eliminar_metodo', args=[self.metodo.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('lista_metodos'), fetch_redirect_response=False)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('No se puede eliminar este método de pago' in str(message) for message in messages))
