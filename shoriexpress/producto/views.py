from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from decimal import Decimal

from cuentas.delete_utils import eliminar_con_mensaje
from cuentas.views import admin_shori_required
from .models import Producto
from .cart import Cart
from .cart_helpers import cart_action_response, wants_json, cart_payload
from .horario_validator import HorarioComercialValidator
from receta.models import Receta
from .stock_utils import max_unidades_por_inventario, mensaje_stock_limitado
from .validators import validar_producto_unico


def _max_unidades_por_inventario(producto):
    return max_unidades_por_inventario(producto)


def _contexto_form_producto(request, *, producto=None, from_receta='', form_error=''):
    """Conserva los datos del formulario y el error visible si falla el guardado."""
    usar_post = request.method == 'POST'
    form_values = {
        'nombre_producto': (
            (request.POST.get('nombre') or '').strip()
            if usar_post
            else getattr(producto, 'nombre_producto', '') or ''
        ),
        'descripcion_producto': (
            (request.POST.get('descripcion') or '').strip()
            if usar_post
            else getattr(producto, 'descripcion_producto', '') or ''
        ),
        'precio_venta': (
            request.POST.get('precio', '')
            if usar_post
            else getattr(producto, 'precio_venta', '') or ''
        ),
        'registro_movimiento_inicial': (
            (request.POST.get('registro_movimiento_inicial') or '').strip()
            if usar_post
            else getattr(producto, 'registro_movimiento_inicial', '') or ''
        ),
        'imagen_catalogo': (
            (request.POST.get('imagen_catalogo') or '').strip()
            if usar_post
            else getattr(producto, 'imagen_catalogo', '') or ''
        ),
        'crear_receta_despues': (
            request.POST.get('crear_receta_despues') == '1'
            if usar_post
            else bool(from_receta)
        ),
    }
    return {
        'producto': producto,
        'from_receta': from_receta,
        'form_values': form_values,
        'form_error': form_error,
        'error_en_nombre': bool(
            form_error and 'nombre' in form_error.lower()
        ),
    }


def _render_form_producto_con_error(request, *, producto=None, from_receta='', mensaje=''):
    messages.error(request, mensaje)
    return render(
        request,
        'producto/form_producto.html',
        _contexto_form_producto(
            request,
            producto=producto,
            from_receta=from_receta,
            form_error=mensaje,
        ),
    )


