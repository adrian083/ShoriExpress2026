"""Eliminación segura con mensajes de la aplicación (sin error del host)."""
from django.contrib import messages
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect


def eliminar_con_mensaje(request, instance, *, mensaje_ok, url_redirect, mensaje_error=None):
    """
    Elimina un registro y redirige con mensaje de éxito o error legible.
  """
    etiqueta = mensaje_error or (
        'No se puede eliminar porque tiene registros relacionados en el sistema.'
    )
    try:
        instance.delete()
        messages.success(request, mensaje_ok)
    except (ProtectedError, IntegrityError):
        messages.error(request, etiqueta)
    return redirect(url_redirect)
