"""Lógica de bonos de fidelidad al entregar pedidos."""
from decimal import Decimal

from django.db import transaction

from dashboard.models import ConfiguracionSistema

MAX_BONOS = 10


def otorgar_bono_si_aplica(pedido) -> int:
    """
    Otorga 1 bono cuando el pedido está entregado y el total alcanza el umbral.
    Idempotente: no duplica si el recibo ya registró puntos_ganados.
    Retorna 1 si se acreditó al usuario, 0 en caso contrario.
    """
    if pedido.estado_pedido != 'entregado':
        return 0

    recibo = getattr(pedido, 'recibo', None)
    if recibo is None:
        return 0

    if recibo.puntos_ganados > 0:
        return 0

    config = ConfiguracionSistema.get_config()
    umbral = Decimal(str(config.umbral_bonos))
    total = Decimal(str(pedido.total_pedido))
    if total < umbral:
        return 0

    bonos_otorgados = 0
    with transaction.atomic():
        usuario = pedido.usuario
        usuario.refresh_from_db()
        recibo.refresh_from_db()
        if recibo.puntos_ganados > 0:
            return 0

        if usuario.bonos_fidelidad < MAX_BONOS:
            usuario.bonos_fidelidad = min(usuario.bonos_fidelidad + 1, MAX_BONOS)
            usuario.save(update_fields=['bonos_fidelidad'])
            bonos_otorgados = 1

        recibo.puntos_ganados = 1
        recibo.save(update_fields=['puntos_ganados'])

    return bonos_otorgados
