from unittest.mock import patch

from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.db.models.deletion import ProtectedError
from django.test import RequestFactory, TestCase
from django.urls import reverse

from cuentas.delete_utils import eliminar_con_mensaje
from inventario.models import Inventario


def _request_with_messages(method='post', path='/'):
    factory = RequestFactory()
    request = getattr(factory, method)(path)
    session_middleware = __import__(
        'django.contrib.sessions.middleware', fromlist=['SessionMiddleware']
    ).SessionMiddleware(lambda r: None)
    session_middleware.process_request(request)
    request.session.save()
    MessageMiddleware(lambda r: None).process_request(request)
    return request


class EliminarConMensajeTest(TestCase):
    def test_eliminar_con_mensaje_exito(self):
        insumo = Inventario.objects.create(
            nombre_insumo='Sal',
            categoria_insumo='Condimento',
            stock_actual=1,
            stock_minimo=1,
            precio_compra_referencia=100,
        )
        request = _request_with_messages()

        response = eliminar_con_mensaje(
            request,
            insumo,
            mensaje_ok='Insumo eliminado.',
            url_redirect='lista_inventario',
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('lista_inventario'))
        msgs = list(get_messages(request))
        self.assertEqual(str(msgs[0]), 'Insumo eliminado.')
        self.assertFalse(Inventario.objects.filter(pk=insumo.pk).exists())

    def test_eliminar_con_mensaje_protegido(self):
        insumo = Inventario.objects.create(
            nombre_insumo='Carne',
            categoria_insumo='Proteína',
            stock_actual=5,
            stock_minimo=1,
            precio_compra_referencia=100,
        )
        request = _request_with_messages()

        with patch.object(
            Inventario,
            'delete',
            side_effect=ProtectedError('blocked', {Inventario: {insumo}}),
        ):
            response = eliminar_con_mensaje(
                request,
                insumo,
                mensaje_ok='Insumo eliminado.',
                url_redirect='lista_inventario',
                mensaje_error='No se puede eliminar por recetas.',
            )

        self.assertEqual(response.status_code, 302)
        msgs = list(get_messages(request))
        self.assertEqual(str(msgs[0]), 'No se puede eliminar por recetas.')
