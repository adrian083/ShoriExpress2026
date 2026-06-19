"""
Carga datos de demostración (roles, usuarios, inventario, productos, recetas).
Idempotente: se puede ejecutar varias veces sin duplicar registros.

Contraseña de todos los usuarios demo: configurable con SEED_DEMO_PASSWORD en .env
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

from cuentas.demo_credentials import get_demo_password
from inventario.models import Inventario, InventarioLote
from metodo_pago.models import MetodoPago
from producto.models import Producto
from receta.models import Receta
from rol.models import Rol
from usuario.models import Usuario

from cuentas.password_utils import hash_password

ROLES = ['Administrador', 'Cliente', 'Empleado', 'Reparto']

USUARIOS = [
    {
        'documento': '1000000001',
        'nombre_usuario': 'admin',
        'primer_nombre': 'Sofía',
        'apellido': 'Morales',
        'correo': 'admin@shoriexpress.local',
        'telefono': '3001112233',
        'direccion': 'Calle 72 #10-34, Chapinero, Bogotá',
        'rol': 'Administrador',
        'puntos_acumulados': 0,
        'bonos_fidelidad': 0,
    },
    {
        'documento': '52345678',
        'nombre_usuario': 'mariag',
        'primer_nombre': 'María',
        'apellido': 'Gómez Lozano',
        'correo': 'maria@ejemplo.com',
        'telefono': '3109876543',
        'direccion': 'Carrera 13 #64-39, Bogotá',
        'rol': 'Cliente',
        'puntos_acumulados': 120,
        'bonos_fidelidad': 7,
    },
    {
        'documento': '79876543',
        'nombre_usuario': 'carlosr',
        'primer_nombre': 'Carlos',
        'apellido': 'Rincón Vega',
        'correo': 'carlos@ejemplo.com',
        'telefono': '3205554411',
        'direccion': 'Avenida Ciudad de Cali #51-66, Bogotá',
        'rol': 'Cliente',
        'puntos_acumulados': 45,
        'bonos_fidelidad': 0,
    },
    {
        'documento': '1122334455',
        'nombre_usuario': 'andrea_cocina',
        'primer_nombre': 'Andrea',
        'apellido': 'Benítez',
        'correo': 'empleado@shoriexpress.local',
        'telefono': '3004445566',
        'direccion': 'Cl. 47 sur #13a-39, Local Shori',
        'rol': 'Empleado',
        'puntos_acumulados': 0,
        'bonos_fidelidad': 0,
    },
    {
        'documento': '9012345678',
        'nombre_usuario': 'diegoreparto',
        'primer_nombre': 'Diego',
        'apellido': 'Moncada',
        'correo': 'diego.reparto@shoriexpress.local',
        'telefono': '3112003344',
        'direccion': 'Kr 24 #17-68 sur, Tunjuelito, Bogotá',
        'rol': 'Reparto',
        'puntos_acumulados': 0,
        'bonos_fidelidad': 0,
    },
]

METODOS_PAGO = [
    ('Efectivo', 'Pago en efectivo (domicilio o mostrador)'),
    ('Nequi', 'Pago o transferencia con Nequi al número del local'),
    ('Daviplata', 'Daviplata QR o transferencia'),
    ('Tarjeta débito/crédito', 'Datáfono Bancolombia en punto de venta'),
    ('Transferencia bancaria', 'Pagos a cuentas Bancolombia / BBVA'),
]

INSUMOS = [
    ('Chorizo artesanal res cervuno 12 mm', 'Cárnicos', 'KG', '18.50', '5.00', '40.00', '18900.00', '0.00'),
    ('Pan brioche perro caliente', 'Panadería', 'UN', '120.00', '30.00', '200.00', '820.00', '0.00'),
    ('Papa criolla pastusa', 'Verduras', 'KG', '25.00', '8.00', '50.00', '3600.00', '0.00'),
    ('Queso mozzarella rallado Ronquer', 'Lácteos', 'KG', '4.20', '1.00', '10.00', '12400.00', '0.00'),
    ('Aceite vegetal oleica 900 ml', 'Abarrotes', 'LT', '8.00', '2.00', '15.00', '9800.00', '19.00'),
    ('Cebolla cabezona roja', 'Verduras', 'KG', '12.00', '3.00', '25.00', '2900.00', '0.00'),
    ('Sal refisal yodada', 'Abarrotes', 'KG', '5.00', '1.00', '12.00', '2200.00', '19.00'),
    ('Salsa tártara lonko 250 g', 'Abarrotes', 'UN', '40.00', '10.00', '80.00', '4500.00', '19.00'),
    ('Arepa boyacense blanca', 'Panadería', 'UN', '200.00', '50.00', '400.00', '650.00', '0.00'),
    ('Maracuyá badea malla 10 u', 'Frutas', 'UN', '15.00', '5.00', '40.00', '18500.00', '0.00'),
    ('Gaseosa Postobón 400 ml retornable', 'Bebidas', 'UN', '96.00', '24.00', '200.00', '1600.00', '19.00'),
]

PRODUCTOS = [
    (
        'Perro chorizo clásico',
        'Chorizo a la plancha en pan brioche, salsas lácteas, papa en cascos y toque de cebolla caramelizada.',
        '15900.00',
        False,
        'Lote SE-2026-001 chorizo Morlin / Pan La Especial',
    ),
    (
        'Chorizo a la plancha (250 g)',
        'Porción generosa con chimichurri, arepa boyacense o media papa a la francesa (elige en notas).',
        '19500.00',
        False,
        None,
    ),
    (
        'Combo familiar 4 personas',
        'Cuatro perros clásicos, papa medianera para compartir y cuatro gaseosas 400 ml.',
        '68900.00',
        True,
        None,
    ),
    (
        'Papa chorizo gratinada',
        'Papa criolla cocida con trozos de chorizo, queso mozzarella gratinado y perejil.',
        '13200.00',
        False,
        None,
    ),
    (
        'Gaseosa personal 400 ml',
        'Gaseosa fría (marca según disponibilidad en nevera).',
        '3800.00',
        False,
        None,
    ),
    (
        'Arepa con chorizo antioqueño',
        'Arepa blanca asada con medio chorizo desmechado y hogao casero.',
        '9800.00',
        False,
        None,
    ),
    (
        'Jugo natural maracuyá',
        'Jugo en agua o en leche 400 ml, pulpa fresca.',
        '6500.00',
        False,
        None,
    ),
]

LOTES = [
    ('Chorizo artesanal res cervuno 12 mm', 'SE-2026-001', '10.00', '2026-07-01'),
    ('Pan brioche perro caliente', 'PAN-BRIO-ENE26', '80.00', '2026-02-20'),
    ('Papa criolla pastusa', 'PAP-PST-004', '20.00', '2026-04-25'),
    ('Gaseosa Postobón 400 ml retornable', 'GAS-PTB-ENE', '48.00', '2026-12-01'),
]

# (producto, insumo, cantidad)
RECETAS = [
    ('Perro chorizo clásico', 'Chorizo artesanal res cervuno 12 mm', '0.12'),
    ('Perro chorizo clásico', 'Pan brioche perro caliente', '1.00'),
    ('Perro chorizo clásico', 'Papa criolla pastusa', '0.08'),
    ('Perro chorizo clásico', 'Cebolla cabezona roja', '0.02'),
    ('Perro chorizo clásico', 'Salsa tártara lonko 250 g', '0.04'),
    ('Chorizo a la plancha (250 g)', 'Chorizo artesanal res cervuno 12 mm', '0.25'),
    ('Chorizo a la plancha (250 g)', 'Cebolla cabezona roja', '0.08'),
    ('Chorizo a la plancha (250 g)', 'Arepa boyacense blanca', '1.00'),
    ('Papa chorizo gratinada', 'Papa criolla pastusa', '0.30'),
    ('Papa chorizo gratinada', 'Chorizo artesanal res cervuno 12 mm', '0.10'),
    ('Papa chorizo gratinada', 'Queso mozzarella rallado Ronquer', '0.06'),
    ('Arepa con chorizo antioqueño', 'Chorizo artesanal res cervuno 12 mm', '0.45'),
    ('Arepa con chorizo antioqueño', 'Arepa boyacense blanca', '1.00'),
    ('Combo familiar 4 personas', 'Chorizo artesanal res cervuno 12 mm', '0.08'),
    ('Combo familiar 4 personas', 'Pan brioche perro caliente', '4.00'),
    ('Combo familiar 4 personas', 'Papa criolla pastusa', '0.60'),
    ('Combo familiar 4 personas', 'Gaseosa Postobón 400 ml retornable', '4.00'),
    ('Jugo natural maracuyá', 'Maracuyá badea malla 10 u', '0.35'),
    ('Gaseosa personal 400 ml', 'Gaseosa Postobón 400 ml retornable', '1.00'),
]


class Command(BaseCommand):
    help = 'Carga datos de demostración para ShoriExpress (idempotente).'

    def handle(self, *args, **options):
        demo_password = get_demo_password()
        roles = self._seed_roles()
        usuarios = self._seed_usuarios(roles, demo_password)
        pagos = self._seed_metodos_pago()
        insumos = self._seed_insumos()
        productos = self._seed_productos()
        lotes = self._seed_lotes(insumos)
        recetas = self._seed_recetas(insumos, productos)

        self.stdout.write(self.style.SUCCESS(
            f'Demo lista: {len(roles)} roles, {usuarios} usuarios, {pagos} métodos de pago, '
            f'{len(insumos)} insumos, {len(productos)} productos, {lotes} lotes, {recetas} recetas.'
        ))
        self.stdout.write('Contraseña de todos los usuarios demo: ver SEED_DEMO_PASSWORD en .env')
        self.stdout.write('Admin: usuario admin | Cliente: mariag | Empleado: andrea_cocina')

    def _seed_roles(self):
        created = []
        for nombre in ROLES:
            rol, was_created = Rol.objects.get_or_create(nombre_rol=nombre)
            created.append(rol)
            if was_created:
                self.stdout.write(f'  + Rol: {nombre}')
        return created

    def _seed_usuarios(self, roles, demo_password):
        roles_map = {r.nombre_rol: r for r in roles}
        count = 0
        pwd_hash = hash_password(demo_password)
        for data in USUARIOS:
            rol = roles_map[data['rol']]
            _, was_created = Usuario.objects.get_or_create(
                documento=data['documento'],
                defaults={
                    'tipo_documento': 'CC',
                    'nombre_usuario': data['nombre_usuario'],
                    'primer_nombre': data['primer_nombre'],
                    'apellido': data['apellido'],
                    'correo': data['correo'],
                    'telefono': data['telefono'],
                    'direccion': data['direccion'],
                    'contrasena': pwd_hash,
                    'puntos_acumulados': data['puntos_acumulados'],
                    'bonos_fidelidad': data['bonos_fidelidad'],
                    'estado': 'activo',
                    'rol': rol,
                },
            )
            if was_created:
                count += 1
                self.stdout.write(f'  + Usuario: {data["nombre_usuario"]}')
        return count

    def _seed_metodos_pago(self):
        count = 0
        for nombre, descripcion in METODOS_PAGO:
            _, was_created = MetodoPago.objects.get_or_create(
                nombre_metodo=nombre,
                defaults={'descripcion': descripcion, 'esta_activo': True},
            )
            if was_created:
                count += 1
                self.stdout.write(f'  + Método de pago: {nombre}')
        return count

    def _seed_insumos(self):
        insumos = {}
        for row in INSUMOS:
            nombre, categoria, unidad, stock, minimo, maximo, precio, iva = row
            insumo, was_created = Inventario.objects.get_or_create(
                nombre_insumo=nombre,
                defaults={
                    'categoria_insumo': categoria,
                    'unidad_medida': unidad,
                    'stock_actual': Decimal(stock),
                    'stock_minimo': Decimal(minimo),
                    'stock_maximo': Decimal(maximo),
                    'precio_compra_referencia': Decimal(precio),
                    'iva_porcentaje': Decimal(iva),
                    'estado_insumo': 'disponible',
                },
            )
            insumos[nombre] = insumo
            if was_created:
                self.stdout.write(f'  + Insumo: {nombre}')
        return insumos

    def _seed_productos(self):
        productos = {}
        for nombre, descripcion, precio, es_combo, registro in PRODUCTOS:
            producto, was_created = Producto.objects.get_or_create(
                nombre_producto=nombre,
                defaults={
                    'descripcion_producto': descripcion,
                    'precio_venta': Decimal(precio),
                    'es_combo': es_combo,
                    'esta_disponible': True,
                    'esta_habilitado': True,
                    'registro_movimiento_inicial': registro or '',
                },
            )
            productos[nombre] = producto
            if was_created:
                self.stdout.write(f'  + Producto: {nombre}')
        return productos

    def _seed_lotes(self, insumos):
        count = 0
        for insumo_nombre, codigo, cantidad, vencimiento in LOTES:
            insumo = insumos[insumo_nombre]
            _, was_created = InventarioLote.objects.get_or_create(
                insumo=insumo,
                codigo_lote=codigo,
                defaults={
                    'cantidad': Decimal(cantidad),
                    'fecha_vencimiento': vencimiento,
                },
            )
            if was_created:
                count += 1
                self.stdout.write(f'  + Lote: {codigo}')
        return count

    def _seed_recetas(self, insumos, productos):
        count = 0
        for prod_nombre, insumo_nombre, cantidad in RECETAS:
            _, was_created = Receta.objects.get_or_create(
                producto=productos[prod_nombre],
                insumo=insumos[insumo_nombre],
                defaults={'cantidad_requerida': Decimal(cantidad)},
            )
            if was_created:
                count += 1
        if count:
            self.stdout.write(f'  + {count} recetas')
        return count
