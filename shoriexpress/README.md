# ShoriExpress

Sistema de gestión para restaurante de chorizos.

## Instalación

1. Clona el repositorio.
2. Instala dependencias: `pip install -r requirements.txt`
3. Configura la base de datos MySQL en settings.py o usa SQLite con `USE_SQLITE=true`.
4. Ejecuta migraciones: `python manage.py migrate`
5. Carga datos de demostración: `python manage.py seed_demo`  
   (o ejecuta el SQL en `sql/seed_datos_demo_mysql.sql` si usas MySQL)
6. Crea superusuario: `python manage.py createsuperuser`
7. Ejecuta el servidor: `python manage.py runserver`

## Funcionalidades

- Gestión de usuarios, roles, productos, inventario, pedidos.
- Validaciones robustas para evitar errores.
- Prevención de pedidos múltiples activos.
- Reconciliación automática de totales.

## Pruebas

Ejecuta `python manage.py test` para correr las pruebas.