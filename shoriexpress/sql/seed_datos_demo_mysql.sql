-- =============================================================================
-- Shori Express — datos de demostración (MySQL / MariaDB, XAMPP)
-- =============================================================================
-- Antes de ejecutar:
--   1. CREATE DATABASE shori_express CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
--   2. python manage.py migrate
--   3. USE shori_express (o tu nombre de base).
--
-- NO usa TRUNCATE. Solo inserta filas que aún no existen (documento, correo,
-- nombres de insumo/producto, par insumo+código de lote, par producto+insumo
-- en receta, pedidos identificados por fecha+usuario+total, etc.).
-- Ejecutable varias veces de forma segura.
--
-- Contraseñas (login legado): Shori2024!
--   admin@shoriexpress.local, maria@ejemplo.com, carlos@ejemplo.com, etc.
-- =============================================================================

SET NAMES utf8mb4;

USE shori_express;

-- Roles
INSERT INTO rol_rol (nombre_rol)
SELECT 'Administrador' WHERE NOT EXISTS (SELECT 1 FROM rol_rol WHERE nombre_rol = 'Administrador');
INSERT INTO rol_rol (nombre_rol)
SELECT 'Cliente' WHERE NOT EXISTS (SELECT 1 FROM rol_rol WHERE nombre_rol = 'Cliente');
INSERT INTO rol_rol (nombre_rol)
SELECT 'Empleado' WHERE NOT EXISTS (SELECT 1 FROM rol_rol WHERE nombre_rol = 'Empleado');
INSERT INTO rol_rol (nombre_rol)
SELECT 'Reparto' WHERE NOT EXISTS (SELECT 1 FROM rol_rol WHERE nombre_rol = 'Reparto');

-- Usuarios
INSERT INTO usuario_usuario (
  tipo_documento, documento, primer_nombre, apellido, correo, telefono,
  direccion, nombre_usuario, contrasena, puntos_acumulados, bonos_fidelidad,
  estado, fecha_registro, rol_id
)
SELECT 'CC', '1000000001', 'Sofía', 'Morales', 'admin@shoriexpress.local', '3001112233',
       'Calle 72 #10-34, Chapinero, Bogotá', 'admin', 'Shori2024!', 0, 0,
       'activo', '2026-01-10 09:00:00', r.id
FROM rol_rol r
WHERE r.nombre_rol = 'Administrador'
  AND NOT EXISTS (SELECT 1 FROM usuario_usuario u WHERE u.documento = '1000000001');

INSERT INTO usuario_usuario (
  tipo_documento, documento, primer_nombre, apellido, correo, telefono,
  direccion, nombre_usuario, contrasena, puntos_acumulados, bonos_fidelidad,
  estado, fecha_registro, rol_id
)
SELECT 'CC', '52345678', 'María', 'Gómez Lozano', 'maria@ejemplo.com', '3109876543',
       'Carrera 13 #64-39, Bogotá', 'mariag', 'Shori2024!', 120, 7,
       'activo', '2026-02-01 11:30:00', r.id
FROM rol_rol r
WHERE r.nombre_rol = 'Cliente'
  AND NOT EXISTS (SELECT 1 FROM usuario_usuario u WHERE u.documento = '52345678');

INSERT INTO usuario_usuario (
  tipo_documento, documento, primer_nombre, apellido, correo, telefono,
  direccion, nombre_usuario, contrasena, puntos_acumulados, bonos_fidelidad,
  estado, fecha_registro, rol_id
)
SELECT 'CC', '79876543', 'Carlos', 'Rincón Vega', 'carlos@ejemplo.com', '3205554411',
       'Avenida Ciudad de Cali #51-66, Bogotá', 'carlosr', 'Shori2024!', 45, 0,
       'activo', '2026-03-05 16:00:00', r.id
FROM rol_rol r
WHERE r.nombre_rol = 'Cliente'
  AND NOT EXISTS (SELECT 1 FROM usuario_usuario u WHERE u.documento = '79876543');

INSERT INTO usuario_usuario (
  tipo_documento, documento, primer_nombre, apellido, correo, telefono,
  direccion, nombre_usuario, contrasena, puntos_acumulados, bonos_fidelidad,
  estado, fecha_registro, rol_id
)
SELECT 'CC', '1122334455', 'Andrea', 'Benítez', 'empleado@shoriexpress.local', '3004445566',
       'Cl. 47 sur #13a-39, Local Shori', 'andrea_cocina', 'Shori2024!', 0, 0,
       'activo', '2026-01-15 08:00:00', r.id
FROM rol_rol r
WHERE r.nombre_rol = 'Empleado'
  AND NOT EXISTS (SELECT 1 FROM usuario_usuario u WHERE u.documento = '1122334455');

INSERT INTO usuario_usuario (
  tipo_documento, documento, primer_nombre, apellido, correo, telefono,
  direccion, nombre_usuario, contrasena, puntos_acumulados, bonos_fidelidad,
  estado, fecha_registro, rol_id
)
SELECT 'CC', '9012345678', 'Diego', 'Moncada', 'diego.reparto@shoriexpress.local', '3112003344',
       'Kr 24 #17-68 sur, Tunjuelito, Bogotá', 'diegoreparto', 'Shori2024!', 0, 0,
       'activo', '2026-02-20 07:00:00', r.id
