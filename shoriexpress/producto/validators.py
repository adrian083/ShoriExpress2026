"""Validaciones compartidas para productos."""

from django.core.exceptions import ValidationError

from .models import Producto


def normalizar_texto_producto(valor):
    return " ".join((valor or "").strip().lower().split())


def buscar_duplicado_producto(nombre, excluir_pk=None):
    """
    Busca otro producto con el mismo nombre.
    La comparación ignora mayúsculas; el nombre debe ser único en el catálogo.
    """
    nombre_limpio = (nombre or "").strip()
    if not nombre_limpio:
        return None

    qs = Producto.objects.filter(nombre_producto__iexact=nombre_limpio)
    if excluir_pk:
        qs = qs.exclude(pk=excluir_pk)
    return qs.first()


def validar_producto_unico(nombre, excluir_pk=None):
    duplicado = buscar_duplicado_producto(nombre, excluir_pk=excluir_pk)
    if duplicado:
        raise ValidationError(
            "Ya existe un producto con ese nombre. Usa un nombre diferente."
        )
