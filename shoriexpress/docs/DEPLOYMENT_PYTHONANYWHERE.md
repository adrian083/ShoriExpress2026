# Despliegue en PythonAnywhere — ShoriExpress

Guía paso a paso para dejar tu proyecto en línea **gratis**, con datos de demo y base persistente.

---

## Antes de empezar

1. Crea cuenta en [pythonanywhere.com](https://www.pythonanywhere.com) (plan **Beginner** gratis).
2. Sube tu código a GitHub (o usa el repo que ya tienes: `adrian083/ShoriExpress2026`).
3. Anota tu **usuario de PythonAnywhere** (ej. `adrian083` → tu URL será `adrian083.pythonanywhere.com`).

---

## Paso 1 — Clonar el proyecto

En PythonAnywhere, abre una consola **Bash** (pestaña *Consoles* → *Bash*) y ejecuta:

```bash
cd ~
git clone https://github.com/adrian083/ShoriExpress2026.git
cd ShoriExpress2026/shoriexpress
```

---

## Paso 2 — Entorno virtual e instalación

```bash
mkvirtualenv --python=/usr/bin/python3.11 shoriexpress
pip install -r requirements.txt
```

> Si `python3.11` no existe, prueba con `python3.10`.

---

## Paso 3 — Variables de entorno

Crea el archivo `.env` en la carpeta `shoriexpress`:

```bash
nano ~/ShoriExpress2026/shoriexpress/.env
```

Pega esto (cambia los valores):

```env
DJANGO_SECRET_KEY=una-clave-muy-larga-y-aleatoria-de-al-menos-50-caracteres
DJANGO_DEBUG=False
USE_SQLITE=true
PYTHONANYWHERE_DOMAIN=TU_USUARIO.pythonanywhere.com
DJANGO_ALLOWED_HOSTS=TU_USUARIO.pythonanywhere.com
SEED_DEMO_PASSWORD=Shori2024!
```

Guarda con `Ctrl+O`, Enter, `Ctrl+X`.

---

## Paso 4 — Base de datos, estáticos y datos demo

Con el virtualenv activo (`workon shoriexpress` si hace falta):

```bash
cd ~/ShoriExpress2026/shoriexpress
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_demo
```

El comando `seed_demo` carga roles, usuarios, productos, inventario y recetas. Es seguro ejecutarlo más de una vez.

---

## Paso 5 — Crear la Web App

1. Ve a la pestaña **Web**.
2. Clic en **Add a new web app**.
3. Elige **Manual configuration** (no uses el asistente de Django).
4. Selecciona **Python 3.11** (o 3.10).
5. En **Virtualenv**, escribe: `/home/TU_USUARIO/.virtualenvs/shoriexpress`
6. Clic en el enlace del archivo **WSGI configuration file**.
7. Borra todo y pega el contenido de `deploy/pythonanywhere_wsgi.py.example`, cambiando `USERNAME` por tu usuario.
8. Guarda el archivo.

---

## Paso 6 — Archivos estáticos y media

En la pestaña **Web**, sección **Static files**, agrega:

| URL           | Directory                                              |
|---------------|--------------------------------------------------------|
| `/static/`    | `/home/TU_USUARIO/ShoriExpress2026/shoriexpress/staticfiles` |
| `/media/`     | `/home/TU_USUARIO/ShoriExpress2026/shoriexpress/media`       |

Guarda y pulsa el botón verde **Reload** arriba a la derecha.

---

## Paso 7 — Probar la app

Abre: `https://TU_USUARIO.pythonanywhere.com`

### Usuarios de demo (contraseña: `Shori2024!`)

| Rol           | Usuario         | Correo                        |
|---------------|-----------------|-------------------------------|
| Administrador | `admin`         | admin@shoriexpress.local      |
| Cliente       | `mariag`        | maria@ejemplo.com             |
| Empleado      | `andrea_cocina` | empleado@shoriexpress.local   |

---

## Actualizar el proyecto después de cambios en GitHub

```bash
cd ~/ShoriExpress2026
git pull
cd shoriexpress
workon shoriexpress
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Luego en la pestaña **Web** → **Reload**.

---

## Errores frecuentes

| Error | Solución |
|-------|----------|
| **DisallowedHost** | Revisa `DJANGO_ALLOWED_HOSTS` y `PYTHONANYWHERE_DOMAIN` en `.env` y en el WSGI |
| **Sin CSS** | Ejecuta `collectstatic` y verifica el mapeo `/static/` en Web |
| **500 al entrar** | Revisa el **Error log** en la pestaña Web |
| **DJANGO_SECRET_KEY** | Debe existir en `.env` o en el WSGI |

---

## Ventajas frente a Render gratis

- La app **no se duerme**.
- SQLite **persiste** entre recargas.
- Ideal para una exposición o sustentación.
