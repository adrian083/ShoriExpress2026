from decimal import Decimal

from django.test import TestCase

from inventario.models import Inventario
from producto.models import Producto
from receta.models import Receta


class RecetaModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.producto = Producto.objects.create(
            nombre_producto='Perro',
            precio_venta=Decimal('12.00'),
            esta_disponible=True,
            esta_habilitado=True,
        )
        cls.insumo = Inventario.objects.create(
            nombre_insumo='Pan',
            categoria_insumo='Base',
            stock_actual=Decimal('5.00'),
            stock_minimo=Decimal('1.00'),
            precio_compra_referencia=Decimal('1000.00'),
        )
        cls.receta = Receta.objects.create(
            producto=cls.producto,
            insumo=cls.insumo,
            cantidad_requerida=Decimal('0.50'),
        )

    def test_receta_str_contains_product_and_required_quantity(self):
        expected = 'Perro utiliza 0.50 de Pan'
        self.assertEqual(str(self.receta), expected)