@require_GET
def api_configuracion_horario(request):
    """
    API endpoint para obtener configuración de horario comercial
    Útil para validación en frontend sin recargar la página
    """
    try:
        config_horario = HorarioComercialValidator.obtener_config_horario()
        return JsonResponse({
            'success': True,
            'data': config_horario
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["GET", "POST"])
def agregar_item(request, producto_id):
    """
    Agrega un producto al carrito con validación de horario
    """
    # Validar horario comercial
    if not HorarioComercialValidator.es_dentro_horario():
        msg = HorarioComercialValidator.obtener_mensaje_fuera_horario()
        if wants_json(request):
            return cart_action_response(request, message=msg, message_type='error', redirect_name='ver_carrito')
        messages.error(request, msg)
        return redirect('ver_carrito')
    
    cart = Cart(request)
    producto = get_object_or_404(Producto, pk=producto_id)

    if not producto.esta_habilitado or not producto.esta_disponible:
        msg = f"❌ {producto.nombre_producto} no está disponible actualmente."
        if wants_json(request):
            return cart_action_response(request, message=msg, message_type='error', redirect_name='landing')
        messages.error(request, msg)
        return redirect('landing')

    actual = int(cart.cart.get(str(producto.pk), {}).get("cantidad", 0))
    max_disponible = _max_unidades_por_inventario(producto)
    if max_disponible is not None and max_disponible <= 0:
        msg = mensaje_stock_limitado(producto, max_disponible)
        return cart_action_response(request, message=msg, message_type='error')

    if max_disponible is not None and (actual + 1) > max_disponible:
        msg = mensaje_stock_limitado(producto, max_disponible)
        if actual > 0:
            msg += " Ya tienes unidades en el carrito; ajusta la cantidad manualmente."
        return cart_action_response(request, message=msg, message_type='warning', redirect_name='ver_carrito')

    cart.add(producto=producto)
    msg = f"✓ ¡{producto.nombre_producto} agregado al carrito!"
    if max_disponible is not None and max_disponible <= 5:
        msg += f" Stock disponible: {max_disponible} unidad(es)."
    if wants_json(request):
        return cart_action_response(request, message=msg, message_type='success')

    messages.success(request, msg)
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect('landing')


@require_http_methods(["GET", "POST"])
def eliminar_item(request, producto_id):
    cart = Cart(request)
    producto = get_object_or_404(Producto, pk=producto_id)
    cart.remove(producto)
    return cart_action_response(
        request,
        message=f"✓ {producto.nombre_producto} eliminado del carrito.",
        message_type='success',
    )


@require_http_methods(["GET", "POST"])
def restar_producto(request, producto_id):
    cart = Cart(request)
    producto = get_object_or_404(Producto, pk=producto_id)
    if int(cart.cart.get(str(producto.pk), {}).get("cantidad", 0)) <= 0:
        return cart_action_response(
            request,
            message="No puedes restar una cantidad inexistente.",
            message_type='warning',
        )
    cart.decrement(producto)
    return cart_action_response(
        request,
        message=f"Cantidad de {producto.nombre_producto} actualizada.",
        message_type='info',
    )


@require_http_methods(["GET", "POST"])
def set_cantidad_carrito(request, producto_id):
    """Establece la cantidad manualmente desde el carrito."""
    raw = request.POST.get('cantidad') if request.method == 'POST' else request.GET.get('cantidad')
    try:
        cantidad = int(raw)
    except (TypeError, ValueError):
        return cart_action_response(
            request,
            message='Ingresa una cantidad válida (número entero).',
            message_type='error',
        )

    if cantidad < 0:
        return cart_action_response(
            request,
            message='La cantidad no puede ser negativa.',
            message_type='error',
        )

    cart = Cart(request)
    producto = get_object_or_404(Producto, pk=producto_id)

    if cantidad == 0:
        cart.remove(producto)
        return cart_action_response(
            request,
            message=f"✓ {producto.nombre_producto} eliminado del carrito.",
            message_type='success',
        )

    if not producto.esta_habilitado or not producto.esta_disponible:
        return cart_action_response(
            request,
            message=f"❌ {producto.nombre_producto} no está disponible actualmente.",
            message_type='error',
        )

    max_disponible = _max_unidades_por_inventario(producto)
    if max_disponible is not None and cantidad > max_disponible:
        msg = (
            f"Solo hay {max_disponible} unidad(es) disponible(s) de {producto.nombre_producto}. "
            "Indica una cantidad menor o igual en el carrito."
        )
        return cart_action_response(request, message=msg, message_type='error')

    cart.set_quantity(producto, cantidad)
    msg = f"Cantidad de {producto.nombre_producto} actualizada a {cantidad}."
    return cart_action_response(request, message=msg, message_type='success')


@require_http_methods(["GET", "POST"])
def limpiar_carrito(request):
    cart = Cart(request)
    cart.clear()
    return cart_action_response(
        request,
        message="Carrito vaciado.",
        message_type='info',
    )


@require_GET
def index(request):
    productos = Producto.objects.filter(esta_disponible=True, esta_habilitado=True)
    return render(request, 'index.html', {'productos': productos})


@admin_shori_required
@require_GET
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'producto/lista_productos.html', {'productos': productos})


