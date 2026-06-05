import logging
from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from cuentas.views import admin_shori_required, login_shori_required
from detalle_pedido.models import DetallePedido
from metodo_pago.models import MetodoPago
from inventario.models import Inventario
from movimiento_inventario.models import MovimientoInventario
from receta.models import Receta
from recibo.models import Recibo
from usuario.models import Usuario
from producto.cart import Cart
from producto.horario_validator import HorarioComercialValidator
from producto.models import Producto

from .models import Pedido

logger = logging.getLogger(__name__)

UMBRAL_BONOS = Decimal("50000.00")
MINUTOS_ENTREGA_ESTIMADOS = 45
MAX_BONOS = 10
COSTO_REDENCION_BONOS = 5
DESCUENTO_REDENCION = Decimal("0.05")


@login_shori_required
@require_GET
def ver_checkout(request):
    """Muestra el resumen final antes de procesar la compra."""
    cart = Cart(request)
    if not request.session.get('cart') or len(request.session.get('cart')) == 0:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('landing')
    
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        usuario = Usuario.objects.get(pk=usuario_id)
        if Pedido.objects.filter(
            usuario=usuario, 
            estado_pedido__in=['pendiente', 'preparacion', 'listo']
        ).exists():
            messages.warning(
                request, 
                "Tienes un pedido activo. Completa o cancela ese pedido antes de hacer uno nuevo."
            )
            return redirect('mis_pedidos')
    
    return render(request, 'pedido/checkout.html', {'cart': cart})


