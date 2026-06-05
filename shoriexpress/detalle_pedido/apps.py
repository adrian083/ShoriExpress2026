from django.apps import AppConfig


class DetallePedidoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'detalle_pedido'

    def ready(self):
        import detalle_pedido.signals  # noqa
