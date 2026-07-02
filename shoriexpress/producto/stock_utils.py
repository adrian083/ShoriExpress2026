"""Utilidades de stock para venta al cliente."""

from decimal import Decimal

from receta.models import Receta


def max_unidades_por_inventario(producto):
    """
    Máximo de unidades vendibles según recetas e inventario.
    None si el producto no tiene receta (sin límite por insumos).
    """
    recetas = Receta.objects.select_related("insumo").filter(producto=producto)
    if not recetas.exists():
        return None

    maximos = []
    for receta in recetas:
        if receta.cantidad_requerida is None or receta.cantidad_requerida <= 0:
            continue
        if receta.insumo.stock_actual is None or receta.insumo.stock_actual <= 0:
            return 0
        maximos.append(
            int(Decimal(receta.insumo.stock_actual) // Decimal(receta.cantidad_requerida))
        )

    if not maximos:
        return None
    return max(0, min(maximos))


def mensaje_stock_limitado(producto, max_disponible):
    if max_disponible is None:
        return None
    if max_disponible <= 0:
        return f"Sin stock disponible para {producto.nombre_producto}."
    return (
        f"Stock limitado para {producto.nombre_producto}: "
        f"máximo {max_disponible} unidad(es). Indica en el carrito cuántas deseas comprar."
    )
