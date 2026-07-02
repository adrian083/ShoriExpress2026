from decimal import Decimal

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from pedido.models import Pedido
from recibo.services import sincronizar_recibo_con_pedido
from .models import DetallePedido


@receiver([post_save, post_delete], sender=DetallePedido)
def recalcular_total_pedido(sender, instance, **kwargs):
    """
    Recalcula el total del pedido cada vez que se crea, edita o elimina un detalle.
    Si el pedido usó bonos, conserva el descuento registrado en descuento_bonos.
    """
    pedido_id = instance.pedido_id
    if not pedido_id:
        return

    try:
        pedido = Pedido.objects.get(pk=pedido_id)
    except Pedido.DoesNotExist:
        return

    with transaction.atomic():
        subtotal_lineas = sum(
            detalle.cantidad * detalle.precio_unitario_momento
            for detalle in pedido.detalles.all()
        )
        descuento = Decimal(str(pedido.descuento_bonos or 0))
        if pedido.usar_bonos and descuento > 0:
            total = (subtotal_lineas - descuento).quantize(Decimal('0.01'))
        else:
            total = subtotal_lineas
        pedido.total_pedido = total
        pedido.save(update_fields=['total_pedido'])

    sincronizar_recibo_con_pedido(pedido)