from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from decimal import Decimal

from cuentas.views import admin_shori_required
from .models import Producto
from .cart import Cart
from .horario_validator import HorarioComercialValidator
from receta.models import Receta


def _max_unidades_por_inventario(producto):
    recetas = Receta.objects.select_related("insumo").filter(producto=producto)
    if not recetas.exists():
        return None
    maximos = []
    for r in recetas:
        if r.cantidad_requerida is None or r.cantidad_requerida <= 0:
            continue
        if r.insumo.stock_actual is None or r.insumo.stock_actual <= 0:
            return 0
        maximos.append(int(Decimal(r.insumo.stock_actual) // Decimal(r.cantidad_requerida)))
    if not maximos:
        return None
    return max(0, min(maximos))


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
        messages.error(
            request,
            HorarioComercialValidator.obtener_mensaje_fuera_horario()
        )
        return redirect('ver_carrito')
    
    cart = Cart(request)
    producto = get_object_or_404(Producto, pk=producto_id)

    if not producto.esta_habilitado or not producto.esta_disponible:
        messages.error(request, f"❌ {producto.nombre_producto} no está disponible actualmente.")
        return redirect('landing')

    actual = int(cart.cart.get(str(producto.pk), {}).get("cantidad", 0))
    max_disponible = _max_unidades_por_inventario(producto)
    if max_disponible is not None and (actual + 1) > max_disponible:
        if max_disponible <= 0:
            messages.error(request, f"❌ Sin stock disponible para {producto.nombre_producto}.")
        else:
            messages.warning(request, f"⚠️ No puedes agregar más de {max_disponible} unidad(es) de {producto.nombre_producto}.")
        return redirect('ver_carrito')

    cart.add(producto=producto)
    messages.success(request, f"✓ ¡{producto.nombre_producto} agregado al carrito!")
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect('landing')


@require_POST
def eliminar_item(request, producto_id):
    cart = Cart(request)
    producto = get_object_or_404(Producto, pk=producto_id)
    cart.remove(producto)
    return redirect('ver_carrito')


@require_POST
def restar_producto(request, producto_id):
    cart = Cart(request)
    producto = get_object_or_404(Producto, pk=producto_id)
    if int(cart.cart.get(str(producto.pk), {}).get("cantidad", 0)) <= 0:
        messages.warning(request, "No puedes restar una cantidad inexistente.")
        return redirect('ver_carrito')
    cart.decrement(producto)
    return redirect('ver_carrito')


@require_POST
def limpiar_carrito(request):
    cart = Cart(request)
    cart.clear()
    messages.info(request, "Carrito vaciado.")
    return redirect('ver_carrito')


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
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        precio = request.POST.get('precio')
        imagen = request.FILES.get('imagen')

        producto = Producto.objects.create(
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

        crear_receta_despues = request.POST.get('crear_receta_despues')
        if crear_receta_despues:
            messages.success(request, f"Producto '{nombre}' creado. Asigna los ingredientes.")
            return redirect(f"/recetas/crear/?producto_id={producto.pk}")

        messages.success(request, f"Producto '{nombre}' creado exitosamente.")
        return redirect('lista_productos')

    return render(request, 'producto/form_producto.html', {'from_receta': from_receta})


@admin_shori_required
@require_http_methods(["GET", "POST"])
def editar_producto(request, id):
    producto = get_object_or_404(Producto, pk=id)

    if request.method == 'POST':
        producto.nombre_producto = request.POST.get('nombre')
        producto.descripcion_producto = request.POST.get('descripcion', '')
        producto.precio_venta = request.POST.get('precio')
        producto.registro_movimiento_inicial = request.POST.get(
            'registro_movimiento_inicial', ''
        ).strip() or None
        producto.imagen_catalogo = (request.POST.get("imagen_catalogo") or "").strip()

        nueva_imagen = request.FILES.get('imagen')
        if nueva_imagen:
            producto.imagen = nueva_imagen

        producto.save()
        messages.success(request, f"Producto '{producto.nombre_producto}' actualizado.")
        return redirect('lista_productos')

    return render(request, 'producto/form_producto.html', {'producto': producto})


@admin_shori_required
@require_http_methods(["GET", "POST"])
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, pk=id)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, "Producto eliminado.")
        return redirect('lista_productos')
    return render(request, 'producto/eliminar_producto.html', {'producto': producto})