FROM rol_rol r
WHERE r.nombre_rol = 'Reparto'
  AND NOT EXISTS (SELECT 1 FROM usuario_usuario u WHERE u.documento = '9012345678');

-- Métodos de pago (compatible con migración que crea Efectivo)
INSERT INTO metodo_pago_metodopago (nombre_metodo, descripcion, esta_activo)
SELECT 'Efectivo', 'Pago en efectivo (domicilio o mostrador)', 1
WHERE NOT EXISTS (SELECT 1 FROM metodo_pago_metodopago WHERE nombre_metodo = 'Efectivo');

INSERT INTO metodo_pago_metodopago (nombre_metodo, descripcion, esta_activo)
SELECT 'Nequi', 'Pago o transferencia con Nequi al número del local', 1
WHERE NOT EXISTS (SELECT 1 FROM metodo_pago_metodopago WHERE nombre_metodo = 'Nequi');

INSERT INTO metodo_pago_metodopago (nombre_metodo, descripcion, esta_activo)
SELECT 'Daviplata', 'Daviplata QR o transferencia', 1
WHERE NOT EXISTS (SELECT 1 FROM metodo_pago_metodopago WHERE nombre_metodo = 'Daviplata');

INSERT INTO metodo_pago_metodopago (nombre_metodo, descripcion, esta_activo)
SELECT 'Tarjeta débito/crédito', 'Datáfono Bancolombia en punto de venta', 1
WHERE NOT EXISTS (SELECT 1 FROM metodo_pago_metodopago WHERE nombre_metodo = 'Tarjeta débito/crédito');

INSERT INTO metodo_pago_metodopago (nombre_metodo, descripcion, esta_activo)
SELECT 'Transferencia bancaria', 'Pagos a cuentas Bancolombia / BBVA', 1
WHERE NOT EXISTS (SELECT 1 FROM metodo_pago_metodopago WHERE nombre_metodo = 'Transferencia bancaria');

-- Insumos (nombres específicos para evitar colisiones con datos ya cargados)
INSERT INTO inventario_inventario (
  nombre_insumo, categoria_insumo, unidad_medida, stock_actual, stock_minimo,
  stock_maximo, precio_compra_referencia, iva_porcentaje, estado_insumo
)
SELECT 'Chorizo artesanal res cervuno 12 mm', 'Cárnicos', 'KG', 18.50, 5.00, 40.00, 18900.00, 0.00, 'disponible'
WHERE NOT EXISTS (SELECT 1 FROM inventario_inventario WHERE nombre_insumo = 'Chorizo artesanal res cervuno 12 mm');

INSERT INTO inventario_inventario (
  nombre_insumo, categoria_insumo, unidad_medida, stock_actual, stock_minimo,
  stock_maximo, precio_compra_referencia, iva_porcentaje, estado_insumo
)
SELECT 'Pan brioche perro caliente', 'Panadería', 'UN', 120.00, 30.00, 200.00, 820.00, 0.00, 'disponible'
WHERE NOT EXISTS (SELECT 1 FROM inventario_inventario WHERE nombre_insumo = 'Pan brioche perro caliente');

INSERT INTO inventario_inventario (
  nombre_insumo, categoria_insumo, unidad_medida, stock_actual, stock_minimo,
  stock_maximo, precio_compra_referencia, iva_porcentaje, estado_insumo
)
SELECT 'Papa criolla pastusa', 'Verduras', 'KG', 25.00, 8.00, 50.00, 3600.00, 0.00, 'disponible'
WHERE NOT EXISTS (SELECT 1 FROM inventario_inventario WHERE nombre_insumo = 'Papa criolla pastusa');

INSERT INTO inventario_inventario (
  nombre_insumo, categoria_insumo, unidad_medida, stock_actual, stock_minimo,
  stock_maximo, precio_compra_referencia, iva_porcentaje, estado_insumo
)
SELECT 'Queso mozzarella rallado Ronquer', 'Lácteos', 'KG', 4.20, 1.00, 10.00, 12400.00, 0.00, 'disponible'
WHERE NOT EXISTS (SELECT 1 FROM inventario_inventario WHERE nombre_insumo = 'Queso mozzarella rallado Ronquer');

INSERT INTO inventario_inventario (
  nombre_insumo, categoria_insumo, unidad_medida, stock_actual, stock_minimo,
  stock_maximo, precio_compra_referencia, iva_porcentaje, estado_insumo
)
SELECT 'Aceite vegetal oleica 900 ml', 'Abarrotes', 'LT', 8.00, 2.00, 15.00, 9800.00, 19.00, 'disponible'
WHERE NOT EXISTS (SELECT 1 FROM inventario_inventario WHERE nombre_insumo = 'Aceite vegetal oleica 900 ml');

INSERT INTO inventario_inventario (
  nombre_insumo, categoria_insumo, unidad_medida, stock_actual, stock_minimo,
  stock_maximo, precio_compra_referencia, iva_porcentaje, estado_insumo
)
SELECT 'Cebolla cabezona roja', 'Verduras', 'KG', 12.00, 3.00, 25.00, 2900.00, 0.00, 'disponible'
WHERE NOT EXISTS (SELECT 1 FROM inventario_inventario WHERE nombre_insumo = 'Cebolla cabezona roja');

