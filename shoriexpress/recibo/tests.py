from decimal import Decimal

from django.test import TestCase

from metodo_pago.models import MetodoPago
from pedido.models import Pedido
from recibo.models import Recibo
from rol.models import Rol
from usuario.models import Usuario


class ReciboModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol = Rol.objects.create(nombre_rol='Cliente')
        cls.usuario = Usuario.objects.create(
            tipo_documento='CC',
            documento='11111111',
            primer_nombre='Luis',
            apellido='Rojas',
            correo='luis@example.com',
            telefono='3001111111',
            direccion='Calle 22',
            nombre_usuario='luisr',
            contrasena='secret',
            rol=cls.rol,
        )
        cls.pedido = Pedido.objects.create(
            usuario=cls.usuario,
            tipo_pedido='local',
            estado_pedido='pendiente',
            total_pedido=Decimal('15.00'),
        )
        cls.metodo = MetodoPago.objects.create(nombre_metodo='Tarjeta', esta_activo=True)
        cls.recibo = Recibo.objects.create(
            pedido=cls.pedido,
            metodo_pago=cls.metodo,
            subtotal=Decimal('12.00'),
            iva_total=Decimal('3.00'),
            total_pagado=Decimal('15.00'),
            puntos_ganados=5,
        )

    def test_recibo_str_contains_order(self):
        expected = f'Recibo #{self.recibo.id} - Pedido #{self.pedido.id}'
        self.assertEqual(str(self.recibo), expected)

    def test_numero_recibo_uses_internal_id(self):
        self.assertEqual(self.recibo.numero_recibo, self.recibo.id)