@admin_shori_required
@require_POST
def toggle_disponible(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    producto.esta_disponible = not producto.esta_disponible
    producto.save(update_fields=['esta_disponible'])
    messages.success(request, f"Producto '{producto.nombre_producto}' {'habilitado' if producto.esta_disponible else 'inhabilitado'}.")
    return redirect('lista_productos')


@admin_shori_required
@require_POST
def toggle_habilitado(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    producto.esta_habilitado = not producto.esta_habilitado
    producto.save(update_fields=['esta_habilitado'])
    messages.success(
        request,
        f"Producto '{producto.nombre_producto}' {'ahora se muestra en la página' if producto.esta_habilitado else 'ya no se muestra en la página'}."
    )
    return redirect('lista_productos')


@admin_shori_required
@require_http_methods(["GET", "POST"])
def crear_producto(request):
    from_receta = request.GET.get('from_receta', '')

    if request.method == 'POST':
        nombre = (request.POST.get('nombre') or '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()
        precio = request.POST.get('precio')
        imagen = request.FILES.get('imagen')

        if not nombre or len(nombre) < 3:
            return _render_form_producto_con_error(
                request,
                from_receta=from_receta,
                mensaje='El nombre del producto debe tener al menos 3 caracteres.',
            )

        try:
            validar_producto_unico(nombre)
        except ValidationError as exc:
            return _render_form_producto_con_error(
                request,
                from_receta=from_receta,
                mensaje=exc.messages[0],
            )

        try:
            producto = Producto(
                nombre_producto=nombre,
                descripcion_producto=descripcion,
                precio_venta=precio,
                imagen=imagen,
                imagen_catalogo=(request.POST.get("imagen_catalogo") or "").strip(),
                registro_movimiento_inicial=request.POST.get(
                    "registro_movimiento_inicial", ""
                ).strip()
                or None,
            )
            producto.full_clean()
            producto.save()
        except ValidationError as exc:
            msg = exc.messages[0] if getattr(exc, 'messages', None) else str(exc)
            return _render_form_producto_con_error(
                request,
                from_receta=from_receta,
                mensaje=msg,
            )
        except Exception as exc:
            return _render_form_producto_con_error(
                request,
                from_receta=from_receta,
                mensaje=f'No se pudo guardar el producto: {exc}',
            )

        crear_receta_despues = request.POST.get('crear_receta_despues')
        if crear_receta_despues:
            messages.success(request, f"Producto '{nombre}' creado. Asigna los ingredientes.")
            return redirect(f"/recetas/crear/?producto_id={producto.pk}")

        messages.success(request, f"Producto '{nombre}' creado exitosamente.")
        return redirect('lista_productos')

    return render(
        request,
        'producto/form_producto.html',
        _contexto_form_producto(request, from_receta=from_receta),
    )


@admin_shori_required
@require_http_methods(["GET", "POST"])
def editar_producto(request, id):
    producto = get_object_or_404(Producto, pk=id)

    if request.method == 'POST':
        nombre = (request.POST.get('nombre') or '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()

        try:
            validar_producto_unico(nombre, excluir_pk=producto.pk)
        except ValidationError as exc:
            return _render_form_producto_con_error(
                request,
                producto=producto,
                mensaje=exc.messages[0],
            )

        producto.nombre_producto = nombre
        producto.descripcion_producto = descripcion
        producto.precio_venta = request.POST.get('precio')
        producto.registro_movimiento_inicial = request.POST.get(
            'registro_movimiento_inicial', ''
        ).strip() or None
        producto.imagen_catalogo = (request.POST.get("imagen_catalogo") or "").strip()

        nueva_imagen = request.FILES.get('imagen')
        if nueva_imagen:
            producto.imagen = nueva_imagen

        try:
            producto.full_clean()
            producto.save()
        except ValidationError as exc:
            msg = exc.messages[0] if getattr(exc, 'messages', None) else str(exc)
            return _render_form_producto_con_error(
                request,
                producto=producto,
                mensaje=msg,
            )

        messages.success(request, f"Producto '{producto.nombre_producto}' actualizado.")
        return redirect('lista_productos')

    return render(
        request,
        'producto/form_producto.html',
        _contexto_form_producto(request, producto=producto),
    )


@admin_shori_required
@require_http_methods(["GET", "POST"])
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, pk=id)
    if request.method == 'POST':
        nombre = producto.nombre_producto
        response = eliminar_con_mensaje(
            request,
            producto,
            mensaje_ok=f"Producto '{nombre}' eliminado.",
            url_redirect='lista_productos',
            mensaje_error=(
                "No se puede eliminar el producto porque tiene pedidos, recetas u otros registros asociados."
            ),
        )
        return response
    return render(request, 'producto/eliminar_producto.html', {'producto': producto})
