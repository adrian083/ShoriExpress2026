# Guía rápida de despliegue

Esta guía te muestra cómo dejar el proyecto listo para una demostración en un host gratuito.

## 1) Prepara el repositorio
1. Asegúrate de que tu proyecto esté subido a GitHub.
2. Verifica que existan los archivos:
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`

## 2) Ajusta la configuración para producción
En el panel de tu host, agrega estas variables de entorno:

- `DJANGO_SECRET_KEY=<una clave larga y aleatoria>`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=<tu-dominio-o-render-app>`
- `USE_SQLITE=true`

> Si el host te permite PostgreSQL o MySQL, puedes usar esa opción para una demo más seria.

## 3) Comandos que debe ejecutar el host
El host normalmente ejecutará automáticamente:

- `pip install -r requirements.txt`
- `python manage.py collectstatic --noinput`
- `python manage.py migrate`

Y el inicio del servidor se hará con:

- `gunicorn shoriexpress.wsgi`

## 4) Crear superusuario
Después del despliegue, ejecuta:

- `python manage.py createsuperuser`

Esto te permitirá entrar al panel de administración.

## 5) Revisar que todo funcione
Verifica que puedas entrar a:
- la página principal,
- el login,
- el panel administrativo,
- y la parte donde se ven productos.

## 6) Recomendación para sustentación
Para una presentación rápida, usa:
- `USE_SQLITE=true`,
- `DJANGO_DEBUG=False`,
- un dominio simple,
- y datos de ejemplo cargados antes de la exposición.
