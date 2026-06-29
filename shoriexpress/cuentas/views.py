import json
import urllib.error
import urllib.request
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from functools import wraps

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from metodo_pago.models import MetodoPago
from producto.cart import Cart
from producto.horario_validator import HorarioComercialValidator
from usuario.models import Usuario
from rol.models import Rol

from .password_utils import hash_password, password_coincide, rehash_si_legado
from .demo_credentials import get_demo_password

# Roles que tienen acceso al panel de administración/dashboard
ROLES_ADMIN = ['admin', 'administrador', 'empleado']
USERNAME_RE = re.compile(r'^[A-Za-z0-9_.]{4,50}$')
DOCUMENTO_RE = re.compile(r'^[A-Za-z0-9]{5,20}$')
NOMBRE_RE = re.compile(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{2,40}$')
TELEFONO_RE = re.compile(r'^[0-9]{10}$')

SESSION_TIMEOUT_MINUTES = 30
MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 5
PASSWORD_EXPIRY_DAYS = 90


def csrf_failure(request, reason=''):
    """Muestra error de la app en lugar de la página 403 del host."""
    messages.error(
        request,
        'No se pudo completar la acción (sesión o token inválido). '
        'Recarga la página e intenta de nuevo.',
    )
    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(
        url=referer,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(referer)
    return redirect('landing')


def _session_expired(request):
    last_activity = request.session.get('last_activity')
    if not last_activity:
        return False
    try:
        last = float(last_activity)
    except (TypeError, ValueError):
        return True
    return (timezone.now().timestamp() - last) > (SESSION_TIMEOUT_MINUTES * 60)


def _actualizar_actividad_sesion(request):
    request.session['last_activity'] = timezone.now().timestamp()


def _incrementar_intentos_login(request):
    intentos = request.session.get('login_failed_attempts', 0) + 1
    request.session['login_failed_attempts'] = intentos
    if intentos >= MAX_FAILED_LOGIN_ATTEMPTS:
        request.session['login_failed_attempts'] = 0
        request.session['login_lock_until'] = timezone.now().timestamp() + (LOCKOUT_MINUTES * 60)
        return True
    return False


def _normalizar_fecha(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return timezone.make_aware(value) if timezone.is_naive(value) else value
    if isinstance(value, str):
        candidate = value.strip()
        if candidate in {'', '0000-00-00', '0000-00-00 00:00:00', '0000-00-00 00:00:00.000000'}:
            return None
        try:
            parsed = datetime.fromisoformat(candidate.replace(' ', 'T'))
        except ValueError:
            return None
        return timezone.make_aware(parsed) if timezone.is_naive(parsed) else parsed
    return None


def _password_vencida(usuario):
    fecha = _normalizar_fecha(getattr(usuario, 'ultima_actualizacion_password', None))
    if not fecha:
        return False
    return (timezone.now() - fecha).days >= PASSWORD_EXPIRY_DAYS



def _es_rol_admin(nombre_rol):
    """Verifica si un rol tiene acceso al dashboard."""
    if not nombre_rol:
        return False
    return nombre_rol.strip().lower() in ROLES_ADMIN


def _get_usuario_sesion(request):
    """Helper: obtener el usuario logueado desde la sesión."""
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        try:
            return Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            request.session.flush()
    return None


def _redirect_seguro_tras_login(request, default_name='landing'):
    """Evita redirección abierta (open redirect): solo rutas relativas del mismo sitio."""
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and next_url.startswith('/') and not next_url.startswith('//'):
        if url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
    return redirect(default_name)


def _ensure_default_admin_user():
    """Crea un usuario demo de administración si la base de datos está vacía."""
    if Usuario.objects.exists():
        return None

    rol_admin = Rol.objects.filter(nombre_rol__iexact='administrador').first()
    if not rol_admin:
        rol_admin = Rol.objects.filter(nombre_rol__iexact='admin').first()
    if not rol_admin:
        rol_admin = Rol.objects.create(nombre_rol='Administrador')

    return Usuario.objects.create(
        tipo_documento='CC',
        documento='1000000001',
        nombre_usuario='admin',
        contrasena=hash_password(get_demo_password()),
        primer_nombre='Admin',
        apellido='Sistema',
        correo='admin@shoriexpress.local',
        telefono='3000000000',
        direccion='Oficina central',
        puntos_acumulados=0,
        estado='activo',
        rol=rol_admin,
    )


@require_GET
def landing(request):
    """Página comercial pública con secciones informativas."""
    try:
        from producto.models import Producto
        productos = Producto.objects.filter(
            esta_disponible=True
        ).order_by('nombre_producto')[:6]
    except Exception:
        productos = []

    usuario_logueado = _get_usuario_sesion(request)
    es_admin = False
    if usuario_logueado and usuario_logueado.rol:
        es_admin = _es_rol_admin(usuario_logueado.rol.nombre_rol)

    return render(request, 'cuentas/landing.html', {
        'productos': productos,
        'usuario_logueado': usuario_logueado,
        'es_admin': es_admin,
    })


@require_GET
@ensure_csrf_cookie
def ver_carrito(request):
    """Vista para visualizar los productos agregados al carrito."""
    usuario_logueado = _get_usuario_sesion(request)
    metodo_efectivo = MetodoPago.objects.filter(
        esta_activo=True, nombre_metodo__iexact="Efectivo"
    ).order_by("nombre_metodo").first()

    cart = Cart(request)
    total = 0.0
    for _, value in cart.cart.items():
        total += float(value["precio"]) * int(value["cantidad"])

    bonos = int(getattr(usuario_logueado, "bonos_fidelidad", 0) or 0) if usuario_logueado else 0
    puede_redimir = bonos >= 5 and total > 0
    total_con_descuento = round(total * 0.95, 2) if puede_redimir else None
    descuento_valor = round(total - total_con_descuento, 2) if puede_redimir else None

    horario = HorarioComercialValidator.obtener_config_horario()

    return render(request, 'cuentas/carrito.html', {
        'usuario_logueado': usuario_logueado,
        'metodo_efectivo': metodo_efectivo,
        'bonos_disponibles': bonos,
        'puede_redimir_bonos': puede_redimir,
        'descuento_bonos_valor': descuento_valor,
        'total_con_descuento_bonos': total_con_descuento,
        'horario': horario,
    })


@require_GET
def ver_menu_publico(request):
    """Página dedicada al menú (productos disponibles)."""
    try:
        from producto.models import Producto
        productos = Producto.objects.filter(
            esta_disponible=True
        ).prefetch_related('ingredientes__insumo').order_by("nombre_producto")
    except Exception:
        productos = []
    usuario_logueado = _get_usuario_sesion(request)
    es_admin = False
    if usuario_logueado and usuario_logueado.rol:
        es_admin = _es_rol_admin(usuario_logueado.rol.nombre_rol)
    return render(request, "cuentas/menu_publico.html", {
        "productos": productos,
        "usuario_logueado": usuario_logueado,
        "es_admin": es_admin,
    })


@require_GET
def api_hora_bogota(request):
    """Consume la API pública de hora (America/Bogotá) para tiempos de entrega en el cliente."""
    try:
        req = urllib.request.Request(
            "https://worldtimeapi.org/api/timezone/America/Bogota",
            headers={"User-Agent": "ShoriExpress/1.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        return JsonResponse({
            "ok": True,
            "datetime": data.get("datetime"),
            "timezone": data.get("timezone"),
            "source": "worldtimeapi.org",
        })
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        now = timezone.now()
        bogota = now.astimezone(ZoneInfo("America/Bogota"))
        return JsonResponse({
            "ok": False,
            "datetime": bogota.isoformat(),
            "timezone": "America/Bogota",
            "source": "fallback",
        })

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista de inicio de sesión con soporte para redirección inteligente."""
    # Si ya está logueado, redirigir según rol o al 'next' seguro
    if request.session.get('usuario_id'):
        return _redirect_seguro_tras_login(request, default_name='home' if _es_rol_admin(request.session.get('usuario_rol', '')) else 'landing')

    if request.method == 'POST':
        lock_until = request.session.get('login_lock_until')
        if lock_until:
            try:
                lock_timestamp = float(lock_until)
            except (TypeError, ValueError):
                lock_timestamp = 0
            if timezone.now().timestamp() < lock_timestamp:
                seconds = int(lock_timestamp - timezone.now().timestamp())
                messages.error(request, f'Demasiados intentos fallidos. Intenta de nuevo en {seconds} segundos.')
                return render(request, 'cuentas/login.html', {
                    'login_next': request.POST.get('next') or request.GET.get('next') or '',
                })

        username = request.POST.get('username', '').strip().lower()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Por favor completa todos los campos.')
            _incrementar_intentos_login(request)
            return render(request, 'cuentas/login.html', {
                'login_next': request.POST.get('next') or request.GET.get('next') or '',
            })

        if not USERNAME_RE.fullmatch(username):
            messages.error(request, 'Usuario inválido. Usa 4 a 50 caracteres (letras, números, punto o guion bajo).')
            return render(request, 'cuentas/login.html', {
                'login_next': request.POST.get('next') or request.GET.get('next') or '',
            })

        if not Usuario.objects.exists():
            _ensure_default_admin_user()

        usuario = Usuario.objects.filter(nombre_usuario__iexact=username).first()
        if not usuario:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            _incrementar_intentos_login(request)
            return render(request, 'cuentas/login.html', {
                'login_next': request.POST.get('next') or request.GET.get('next') or '',
            })

        if not password_coincide(usuario, password):
            messages.error(request, 'Usuario o contraseña incorrectos.')
            _incrementar_intentos_login(request)
            return render(request, 'cuentas/login.html', {
                'login_next': request.POST.get('next') or request.GET.get('next') or '',
            })

        if usuario.estado == 'inactivo':
            messages.error(request, 'Tu cuenta está inactiva. Contacta al administrador.')
            _incrementar_intentos_login(request)
            return render(request, 'cuentas/login.html', {
                'login_next': request.POST.get('next') or request.GET.get('next') or '',
            })

        rehash_si_legado(usuario, password)

        request.session.cycle_key()
        nombre_rol = usuario.rol.nombre_rol if usuario.rol else ''
        request.session['usuario_id'] = usuario.pk
        request.session['usuario_nombre'] = f"{usuario.primer_nombre} {usuario.apellido}"
        request.session['usuario_username'] = usuario.nombre_usuario
        request.session['usuario_rol'] = nombre_rol
        request.session['last_activity'] = timezone.now().timestamp()
        request.session['login_failed_attempts'] = 0
        request.session.pop('login_lock_until', None)

        messages.success(request, f'¡Bienvenido, {usuario.primer_nombre}!')

        return _redirect_seguro_tras_login(
            request,
            default_name='home' if _es_rol_admin(nombre_rol) else 'landing',
        )

    return render(request, 'cuentas/login.html', {
        'login_next': request.GET.get('next') or '',
    })


@require_http_methods(["GET", "POST"])
def recuperar_contrasena(request):
    """Permite recuperar y renovar la contraseña mediante correo y documento."""
    if request.method == 'POST':
        documento = request.POST.get('documento', '').strip()
        correo = request.POST.get('correo', '').strip().lower()
        nueva = request.POST.get('nueva_contrasena', '').strip()
        confirmar = request.POST.get('confirmar_contrasena', '').strip()

        if not documento or not correo or not nueva or not confirmar:
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'cuentas/recuperar_contrasena.html')

        if nueva != confirmar:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'cuentas/recuperar_contrasena.html')

        if len(nueva) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'cuentas/recuperar_contrasena.html')

        try:
            usuario = Usuario.objects.get(documento=documento, correo__iexact=correo)
        except Usuario.DoesNotExist:
            messages.error(request, 'No se encontró un usuario con esos datos.')
            return render(request, 'cuentas/recuperar_contrasena.html')

        usuario.contrasena = hash_password(nueva)
        usuario.ultima_actualizacion_password = timezone.now()
        usuario.save(update_fields=['contrasena', 'ultima_actualizacion_password'])

        request.session.cycle_key()
        messages.success(request, 'Contraseña renovada correctamente. Ahora puedes iniciar sesión con tu nueva clave.')
        return redirect('login')

    return render(request, 'cuentas/recuperar_contrasena.html')


@require_http_methods(["GET", "POST"])
def register_view(request):
    """Vista de registro de nuevos usuarios."""
    if request.session.get('usuario_id'):
        usuario_rol = request.session.get('usuario_rol', '')
        if _es_rol_admin(usuario_rol):
            return redirect('home')
        else:
            return redirect('landing')

    if request.method == 'POST':
        tipo_doc = request.POST.get('tipo_doc', '').strip()
        documento = request.POST.get('documento', '').strip()
        username = request.POST.get('username', '').strip().lower()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        correo = request.POST.get('correo', '').strip().lower()
        telefono = request.POST.get('telefono', '').strip()
        direccion = request.POST.get('direccion', '').strip()

        errores = []
        if not all([tipo_doc, documento, username, password, password_confirm, nombre, apellido, correo, telefono, direccion]):
            errores.append('Todos los campos obligatorios deben ser completados.')

        if password != password_confirm:
            errores.append('Las contraseñas no coinciden.')

        if len(password) < 8:
            errores.append('La contraseña debe tener al menos 8 caracteres.')

        if not USERNAME_RE.fullmatch(username):
            errores.append('El usuario debe tener 4 a 50 caracteres y solo usar letras, números, punto o guion bajo.')

        if not DOCUMENTO_RE.fullmatch(documento):
            errores.append('El documento debe tener entre 5 y 20 caracteres alfanuméricos, sin espacios.')

        if not NOMBRE_RE.fullmatch(nombre):
            errores.append('El nombre solo puede contener letras y espacios (2 a 40 caracteres).')

        if not NOMBRE_RE.fullmatch(apellido):
            errores.append('El apellido solo puede contener letras y espacios (2 a 40 caracteres).')

        if len(direccion) < 5 or len(direccion) > 100:
            errores.append('La dirección debe tener entre 5 y 100 caracteres.')

        if not TELEFONO_RE.fullmatch(telefono):
            errores.append('El teléfono debe tener exactamente 10 dígitos numéricos.')

        tipos_doc_validos = {op[0] for op in Usuario.TIPO_DOC_CHOICES}
        if tipo_doc not in tipos_doc_validos:
            errores.append('El tipo de documento seleccionado no es válido.')

        if Usuario.objects.filter(nombre_usuario=username).exists():
            errores.append(f'El nombre de usuario "{username}" ya está en uso.')

        if Usuario.objects.filter(documento=documento).exists():
            errores.append(f'El documento "{documento}" ya está registrado.')

        if Usuario.objects.filter(correo=correo).exists():
            errores.append(f'El correo "{correo}" ya está registrado.')

        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'cuentas/register.html', {'form_data': request.POST})

        try:
            rol_cliente = Rol.objects.filter(nombre_rol__icontains='cliente').first()
            if not rol_cliente:
                rol_cliente = Rol.objects.first()

            usuario = Usuario.objects.create(
                tipo_documento=tipo_doc,
                documento=documento,
                nombre_usuario=username,
                contrasena=hash_password(password),
                primer_nombre=nombre,
                apellido=apellido,
                correo=correo,
                telefono=telefono,
                direccion=direccion,
                puntos_acumulados=0,
                estado='activo',
                rol=rol_cliente,
            )

            request.session.cycle_key()
            request.session['usuario_id'] = usuario.pk
            request.session['usuario_nombre'] = f"{usuario.primer_nombre} {usuario.apellido}"
            request.session['usuario_username'] = usuario.nombre_usuario
            request.session['usuario_rol'] = rol_cliente.nombre_rol if rol_cliente else ''

            messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido, {nombre}.')
            return redirect('landing')

        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {e}')
            return render(request, 'cuentas/register.html', {'form_data': request.POST})

    return render(request, 'cuentas/register.html')


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Cerrar sesión."""
    request.session.flush()
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('landing')


def login_shori_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            from urllib.parse import quote
            return redirect(f'/login/?next={quote(request.get_full_path(), safe="/")}')

        if _session_expired(request):
            request.session.flush()
            messages.warning(request, 'Sesión cerrada por inactividad. Vuelve a ingresar.')
            from urllib.parse import quote
            return redirect(f'/login/?next={quote(request.get_full_path(), safe="/")}')

        usuario = _get_usuario_sesion(request)
        if usuario and _password_vencida(usuario) and not request.path.startswith(f'/mi-cuenta/{usuario.pk}'):
            messages.warning(request, 'Tu contraseña ya tiene más de 90 días. Actualízala para continuar.')
            return redirect('mi_cuenta', id=usuario.pk)

        _actualizar_actividad_sesion(request)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_shori_required(view_func):
    """Panel interno: sesión + rol admin/empleado/administrador."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            from urllib.parse import quote
            return redirect(f'/login/?next={quote(request.get_full_path(), safe="/")}')

        if _session_expired(request):
            request.session.flush()
            messages.warning(request, 'Sesión cerrada por inactividad. Vuelve a ingresar.')
            from urllib.parse import quote
            return redirect(f'/login/?next={quote(request.get_full_path(), safe="/")}')

        u = _get_usuario_sesion(request)
        if not u or not u.rol or not _es_rol_admin(u.rol.nombre_rol):
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('landing')

        _actualizar_actividad_sesion(request)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def super_admin_required(view_func):
    """Panel crítico: solo administradores."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            from urllib.parse import quote
            return redirect(f'/login/?next={quote(request.get_full_path(), safe="/")}')

        if _session_expired(request):
            request.session.flush()
            messages.warning(request, 'Sesión cerrada por inactividad. Vuelve a ingresar.')
            from urllib.parse import quote
            return redirect(f'/login/?next={quote(request.get_full_path(), safe="/")}')

        u = _get_usuario_sesion(request)
        if not u or not u.rol or u.rol.nombre_rol.strip().lower() != 'administrador':
            messages.error(request, 'Solo administradores pueden acceder a esta sección.')
            return redirect('landing')

        _actualizar_actividad_sesion(request)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_shori_required
@require_GET
def mis_pedidos(request):
    from pedido.models import Pedido
    usuario_id = request.session.get('usuario_id')
    pedidos = Pedido.objects.filter(usuario_id=usuario_id).order_by('-fecha_pedido')
    
    return render(request, 'cuentas/mis_pedidos.html', {
        'pedidos': pedidos,
        'usuario_logueado': _get_usuario_sesion(request),
    })

@login_shori_required
@require_GET
def detalle_pedido(request, pedido_id):
    from pedido.models import Pedido
    from detalle_pedido.models import DetallePedido
    from recibo.models import Recibo

    usuario_id = request.session.get('usuario_id')
    try:
        pedido = Pedido.objects.get(pk=pedido_id, usuario_id=usuario_id)
    except Pedido.DoesNotExist:
        messages.error(request, "El pedido no existe o no tienes permiso para verlo.")
        return redirect('mis_pedidos')

    detalles = DetallePedido.objects.filter(pedido=pedido).select_related("producto")
    recibo = Recibo.objects.filter(pedido=pedido).select_related("metodo_pago").first()

    return render(request, 'cuentas/detalle_pedido.html', {
        'pedido': pedido,
        'detalles': detalles,
        'recibo': recibo,
        'usuario_logueado': _get_usuario_sesion(request),
    })