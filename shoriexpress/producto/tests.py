from decimal import Decimal

from django.test import TestCase

from inventario.models import Inventario
from producto.models import Producto
from receta.models import Receta


class ProductoAvailabilityTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.producto = Producto.objects.create(
            nombre_producto='Perro Clásico',
            descripcion_producto='Producto de prueba',
            precio_venta=Decimal('9.50'),
            esta_disponible=True,
            esta_habilitado=True,
        )
        cls.insumo = Inventario.objects.create(
            nombre_insumo='Pan',
            categoria_insumo='Base',
            stock_actual=Decimal('1.00'),
            stock_minimo=Decimal('1.00'),
            precio_compra_referencia=Decimal('1000.00'),
        )

    def test_check_ingredient_stock_returns_true_for_sufficient_supply(self):
        Receta.objects.create(
            producto=self.producto,
            insumo=self.insumo,
            cantidad_requerida=Decimal('1.00'),
        )

        hay_stock, faltantes = self.producto.check_ingredient_stock()

        self.assertTrue(hay_stock)
        self.assertEqual(faltantes, [])

    def test_update_availability_based_on_stock_disables_product_when_ingredients_are_insufficient(self):
        Receta.objects.create(
            producto=self.producto,
            insumo=self.insumo,
            cantidad_requerida=Decimal('5.00'),
        )

        result = self.producto.update_availability_based_on_stock()

        self.assertFalse(result)
        self.producto.refresh_from_db()
        self.assertFalse(self.producto.esta_habilitado)

    def test_is_available_for_sale_is_false_when_stock_is_insufficient(self):
        Receta.objects.create(
            producto=self.producto,
            insumo=self.insumo,
            cantidad_requerida=Decimal('5.00'),
        )

        self.assertFalse(self.producto.is_available_for_sale)

