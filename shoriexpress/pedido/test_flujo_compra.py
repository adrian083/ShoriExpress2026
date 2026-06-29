from datetime import time
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from cuentas.password_utils import hash_password
from dashboard.models import ConfiguracionSistema
from inventario.models import Inventario
from metodo_pago.models import MetodoPago
from pedido.bonos import otorgar_bono_si_aplica
from pedido.models import Pedido
from producto.models import Producto
from receta.models import Receta
from recibo.models import Recibo
from rol.models import Rol
from usuario.models import Usuario


class BonosFidelidadTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol_cliente = Rol.objects.create(nombre_rol='Cliente')
        cls.rol_admin = Rol.objects.create(nombre_rol='Administrador')
        cls.cliente = Usuario.objects.create(
            tipo_documento='CC',
            documento='80000001',
            primer_nombre='Cliente',
            apellido='Bono',
            correo='cliente.bono@test.com',
            telefono='3008000001',
            direccion='Calle 1',
            nombre_usuario='cliente_bono',
            contrasena=hash_password('test-secret'),
            rol=cls.rol_cliente,
            bonos_fidelidad=0,
        )
        cls.admin = Usuario.objects.create(
            tipo_documento='CC',
            documento='80000002',
            primer_nombre='Admin',
            apellido='Bono',
            correo='admin.bono@test.com',
            telefono='3008000002',
            direccion='Calle 2',
            nombre_usuario='admin_bono',
            contrasena=hash_password('test-secret'),
            rol=cls.rol_admin,
        )
        ConfiguracionSistema.objects.create(
            nombre_sistema='ShoriExpress',
            hora_apertura=time(0, 0),
            hora_cierre=time(23, 59),
            porcentaje_iva=Decimal('19.00'),
            umbral_bonos=Decimal('50000.00'),
        )
        cls.metodo = MetodoPago.objects.get_or_create(
            nombre_metodo='Efectivo',
            defaults={'descripcion': 'Efectivo', 'esta_activo': True},
        )[0]

    def _crear_pedido_con_recibo(self, total, estado='pendiente', bonos_usuario=0):
        self.cliente.bonos_fidelidad = bonos_usuario
        self.cliente.save(update_fields=['bonos_fidelidad'])
        pedido = Pedido.objects.create(
            usuario=self.cliente,
            tipo_pedido='domicilio',
            direccion_pedido='Calle 1',
            estado_pedido=estado,
            total_pedido=Decimal(str(total)),
        )
        recibo = Recibo.objects.create(
            pedido=pedido,
            metodo_pago=self.metodo,
            subtotal=Decimal(str(total)) / Decimal('1.19'),
            iva_total=Decimal('0'),
            total_pagado=Decimal(str(total)),
            puntos_ganados=0,
        )
        return pedido, recibo

    def test_no_otorga_bono_si_pedido_no_esta_entregado(self):
        pedido, _ = self._crear_pedido_con_recibo(68900, estado='pendiente')
        self.assertEqual(otorgar_bono_si_aplica(pedido), 0)
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.bonos_fidelidad, 0)

    def test_no_otorga_bono_si_total_menor_al_umbral(self):
        pedido, _ = self._crear_pedido_con_recibo(15900, estado='entregado')
        self.assertEqual(otorgar_bono_si_aplica(pedido), 0)

    def test_otorga_bono_al_entregar_pedido_calificado(self):
        pedido, recibo = self._crear_pedido_con_recibo(68900, estado='entregado')
        self.assertEqual(otorgar_bono_si_aplica(pedido), 1)
        self.cliente.refresh_from_db()
        recibo.refresh_from_db()
        self.assertEqual(self.cliente.bonos_fidelidad, 1)
        self.assertEqual(recibo.puntos_ganados, 1)

    def test_no_duplica_bono_si_ya_fue_otorgado(self):
        pedido, recibo = self._crear_pedido_con_recibo(68900, estado='entregado', bonos_usuario=1)
        recibo.puntos_ganados = 1
        recibo.save(update_fields=['puntos_ganados'])
        self.assertEqual(otorgar_bono_si_aplica(pedido), 0)
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.bonos_fidelidad, 1)

    def test_cambiar_estado_a_entregado_acredita_bono(self):
        pedido, _ = self._crear_pedido_con_recibo(68900, estado='pendiente')
        session = self.client.session
        session['usuario_id'] = self.admin.pk
        session['usuario_rol'] = 'Administrador'
        session['last_activity'] = 0
        session.save()

        response = self.client.post(
            reverse('cambiar_estado', kwargs={'pedido_id': pedido.pk}),
            {'nuevo_estado': 'entregado'},
        )

        self.assertEqual(response.status_code, 302)
        self.cliente.refresh_from_db()
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado_pedido, 'entregado')
        self.assertEqual(self.cliente.bonos_fidelidad, 1)


class FinalizarCompraTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rol = Rol.objects.create(nombre_rol='Cliente')
        cls.usuario = Usuario.objects.create(
            tipo_documento='CC',
            documento='70000001',
            primer_nombre='Compra',
            apellido='Test',
            correo='compra@test.com',
            telefono='3007000001',
            direccion='Calle 10',
            nombre_usuario='compra_test',
            contrasena=hash_password('test-secret'),
            rol=cls.rol,
            bonos_fidelidad=5,
        )
        cls.insumo = Inventario.objects.create(
            nombre_insumo='Insumo checkout',
            categoria_insumo='Base',
            unidad_medida='UN',
            stock_actual=Decimal('100.00'),
            stock_minimo=Decimal('1.00'),
            precio_compra_referencia=Decimal('1000.00'),
        )
        cls.producto = Producto.objects.create(
            nombre_producto='Combo test',
            descripcion_producto='Para prueba checkout',
            precio_venta=Decimal('68900.00'),
            esta_disponible=True,
            esta_habilitado=True,
        )
        Receta.objects.create(
            producto=cls.producto,
            insumo=cls.insumo,
            cantidad_requerida=Decimal('1.00'),
        )
        MetodoPago.objects.get_or_create(
            nombre_metodo='Efectivo',
            defaults={'descripcion': 'Efectivo', 'esta_activo': True},
        )
        ConfiguracionSistema.objects.create(
            nombre_sistema='ShoriExpress',
            hora_apertura=time(0, 0),
            hora_cierre=time(23, 59),
            porcentaje_iva=Decimal('19.00'),
            umbral_bonos=Decimal('50000.00'),
        )

    def _login_y_carrito(self, cantidad=1):
        session = self.client.session
        session['usuario_id'] = self.usuario.pk
        session['usuario_rol'] = 'Cliente'
        session['last_activity'] = 0
        precio = str(self.producto.precio_venta)
        session['cart'] = {
            str(self.producto.pk): {
                'producto_id': self.producto.pk,
                'nombre': self.producto.nombre_producto,
                'precio': precio,
                'cantidad': cantidad,
                'total': precio,
            }
        }
        session.save()

    @patch('pedido.views.HorarioComercialValidator.es_dentro_horario', return_value=True)
    def test_finalizar_compra_no_suma_bono_al_pagar(self, _mock_horario):
        self._login_y_carrito()
        bonos_antes = self.usuario.bonos_fidelidad

        response = self.client.post(
            reverse('finalizar_compra'),
            {
                'tipo_pedido': 'domicilio',
                'direccion_pedido': 'Calle 10',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.bonos_fidelidad, bonos_antes)
        pedido = Pedido.objects.filter(usuario=self.usuario).latest('pk')
        self.assertEqual(pedido.recibo.puntos_ganados, 0)

    @patch('pedido.views.HorarioComercialValidator.es_dentro_horario', return_value=True)
    def test_finalizar_compra_redime_bonos_con_descuento(self, _mock_horario):
        self._login_y_carrito()
        bonos_antes = self.usuario.bonos_fidelidad

        response = self.client.post(
            reverse('finalizar_compra'),
            {
                'tipo_pedido': 'domicilio',
                'direccion_pedido': 'Calle 10',
                'redimir_bonos': '1',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.usuario.refresh_from_db()
        pedido = Pedido.objects.filter(usuario=self.usuario).latest('pk')
        self.assertTrue(pedido.usar_bonos)
        self.assertEqual(self.usuario.bonos_fidelidad, bonos_antes - 5)
        self.assertEqual(pedido.descuento_bonos, Decimal('3445.00'))
        self.assertEqual(pedido.total_pedido, Decimal('65455.00'))
        self.assertEqual(pedido.recibo.total_pagado, Decimal('65455.00'))