INSERT INTO inventario_inventario (
  nombre_insumo, categoria_insumo, unidad_medida, stock_actual, stock_minimo,
  stock_maximo, precio_compra_referencia, iva_porcentaje, estado_insumo
)
SELECT 'Sal refisal yodada', 'Abarrotes', 'KG', 5.00, 1.00, 12.00, 2200.00, 19.00, 'disponible'
WHERE NOT EXISTS (SELECT 1 FROM inventario_inventario WHERE nombre_insumo = 'Sal refisal yodada');

INSERT INTO inventario_inventario (
  nombre_insumo, categoria_insumo, unidad_medida, stock_actual, stock_minimo,
  stock_maximo, precio_compra_referencia, iva_porcentaje, estado_insumo
)
SELECT 'Salsa tártara lonko 250 g', 'Abarrotes', 'UN', 40.00, 10.00, 80.00, 4500.00, 19.00, 'disponible'
WHERE NOT EXISTS (SELECT 1 FROM inventario_inventario WHERE nombre_insumo = 'Salsa tártara lonko 250 g');

INSERT INTO inventario_inventario (
  nombre_insumo, categoria_insumo, unidad_medida, stock_actual, stock_minimo,
  stock_maximo, precio_compra_referencia, iva_porcentaje, estado_insumo
)
SELECT 'Arepa boyacense blanca', 'Panadería', 'UN', 200.00, 50.00, 400.00, 650.00, 0.00, 'disponible'
WHERE NOT EXISTS (SELECT 1 FROM inventario_inventario WHERE nombre_insumo = 'Arepa boyacense blanca');

INSERT INTO inventario_inventario (
  nombre_insumo, categoria_insumo, unidad_medida, stock_actual, stock_minimo,
  stock_maximo, precio_compra_referencia, iva_porcentaje, estado_insumo
)
SELECT 'Maracuyá badea malla 10 u', 'Frutas', 'UN', 15.00, 5.00, 40.00, 18500.00, 0.00, 'disponible'
WHERE NOT EXISTS (SELECT 1 FROM inventario_inventario WHERE nombre_insumo = 'Maracuyá badea malla 10 u');

INSERT INTO inventario_inventario (
  nombre_insumo, categoria_insumo, unidad_medida, stock_actual, stock_minimo,
  stock_maximo, precio_compra_referencia, iva_porcentaje, estado_insumo
)
SELECT 'Gaseosa Postobón 400 ml retornable', 'Bebidas', 'UN', 96.00, 24.00, 200.00, 1600.00, 19.00, 'disponible'
WHERE NOT EXISTS (SELECT 1 FROM inventario_inventario WHERE nombre_insumo = 'Gaseosa Postobón 400 ml retornable');

-- Productos del menú
INSERT INTO producto_producto (
  nombre_producto, descripcion_producto, imagen, precio_venta, es_combo,
  esta_disponible, registro_movimiento_inicial
)
SELECT 'Perro chorizo clásico',
       'Chorizo a la plancha en pan brioche, salsas lácteas, papa en cascos y toque de cebolla caramelizada.',
       NULL, 15900.00, 0, 1,
       'Lote SE-2026-001 chorizo Morlin / Pan La Especial'
WHERE NOT EXISTS (SELECT 1 FROM producto_producto WHERE nombre_producto = 'Perro chorizo clásico');

INSERT INTO producto_producto (
  nombre_producto, descripcion_producto, imagen, precio_venta, es_combo,
  esta_disponible, registro_movimiento_inicial
)
SELECT 'Chorizo a la plancha (250 g)',
       'Porción generosa con chimichurri, arepa boyacense o media papa a la francesa (elige en notas).',
       NULL, 19500.00, 0, 1, NULL
WHERE NOT EXISTS (SELECT 1 FROM producto_producto WHERE nombre_producto = 'Chorizo a la plancha (250 g)');

INSERT INTO producto_producto (
  nombre_producto, descripcion_producto, imagen, precio_venta, es_combo,
  esta_disponible, registro_movimiento_inicial
)
SELECT 'Combo familiar 4 personas',
       'Cuatro perros clásicos, papa medianera para compartir y cuatro gaseosas 400 ml.',
       NULL, 68900.00, 1, 1, NULL
WHERE NOT EXISTS (SELECT 1 FROM producto_producto WHERE nombre_producto = 'Combo familiar 4 personas');

INSERT INTO producto_producto (
  nombre_producto, descripcion_producto, imagen, precio_venta, es_combo,
  esta_disponible, registro_movimiento_inicial
)
SELECT 'Papa chorizo gratinada',
       'Papa criolla cocida con trozos de chorizo, queso mozzarella gratinado y perejil.',
       NULL, 13200.00, 0, 1, NULL
WHERE NOT EXISTS (SELECT 1 FROM producto_producto WHERE nombre_producto = 'Papa chorizo gratinada');

INSERT INTO producto_producto (
  nombre_producto, descripcion_producto, imagen, precio_venta, es_combo,
  esta_disponible, registro_movimiento_inicial
)
SELECT 'Gaseosa personal 400 ml',
       'Gaseosa fría (marca según disponibilidad en nevera).',
       NULL, 3800.00, 0, 1, NULL
