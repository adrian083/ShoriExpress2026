from decimal import Decimal
from unittest.mock import patch

from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

from inventario.models import Inventario
from producto import views as producto_views
from producto.models import Producto
from receta.models import Receta
from rol.models import Rol
from usuario.models import Usuario


class ProductoAvailabilityTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol_admin = Rol.objects.create(nombre_rol='Administrador')
        cls.admin_user = Usuario.objects.create(
            tipo_documento='CC',
            documento='1234567890',
            primer_nombre='Admin',
            apellido='Shori',
            correo='admin@test.com',
            telefono='1234567890',
            direccion='Calle 1',
            nombre_usuario='admin_test',
            contrasena='1234',
            rol=cls.rol_admin,
            estado='activo',
        )
        cls.producto = Producto.objects.create(
            nombre_producto='Perro Clásico',
            descripcion_producto='Producto de prueba',
            precio_venta=Decimal('9.50'),
            esta_disponible=True,
            esta_habilitado=True,
        )
        cls.insumo = Inventario.objects.create(
            nombre_insumo='Pan',
            categoria_insumo='Base',
            stock_actual=Decimal('1.00'),
            stock_minimo=Decimal('1.00'),
            precio_compra_referencia=Decimal('1000.00'),
        )

    def test_check_ingredient_stock_returns_true_for_sufficient_supply(self):
        Receta.objects.create(
            producto=self.producto,
            insumo=self.insumo,
            cantidad_requerida=Decimal('1.00'),
        )

        hay_stock, faltantes = self.producto.check_ingredient_stock()

        self.assertTrue(hay_stock)
        self.assertEqual(faltantes, [])

    def test_update_availability_based_on_stock_disables_product_when_ingredients_are_insufficient(self):
        Receta.objects.create(
            producto=self.producto,
            insumo=self.insumo,
            cantidad_requerida=Decimal('5.00'),
        )

        result = self.producto.update_availability_based_on_stock()

        self.assertFalse(result)
        self.producto.refresh_from_db()
        self.assertFalse(self.producto.esta_habilitado)

    def test_is_available_for_sale_is_false_when_stock_is_insufficient(self):
        Receta.objects.create(
            producto=self.producto,
            insumo=self.insumo,
            cantidad_requerida=Decimal('5.00'),
        )

        self.assertFalse(self.producto.is_available_for_sale)

    def test_toggle_habilitado_altera_el_estado_de_visibilidad(self):
        factory = RequestFactory()
        request = factory.post(
            reverse('toggle_habilitado', kwargs={'producto_id': self.producto.pk})
        )

        session_middleware = SessionMiddleware(lambda r: None)
        session_middleware.process_request(request)
        request.session['usuario_id'] = str(self.admin_user.pk)
        request.session['last_activity'] = 0
        request.session.save()

        message_middleware = MessageMiddleware(lambda r: None)
        message_middleware.process_request(request)

        response = producto_views.toggle_habilitado(
            request,
            producto_id=self.producto.pk,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('lista_productos'))
        self.producto.refresh_from_db()
        self.assertFalse(self.producto.esta_habilitado)

    def test_agregar_producto_via_get_agrega_al_carrito(self):
        with patch('producto.views.HorarioComercialValidator.es_dentro_horario', return_value=True):
            response = self.client.get(
                reverse('agregar_al_carrito', kwargs={'producto_id': self.producto.pk})
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('landing'))

    def test_restar_y_eliminar_carrito_requieren_post(self):
        with patch('producto.views.HorarioComercialValidator.es_dentro_horario', return_value=True):
            self.client.get(reverse('agregar_al_carrito', kwargs={'producto_id': self.producto.pk}))
            self.client.get(reverse('agregar_al_carrito', kwargs={'producto_id': self.producto.pk}))

        get_restar = self.client.get(
            reverse('restar_producto', kwargs={'producto_id': self.producto.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'ajax': '1'},
        )
        self.assertEqual(get_restar.status_code, 200)
        self.assertTrue(get_restar.json()['success'])

        get_eliminar = self.client.get(
            reverse('eliminar_del_carrito', kwargs={'producto_id': self.producto.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'ajax': '1'},
        )
        self.assertEqual(get_eliminar.status_code, 200)

        get_limpiar = self.client.get(
            reverse('limpiar_carrito'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            data={'ajax': '1'},
        )
        self.assertEqual(get_limpiar.status_code, 200)
        session = self.client.session
        self.assertEqual(session.get('cart', {}), {})

    def test_set_cantidad_carrito_via_get(self):
        with patch('producto.views.HorarioComercialValidator.es_dentro_horario', return_value=True):
            self.client.get(reverse('agregar_al_carrito', kwargs={'producto_id': self.producto.pk}))

        response = self.client.get(
            reverse('set_cantidad_carrito', kwargs={'producto_id': self.producto.pk}),
            {'cantidad': 3, 'ajax': '1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['items'][0]['cantidad'], 3)

