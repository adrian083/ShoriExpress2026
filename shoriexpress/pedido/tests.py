from decimal import Decimal

from django.test import TestCase

from pedido.models import Pedido
from rol.models import Rol
from usuario.models import Usuario


class PedidoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol = Rol.objects.create(nombre_rol='Cliente')
        cls.usuario = Usuario.objects.create(
            tipo_documento='CC',
            documento='98765432',
            primer_nombre='Ana',
            apellido='Lopez',
            correo='ana@example.com',
            telefono='3007654321',
            direccion='Carrera 5',
            nombre_usuario='analo',
            contrasena='secret',
            rol=cls.rol,
        )
        cls.pedido = Pedido.objects.create(
            usuario=cls.usuario,
            tipo_pedido='domicilio',
            direccion_pedido='Calle 9',
            estado_pedido='pendiente',
            total_pedido=Decimal('25.50'),
        )

    def test_pedido_defaults_and_str(self):
        self.assertEqual(self.pedido.estado_pedido, 'pendiente')
        self.assertEqual(self.pedido.tipo_pedido, 'domicilio')
        self.assertEqual(str(self.pedido), f'Pedido #{self.pedido.id} - Ana (pendiente)')

    def test_pedido_guarda_instrucciones(self):
        pedido = Pedido.objects.create(
            usuario=self.usuario,
            tipo_pedido='domicilio',
            direccion_pedido='Calle 9',
            estado_pedido='pendiente',
            total_pedido=Decimal('25.50'),
            instrucciones_pedido='Sin cebolla y con salsa aparte',
        )

        self.assertEqual(pedido.instrucciones_pedido, 'Sin cebolla y con salsa aparte')