WHERE NOT EXISTS (SELECT 1 FROM producto_producto WHERE nombre_producto = 'Gaseosa personal 400 ml');

INSERT INTO producto_producto (
  nombre_producto, descripcion_producto, imagen, precio_venta, es_combo,
  esta_disponible, registro_movimiento_inicial
)
SELECT 'Arepa con chorizo antioqueño',
       'Arepa blanca asada con medio chorizo desmechado y hogao casero.',
       NULL, 9800.00, 0, 1, NULL
WHERE NOT EXISTS (SELECT 1 FROM producto_producto WHERE nombre_producto = 'Arepa con chorizo antioqueño');

INSERT INTO producto_producto (
  nombre_producto, descripcion_producto, imagen, precio_venta, es_combo,
  esta_disponible, registro_movimiento_inicial
)
SELECT 'Jugo natural maracuyá',
       'Jugo en agua o en leche 400 ml, pulpa fresca.',
       NULL, 6500.00, 0, 1, NULL
WHERE NOT EXISTS (SELECT 1 FROM producto_producto WHERE nombre_producto = 'Jugo natural maracuyá');

-- Lotes (único por insumo + codigo_lote)
INSERT INTO inventario_inventariolote (codigo_lote, cantidad, fecha_registro, fecha_vencimiento, insumo_id)
SELECT 'SE-2026-001', 10.00, '2026-01-08 10:00:00', '2026-07-01', i.id
FROM inventario_inventario i
WHERE i.nombre_insumo = 'Chorizo artesanal res cervuno 12 mm'
  AND NOT EXISTS (
    SELECT 1 FROM inventario_inventariolote l
    WHERE l.insumo_id = i.id AND l.codigo_lote = 'SE-2026-001'
  );

INSERT INTO inventario_inventariolote (codigo_lote, cantidad, fecha_registro, fecha_vencimiento, insumo_id)
SELECT 'PAN-BRIO-ENE26', 80.00, '2026-01-09 08:00:00', '2026-02-20', i.id
FROM inventario_inventario i
WHERE i.nombre_insumo = 'Pan brioche perro caliente'
  AND NOT EXISTS (
    SELECT 1 FROM inventario_inventariolote l
    WHERE l.insumo_id = i.id AND l.codigo_lote = 'PAN-BRIO-ENE26'
  );

INSERT INTO inventario_inventariolote (codigo_lote, cantidad, fecha_registro, fecha_vencimiento, insumo_id)
SELECT 'PAP-PST-004', 20.00, '2026-01-10 07:30:00', '2026-04-25', i.id
FROM inventario_inventario i
WHERE i.nombre_insumo = 'Papa criolla pastusa'
  AND NOT EXISTS (
    SELECT 1 FROM inventario_inventariolote l
    WHERE l.insumo_id = i.id AND l.codigo_lote = 'PAP-PST-004'
  );

INSERT INTO inventario_inventariolote (codigo_lote, cantidad, fecha_registro, fecha_vencimiento, insumo_id)
SELECT 'GAS-PTB-ENE', 48.00, '2026-01-11 12:00:00', '2026-12-01', i.id
FROM inventario_inventario i
WHERE i.nombre_insumo = 'Gaseosa Postobón 400 ml retornable'
  AND NOT EXISTS (
    SELECT 1 FROM inventario_inventariolote l
    WHERE l.insumo_id = i.id AND l.codigo_lote = 'GAS-PTB-ENE'
  );

-- Recetas (único producto + insumo)
INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.12, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Perro chorizo clásico'
WHERE i.nombre_insumo = 'Chorizo artesanal res cervuno 12 mm'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 1.00, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Perro chorizo clásico'
WHERE i.nombre_insumo = 'Pan brioche perro caliente'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.08, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Perro chorizo clásico'
WHERE i.nombre_insumo = 'Papa criolla pastusa'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.02, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Perro chorizo clásico'
WHERE i.nombre_insumo = 'Cebolla cabezona roja'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.04, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Perro chorizo clásico'
WHERE i.nombre_insumo = 'Salsa tártara lonko 250 g'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.25, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Chorizo a la plancha (250 g)'
WHERE i.nombre_insumo = 'Chorizo artesanal res cervuno 12 mm'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.08, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Chorizo a la plancha (250 g)'
WHERE i.nombre_insumo = 'Cebolla cabezona roja'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 1.00, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Chorizo a la plancha (250 g)'
WHERE i.nombre_insumo = 'Arepa boyacense blanca'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.30, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Papa chorizo gratinada'
WHERE i.nombre_insumo = 'Papa criolla pastusa'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.10, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Papa chorizo gratinada'
WHERE i.nombre_insumo = 'Chorizo artesanal res cervuno 12 mm'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.06, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Papa chorizo gratinada'
WHERE i.nombre_insumo = 'Queso mozzarella rallado Ronquer'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.45, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Arepa con chorizo antioqueño'
WHERE i.nombre_insumo = 'Chorizo artesanal res cervuno 12 mm'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 1.00, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Arepa con chorizo antioqueño'
WHERE i.nombre_insumo = 'Arepa boyacense blanca'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.08, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Combo familiar 4 personas'
WHERE i.nombre_insumo = 'Chorizo artesanal res cervuno 12 mm'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 4.00, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Combo familiar 4 personas'
WHERE i.nombre_insumo = 'Pan brioche perro caliente'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.60, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Combo familiar 4 personas'
WHERE i.nombre_insumo = 'Papa criolla pastusa'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 4.00, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Combo familiar 4 personas'
WHERE i.nombre_insumo = 'Gaseosa Postobón 400 ml retornable'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 0.35, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Jugo natural maracuyá'
WHERE i.nombre_insumo = 'Maracuyá badea malla 10 u'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

