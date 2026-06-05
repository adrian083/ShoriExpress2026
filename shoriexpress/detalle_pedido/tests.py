from datetime import time
from decimal import Decimal

from django.test import TestCase

from dashboard.models import ConfiguracionSistema
from detalle_pedido.models import DetallePedido
from pedido.models import Pedido
from producto.models import Producto
from rol.models import Rol
from usuario.models import Usuario


class DetallePedidoBusinessLogicTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol = Rol.objects.create(nombre_rol='Cliente')
        cls.usuario = Usuario.objects.create(
            tipo_documento='CC',
            documento='12345678',
            primer_nombre='Carlos',
            apellido='García',
            correo='carlos@example.com',
            telefono='3001234567',
            direccion='Calle 10',
            nombre_usuario='carlos01',
            contrasena='secret',
            rol=cls.rol,
        )
        cls.producto = Producto.objects.create(
            nombre_producto='Sándwich Clásico',
            descripcion_producto='Sándwich delicioso',
            precio_venta=Decimal('8.50'),
            esta_disponible=True,
            esta_habilitado=True,
        )
        cls.pedido = Pedido.objects.create(
            usuario=cls.usuario,
            tipo_pedido='local',
            estado_pedido='pendiente',
            total_pedido=Decimal('17.00'),
        )
        cls.detalle = DetallePedido.objects.create(
            pedido=cls.pedido,
            producto=cls.producto,
            cantidad=2,
            precio_unitario_momento=Decimal('8.50'),
            stock_remanente_post_venta=10,
        )
        cls.config = ConfiguracionSistema.objects.create(
            nombre_sistema='ShoriExpress',
            hora_apertura=time(8, 0),
            hora_cierre=time(19, 0),
            porcentaje_iva=Decimal('19.00'),
            umbral_bonos=Decimal('50000.00'),
        )

    def test_subtotal_uses_quantity_and_unit_price(self):
        self.assertEqual(self.detalle.subtotal, Decimal('17.00'))

    def test_subtotal_con_iva_uses_configured_tax(self):
        self.assertEqual(self.detalle.subtotal_con_iva, Decimal('20.23'))

    def test_str_representation_contains_product_and_order(self):
        expected = f"2 x {self.producto.nombre_producto} (Pedido #{self.pedido.id})"
        self.assertEqual(str(self.detalle), expected)

