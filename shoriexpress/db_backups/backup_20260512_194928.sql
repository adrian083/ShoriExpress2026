-- Resaldo de base de datos: shori_express
-- Fecha: 2026-05-12 19:49:28
-- Creado con Python puro (alternativa a mysqldump)

-- Estructura de tabla: auth_group
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Fin de tabla

-- Estructura de tabla: auth_group_permissions
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Fin de tabla

-- Estructura de tabla: auth_permission
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: auth_permission
INSERT INTO `auth_permission` VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO `auth_permission` VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO `auth_permission` VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO `auth_permission` VALUES (4, 'Can view log entry', 1, 'view_logentry');
INSERT INTO `auth_permission` VALUES (5, 'Can add permission', 2, 'add_permission');
INSERT INTO `auth_permission` VALUES (6, 'Can change permission', 2, 'change_permission');
INSERT INTO `auth_permission` VALUES (7, 'Can delete permission', 2, 'delete_permission');
INSERT INTO `auth_permission` VALUES (8, 'Can view permission', 2, 'view_permission');
INSERT INTO `auth_permission` VALUES (9, 'Can add group', 3, 'add_group');
INSERT INTO `auth_permission` VALUES (10, 'Can change group', 3, 'change_group');
INSERT INTO `auth_permission` VALUES (11, 'Can delete group', 3, 'delete_group');
INSERT INTO `auth_permission` VALUES (12, 'Can view group', 3, 'view_group');
INSERT INTO `auth_permission` VALUES (13, 'Can add user', 4, 'add_user');
INSERT INTO `auth_permission` VALUES (14, 'Can change user', 4, 'change_user');
INSERT INTO `auth_permission` VALUES (15, 'Can delete user', 4, 'delete_user');
INSERT INTO `auth_permission` VALUES (16, 'Can view user', 4, 'view_user');
INSERT INTO `auth_permission` VALUES (17, 'Can add content type', 5, 'add_contenttype');
INSERT INTO `auth_permission` VALUES (18, 'Can change content type', 5, 'change_contenttype');
INSERT INTO `auth_permission` VALUES (19, 'Can delete content type', 5, 'delete_contenttype');
INSERT INTO `auth_permission` VALUES (20, 'Can view content type', 5, 'view_contenttype');
INSERT INTO `auth_permission` VALUES (21, 'Can add session', 6, 'add_session');
INSERT INTO `auth_permission` VALUES (22, 'Can change session', 6, 'change_session');
INSERT INTO `auth_permission` VALUES (23, 'Can delete session', 6, 'delete_session');
INSERT INTO `auth_permission` VALUES (24, 'Can view session', 6, 'view_session');
INSERT INTO `auth_permission` VALUES (25, 'Can add Rol', 7, 'add_rol');
INSERT INTO `auth_permission` VALUES (26, 'Can change Rol', 7, 'change_rol');
INSERT INTO `auth_permission` VALUES (27, 'Can delete Rol', 7, 'delete_rol');
INSERT INTO `auth_permission` VALUES (28, 'Can view Rol', 7, 'view_rol');
INSERT INTO `auth_permission` VALUES (29, 'Can add Usuario', 8, 'add_usuario');
INSERT INTO `auth_permission` VALUES (30, 'Can change Usuario', 8, 'change_usuario');
INSERT INTO `auth_permission` VALUES (31, 'Can delete Usuario', 8, 'delete_usuario');
INSERT INTO `auth_permission` VALUES (32, 'Can view Usuario', 8, 'view_usuario');
INSERT INTO `auth_permission` VALUES (33, 'Can add Insumo de Inventario', 9, 'add_inventario');
INSERT INTO `auth_permission` VALUES (34, 'Can change Insumo de Inventario', 9, 'change_inventario');
INSERT INTO `auth_permission` VALUES (35, 'Can delete Insumo de Inventario', 9, 'delete_inventario');
INSERT INTO `auth_permission` VALUES (36, 'Can view Insumo de Inventario', 9, 'view_inventario');
INSERT INTO `auth_permission` VALUES (37, 'Can add Lote de inventario', 10, 'add_inventariolote');
INSERT INTO `auth_permission` VALUES (38, 'Can change Lote de inventario', 10, 'change_inventariolote');
INSERT INTO `auth_permission` VALUES (39, 'Can delete Lote de inventario', 10, 'delete_inventariolote');
INSERT INTO `auth_permission` VALUES (40, 'Can view Lote de inventario', 10, 'view_inventariolote');
INSERT INTO `auth_permission` VALUES (41, 'Can add Producto', 11, 'add_producto');
INSERT INTO `auth_permission` VALUES (42, 'Can change Producto', 11, 'change_producto');
INSERT INTO `auth_permission` VALUES (43, 'Can delete Producto', 11, 'delete_producto');
INSERT INTO `auth_permission` VALUES (44, 'Can view Producto', 11, 'view_producto');
INSERT INTO `auth_permission` VALUES (45, 'Can add Receta / Escandallo', 12, 'add_receta');
INSERT INTO `auth_permission` VALUES (46, 'Can change Receta / Escandallo', 12, 'change_receta');
INSERT INTO `auth_permission` VALUES (47, 'Can delete Receta / Escandallo', 12, 'delete_receta');
INSERT INTO `auth_permission` VALUES (48, 'Can view Receta / Escandallo', 12, 'view_receta');
INSERT INTO `auth_permission` VALUES (49, 'Can add Movimiento de Inventario', 13, 'add_movimientoinventario');
INSERT INTO `auth_permission` VALUES (50, 'Can change Movimiento de Inventario', 13, 'change_movimientoinventario');
INSERT INTO `auth_permission` VALUES (51, 'Can delete Movimiento de Inventario', 13, 'delete_movimientoinventario');
INSERT INTO `auth_permission` VALUES (52, 'Can view Movimiento de Inventario', 13, 'view_movimientoinventario');
INSERT INTO `auth_permission` VALUES (53, 'Can add Pedido', 14, 'add_pedido');
INSERT INTO `auth_permission` VALUES (54, 'Can change Pedido', 14, 'change_pedido');
INSERT INTO `auth_permission` VALUES (55, 'Can delete Pedido', 14, 'delete_pedido');
INSERT INTO `auth_permission` VALUES (56, 'Can view Pedido', 14, 'view_pedido');
INSERT INTO `auth_permission` VALUES (57, 'Can add Detalle del Pedido', 15, 'add_detallepedido');
INSERT INTO `auth_permission` VALUES (58, 'Can change Detalle del Pedido', 15, 'change_detallepedido');
INSERT INTO `auth_permission` VALUES (59, 'Can delete Detalle del Pedido', 15, 'delete_detallepedido');
INSERT INTO `auth_permission` VALUES (60, 'Can view Detalle del Pedido', 15, 'view_detallepedido');
INSERT INTO `auth_permission` VALUES (61, 'Can add Método de Pago', 16, 'add_metodopago');
INSERT INTO `auth_permission` VALUES (62, 'Can change Método de Pago', 16, 'change_metodopago');
INSERT INTO `auth_permission` VALUES (63, 'Can delete Método de Pago', 16, 'delete_metodopago');
INSERT INTO `auth_permission` VALUES (64, 'Can view Método de Pago', 16, 'view_metodopago');
INSERT INTO `auth_permission` VALUES (65, 'Can add Recibo / Factura', 17, 'add_recibo');
INSERT INTO `auth_permission` VALUES (66, 'Can change Recibo / Factura', 17, 'change_recibo');
INSERT INTO `auth_permission` VALUES (67, 'Can delete Recibo / Factura', 17, 'delete_recibo');
INSERT INTO `auth_permission` VALUES (68, 'Can view Recibo / Factura', 17, 'view_recibo');
INSERT INTO `auth_permission` VALUES (69, 'Can add Configuración del Sistema', 18, 'add_configuracionsistema');
INSERT INTO `auth_permission` VALUES (70, 'Can change Configuración del Sistema', 18, 'change_configuracionsistema');
INSERT INTO `auth_permission` VALUES (71, 'Can delete Configuración del Sistema', 18, 'delete_configuracionsistema');
INSERT INTO `auth_permission` VALUES (72, 'Can view Configuración del Sistema', 18, 'view_configuracionsistema');