INSERT INTO receta_receta (cantidad_requerida, insumo_id, producto_id)
SELECT 1.00, i.id, p.id
FROM inventario_inventario i
JOIN producto_producto p ON p.nombre_producto = 'Gaseosa personal 400 ml'
WHERE i.nombre_insumo = 'Gaseosa Postobón 400 ml retornable'
  AND NOT EXISTS (SELECT 1 FROM receta_receta r WHERE r.producto_id = p.id AND r.insumo_id = i.id);

-- Pedidos (identificados por fecha_pedido + documento cliente + total)
INSERT INTO pedido_pedido (
  fecha_pedido, tipo_pedido, direccion_pedido, estado_pedido, total_pedido,
  usuario_id, fecha_entrega_estimada, fecha_entrega_real
)
SELECT '2026-04-01 12:15:00', 'domicilio', 'Carrera 13 #64-39, Bogotá', 'entregado', 35300.00,
       u.id, '2026-04-01 13:00:00', '2026-04-01 13:08:00'
FROM usuario_usuario u
WHERE u.documento = '52345678'
  AND NOT EXISTS (
    SELECT 1 FROM pedido_pedido p
    WHERE p.usuario_id = u.id AND p.fecha_pedido = '2026-04-01 12:15:00' AND p.total_pedido = 35300.00
  );

INSERT INTO pedido_pedido (
  fecha_pedido, tipo_pedido, direccion_pedido, estado_pedido, total_pedido,
  usuario_id, fecha_entrega_estimada, fecha_entrega_real
)
SELECT '2026-04-03 18:40:00', 'llevar', NULL, 'preparacion', 19500.00,
       u.id, '2026-04-03 19:25:00', NULL
FROM usuario_usuario u
WHERE u.documento = '79876543'
  AND NOT EXISTS (
    SELECT 1 FROM pedido_pedido p
    WHERE p.usuario_id = u.id AND p.fecha_pedido = '2026-04-03 18:40:00' AND p.total_pedido = 19500.00
  );

INSERT INTO pedido_pedido (
  fecha_pedido, tipo_pedido, direccion_pedido, estado_pedido, total_pedido,
  usuario_id, fecha_entrega_estimada, fecha_entrega_real
)
SELECT '2026-04-08 13:00:00', 'local', NULL, 'listo', 68900.00,
       u.id, '2026-04-08 13:45:00', NULL
FROM usuario_usuario u
WHERE u.documento = '52345678'
  AND NOT EXISTS (
    SELECT 1 FROM pedido_pedido p
    WHERE p.usuario_id = u.id AND p.fecha_pedido = '2026-04-08 13:00:00' AND p.total_pedido = 68900.00
  );

INSERT INTO pedido_pedido (
  fecha_pedido, tipo_pedido, direccion_pedido, estado_pedido, total_pedido,
  usuario_id, fecha_entrega_estimada, fecha_entrega_real
)
SELECT '2026-04-09 10:05:00', 'domicilio', 'Avenida Ciudad de Cali #51-66, Bogotá', 'pendiente', 13200.00,
       u.id, NULL, NULL
FROM usuario_usuario u
WHERE u.documento = '79876543'
  AND NOT EXISTS (
    SELECT 1 FROM pedido_pedido p
    WHERE p.usuario_id = u.id AND p.fecha_pedido = '2026-04-09 10:05:00' AND p.total_pedido = 13200.00
  );

INSERT INTO pedido_pedido (
  fecha_pedido, tipo_pedido, direccion_pedido, estado_pedido, total_pedido,
  usuario_id, fecha_entrega_estimada, fecha_entrega_real
)
SELECT '2026-04-07 14:20:00', 'local', NULL, 'entregado', 32200.00,
       u.id, '2026-04-07 14:55:00', '2026-04-07 15:02:00'
FROM usuario_usuario u
WHERE u.documento = '52345678'
  AND NOT EXISTS (
    SELECT 1 FROM pedido_pedido p
    WHERE p.usuario_id = u.id AND p.fecha_pedido = '2026-04-07 14:20:00' AND p.total_pedido = 32200.00
  );

INSERT INTO pedido_pedido (
  fecha_pedido, tipo_pedido, direccion_pedido, estado_pedido, total_pedido,
  usuario_id, fecha_entrega_estimada, fecha_entrega_real
)
SELECT '2026-04-09 19:30:00', 'domicilio', 'Kr 24 #17-68 sur, Tunjuelito', 'cancelado', 15900.00,
       u.id, '2026-04-09 20:00:00', NULL
FROM usuario_usuario u
WHERE u.documento = '9012345678'
  AND NOT EXISTS (
    SELECT 1 FROM pedido_pedido p
    WHERE p.usuario_id = u.id AND p.fecha_pedido = '2026-04-09 19:30:00' AND p.total_pedido = 15900.00
  );

