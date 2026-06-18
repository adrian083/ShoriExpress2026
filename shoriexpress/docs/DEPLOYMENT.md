# Guía de despliegue — ShoriExpress (gratis en Render)

Tu proyecto ya está preparado para **Render** (plan gratuito). Es la opción más sencilla para una exposición: conectas GitHub y en unos minutos queda en línea.

> **Importante:** El código Django vive en la carpeta `shoriexpress/` dentro del repositorio. En Render debes indicar esa carpeta como **Root Directory**.

---

## Opción A — Despliegue automático (recomendado)

1. Entra a [render.com](https://render.com) y crea cuenta (puedes usar GitHub).
2. Ve a **Blueprints** → **New Blueprint Instance**.
3. Conecta el repositorio: `adrian083/ShoriExpress2026`.
4. Render leerá el archivo `render.yaml` de la raíz y creará el servicio.
5. Espera 5–10 minutos a que termine el **Build** y el **Deploy**.
6. Abre la URL que te da Render (algo como `https://shoriexpress-xxxx.onrender.com`).

### Variables de entorno (ya vienen en `render.yaml`)

| Variable | Valor |
|----------|-------|
| `DJANGO_SECRET_KEY` | Se genera sola |
| `DJANGO_DEBUG` | `False` |
| `USE_SQLITE` | `true` |

No necesitas configurar `DJANGO_ALLOWED_HOSTS`: Render lo detecta automáticamente.

---

## Opción B — Crear el servicio a mano

Si prefieres no usar Blueprint:

1. **New** → **Web Service** → conecta tu repo de GitHub.
2. Configura así:

| Campo | Valor |
|-------|-------|
| **Root Directory** | `shoriexpress` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput` |
| **Start Command** | `gunicorn shoriexpress.wsgi --bind 0.0.0.0:$PORT --log-file -` |

3. En **Environment**, agrega:

```
DJANGO_SECRET_KEY = (genera una clave larga aleatoria)
DJANGO_DEBUG = False
USE_SQLITE = true
```

4. Clic en **Create Web Service**.

---

## Iniciar sesión en la demo

La primera vez que alguien intente entrar al login, si la base está vacía, el sistema crea automáticamente un usuario administrador:

| Campo | Valor |
|-------|-------|
| Usuario | `admin` |
| Contraseña | `Shori2024!` |

---

## Qué revisar antes de la exposición

- [ ] La página principal carga con estilos (CSS).
- [ ] Puedes iniciar sesión con `admin` / `Shori2024!`.
- [ ] El menú de productos se ve correctamente.
- [ ] El panel interno (`/panel/` o `/dashboard/`) funciona.

---

## Limitaciones del plan gratuito de Render

- La app **se duerme** tras ~15 min sin visitas. La primera carga puede tardar **30–60 segundos** (normal en el plan free).
- Los datos en SQLite **pueden perderse** si Render vuelve a desplegar. Para la exposición, entra una vez antes y verifica el login.
- Las imágenes que subas en producción **no persisten** entre redespliegues (solo afecta si subes archivos nuevos en la nube).

---

## Si algo falla

1. En Render, abre tu servicio → pestaña **Logs**.
2. Errores frecuentes:
   - **Root Directory incorrecto** → debe ser `shoriexpress`, no la raíz del repo.
   - **DJANGO_SECRET_KEY no definida** → agrégala en Environment.
   - **DisallowedHost** → vuelve a desplegar con el código actual (ya incluye soporte para Render).
   - **Sin estilos** → el build debe ejecutar `collectstatic` (ya está en los comandos de arriba).

---

## Otras opciones gratuitas (alternativas)

| Servicio | Ventaja | Desventaja |
|----------|---------|------------|
| **Render** | Muy fácil con GitHub | Se duerme en plan free |
| **PythonAnywhere** | Estable para Django | Configuración manual, dominio `*.pythonanywhere.com` |
| **Railway** | Rápido | Créditos limitados al mes |

Para tu exposición de mañana, **Render con esta guía** es la opción más rápida.
