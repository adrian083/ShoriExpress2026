from decimal import Decimal

from django.test import TestCase

from inventario.models import Inventario


class InventarioModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.insumo = Inventario.objects.create(
            nombre_insumo='Tomate',
            categoria_insumo='Vegetal',
            unidad_medida='KG',
            stock_actual=Decimal('10.50'),
            stock_minimo=Decimal('2.00'),
            stock_maximo=Decimal('20.00'),
            precio_compra_referencia=Decimal('5000.00'),
            iva_porcentaje=Decimal('19.00'),
            estado_insumo='disponible',
        )

    def test_inventario_str_uses_name_and_stock(self):
        expected = 'Tomate (10.50 Kilogramos)'
        self.assertEqual(str(self.insumo), expected)