-- Detalle de pedidos (anti-duplicado por pedido + producto + cantidad + precio)
INSERT INTO detalle_pedido_detallepedido (cantidad, precio_unitario_momento, notas_especiales, pedido_id, producto_id)
SELECT 2, 15900.00, 'Uno sin cebolla, extra tártara', pe.id, pr.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '52345678'
JOIN producto_producto pr ON pr.nombre_producto = 'Perro chorizo clásico'
WHERE pe.fecha_pedido = '2026-04-01 12:15:00' AND pe.total_pedido = 35300.00
  AND NOT EXISTS (
    SELECT 1 FROM detalle_pedido_detallepedido d
    WHERE d.pedido_id = pe.id AND d.producto_id = pr.id AND d.cantidad = 2 AND d.precio_unitario_momento = 15900.00
  );

INSERT INTO detalle_pedido_detallepedido (cantidad, precio_unitario_momento, notas_especiales, pedido_id, producto_id)
SELECT 1, 3500.00, 'Precio promo happy hour', pe.id, pr.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '52345678'
JOIN producto_producto pr ON pr.nombre_producto = 'Gaseosa personal 400 ml'
WHERE pe.fecha_pedido = '2026-04-01 12:15:00' AND pe.total_pedido = 35300.00
  AND NOT EXISTS (
    SELECT 1 FROM detalle_pedido_detallepedido d
    WHERE d.pedido_id = pe.id AND d.producto_id = pr.id AND d.cantidad = 1 AND d.precio_unitario_momento = 3500.00
  );

INSERT INTO detalle_pedido_detallepedido (cantidad, precio_unitario_momento, notas_especiales, pedido_id, producto_id)
SELECT 1, 19500.00, 'Corte al punto, poca grasa', pe.id, pr.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '79876543'
JOIN producto_producto pr ON pr.nombre_producto = 'Chorizo a la plancha (250 g)'
WHERE pe.fecha_pedido = '2026-04-03 18:40:00' AND pe.total_pedido = 19500.00
  AND NOT EXISTS (
    SELECT 1 FROM detalle_pedido_detallepedido d
    WHERE d.pedido_id = pe.id AND d.producto_id = pr.id AND d.cantidad = 1 AND d.precio_unitario_momento = 19500.00
  );

INSERT INTO detalle_pedido_detallepedido (cantidad, precio_unitario_momento, notas_especiales, pedido_id, producto_id)
SELECT 1, 68900.00, 'Llevar bolsas recicladas', pe.id, pr.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '52345678'
JOIN producto_producto pr ON pr.nombre_producto = 'Combo familiar 4 personas'
WHERE pe.fecha_pedido = '2026-04-08 13:00:00' AND pe.total_pedido = 68900.00
  AND NOT EXISTS (
    SELECT 1 FROM detalle_pedido_detallepedido d
    WHERE d.pedido_id = pe.id AND d.producto_id = pr.id AND d.cantidad = 1 AND d.precio_unitario_momento = 68900.00
  );

INSERT INTO detalle_pedido_detallepedido (cantidad, precio_unitario_momento, notas_especiales, pedido_id, producto_id)
SELECT 1, 13200.00, NULL, pe.id, pr.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '79876543'
JOIN producto_producto pr ON pr.nombre_producto = 'Papa chorizo gratinada'
WHERE pe.fecha_pedido = '2026-04-09 10:05:00' AND pe.total_pedido = 13200.00
  AND NOT EXISTS (
    SELECT 1 FROM detalle_pedido_detallepedido d
    WHERE d.pedido_id = pe.id AND d.producto_id = pr.id AND d.cantidad = 1 AND d.precio_unitario_momento = 13200.00
  );

INSERT INTO detalle_pedido_detallepedido (cantidad, precio_unitario_momento, notas_especiales, pedido_id, producto_id)
SELECT 1, 15900.00, 'Servilletas extra', pe.id, pr.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '52345678'
JOIN producto_producto pr ON pr.nombre_producto = 'Perro chorizo clásico'
WHERE pe.fecha_pedido = '2026-04-07 14:20:00' AND pe.total_pedido = 32200.00
  AND NOT EXISTS (
    SELECT 1 FROM detalle_pedido_detallepedido d
    WHERE d.pedido_id = pe.id AND d.producto_id = pr.id AND d.cantidad = 1 AND d.precio_unitario_momento = 15900.00
  );

INSERT INTO detalle_pedido_detallepedido (cantidad, precio_unitario_momento, notas_especiales, pedido_id, producto_id)
SELECT 1, 6500.00, 'En agua, poco azúcar', pe.id, pr.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '52345678'
JOIN producto_producto pr ON pr.nombre_producto = 'Jugo natural maracuyá'
WHERE pe.fecha_pedido = '2026-04-07 14:20:00' AND pe.total_pedido = 32200.00
  AND NOT EXISTS (
    SELECT 1 FROM detalle_pedido_detallepedido d
    WHERE d.pedido_id = pe.id AND d.producto_id = pr.id AND d.cantidad = 1 AND d.precio_unitario_momento = 6500.00
  );