-- Fin de tabla

-- Estructura de tabla: auth_user
DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Fin de tabla

-- Estructura de tabla: auth_user_groups
DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Fin de tabla

-- Estructura de tabla: auth_user_user_permissions
DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Fin de tabla

-- Estructura de tabla: dashboard_configuracion
DROP TABLE IF EXISTS `dashboard_configuracion`;
CREATE TABLE `dashboard_configuracion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre_sistema` varchar(100) NOT NULL,
  `hora_apertura` time(6) NOT NULL,
  `hora_cierre` time(6) NOT NULL,
  `porcentaje_iva` decimal(5,2) NOT NULL,
  `umbral_bonos` decimal(10,2) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: dashboard_configuracion
INSERT INTO `dashboard_configuracion` VALUES (1, 'ShoriExpress', '8:00:00', '19:00:00', '19.00', '50000.00', '2026-04-24 02:48:35.763315', '2026-04-24 02:48:35.763328');

-- Fin de tabla

-- Estructura de tabla: detalle_pedido_detallepedido
DROP TABLE IF EXISTS `detalle_pedido_detallepedido`;
CREATE TABLE `detalle_pedido_detallepedido` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `cantidad` int unsigned NOT NULL,
  `precio_unitario_momento` decimal(10,2) NOT NULL,
  `notas_especiales` varchar(255) DEFAULT NULL,
  `pedido_id` bigint NOT NULL,
  `producto_id` bigint NOT NULL,
  `stock_remanente_post_venta` int unsigned DEFAULT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `detalle_pedido_detal_pedido_id_11ca3e13_fk_pedido_pe` (`pedido_id`),
  KEY `detalle_pedido_detal_producto_id_331558e8_fk_producto_` (`producto_id`),
  CONSTRAINT `detalle_pedido_detal_pedido_id_11ca3e13_fk_pedido_pe` FOREIGN KEY (`pedido_id`) REFERENCES `pedido_pedido` (`id`),
  CONSTRAINT `detalle_pedido_detal_producto_id_331558e8_fk_producto_` FOREIGN KEY (`producto_id`) REFERENCES `producto_producto` (`id`),
  CONSTRAINT `detalle_pedido_detallepedido_chk_1` CHECK ((`cantidad` >= 0)),
  CONSTRAINT `detalle_pedido_detallepedido_chk_2` CHECK ((`stock_remanente_post_venta` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: detalle_pedido_detallepedido
INSERT INTO `detalle_pedido_detallepedido` VALUES (1, 2, '15900.00', 'Uno sin cebolla, extra tártara', 1, 1, NULL, '0000-00-00 00:00:00.000000');
INSERT INTO `detalle_pedido_detallepedido` VALUES (2, 1, '3500.00', 'Precio promo happy hour', 1, 5, NULL, '0000-00-00 00:00:00.000000');
INSERT INTO `detalle_pedido_detallepedido` VALUES (3, 1, '19500.00', 'Corte al punto, poca grasa', 2, 2, NULL, '0000-00-00 00:00:00.000000');
INSERT INTO `detalle_pedido_detallepedido` VALUES (4, 1, '68900.00', 'Llevar bolsas recicladas', 3, 3, NULL, '0000-00-00 00:00:00.000000');
INSERT INTO `detalle_pedido_detallepedido` VALUES (5, 1, '13200.00', NULL, 4, 4, NULL, '0000-00-00 00:00:00.000000');
INSERT INTO `detalle_pedido_detallepedido` VALUES (6, 1, '15900.00', 'Servilletas extra', 5, 1, NULL, '0000-00-00 00:00:00.000000');
INSERT INTO `detalle_pedido_detallepedido` VALUES (7, 1, '6500.00', 'En agua, poco azúcar', 5, 7, NULL, '0000-00-00 00:00:00.000000');
INSERT INTO `detalle_pedido_detallepedido` VALUES (8, 1, '9800.00', 'Hogao aparte', 5, 6, NULL, '0000-00-00 00:00:00.000000');
INSERT INTO `detalle_pedido_detallepedido` VALUES (9, 1, '15900.00', 'Cliente canceló por demora', 6, 1, NULL, '0000-00-00 00:00:00.000000');

-- Fin de tabla

-- Estructura de tabla: django_admin_log
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Fin de tabla

-- Estructura de tabla: django_content_type
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: django_content_type
INSERT INTO `django_content_type` VALUES (1, 'admin', 'logentry');
INSERT INTO `django_content_type` VALUES (3, 'auth', 'group');
INSERT INTO `django_content_type` VALUES (2, 'auth', 'permission');
INSERT INTO `django_content_type` VALUES (4, 'auth', 'user');
INSERT INTO `django_content_type` VALUES (5, 'contenttypes', 'contenttype');
INSERT INTO `django_content_type` VALUES (18, 'dashboard', 'configuracionsistema');
INSERT INTO `django_content_type` VALUES (15, 'detalle_pedido', 'detallepedido');
INSERT INTO `django_content_type` VALUES (9, 'inventario', 'inventario');
INSERT INTO `django_content_type` VALUES (10, 'inventario', 'inventariolote');
INSERT INTO `django_content_type` VALUES (16, 'metodo_pago', 'metodopago');
INSERT INTO `django_content_type` VALUES (13, 'movimiento_inventario', 'movimientoinventario');
INSERT INTO `django_content_type` VALUES (14, 'pedido', 'pedido');
INSERT INTO `django_content_type` VALUES (11, 'producto', 'producto');
INSERT INTO `django_content_type` VALUES (12, 'receta', 'receta');
INSERT INTO `django_content_type` VALUES (17, 'recibo', 'recibo');
INSERT INTO `django_content_type` VALUES (7, 'rol', 'rol');
INSERT INTO `django_content_type` VALUES (6, 'sessions', 'session');
INSERT INTO `django_content_type` VALUES (8, 'usuario', 'usuario');

-- Fin de tabla

-- Estructura de tabla: django_migrations
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: django_migrations
INSERT INTO `django_migrations` VALUES (1, 'contenttypes', '0001_initial', '2026-04-24 02:46:50.437245');
INSERT INTO `django_migrations` VALUES (2, 'auth', '0001_initial', '2026-04-24 02:46:50.945001');
INSERT INTO `django_migrations` VALUES (3, 'admin', '0001_initial', '2026-04-24 02:46:51.071756');
INSERT INTO `django_migrations` VALUES (4, 'admin', '0002_logentry_remove_auto_add', '2026-04-24 02:46:51.077967');
INSERT INTO `django_migrations` VALUES (5, 'admin', '0003_logentry_add_action_flag_choices', '2026-04-24 02:46:51.085112');
INSERT INTO `django_migrations` VALUES (6, 'contenttypes', '0002_remove_content_type_name', '2026-04-24 02:46:51.179431');
INSERT INTO `django_migrations` VALUES (7, 'auth', '0002_alter_permission_name_max_length', '2026-04-24 02:46:51.234207');
INSERT INTO `django_migrations` VALUES (8, 'auth', '0003_alter_user_email_max_length', '2026-04-24 02:46:51.250283');
INSERT INTO `django_migrations` VALUES (9, 'auth', '0004_alter_user_username_opts', '2026-04-24 02:46:51.256604');
INSERT INTO `django_migrations` VALUES (10, 'auth', '0005_alter_user_last_login_null', '2026-04-24 02:46:51.303623');
INSERT INTO `django_migrations` VALUES (11, 'auth', '0006_require_contenttypes_0002', '2026-04-24 02:46:51.306495');
INSERT INTO `django_migrations` VALUES (12, 'auth', '0007_alter_validators_add_error_messages', '2026-04-24 02:46:51.315627');
INSERT INTO `django_migrations` VALUES (13, 'auth', '0008_alter_user_username_max_length', '2026-04-24 02:46:51.388078');
INSERT INTO `django_migrations` VALUES (14, 'auth', '0009_alter_user_last_name_max_length', '2026-04-24 02:46:51.490343');
INSERT INTO `django_migrations` VALUES (15, 'auth', '0010_alter_group_name_max_length', '2026-04-24 02:46:51.508031');
INSERT INTO `django_migrations` VALUES (16, 'auth', '0011_update_proxy_permissions', '2026-04-24 02:46:51.513848');
INSERT INTO `django_migrations` VALUES (17, 'auth', '0012_alter_user_first_name_max_length', '2026-04-24 02:46:51.585870');
INSERT INTO `django_migrations` VALUES (18, 'dashboard', '0001_initial', '2026-04-24 02:46:51.603572');
INSERT INTO `django_migrations` VALUES (19, 'producto', '0001_initial', '2026-04-24 02:46:51.621808');
INSERT INTO `django_migrations` VALUES (20, 'rol', '0001_initial', '2026-04-24 02:46:51.648544');
INSERT INTO `django_migrations` VALUES (21, 'usuario', '0001_initial', '2026-04-24 02:46:51.755742');
INSERT INTO `django_migrations` VALUES (22, 'pedido', '0001_initial', '2026-04-24 02:46:51.822226');
INSERT INTO `django_migrations` VALUES (23, 'detalle_pedido', '0001_initial', '2026-04-24 02:46:51.940948');
INSERT INTO `django_migrations` VALUES (24, 'detalle_pedido', '0002_detallepedido_auditing', '2026-04-24 02:46:52.053345');
INSERT INTO `django_migrations` VALUES (25, 'detalle_pedido', '0003_alter_detallepedido_fecha_creacion', '2026-04-24 02:46:52.119125');
INSERT INTO `django_migrations` VALUES (26, 'inventario', '0001_initial', '2026-04-24 02:46:52.141049');
INSERT INTO `django_migrations` VALUES (27, 'inventario', '0002_entrega_bonos_lotes_movimiento_inicial', '2026-04-24 02:46:52.234644');
INSERT INTO `django_migrations` VALUES (28, 'metodo_pago', '0001_initial', '2026-04-24 02:46:52.260618');
INSERT INTO `django_migrations` VALUES (29, 'metodo_pago', '0002_seed_efectivo', '2026-04-24 02:46:52.276412');
INSERT INTO `django_migrations` VALUES (30, 'movimiento_inventario', '0001_initial', '2026-04-24 02:46:52.403225');
INSERT INTO `django_migrations` VALUES (31, 'movimiento_inventario', '0002_entrega_bonos_lotes_movimiento_inicial', '2026-04-24 02:46:52.412415');
INSERT INTO `django_migrations` VALUES (32, 'pedido', '0002_entrega_bonos_lotes_movimiento_inicial', '2026-04-24 02:46:52.499282');
INSERT INTO `django_migrations` VALUES (33, 'producto', '0002_alter_producto_imagen', '2026-04-24 02:46:52.504334');
INSERT INTO `django_migrations` VALUES (34, 'producto', '0003_entrega_bonos_lotes_movimiento_inicial', '2026-04-24 02:46:52.544812');
INSERT INTO `django_migrations` VALUES (35, 'producto', '0004_imagen_catalogo', '2026-04-24 02:46:52.587006');
INSERT INTO `django_migrations` VALUES (36, 'receta', '0001_initial', '2026-04-24 02:46:52.714398');
INSERT INTO `django_migrations` VALUES (37, 'recibo', '0001_initial', '2026-04-24 02:46:52.853411');
INSERT INTO `django_migrations` VALUES (38, 'sessions', '0001_initial', '2026-04-24 02:46:52.885208');
INSERT INTO `django_migrations` VALUES (39, 'usuario', '0002_entrega_bonos_lotes_movimiento_inicial', '2026-04-24 02:46:52.959371');
INSERT INTO `django_migrations` VALUES (40, 'usuario', '0003_usuario_ultima_actualizacion_password', '2026-04-24 02:46:53.025998');
INSERT INTO `django_migrations` VALUES (41, 'pedido', '0003_pedido_descuento_bonos_pedido_usar_bonos', '2026-04-24 02:50:30.837642');
INSERT INTO `django_migrations` VALUES (42, 'usuario', '0004_auto_20260423_2151', '2026-04-24 02:51:23.981214');
INSERT INTO `django_migrations` VALUES (43, 'producto', '0005_producto_esta_habilitado', '2026-04-24 03:02:24.967072');
INSERT INTO `django_migrations` VALUES (44, 'pedido', '0004_alter_pedido_usuario', '2026-05-12 23:44:05.734578');

-- Fin de tabla

-- Estructura de tabla: django_session
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: django_session
INSERT INTO `django_session` VALUES ('6a0xdbj0j76677y322v91xakhk25sn8b', '.eJxNir0KwjAQgF9Fbi7SWGxrNh_AyVUIZ5PKQZKTy0WQ0neXTnX8fhaYUBTssjZQS0UhduTBmh0zp6cEsHDn-VHbNng83FgwhgL7VUuQjGn70CfKf0k4goXrZqmooGeBBiIWdTgpfUi_YM0wjH3Xdb059ufTZTQNRH5RdjNSDN6hakhvLWDb9Qd4vj5T:1wMxmr:Xa59sF58Sf53-nB37uEEZLMyZzwVUw9qEHQxKGwstxg', '2026-05-13 02:49:21.667310');
INSERT INTO `django_session` VALUES ('bxl8sv6vht90v4ggcy48ux9z5f02vore', 'eyJjYXJ0Ijp7fX0:1wMx9B:Y4qiTcUQdWZ3KVaIOppITDoZwsAJzOlAAgg262zyiBY', '2026-05-13 02:08:21.210048');
INSERT INTO `django_session` VALUES ('lbs63i0drpfzbbrdbjmn6599urgz0nlt', '.eJxNir0KwjAQgF9Fbi6SKrVtNh_AyVUIZ5PKQZKTy0WQ0neXTnX8fhaYUBTssjZQS0UhduTBtjtmTk8JYOHO86MaEzwebiwYQ4H9qiVIxrR96BPlvyQcwcJ1s1RU0LNAAxGLOpyUPqRfsG3f98aY4dwdT5ehG8cGIr8ouxkpBu9QNaS3FrBm_QF4cj5U:1wG75n:4Kg2K2wYeUsMX9XocgbNeEKAuWsaeJ525n7YmxpADAw', '2026-04-24 05:20:35.269883');

-- Fin de tabla

-- Estructura de tabla: inventario_inventario
DROP TABLE IF EXISTS `inventario_inventario`;
CREATE TABLE `inventario_inventario` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre_insumo` varchar(100) NOT NULL,
  `categoria_insumo` varchar(50) NOT NULL,
  `unidad_medida` varchar(10) NOT NULL,
  `stock_actual` decimal(10,2) NOT NULL,
  `stock_minimo` decimal(10,2) NOT NULL,
  `stock_maximo` decimal(10,2) DEFAULT NULL,
  `precio_compra_referencia` decimal(10,2) NOT NULL,
  `iva_porcentaje` decimal(5,2) NOT NULL,
  `estado_insumo` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: inventario_inventario
INSERT INTO `inventario_inventario` VALUES (1, 'Chorizo artesanal res cervuno 12 mm', 'Cárnicos', 'KG', '18.50', '5.00', '40.00', '18900.00', '0.00', 'disponible');
INSERT INTO `inventario_inventario` VALUES (2, 'Pan brioche perro caliente', 'Panadería', 'UN', '120.00', '30.00', '200.00', '820.00', '0.00', 'disponible');
INSERT INTO `inventario_inventario` VALUES (3, 'Papa criolla pastusa', 'Verduras', 'KG', '25.00', '8.00', '50.00', '3600.00', '0.00', 'disponible');
INSERT INTO `inventario_inventario` VALUES (4, 'Queso mozzarella rallado Ronquer', 'Lácteos', 'KG', '4.20', '1.00', '10.00', '12400.00', '0.00', 'disponible');
INSERT INTO `inventario_inventario` VALUES (5, 'Aceite vegetal oleica 900 ml', 'Abarrotes', 'LT', '8.00', '2.00', '15.00', '9800.00', '19.00', 'disponible');
INSERT INTO `inventario_inventario` VALUES (6, 'Cebolla cabezona roja', 'Verduras', 'KG', '12.00', '3.00', '25.00', '2900.00', '0.00', 'disponible');
INSERT INTO `inventario_inventario` VALUES (7, 'Sal refisal yodada', 'Abarrotes', 'KG', '5.00', '1.00', '12.00', '2200.00', '19.00', 'disponible');
INSERT INTO `inventario_inventario` VALUES (8, 'Salsa tártara lonko 250 g', 'Abarrotes', 'UN', '40.00', '10.00', '80.00', '4500.00', '19.00', 'disponible');
INSERT INTO `inventario_inventario` VALUES (9, 'Arepa boyacense blanca', 'Panadería', 'UN', '200.00', '50.00', '400.00', '650.00', '0.00', 'disponible');
INSERT INTO `inventario_inventario` VALUES (10, 'Maracuyá badea malla 10 u', 'Frutas', 'UN', '15.00', '5.00', '40.00', '18500.00', '0.00', 'disponible');
INSERT INTO `inventario_inventario` VALUES (11, 'Gaseosa Postobón 400 ml retornable', 'Bebidas', 'UN', '96.00', '24.00', '200.00', '1600.00', '19.00', 'disponible');

-- Fin de tabla

-- Estructura de tabla: inventario_inventariolote
DROP TABLE IF EXISTS `inventario_inventariolote`;
CREATE TABLE `inventario_inventariolote` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `codigo_lote` varchar(50) NOT NULL,
  `cantidad` decimal(10,2) NOT NULL,
  `fecha_registro` datetime(6) NOT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `insumo_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `inventario_inventariolote_insumo_id_codigo_lote_f26aa543_uniq` (`insumo_id`,`codigo_lote`),
  CONSTRAINT `inventario_inventari_insumo_id_ff4e0c12_fk_inventari` FOREIGN KEY (`insumo_id`) REFERENCES `inventario_inventario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: inventario_inventariolote
INSERT INTO `inventario_inventariolote` VALUES (1, 'SE-2026-001', '10.00', '2026-01-08 10:00:00', '2026-07-01', 1);
INSERT INTO `inventario_inventariolote` VALUES (2, 'PAN-BRIO-ENE26', '80.00', '2026-01-09 08:00:00', '2026-02-20', 2);
INSERT INTO `inventario_inventariolote` VALUES (3, 'PAP-PST-004', '20.00', '2026-01-10 07:30:00', '2026-04-25', 3);
INSERT INTO `inventario_inventariolote` VALUES (4, 'GAS-PTB-ENE', '48.00', '2026-01-11 12:00:00', '2026-12-01', 11);

-- Fin de tabla

-- Estructura de tabla: metodo_pago_metodopago
DROP TABLE IF EXISTS `metodo_pago_metodopago`;
CREATE TABLE `metodo_pago_metodopago` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre_metodo` varchar(50) NOT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  `esta_activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre_metodo` (`nombre_metodo`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: metodo_pago_metodopago
INSERT INTO `metodo_pago_metodopago` VALUES (1, 'Efectivo', 'Pago en efectivo (domicilio o punto de venta)', 1);
INSERT INTO `metodo_pago_metodopago` VALUES (2, 'Nequi', 'Pago o transferencia con Nequi al número del local', 1);
INSERT INTO `metodo_pago_metodopago` VALUES (3, 'Daviplata', 'Daviplata QR o transferencia', 1);
INSERT INTO `metodo_pago_metodopago` VALUES (4, 'Tarjeta débito/crédito', 'Datáfono Bancolombia en punto de venta', 1);
INSERT INTO `metodo_pago_metodopago` VALUES (5, 'Transferencia bancaria', 'Pagos a cuentas Bancolombia / BBVA', 1);

-- Fin de tabla

-- Estructura de tabla: movimiento_inventario_movimientoinventario
DROP TABLE IF EXISTS `movimiento_inventario_movimientoinventario`;
CREATE TABLE `movimiento_inventario_movimientoinventario` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `lote` varchar(50) DEFAULT NULL,
  `tipo_movimiento` varchar(20) NOT NULL,
  `cantidad` decimal(10,2) NOT NULL,
  `fecha_movimiento` datetime(6) NOT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `observaciones` longtext,
  `insumo_id` bigint NOT NULL,
  `usuario_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `movimiento_inventari_insumo_id_a69e6780_fk_inventari` (`insumo_id`),
  KEY `movimiento_inventari_usuario_id_26559db2_fk_usuario_u` (`usuario_id`),
  CONSTRAINT `movimiento_inventari_insumo_id_a69e6780_fk_inventari` FOREIGN KEY (`insumo_id`) REFERENCES `inventario_inventario` (`id`),
  CONSTRAINT `movimiento_inventari_usuario_id_26559db2_fk_usuario_u` FOREIGN KEY (`usuario_id`) REFERENCES `usuario_usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: movimiento_inventario_movimientoinventario
INSERT INTO `movimiento_inventario_movimientoinventario` VALUES (1, 'SE-2026-001', 'entrada_inicial', '25.00', '2026-01-08 10:00:00', '2026-07-01', 'Recepción proveedor Cárnicos Morlin — remisión R-4481', 1, 1);
INSERT INTO `movimiento_inventario_movimientoinventario` VALUES (2, 'PAN-BRIO-ENE26', 'entrada_inicial', '100.00', '2026-01-09 08:00:00', NULL, 'Compra Panadería La Especial — factura POS-9921', 2, 1);
INSERT INTO `movimiento_inventario_movimientoinventario` VALUES (3, NULL, 'entrada', '50.00', '2026-02-14 09:15:00', NULL, 'Compra mayorista Plaza de Mercado Corabastos — papa criolla', 3, 4);
INSERT INTO `movimiento_inventario_movimientoinventario` VALUES (4, NULL, 'salida_desperdicio', '0.80', '2026-03-18 11:00:00', NULL, 'Merma por corte en cámara — chorizo', 1, 4);
INSERT INTO `movimiento_inventario_movimientoinventario` VALUES (5, NULL, 'salida_venta', '0.24', '2026-04-01 12:20:00', NULL, 'Descarte receta — Pedido domicilio Gómez 2026-04-01 (2 perros clásicos)', 1, 4);
INSERT INTO `movimiento_inventario_movimientoinventario` VALUES (6, NULL, 'salida_venta', '2.00', '2026-04-01 12:21:00', NULL, 'Descarte receta — pan brioche mismo pedido', 2, 4);
INSERT INTO `movimiento_inventario_movimientoinventario` VALUES (7, NULL, 'ajuste', '1.50', '2026-03-31 18:00:00', NULL, 'Ajuste inventario físico mensual — aceite (diferencia conteo)', 5, 1);

-- Fin de tabla

-- Estructura de tabla: pedido_pedido
DROP TABLE IF EXISTS `pedido_pedido`;
CREATE TABLE `pedido_pedido` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_pedido` datetime(6) NOT NULL,
  `tipo_pedido` varchar(20) NOT NULL,
  `direccion_pedido` varchar(255) DEFAULT NULL,
  `estado_pedido` varchar(20) NOT NULL,
  `total_pedido` decimal(10,2) NOT NULL,
  `usuario_id` bigint NOT NULL,
  `fecha_entrega_estimada` datetime(6) DEFAULT NULL,
  `fecha_entrega_real` datetime(6) DEFAULT NULL,
  `descuento_bonos` decimal(10,2) NOT NULL,
  `usar_bonos` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `pedido_pedido_usuario_id_00e3febe_fk_usuario_usuario_id` (`usuario_id`),
  CONSTRAINT `pedido_pedido_usuario_id_00e3febe_fk_usuario_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `usuario_usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: pedido_pedido
INSERT INTO `pedido_pedido` VALUES (1, '2026-04-01 12:15:00', 'domicilio', 'Carrera 13 #64-39, Bogotá', 'entregado', '35300.00', 2, '2026-04-01 13:00:00', '2026-04-01 13:08:00', '0.00', 0);
INSERT INTO `pedido_pedido` VALUES (2, '2026-04-03 18:40:00', 'llevar', NULL, 'preparacion', '19500.00', 3, '2026-04-03 19:25:00', NULL, '0.00', 0);
INSERT INTO `pedido_pedido` VALUES (3, '2026-04-08 13:00:00', 'local', NULL, 'listo', '68900.00', 2, '2026-04-08 13:45:00', NULL, '0.00', 0);
INSERT INTO `pedido_pedido` VALUES (4, '2026-04-09 10:05:00', 'domicilio', 'Avenida Ciudad de Cali #51-66, Bogotá', 'pendiente', '13200.00', 3, NULL, NULL, '0.00', 0);
INSERT INTO `pedido_pedido` VALUES (5, '2026-04-07 14:20:00', 'local', NULL, 'entregado', '32200.00', 2, '2026-04-07 14:55:00', '2026-04-07 15:02:00', '0.00', 0);
INSERT INTO `pedido_pedido` VALUES (6, '2026-04-09 19:30:00', 'domicilio', 'Kr 24 #17-68 sur, Tunjuelito', 'cancelado', '15900.00', 5, '2026-04-09 20:00:00', NULL, '0.00', 0);

-- Fin de tabla

-- Estructura de tabla: producto_producto
DROP TABLE IF EXISTS `producto_producto`;
CREATE TABLE `producto_producto` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre_producto` varchar(100) NOT NULL,
  `descripcion_producto` longtext,
  `imagen` varchar(100) DEFAULT NULL,
  `precio_venta` decimal(10,2) NOT NULL,
  `es_combo` tinyint(1) NOT NULL,
  `esta_disponible` tinyint(1) NOT NULL,
  `registro_movimiento_inicial` longtext,
  `imagen_catalogo` varchar(255) NOT NULL,
  `esta_habilitado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: producto_producto
INSERT INTO `producto_producto` VALUES (1, 'Perro chorizo clásico', 'Chorizo a la plancha en pan brioche, salsas lácteas, papa en cascos y toque de cebolla caramelizada.', NULL, '15900.00', 0, 1, 'Lote SE-2026-001 chorizo Morlin / Pan La Especial', '', 1);
INSERT INTO `producto_producto` VALUES (2, 'Chorizo a la plancha (250 g)', 'Porción generosa con chimichurri, arepa boyacense o media papa a la francesa (elige en notas).', NULL, '19500.00', 0, 1, NULL, '', 1);
INSERT INTO `producto_producto` VALUES (3, 'Combo familiar 4 personas', 'Cuatro perros clásicos, papa medianera para compartir y cuatro gaseosas 400 ml.', NULL, '68900.00', 1, 1, NULL, '', 1);
INSERT INTO `producto_producto` VALUES (4, 'Papa chorizo gratinada', 'Papa criolla cocida con trozos de chorizo, queso mozzarella gratinado y perejil.', NULL, '13200.00', 0, 1, NULL, '', 1);
INSERT INTO `producto_producto` VALUES (5, 'Gaseosa personal 400 ml', 'Gaseosa fría (marca según disponibilidad en nevera).', NULL, '3800.00', 0, 1, NULL, '', 1);
INSERT INTO `producto_producto` VALUES (6, 'Arepa con chorizo antioqueño', 'Arepa blanca asada con medio chorizo desmechado y hogao casero.', NULL, '9800.00', 0, 1, NULL, '', 1);
INSERT INTO `producto_producto` VALUES (7, 'Jugo natural maracuyá', 'Jugo en agua o en leche 400 ml, pulpa fresca.', NULL, '6500.00', 0, 1, NULL, '', 1);

-- Fin de tabla

-- Estructura de tabla: receta_receta
DROP TABLE IF EXISTS `receta_receta`;
CREATE TABLE `receta_receta` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `cantidad_requerida` decimal(10,2) NOT NULL,
  `insumo_id` bigint NOT NULL,
  `producto_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `receta_receta_producto_id_insumo_id_9472c976_uniq` (`producto_id`,`insumo_id`),
  KEY `receta_receta_insumo_id_0bdaf018_fk_inventario_inventario_id` (`insumo_id`),
  CONSTRAINT `receta_receta_insumo_id_0bdaf018_fk_inventario_inventario_id` FOREIGN KEY (`insumo_id`) REFERENCES `inventario_inventario` (`id`),
  CONSTRAINT `receta_receta_producto_id_7c42a24a_fk_producto_producto_id` FOREIGN KEY (`producto_id`) REFERENCES `producto_producto` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: receta_receta
INSERT INTO `receta_receta` VALUES (1, '0.12', 1, 1);
INSERT INTO `receta_receta` VALUES (2, '1.00', 2, 1);
INSERT INTO `receta_receta` VALUES (3, '0.08', 3, 1);
INSERT INTO `receta_receta` VALUES (4, '0.02', 6, 1);
INSERT INTO `receta_receta` VALUES (5, '0.04', 8, 1);
INSERT INTO `receta_receta` VALUES (6, '0.25', 1, 2);
INSERT INTO `receta_receta` VALUES (7, '0.08', 6, 2);
INSERT INTO `receta_receta` VALUES (8, '1.00', 9, 2);
INSERT INTO `receta_receta` VALUES (9, '0.30', 3, 4);
INSERT INTO `receta_receta` VALUES (10, '0.10', 1, 4);
INSERT INTO `receta_receta` VALUES (11, '0.06', 4, 4);
INSERT INTO `receta_receta` VALUES (12, '0.45', 1, 6);
INSERT INTO `receta_receta` VALUES (13, '1.00', 9, 6);
INSERT INTO `receta_receta` VALUES (14, '0.08', 1, 3);
INSERT INTO `receta_receta` VALUES (15, '4.00', 2, 3);
INSERT INTO `receta_receta` VALUES (16, '0.60', 3, 3);
INSERT INTO `receta_receta` VALUES (17, '4.00', 11, 3);
INSERT INTO `receta_receta` VALUES (18, '0.35', 10, 7);
INSERT INTO `receta_receta` VALUES (19, '1.00', 11, 5);

-- Fin de tabla

-- Estructura de tabla: recibo_recibo
DROP TABLE IF EXISTS `recibo_recibo`;
CREATE TABLE `recibo_recibo` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_emision` datetime(6) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `iva_total` decimal(10,2) NOT NULL,
  `total_pagado` decimal(10,2) NOT NULL,
  `puntos_ganados` int unsigned NOT NULL,
  `metodo_pago_id` bigint NOT NULL,
  `pedido_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pedido_id` (`pedido_id`),
  KEY `recibo_recibo_metodo_pago_id_9b2b1cd5_fk_metodo_pa` (`metodo_pago_id`),
  CONSTRAINT `recibo_recibo_metodo_pago_id_9b2b1cd5_fk_metodo_pa` FOREIGN KEY (`metodo_pago_id`) REFERENCES `metodo_pago_metodopago` (`id`),
  CONSTRAINT `recibo_recibo_pedido_id_93e088c0_fk_pedido_pedido_id` FOREIGN KEY (`pedido_id`) REFERENCES `pedido_pedido` (`id`),
  CONSTRAINT `recibo_recibo_chk_1` CHECK ((`puntos_ganados` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: recibo_recibo
INSERT INTO `recibo_recibo` VALUES (1, '2026-04-01 12:16:00', '29663.87', '5636.13', '35300.00', 35, 1, 1);
INSERT INTO `recibo_recibo` VALUES (2, '2026-04-03 18:41:00', '16387.39', '3112.61', '19500.00', 19, 2, 2);
INSERT INTO `recibo_recibo` VALUES (3, '2026-04-08 13:01:00', '57899.16', '11000.84', '68900.00', 68, 1, 3);
INSERT INTO `recibo_recibo` VALUES (4, '2026-04-07 14:21:00', '27058.82', '5141.18', '32200.00', 32, 4, 5);

-- Fin de tabla

-- Estructura de tabla: rol_rol
DROP TABLE IF EXISTS `rol_rol`;
CREATE TABLE `rol_rol` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre_rol` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre_rol` (`nombre_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: rol_rol
INSERT INTO `rol_rol` VALUES (1, 'Administrador');
INSERT INTO `rol_rol` VALUES (2, 'Cliente');
INSERT INTO `rol_rol` VALUES (3, 'Empleado');
INSERT INTO `rol_rol` VALUES (4, 'Reparto');

-- Fin de tabla

-- Estructura de tabla: usuario_usuario
DROP TABLE IF EXISTS `usuario_usuario`;
CREATE TABLE `usuario_usuario` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tipo_documento` varchar(10) NOT NULL,
  `documento` varchar(15) NOT NULL,
  `primer_nombre` varchar(40) NOT NULL,
  `apellido` varchar(40) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(100) NOT NULL,
  `nombre_usuario` varchar(50) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `puntos_acumulados` int unsigned NOT NULL,
  `estado` varchar(10) NOT NULL,
  `fecha_registro` datetime(6) NOT NULL,
  `rol_id` bigint NOT NULL,
  `bonos_fidelidad` int unsigned NOT NULL,
  `ultima_actualizacion_password` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `documento` (`documento`),
  UNIQUE KEY `correo` (`correo`),
  UNIQUE KEY `nombre_usuario` (`nombre_usuario`),
  KEY `usuario_usuario_rol_id_3abe68b9_fk_rol_rol_id` (`rol_id`),
  CONSTRAINT `usuario_usuario_rol_id_3abe68b9_fk_rol_rol_id` FOREIGN KEY (`rol_id`) REFERENCES `rol_rol` (`id`),
  CONSTRAINT `usuario_usuario_chk_1` CHECK ((`puntos_acumulados` >= 0)),
  CONSTRAINT `usuario_usuario_chk_2` CHECK ((`bonos_fidelidad` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Datos de tabla: usuario_usuario
INSERT INTO `usuario_usuario` VALUES (1, 'CC', '1000000001', 'Sofía', 'Morales', 'admin@shoriexpress.local', '3001112233', 'Calle 72 #10-34, Chapinero, Bogotá', 'admin', 'pbkdf2_sha256$600000$ZQlLCCbsPW7JtyKtmuZsDE$IBeHci4W6WinAZi6Jxl469YFdKAmRr5jogRppX6OxwE=', 0, 'activo', '2026-01-10 09:00:00', 1, 0, '0000-00-00 00:00:00.000000');
INSERT INTO `usuario_usuario` VALUES (2, 'CC', '52345678', 'María', 'Gómez Lozano', 'maria@ejemplo.com', '3109876543', 'Carrera 13 #64-39, Bogotá', 'mariag', 'pbkdf2_sha256$600000$5y2jlfZB3hBUvqVGVooJpr$AZO9QmIabl2Px7dULFVhB2GRXhATWLCFVwFC3JVZ1mY=', 120, 'activo', '2026-02-01 11:30:00', 2, 7, '0000-00-00 00:00:00.000000');
INSERT INTO `usuario_usuario` VALUES (3, 'CC', '79876543', 'Carlos', 'Rincón Vega', 'carlos@ejemplo.com', '3205554411', 'Avenida Ciudad de Cali #51-66, Bogotá', '', 'Shori2024!', 45, 'activo', '2026-03-05 16:00:00', 2, 0, '0000-00-00 00:00:00.000000');
INSERT INTO `usuario_usuario` VALUES (4, 'CC', '1122334455', 'Andrea', 'Benítez', 'empleado@shoriexpress.local', '3004445566', 'Cl. 47 sur #13a-39, Local Shori', 'andrea_cocina', 'pbkdf2_sha256$600000$TgRcaWJWuk3olRs5jwLuZd$y0pIVkK4rDqlEDrVOYRu7D8j127P+a4OMCc04Uf1xuI=', 0, 'activo', '2026-01-15 08:00:00', 3, 0, '0000-00-00 00:00:00.000000');
INSERT INTO `usuario_usuario` VALUES (5, 'CC', '9012345678', 'Diego', 'Moncada', 'diego.reparto@shoriexpress.local', '3112003344', 'Kr 24 #17-68 sur, Tunjuelito, Bogotá', 'diegoreparto', 'pbkdf2_sha256$600000$D1XURupX3w2rNltuSfkjkB$ZbE5ohy4hiehPU0jvNXbu0/Ksoa22SMfiYzpPiBCaCo=', 0, 'activo', '2026-02-20 07:00:00', 4, 0, '0000-00-00 00:00:00.000000');

-- Fin de tabla

