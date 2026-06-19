from django.db.models import F
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from inventario.models import Inventario
from movimiento_inventario.models import MovimientoInventario
from receta.models import Receta

from .models import Pedido


@receiver(pre_save, sender=Pedido)
def pedido_pre_save(sender, instance, **kwargs):
    """
    - Guarda el estado anterior (para inventario y transiciones).
    - Al pasar a entregado, fija fecha_entrega_real una sola vez.
    """
    if not instance.pk:
        instance._estado_pedido_anterior = None
        return
    try:
        anterior = Pedido.objects.get(pk=instance.pk)
    except Pedido.DoesNotExist:
        instance._estado_pedido_anterior = None
        return
    instance._estado_pedido_anterior = anterior.estado_pedido
    if (
        instance.estado_pedido == "entregado"
        and anterior.estado_pedido != "entregado"
        and instance.fecha_entrega_real is None
    ):
        instance.fecha_entrega_real = timezone.now()


@receiver(post_save, sender=Pedido)
def procesar_inventario_por_pedido(sender, instance, created, **kwargs):
    """
    Descuenta insumos solo al entrar en 'preparacion' (no en cada save mientras sigue ahí).
    """
    anterior = getattr(instance, "_estado_pedido_anterior", None)
    entra_en_preparacion = instance.estado_pedido == "preparacion" and (
        created or anterior != "preparacion"
    )
    if not entra_en_preparacion:
        return

    with transaction.atomic():
        detalles = instance.detalles.all()
        for detalle in detalles:
            recetas = Receta.objects.filter(producto=detalle.producto)
            for ingrediente in recetas:
                cantidad_a_descontar = ingrediente.cantidad_requerida * detalle.cantidad
                insumo_db = Inventario.objects.select_for_update().get(pk=ingrediente.insumo_id)
                if cantidad_a_descontar > insumo_db.stock_actual:
                    raise ValueError(
                        f"Stock insuficiente para '{insumo_db.nombre_insumo}' al procesar el Pedido #{instance.pk}."
                    )

                MovimientoInventario.objects.create(
                    insumo=insumo_db,
                    usuario=instance.usuario,
                    tipo_movimiento="salida_venta",
                    cantidad=cantidad_a_descontar,
                    observaciones=f"Salida automática por Pedido #{instance.pk}",
                )
                insumo_db.stock_actual = F("stock_actual") - cantidad_a_descontar
                insumo_db.save(update_fields=["stock_actual"])
                insumo_db.refresh_from_db(fields=["stock_actual", "stock_minimo"])
                if insumo_db.stock_actual <= 0:
                    insumo_db.stock_actual = 0
                    insumo_db.estado_insumo = "agotado"
                    insumo_db.save(update_fields=["stock_actual", "estado_insumo"])
                elif insumo_db.stock_actual <= insumo_db.stock_minimo:
                    insumo_db.estado_insumo = "pocos"
                    insumo_db.save(update_fields=["estado_insumo"])
                else:
                    insumo_db.estado_insumo = "disponible"
                    insumo_db.save(update_fields=["estado_insumo"])


@receiver(post_save, sender=Pedido)
def otorgar_bonos_al_entregar(sender, instance, created, **kwargs):
    """Acredita bonos de fidelidad cuando el pedido pasa a entregado."""
    anterior = getattr(instance, "_estado_pedido_anterior", None)
    if instance.estado_pedido != "entregado" or anterior == "entregado":
        return

    from .bonos import otorgar_bono_si_aplica
    otorgar_bono_si_aplica(instance)