@login_shori_required
@require_POST
def finalizar_compra(request):
    """Crea el pedido, detalles, recibo de pago y bonos según el total."""
    cart = Cart(request)
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para finalizar la compra.")
        return redirect('login')

    if request.method != 'POST':
        return redirect('ver_carrito')

    try:
        if not HorarioComercialValidator.es_dentro_horario():
            messages.error(
                request,
                HorarioComercialValidator.obtener_mensaje_fuera_horario()
            )
            return redirect("ver_carrito")

        if not cart.cart:
            messages.warning(request, "Tu carrito está vacío.")
            return redirect("ver_carrito")

        metodo = MetodoPago.objects.filter(
            esta_activo=True, nombre_metodo__iexact="Efectivo"
        ).first()
        if not metodo:
            messages.error(
                request,
                "No hay métodos de pago activos. Un administrador debe crear al menos uno.",
            )
            return redirect("ver_carrito")

        with transaction.atomic():
            usuario_instancia = Usuario.objects.get(pk=usuario_id)

            # Verificar que no tenga pedidos activos
            if Pedido.objects.filter(
                usuario=usuario_instancia, 
                estado_pedido__in=['pendiente', 'preparacion', 'listo']
            ).exists():
                messages.error(
                    request, 
                    "Ya tienes un pedido activo. No puedes realizar otro pedido hasta que el actual sea entregado o cancelado."
                )
                return redirect("ver_carrito")

            lineas = []
            total_decimal = Decimal("0")
            for key, value in cart.cart.items():
                producto = Producto.objects.get(pk=value["producto_id"])
                if not producto.esta_habilitado or not producto.esta_disponible:
                    messages.error(
                        request,
                        f"El producto «{producto.nombre_producto}» ya no está disponible. Vuelve al carrito y actualiza tu pedido.",
                    )
                    return redirect("ver_carrito")
                cantidad = int(value["cantidad"])
                if cantidad < 1 or cantidad > 500:
                    messages.error(request, "Cantidad no válida en el carrito.")
                    return redirect("ver_carrito")
                precio_ok = producto.precio_venta.quantize(Decimal("0.01"))
                precio_carrito = Decimal(str(value["precio"])).quantize(Decimal("0.01"))
                if precio_carrito != precio_ok:
                    messages.error(
                        request,
                        "Los precios de algunos productos cambiaron. Vuelve al carrito y actualiza tu pedido.",
                    )
                    return redirect("ver_carrito")
                lineas.append((producto, cantidad, precio_ok))
                total_decimal += precio_ok * cantidad

            total_decimal = total_decimal.quantize(Decimal("0.01"))

            # Validar stock de insumos antes de confirmar
            for producto, cantidad, _ in lineas:
                for receta in Receta.objects.filter(producto=producto).select_related('insumo'):
                    requerido = receta.cantidad_requerida * cantidad
                    if receta.insumo.stock_actual < requerido:
                        messages.error(
                            request,
                            f"No hay suficiente stock de '{receta.insumo.nombre_insumo}' para '{producto.nombre_producto}'. "
                            f"Disponible: {receta.insumo.stock_actual}, requerido: {requerido}."
                        )
                        return redirect("ver_carrito")

            ahora = timezone.now()
            fecha_estimada = ahora + timedelta(minutes=MINUTOS_ENTREGA_ESTIMADOS)

            # Redención: 5 bonos = 5% descuento
            quiere_redimir = request.POST.get("redimir_bonos") == "1"
            redimio = False
            descuento_bonos = Decimal("0")
            if quiere_redimir and usuario_instancia.bonos_fidelidad >= COSTO_REDENCION_BONOS:
                descuento_bonos = (total_decimal * DESCUENTO_REDENCION).quantize(Decimal("0.01"))
                total_decimal = (total_decimal - descuento_bonos).quantize(Decimal("0.01"))
                usuario_instancia.bonos_fidelidad -= COSTO_REDENCION_BONOS
                redimio = True

            pedido = Pedido.objects.create(
                usuario=usuario_instancia,
                tipo_pedido=request.POST.get("tipo_pedido", "domicilio"),
                direccion_pedido=request.POST.get(
                    "direccion_pedido", usuario_instancia.direccion
                ),
                estado_pedido="pendiente",
                total_pedido=total_decimal,
                fecha_entrega_estimada=fecha_estimada,
                usar_bonos=redimio,
                descuento_bonos=descuento_bonos,
            )

            for producto, cantidad, precio_ok in lineas:
                detalle = DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario_momento=str(precio_ok),
                )
                # Descontar inventario y registrar movimientos
                for receta in Receta.objects.filter(producto=producto).select_related('insumo'):
                    requerido = receta.cantidad_requerida * cantidad
                    receta.insumo.stock_actual -= requerido
                    receta.insumo.save(update_fields=['stock_actual'])
                    MovimientoInventario.objects.create(
                        insumo=receta.insumo,
                        usuario=usuario_instancia,
                        tipo_movimiento='salida_venta',
                        cantidad=requerido,
                        observaciones=f"Venta pedido #{pedido.id}, detalle #{detalle.id}",
                    )

            subtotal = (total_decimal / Decimal("1.19")).quantize(Decimal("0.01"))
            iva_total = (total_decimal - subtotal).quantize(Decimal("0.01"))

            bonos_ganados = 0
            if total_decimal >= UMBRAL_BONOS:
                bonos_ganados = 1
                if usuario_instancia.bonos_fidelidad < MAX_BONOS:
                    usuario_instancia.bonos_fidelidad = min(
                        usuario_instancia.bonos_fidelidad + 1, MAX_BONOS
                    )
            if redimio or bonos_ganados > 0:
                usuario_instancia.save(update_fields=["bonos_fidelidad"])

            Recibo.objects.create(
                pedido=pedido,
                metodo_pago=metodo,
                subtotal=subtotal,
                iva_total=iva_total,
                total_pagado=total_decimal,
                puntos_ganados=bonos_ganados,
            )

            cart.clear()

        logger.info("Pedido creado exitosamente", extra={'pedido_id': pedido.id, 'usuario_id': usuario_id})

        if bonos_ganados > 0:
            messages.success(
                request,
                f"¡Pago registrado! Tu compra de ${total_decimal:,.0f} sumó 1 bono. "
                f"Llevas {usuario_instancia.bonos_fidelidad} bonos. "
                f"Entrega estimada: {fecha_estimada.strftime('%d/%m/%Y %H:%M')}.",
            )
        else:
            if redimio:
                messages.success(
                    request,
                    f"¡Pago registrado! Se aplicó 5% de descuento y se descontaron {COSTO_REDENCION_BONOS} bonos. "
                    f"Te quedan {usuario_instancia.bonos_fidelidad} bonos. "
                    f"Entrega estimada: {fecha_estimada.strftime('%d/%m/%Y %H:%M')}.",
                )
                return redirect("mis_pedidos")
            messages.success(
                request,
                "¡Pago registrado! Pedido y recibo generados. "
                f"Entrega estimada: {fecha_estimada.strftime('%d/%m/%Y %H:%M')}.",
            )

        return redirect("mis_pedidos")

    except Exception:
        logger.exception("finalizar_compra")
        messages.error(
            request,
            "No se pudo completar el pago. Intenta de nuevo o contacta al local.",
        )
        return redirect("ver_carrito")


@admin_shori_required
@require_POST
def cambiar_estado(request, pedido_id):
    """Permite actualizar el estado del pedido."""
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado:
            if nuevo_estado == "entregado" and not pedido.fecha_entrega_real:
                pedido.fecha_entrega_real = timezone.now()
            pedido.estado_pedido = nuevo_estado
            if nuevo_estado == "cancelado":
                pedido.fecha_entrega_real = None
            pedido.save()
            messages.success(request, f"Estado del pedido #{pedido.pk} actualizado a {nuevo_estado}.")

    return redirect('lista_pedidos')


