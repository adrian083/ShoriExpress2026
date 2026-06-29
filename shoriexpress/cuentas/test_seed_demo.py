from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from metodo_pago.models import MetodoPago
from producto.models import Producto
from rol.models import Rol
from usuario.models import Usuario


class SeedDemoCommandTest(TestCase):
    def test_seed_demo_es_idempotente_y_crea_datos_base(self):
        out = StringIO()
        call_command('seed_demo', stdout=out)
        call_command('seed_demo', stdout=out)

        self.assertGreaterEqual(Rol.objects.count(), 4)
        self.assertGreaterEqual(Usuario.objects.count(), 1)
        self.assertGreaterEqual(Producto.objects.count(), 1)
        self.assertTrue(MetodoPago.objects.filter(nombre_metodo='Efectivo').exists())
        self.assertIn('Demo lista', out.getvalue())
