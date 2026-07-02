"""Generación y sincronización automática de recibos."""

from decimal import Decimal

from dashboard.models import ConfiguracionSistema
from metodo_pago.models import MetodoPago

from .models import Recibo


def _total_lineas_pedido(pedido):
    return sum(
        detalle.cantidad * Decimal(str(detalle.precio_unitario_momento))
        for detalle in pedido.detalles.all()
    )


def calcular_totales_desde_pedido(pedido):
    subtotal_lineas = _total_lineas_pedido(pedido)
    descuento = Decimal(str(pedido.descuento_bonos or 0))
    if pedido.usar_bonos and descuento > 0:
        total = (subtotal_lineas - descuento).quantize(Decimal("0.01"))
    else:
        total = subtotal_lineas.quantize(Decimal("0.01"))

    config = ConfiguracionSistema.get_config()
    pct = Decimal(str(config.porcentaje_iva or 19)) / Decimal("100")
    if pct > 0:
        subtotal = (total / (Decimal("1") + pct)).quantize(Decimal("0.01"))
        iva = (total - subtotal).quantize(Decimal("0.01"))
    else:
        subtotal = total
        iva = Decimal("0.00")

    return subtotal, iva, total


def obtener_metodo_pago_default():
    metodo = MetodoPago.objects.filter(
        esta_activo=True, nombre_metodo__iexact="Efectivo"
    ).first()
    if metodo:
        return metodo
    return MetodoPago.objects.filter(esta_activo=True).order_by("pk").first()


def generar_recibo_si_aplica(pedido, metodo_pago=None):
    """
    Crea recibo automático si el pedido tiene líneas y aún no tiene recibo.
    Retorna (recibo|None, creado: bool).
    """
    if Recibo.objects.filter(pedido=pedido).exists():
        return Recibo.objects.get(pedido=pedido), False

    if not pedido.detalles.exists():
        return None, False

    metodo = metodo_pago or obtener_metodo_pago_default()
    if not metodo:
        return None, False

    subtotal, iva, total = calcular_totales_desde_pedido(pedido)
    if total <= 0:
        return None, False

    recibo = Recibo.objects.create(
        pedido=pedido,
        metodo_pago=metodo,
        subtotal=subtotal,
        iva_total=iva,
        total_pagado=total,
        puntos_ganados=0,
    )
    return recibo, True


def sincronizar_recibo_con_pedido(pedido):
    """Actualiza totales del recibo existente o lo crea si falta."""
    try:
        recibo = pedido.recibo
    except Recibo.DoesNotExist:
        return generar_recibo_si_aplica(pedido)

    if not pedido.detalles.exists():
        return recibo, False

    subtotal, iva, total = calcular_totales_desde_pedido(pedido)
    recibo.subtotal = subtotal
    recibo.iva_total = iva
    recibo.total_pagado = total
    recibo.save(update_fields=["subtotal", "iva_total", "total_pagado"])
    return recibo, False