@admin_shori_required
@require_GET
def lista_pedidos(request):
    pedidos = list(Pedido.objects.select_related('usuario').all().order_by('-pk'))
    ahora = timezone.now()

    # Semáforo:
    # - verde: a tiempo
    # - amarillo: en riesgo (faltan <= 10 min o atraso <= 10 min)
    # - rojo: tarde (>10 min)
    for p in pedidos:
        p.semaforo = None
        p.semaforo_label = ""
        ref = p.fecha_entrega_real if p.estado_pedido == "entregado" else ahora
        if p.fecha_entrega_estimada:
            diff_min = (ref - p.fecha_entrega_estimada).total_seconds() / 60.0
            if p.estado_pedido in ("cancelado",):
                p.semaforo = "neutral"
                p.semaforo_label = "Cancelado"
            elif p.estado_pedido == "entregado":
                if diff_min <= 10:
                    p.semaforo = "success"
                    p.semaforo_label = "A tiempo"
                else:
                    p.semaforo = "danger"
                    p.semaforo_label = "Con demora"
            else:
                # aún no entregado: si ya se pasó, está tarde; si falta poco, en riesgo
                if diff_min > 10:
                    p.semaforo = "danger"
                    p.semaforo_label = "Tarde"
                elif diff_min >= 0:
                    p.semaforo = "warning"
                    p.semaforo_label = "En riesgo"
                else:
                    # falta tiempo (diff_min negativo)
                    faltan = abs(diff_min)
                    if faltan <= 10:
                        p.semaforo = "warning"
                        p.semaforo_label = "En riesgo"
                    else:
                        p.semaforo = "success"
                        p.semaforo_label = "A tiempo"
    return render(request, 'pedido/lista_pedidos.html', {'pedidos': pedidos})


@admin_shori_required
@require_http_methods(["GET", "POST"])
def crear_pedido(request):
    usuarios = Usuario.objects.all()
    if request.method == 'POST':
        usuario_id = request.POST['id_usuario']
        usuario_instancia = Usuario.objects.get(pk=usuario_id)
        total = Decimal(request.POST.get('total_pedido', '0'))

        Pedido.objects.create(
            usuario=usuario_instancia,
            tipo_pedido=request.POST['tipo_pedido'],
            direccion_pedido=request.POST.get('direccion_pedido', ''),
            estado_pedido=request.POST.get('estado_pedido', 'pendiente'),
            total_pedido=total
        )

        messages.success(
            request,
            "Pedido creado. El recibo y los bonos se registran al generar el pago (recibo).",
        )

        return redirect('lista_pedidos')
    return render(request, 'pedido/form_pedido.html', {'usuarios': usuarios})


@admin_shori_required
@require_http_methods(["GET", "POST"])
def editar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    usuarios = Usuario.objects.all()

    if request.method == 'POST':
        usuario_id = request.POST['id_usuario']
        pedido.usuario = Usuario.objects.get(pk=usuario_id)
        pedido.tipo_pedido = request.POST['tipo_pedido']
        pedido.direccion_pedido = request.POST.get('direccion_pedido', '')
        pedido.estado_pedido = request.POST['estado_pedido']
        pedido.total_pedido = request.POST['total_pedido']
        pedido.save()
        messages.success(request, f"Pedido #{pedido.pk} actualizado.")
        return redirect('lista_pedidos')

    return render(request, 'pedido/form_pedido.html', {
        'pedido': pedido,
        'usuarios': usuarios
    })


@admin_shori_required
@require_http_methods(["GET", "POST"])
def eliminar_pedido(request, id):
    pedido = get_object_or_404(Pedido, pk=id)
    if request.method == 'POST':
        pedido.delete()
        messages.success(request, "Pedido eliminado.")
        return redirect('lista_pedidos')
    return render(request, 'pedido/eliminar_pedido.html', {'pedido': pedido})


@admin_shori_required
@require_GET
def descargar_pedidos_pdf(request):
    pedidos = Pedido.objects.select_related('usuario').all().order_by('-pk')
    context = {
        "pedidos": pedidos,
        "fecha_generacion": timezone.now(),
    }
    try:
        from xhtml2pdf import pisa
        import io

        html_string = render_to_string("pedido/reporte_pedidos_pdf.html", context)
        result = io.BytesIO()
        pdf = pisa.CreatePDF(io.BytesIO(html_string.encode("utf-8")), dest=result, encoding="utf-8")
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="reporte_pedidos.pdf"'
            return response
        messages.warning(
            request,
            "No se pudo generar el PDF (error del motor). Se muestra la vista previa en pantalla.",
        )
    except ImportError:
        messages.warning(
            request,
            "El paquete xhtml2pdf no está instalado. Se muestra la vista previa; instálalo para descargar PDF.",
        )

    return render(request, "pedido/reporte_pedidos_pdf.html", context)
