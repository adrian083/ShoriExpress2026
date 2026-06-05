from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import DetallePedido


@receiver([post_save, post_delete], sender=DetallePedido)
def recalcular_total_pedido(sender, instance, **kwargs):
    """
    Recalcula el total del pedido cada vez que se crea, edita o elimina un detalle.
    """
    pedido = instance.pedido
    with transaction.atomic():
        total = sum(
            detalle.cantidad * detalle.precio_unitario_momento
            for detalle in pedido.detalles.all()
        )
        pedido.total_pedido = total
        pedido.save(update_fields=['total_pedido'])