from datetime import time

from django.core.exceptions import ValidationError
from django.test import TestCase

from dashboard.models import ConfiguracionSistema


class ConfiguracionSistemaHorariosTestCase(TestCase):
    def test_horario_dentro_del_dia(self):
        config = ConfiguracionSistema(
            hora_apertura=time(8, 0),
            hora_cierre=time(18, 0)
        )
        self.assertTrue(config.esta_dentro_horario(time(9, 0)))
        self.assertFalse(config.esta_dentro_horario(time(7, 59)))
        self.assertFalse(config.esta_dentro_horario(time(18, 1)))

    def test_horario_overnight(self):
        config = ConfiguracionSistema(
            hora_apertura=time(20, 0),
            hora_cierre=time(3, 0)
        )
        self.assertTrue(config.esta_dentro_horario(time(22, 0)))
        self.assertTrue(config.esta_dentro_horario(time(2, 30)))
        self.assertFalse(config.esta_dentro_horario(time(12, 0)))

    def test_horario_apertura_cierre_iguales_es_invalido(self):
        config = ConfiguracionSistema(
            hora_apertura=time(8, 0),
            hora_cierre=time(8, 0)
        )

        with self.assertRaises(ValidationError):
            config.full_clean()

    def test_get_config_uses_existing_record(self):
        ConfiguracionSistema.objects.create(
            hora_apertura=time(8, 0),
            hora_cierre=time(22, 0)
        )
        config = ConfiguracionSistema.get_config()
        self.assertEqual(config.hora_cierre, time(22, 0))