INSERT INTO detalle_pedido_detallepedido (cantidad, precio_unitario_momento, notas_especiales, pedido_id, producto_id)
SELECT 1, 9800.00, 'Hogao aparte', pe.id, pr.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '52345678'
JOIN producto_producto pr ON pr.nombre_producto = 'Arepa con chorizo antioqueño'
WHERE pe.fecha_pedido = '2026-04-07 14:20:00' AND pe.total_pedido = 32200.00
  AND NOT EXISTS (
    SELECT 1 FROM detalle_pedido_detallepedido d
    WHERE d.pedido_id = pe.id AND d.producto_id = pr.id AND d.cantidad = 1 AND d.precio_unitario_momento = 9800.00
  );

INSERT INTO detalle_pedido_detallepedido (cantidad, precio_unitario_momento, notas_especiales, pedido_id, producto_id)
SELECT 1, 15900.00, 'Cliente canceló por demora', pe.id, pr.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '9012345678'
JOIN producto_producto pr ON pr.nombre_producto = 'Perro chorizo clásico'
WHERE pe.fecha_pedido = '2026-04-09 19:30:00' AND pe.total_pedido = 15900.00
  AND NOT EXISTS (
    SELECT 1 FROM detalle_pedido_detallepedido d
    WHERE d.pedido_id = pe.id AND d.producto_id = pr.id AND d.cantidad = 1 AND d.precio_unitario_momento = 15900.00
  );

-- Movimientos de inventario (idempotente por insumo + tipo + fecha + observación)
INSERT INTO movimiento_inventario_movimientoinventario (
  lote, tipo_movimiento, cantidad, fecha_movimiento, fecha_vencimiento,
  observaciones, insumo_id, usuario_id
)
SELECT 'SE-2026-001', 'entrada_inicial', 25.00, '2026-01-08 10:00:00', '2026-07-01',
       'Recepción proveedor Cárnicos Morlin — remisión R-4481', i.id, u.id
FROM inventario_inventario i
JOIN usuario_usuario u ON u.documento = '1000000001'
WHERE i.nombre_insumo = 'Chorizo artesanal res cervuno 12 mm'
  AND NOT EXISTS (
    SELECT 1 FROM movimiento_inventario_movimientoinventario m
    WHERE m.insumo_id = i.id AND m.tipo_movimiento = 'entrada_inicial'
      AND m.fecha_movimiento = '2026-01-08 10:00:00'
      AND m.observaciones LIKE '%Morlin%'
  );

INSERT INTO movimiento_inventario_movimientoinventario (
  lote, tipo_movimiento, cantidad, fecha_movimiento, fecha_vencimiento,
  observaciones, insumo_id, usuario_id
)
SELECT 'PAN-BRIO-ENE26', 'entrada_inicial', 100.00, '2026-01-09 08:00:00', NULL,
       'Compra Panadería La Especial — factura POS-9921', i.id, u.id
FROM inventario_inventario i
JOIN usuario_usuario u ON u.documento = '1000000001'
WHERE i.nombre_insumo = 'Pan brioche perro caliente'
  AND NOT EXISTS (
    SELECT 1 FROM movimiento_inventario_movimientoinventario m
    WHERE m.insumo_id = i.id AND m.tipo_movimiento = 'entrada_inicial'
      AND m.fecha_movimiento = '2026-01-09 08:00:00'
      AND m.observaciones LIKE '%Especial%'
  );

INSERT INTO movimiento_inventario_movimientoinventario (
  lote, tipo_movimiento, cantidad, fecha_movimiento, fecha_vencimiento,
  observaciones, insumo_id, usuario_id
)
SELECT NULL, 'entrada', 50.00, '2026-02-14 09:15:00', NULL,
       'Compra mayorista Plaza de Mercado Corabastos — papa criolla', i.id, u.id
FROM inventario_inventario i
JOIN usuario_usuario u ON u.documento = '1122334455'
WHERE i.nombre_insumo = 'Papa criolla pastusa'
  AND NOT EXISTS (
    SELECT 1 FROM movimiento_inventario_movimientoinventario m
    WHERE m.insumo_id = i.id AND m.tipo_movimiento = 'entrada'
      AND m.fecha_movimiento = '2026-02-14 09:15:00'
      AND m.observaciones LIKE '%Corabastos%'
  );

INSERT INTO movimiento_inventario_movimientoinventario (
  lote, tipo_movimiento, cantidad, fecha_movimiento, fecha_vencimiento,
  observaciones, insumo_id, usuario_id
)
SELECT NULL, 'salida_desperdicio', 0.80, '2026-03-18 11:00:00', NULL,
       'Merma por corte en cámara — chorizo', i.id, u.id
FROM inventario_inventario i
JOIN usuario_usuario u ON u.documento = '1122334455'
WHERE i.nombre_insumo = 'Chorizo artesanal res cervuno 12 mm'
  AND NOT EXISTS (
    SELECT 1 FROM movimiento_inventario_movimientoinventario m
    WHERE m.insumo_id = i.id AND m.tipo_movimiento = 'salida_desperdicio'
      AND m.fecha_movimiento = '2026-03-18 11:00:00'
      AND m.observaciones LIKE '%Merma%'
  );

INSERT INTO movimiento_inventario_movimientoinventario (
  lote, tipo_movimiento, cantidad, fecha_movimiento, fecha_vencimiento,
  observaciones, insumo_id, usuario_id
)
SELECT NULL, 'salida_venta', 0.24, '2026-04-01 12:20:00', NULL,
       'Descarte receta — Pedido domicilio Gómez 2026-04-01 (2 perros clásicos)', i.id, u.id
