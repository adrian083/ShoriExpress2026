from django.test import TestCase

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
