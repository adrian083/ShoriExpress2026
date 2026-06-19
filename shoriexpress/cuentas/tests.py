from django.test import RequestFactory, TestCase
from django.urls import reverse

from producto.models import Producto
from rol.models import Rol
from usuario.models import Usuario

from cuentas import password_utils, views as cuentas_views
from .context_processors import user_context
from .testing_helpers import (
    TEST_USER_SECRET,
    login_post_data,
    usuario_con_fecha_credencial_invalida,
)


class CarritoTemplateTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.rol = Rol.objects.create(nombre_rol='Cliente')
        self.usuario = Usuario.objects.create(
            tipo_documento='CC',
            documento='1234567890',
            primer_nombre='Ana',
            apellido='García',
            correo='ana@example.com',
            telefono='3001234567',
            direccion='Calle 10 # 20-30',
            nombre_usuario='anagarcia',
            contrasena=password_utils.hash_password(TEST_USER_SECRET),
            rol=self.rol,
        )

    def test_carrito_muestra_telefono_del_usuario(self):
        request = self.factory.get(reverse('ver_carrito'))
        request.session = self.client.session
        request.session['usuario_id'] = self.usuario.pk
        request.session.save()

        response = cuentas_views.ver_carrito(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '3001234567')
        self.assertContains(response, 'Calle 10 # 20-30')

    def test_logout_via_get_cierra_sesion(self):
        session = self.client.session
        session['usuario_id'] = self.usuario.pk
        session.save()

        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('landing'))
        self.assertNotIn('usuario_id', self.client.session)

    def test_login_acepta_nombres_de_usuario_con_distinta_mayuscula(self):
        response = self.client.post(
            reverse('login'),
            login_post_data('AnAgarcia', TEST_USER_SECRET),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bienvenido')
        self.assertIn('usuario_id', self.client.session)

    def test_credencial_vencida_no_falla_con_valores_invalidos(self):
        usuario = usuario_con_fecha_credencial_invalida()
        check_fn = getattr(cuentas_views, '_password_vencida')

        self.assertFalse(check_fn(usuario))

    def test_context_processor_expone_usuario_logueado_para_el_menu(self):
        request = self.factory.get(reverse('landing'))
        request.session = self.client.session
        request.session['usuario_id'] = self.usuario.pk
        request.session['usuario_rol'] = self.rol.nombre_rol
        request.session.save()

        context = user_context(request)

        self.assertEqual(context['usuario_logueado'], self.usuario)
        self.assertFalse(context['es_admin'])

    def test_menu_publico_muestra_productos_en_menu_aunque_no_esten_habilitados(self):
        Producto.objects.create(
            nombre_producto='Perro test',
            descripcion_producto='Producto visible',
            precio_venta=12000,
            esta_disponible=True,
            esta_habilitado=False,
        )

        request = self.factory.get(reverse('menu_publico'))
        request.session = self.client.session
        response = cuentas_views.ver_menu_publico(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Perro test')
