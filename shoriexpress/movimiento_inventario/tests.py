from decimal import Decimal

from django.test import TestCase

from inventario.models import Inventario
from movimiento_inventario.models import MovimientoInventario
from rol.models import Rol
from usuario.models import Usuario


class MovimientoInventarioModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol = Rol.objects.create(nombre_rol='Cajero')
        cls.usuario = Usuario.objects.create(
            tipo_documento='CC',
            documento='22222222',
            primer_nombre='Marta',
            apellido='Diaz',
            correo='marta@example.com',
            telefono='3002222222',
            direccion='Calle 33',
            nombre_usuario='martad',
            contrasena='secret',
            rol=cls.rol,
        )
        cls.insumo = Inventario.objects.create(
            nombre_insumo='Aceite',
            categoria_insumo='Abarrote',
            stock_actual=Decimal('30.00'),
            stock_minimo=Decimal('5.00'),
            precio_compra_referencia=Decimal('8000.00'),
        )
        cls.movimiento = MovimientoInventario.objects.create(
            insumo=cls.insumo,
            usuario=cls.usuario,
            lote='L-001',
            tipo_movimiento='entrada',
            cantidad=Decimal('10.00'),
            observaciones='Compra inicial',
        )

    def test_movimiento_str_uses_display_and_lote(self):
        expected = 'Entrada por Compra - Aceite (Lote: L-001)'
        self.assertEqual(str(self.movimiento), expected)
