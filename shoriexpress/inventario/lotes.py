"""Actualización de cantidades por lote al registrar movimientos manuales."""
from decimal import Decimal

from .models import InventarioLote


def ajustar_lote_entrada(insumo, codigo_lote, cantidad, fecha_vencimiento=None):
    codigo = (codigo_lote or "").strip()
    if not codigo:
        return
    obj, _ = InventarioLote.objects.get_or_create(
        insumo=insumo,
        codigo_lote=codigo,
        defaults={
            "cantidad": Decimal("0"),
            "fecha_vencimiento": fecha_vencimiento,
        },
    )
    obj.cantidad += cantidad
    if fecha_vencimiento:
        obj.fecha_vencimiento = fecha_vencimiento
    obj.save()


def ajustar_lote_salida(insumo, codigo_lote, cantidad):
    codigo = (codigo_lote or "").strip()
    if not codigo:
        return
    try:
        obj = InventarioLote.objects.get(insumo=insumo, codigo_lote=codigo)
    except InventarioLote.DoesNotExist:
        return
    obj.cantidad -= cantidad
    if obj.cantidad < 0:
        obj.cantidad = Decimal("0")
    obj.save()