FROM inventario_inventario i
JOIN usuario_usuario u ON u.documento = '1122334455'
WHERE i.nombre_insumo = 'Chorizo artesanal res cervuno 12 mm'
  AND NOT EXISTS (
    SELECT 1 FROM movimiento_inventario_movimientoinventario m
    WHERE m.insumo_id = i.id AND m.tipo_movimiento = 'salida_venta'
      AND m.fecha_movimiento = '2026-04-01 12:20:00'
      AND m.observaciones LIKE '%Gómez 2026-04-01%'
  );

INSERT INTO movimiento_inventario_movimientoinventario (
  lote, tipo_movimiento, cantidad, fecha_movimiento, fecha_vencimiento,
  observaciones, insumo_id, usuario_id
)
SELECT NULL, 'salida_venta', 2.00, '2026-04-01 12:21:00', NULL,
       'Descarte receta — pan brioche mismo pedido', i.id, u.id
FROM inventario_inventario i
JOIN usuario_usuario u ON u.documento = '1122334455'
WHERE i.nombre_insumo = 'Pan brioche perro caliente'
  AND NOT EXISTS (
    SELECT 1 FROM movimiento_inventario_movimientoinventario m
    WHERE m.insumo_id = i.id AND m.tipo_movimiento = 'salida_venta'
      AND m.fecha_movimiento = '2026-04-01 12:21:00'
      AND m.observaciones LIKE '%mismo pedido%'
  );

INSERT INTO movimiento_inventario_movimientoinventario (
  lote, tipo_movimiento, cantidad, fecha_movimiento, fecha_vencimiento,
  observaciones, insumo_id, usuario_id
)
SELECT NULL, 'ajuste', 1.50, '2026-03-31 18:00:00', NULL,
       'Ajuste inventario físico mensual — aceite (diferencia conteo)', i.id, u.id
FROM inventario_inventario i
JOIN usuario_usuario u ON u.documento = '1000000001'
WHERE i.nombre_insumo = 'Aceite vegetal oleica 900 ml'
  AND NOT EXISTS (
    SELECT 1 FROM movimiento_inventario_movimientoinventario m
    WHERE m.insumo_id = i.id AND m.tipo_movimiento = 'ajuste'
      AND m.fecha_movimiento = '2026-03-31 18:00:00'
      AND m.observaciones LIKE '%aceite%'
  );

-- Recibos (pedidos pagados; sin recibo si pendiente o cancelado)
INSERT INTO recibo_recibo (
  fecha_emision, subtotal, iva_total, total_pagado, puntos_ganados, metodo_pago_id, pedido_id
)
SELECT '2026-04-01 12:16:00', 29663.87, 5636.13, 35300.00, 35, m.id, pe.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '52345678'
JOIN metodo_pago_metodopago m ON m.nombre_metodo = 'Efectivo'
WHERE pe.fecha_pedido = '2026-04-01 12:15:00' AND pe.total_pedido = 35300.00
  AND NOT EXISTS (SELECT 1 FROM recibo_recibo r WHERE r.pedido_id = pe.id);

INSERT INTO recibo_recibo (
  fecha_emision, subtotal, iva_total, total_pagado, puntos_ganados, metodo_pago_id, pedido_id
)
SELECT '2026-04-03 18:41:00', 16387.39, 3112.61, 19500.00, 19, m.id, pe.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '79876543'
JOIN metodo_pago_metodopago m ON m.nombre_metodo = 'Nequi'
WHERE pe.fecha_pedido = '2026-04-03 18:40:00' AND pe.total_pedido = 19500.00
  AND NOT EXISTS (SELECT 1 FROM recibo_recibo r WHERE r.pedido_id = pe.id);

INSERT INTO recibo_recibo (
  fecha_emision, subtotal, iva_total, total_pagado, puntos_ganados, metodo_pago_id, pedido_id
)
SELECT '2026-04-08 13:01:00', 57899.16, 11000.84, 68900.00, 68, m.id, pe.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '52345678'
JOIN metodo_pago_metodopago m ON m.nombre_metodo = 'Efectivo'
WHERE pe.fecha_pedido = '2026-04-08 13:00:00' AND pe.total_pedido = 68900.00
  AND NOT EXISTS (SELECT 1 FROM recibo_recibo r WHERE r.pedido_id = pe.id);

INSERT INTO recibo_recibo (
  fecha_emision, subtotal, iva_total, total_pagado, puntos_ganados, metodo_pago_id, pedido_id
)
SELECT '2026-04-07 14:21:00', 27058.82, 5141.18, 32200.00, 32, m.id, pe.id
FROM pedido_pedido pe
JOIN usuario_usuario u ON pe.usuario_id = u.id AND u.documento = '52345678'
JOIN metodo_pago_metodopago m ON m.nombre_metodo = 'Tarjeta débito/crédito'
WHERE pe.fecha_pedido = '2026-04-07 14:20:00' AND pe.total_pedido = 32200.00
  AND NOT EXISTS (SELECT 1 FROM recibo_recibo r WHERE r.pedido_id = pe.id);
