from decimal import Decimal

from django.test import TestCase

from dashboard.models import ConfiguracionSistema
from detalle_pedido.models import DetallePedido
from metodo_pago.models import MetodoPago
from pedido.models import Pedido
from producto.models import Producto
from recibo.models import Recibo
from recibo.services import generar_recibo_si_aplica, sincronizar_recibo_con_pedido
from rol.models import Rol
from usuario.models import Usuario


class ReciboAutomaticoTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol = Rol.objects.create(nombre_rol='Cliente')
        cls.usuario = Usuario.objects.create(
            tipo_documento='CC',
            documento='90000001',
            primer_nombre='Recibo',
            apellido='Auto',
            correo='recibo@test.com',
            telefono='3009000001',
            direccion='Calle 1',
            nombre_usuario='recibo_auto',
            contrasena='secret',
            rol=cls.rol,
        )
        cls.pedido = Pedido.objects.create(
            usuario=cls.usuario,
            tipo_pedido='local',
            estado_pedido='pendiente',
            total_pedido=Decimal('0.00'),
        )
        cls.producto = Producto.objects.create(
            nombre_producto='Producto recibo',
            descripcion_producto='Prueba',
            precio_venta=Decimal('11900.00'),
            esta_disponible=True,
            esta_habilitado=True,
        )
        MetodoPago.objects.get_or_create(
            nombre_metodo='Efectivo',
            defaults={'descripcion': 'Efectivo', 'esta_activo': True},
        )
        ConfiguracionSistema.objects.create(
            nombre_sistema='ShoriExpress',
            porcentaje_iva=Decimal('19.00'),
            umbral_bonos=Decimal('50000.00'),
        )

    def test_generar_recibo_automatico_desde_detalle(self):
        self.assertFalse(Recibo.objects.filter(pedido=self.pedido).exists())

        DetallePedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=2,
            precio_unitario_momento=Decimal('11900.00'),
        )

        self.pedido.refresh_from_db()
        recibo = self.pedido.recibo

        self.assertIsNotNone(recibo)
        self.assertEqual(recibo.total_pagado, Decimal('23800.00'))

    def test_no_duplica_recibo_si_ya_existe(self):
        DetallePedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=1,
            precio_unitario_momento=Decimal('11900.00'),
        )
        generar_recibo_si_aplica(self.pedido)
        recibo, creado = generar_recibo_si_aplica(self.pedido)

        self.assertFalse(creado)
        self.assertEqual(Recibo.objects.filter(pedido=self.pedido).count(), 1)
        self.assertEqual(recibo.total_pagado, Decimal('11900.00'))
