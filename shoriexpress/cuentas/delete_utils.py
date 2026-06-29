"""Eliminación segura con mensajes de la aplicación (sin error del host)."""
import logging

from django.contrib import messages
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


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
    except Exception:
        logger.exception('Error inesperado al eliminar %s', instance)
        messages.error(
            request,
            'No se pudo eliminar el registro. Revisa si tiene datos relacionados e intenta de nuevo.',
        )
    return redirect(url_redirect)
