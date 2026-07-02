from decimal import Decimal

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import DecimalField, F, Sum
from django.db.models import Value as V

from cuentas.delete_utils import eliminar_con_mensaje
from cuentas.views import super_admin_required
from detalle_pedido.models import DetallePedido
from metodo_pago.models import MetodoPago
from pedido.models import Pedido
from dashboard.models import ConfiguracionSistema

from .models import Recibo
from .services import calcular_totales_desde_pedido, generar_recibo_si_aplica, sincronizar_recibo_con_pedido


@super_admin_required
@require_GET
def lista_recibos(request):
    """Lista todos los recibos/facturas con búsqueda y filtros"""
    recibos = Recibo.objects.select_related('pedido', 'metodo_pago', 'pedido__usuario').all().order_by('-fecha_emision')
    return render(request, 'recibo/lista_recibos.html', {'recibos': recibos})


@super_admin_required
def detalle_recibo(request, id):
    """Vista detallada de una factura en formato card profesional"""
    recibo = get_object_or_404(
        Recibo.objects.select_related('pedido', 'metodo_pago', 'pedido__usuario'),
        pk=id
    )
    
    detalles = DetallePedido.objects.filter(
        pedido=recibo.pedido
    ).select_related('producto')
    
    config = ConfiguracionSistema.get_config()
    
    context = {
        'recibo': recibo,
        'pedido': recibo.pedido,
        'cliente': recibo.pedido.usuario,
        'vendedor': recibo.pedido.usuario,
        'metodo_pago': recibo.metodo_pago,
        'detalles': detalles,
        'config': config,
    }
    
    return render(request, 'recibo/detalle_recibo.html', context)


@super_admin_required
@require_http_methods(["GET", "POST"])
def crear_recibo(request):
    """Genera recibo automático: solo elige pedido y método de pago."""
    pedidos = Pedido.objects.filter(recibo__isnull=True).prefetch_related('detalles').order_by("-pk")
    metodos = MetodoPago.objects.filter(esta_activo=True)
    config = ConfiguracionSistema.get_config()

    pedidos_con_totales = []
    for pedido in pedidos:
        if pedido.detalles.exists():
            subtotal, iva, total = calcular_totales_desde_pedido(pedido)
        else:
            subtotal = iva = Decimal("0")
            total = Decimal(str(pedido.total_pedido or 0))
        pedidos_con_totales.append({
            "pedido": pedido,
            "subtotal": subtotal,
            "iva": iva,
            "total": total,
        })

    if request.method == 'POST':
        ped_id = request.POST.get('id_pedido')
        met_id = request.POST.get('id_metodo_pago')
        confirmacion_manual = request.POST.get('confirmacion_manual') == '1'

        if not ped_id or not met_id:
            messages.error(request, "Debe seleccionar un pedido y método de pago.")
            return render(request, 'recibo/form_recibo.html', {
                'pedidos_con_totales': pedidos_con_totales,
                'metodos': metodos,
                'config': config,
                'modo_automatico': True,
                'es_recibo_manual': True,
            })

        if not confirmacion_manual:
            messages.warning(
                request,
                "Debes confirmar que entiendes que crear un recibo manual es un caso excepcional.",
            )
            return render(request, 'recibo/form_recibo.html', {
                'pedidos_con_totales': pedidos_con_totales,
                'metodos': metodos,
                'config': config,
                'modo_automatico': True,
                'es_recibo_manual': True,
                'pedido_preseleccionado': ped_id,
                'metodo_preseleccionado': met_id,
            })

        if Recibo.objects.filter(pedido_id=ped_id).exists():
            messages.error(request, "Ese pedido ya tiene un recibo. Edita el existente o elige otro pedido.")
            return render(request, 'recibo/form_recibo.html', {
                'pedidos_con_totales': pedidos_con_totales,
                'metodos': metodos,
                'config': config,
                'modo_automatico': True,
                'es_recibo_manual': True,
            })

        pedido = Pedido.objects.prefetch_related('detalles').get(pk=ped_id)
        metodo = MetodoPago.objects.get(pk=met_id)

        if not pedido.detalles.exists():
            messages.error(
                request,
                "El pedido no tiene productos en el detalle. Agrega líneas al pedido primero.",
            )
            return render(request, 'recibo/form_recibo.html', {
                'pedidos_con_totales': pedidos_con_totales,
                'metodos': metodos,
                'config': config,
                'modo_automatico': True,
                'es_recibo_manual': True,
            })

        subtotal, iva_total, total = calcular_totales_desde_pedido(pedido)
        recibo, _ = generar_recibo_si_aplica(pedido, metodo_pago=metodo)
        if not recibo:
            recibo = Recibo.objects.create(
                pedido=pedido,
                metodo_pago=metodo,
                subtotal=subtotal,
                iva_total=iva_total,
                total_pagado=total,
                puntos_ganados=0,
            )
        else:
            recibo.metodo_pago = metodo
            recibo.subtotal = subtotal
            recibo.iva_total = iva_total
            recibo.total_pagado = total
            recibo.save(update_fields=['metodo_pago', 'subtotal', 'iva_total', 'total_pagado'])

        from pedido.bonos import otorgar_bono_si_aplica
        bonos = otorgar_bono_si_aplica(recibo.pedido)

        messages.warning(
            request,
            "⚠️ Recibo registrado de forma manual. Lo habitual es que el sistema lo genere "
            "al finalizar la compra del cliente o al agregar productos al detalle del pedido.",
        )
        if bonos > 0:
            usuario = recibo.pedido.usuario
            messages.success(
                request,
                f"✓ Recibo #{recibo.id} creado manualmente. "
                f"Cliente ganó {bonos} bono(s) (Total: {usuario.bonos_fidelidad} bonos)."
            )
        else:
            messages.success(
                request,
                f"✓ Recibo #{recibo.id} creado manualmente con totales del pedido.",
            )

        return redirect('detalle_recibo', id=recibo.id)

    if not pedidos_con_totales:
        messages.info(
            request,
            "No hay pedidos pendientes de recibo. El sistema ya generó los recibos automáticamente.",
        )

    return render(request, 'recibo/form_recibo.html', {
        'pedidos_con_totales': pedidos_con_totales,
        'metodos': metodos,
        'config': config,
        'modo_automatico': True,
        'es_recibo_manual': True,
    })


@super_admin_required
@require_http_methods(["GET", "POST"])
def editar_recibo(request, id):
    """Edita un recibo existente"""
    recibo = get_object_or_404(Recibo, pk=id)
    pedidos = Pedido.objects.all()
    metodos = MetodoPago.objects.all()
    config = ConfiguracionSistema.get_config()

    if request.method == 'POST':
        ped_id = request.POST.get('id_pedido')
        met_id = request.POST.get('id_metodo_pago')

        otro = Recibo.objects.filter(pedido_id=ped_id).exclude(pk=recibo.pk).exists()
        if otro:
            messages.error(request, "Ya existe un recibo para ese pedido.")
            return render(request, 'recibo/form_recibo.html', {
                'recibo': recibo,
                'pedidos': pedidos,
                'metodos': metodos
            })

        recibo.pedido = Pedido.objects.get(pk=ped_id)
        recibo.metodo_pago = MetodoPago.objects.get(pk=met_id)
        subtotal, iva_total, total = calcular_totales_desde_pedido(recibo.pedido)
        recibo.subtotal = subtotal
        recibo.iva_total = iva_total
        recibo.total_pagado = total
        nuevo_bonos = int(request.POST.get('puntos_ganados', 0) or 0)
        anterior_bonos = recibo.puntos_ganados
        recibo.puntos_ganados = nuevo_bonos
        recibo.save()
        
        delta = nuevo_bonos - anterior_bonos
        if delta != 0:
            u = recibo.pedido.usuario
            u.bonos_fidelidad = max(0, int(u.bonos_fidelidad) + delta)
            u.save(update_fields=['bonos_fidelidad'])
        
        messages.success(request, f"✓ Recibo #{recibo.id} actualizado correctamente.")
        return redirect('detalle_recibo', id=recibo.id)

    return render(request, 'recibo/form_recibo.html', {
        'recibo': recibo,
        'pedidos': pedidos,
        'metodos': metodos,
        'config': config,
    })


@super_admin_required
@require_http_methods(["GET", "POST"])
def eliminar_recibo(request, id):
    """Elimina un recibo (operación crítica)"""
    recibo = get_object_or_404(Recibo, pk=id)
    if request.method == 'POST':
        recibo_id = recibo.id
        return eliminar_con_mensaje(
            request,
            recibo,
            mensaje_ok=f"✓ Recibo #{recibo_id} eliminado correctamente.",
            url_redirect='lista_recibos',
            mensaje_error="No se puede eliminar el recibo porque tiene registros relacionados.",
        )
    return render(request, 'recibo/eliminar_recibo.html', {'recibo': recibo})


@super_admin_required
@require_GET
def descargar_factura_pdf(request, id):
    """Descarga factura en PDF"""
    recibo = get_object_or_404(
        Recibo.objects.select_related('pedido', 'metodo_pago', 'pedido__usuario'),
        pk=id
    )

    detalles = DetallePedido.objects.filter(
        pedido=recibo.pedido
    ).select_related('producto')

    cliente = recibo.pedido.usuario
    config = ConfiguracionSistema.get_config()

    items = []
    for detalle in detalles:
        subtotal_item = detalle.cantidad * detalle.precio_unitario_momento
        items.append({
            'producto': detalle.producto.nombre_producto,
            'descripcion': detalle.producto.descripcion_producto or '',
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.precio_unitario_momento,
            'subtotal': subtotal_item,
            'stock_remanente': detalle.stock_remanente_post_venta,
        })

    context = {
        'recibo': recibo,
        'cliente': cliente,
        'pedido': recibo.pedido,
        'metodo_pago': recibo.metodo_pago,
        'items': items,
        'config': config,
    }

    try:
        from xhtml2pdf import pisa
        import io

        html_string = render_to_string('recibo/factura_pdf.html', context)
        result = io.BytesIO()
        pdf = pisa.CreatePDF(io.BytesIO(html_string.encode('utf-8')), dest=result, encoding='utf-8')

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Factura_{recibo.pk}.pdf"'
            return response
        messages.warning(
            request,
            'No se pudo generar el PDF de la factura. Se muestra la vista previa.',
        )
    except ImportError:
        messages.warning(request, "Librería xhtml2pdf no disponible. Mostrando vista HTML.")

    return render(request, 'recibo/factura_pdf.html', context)


@super_admin_required
@require_GET
def descargar_reporte_recibos_pdf(request):
    """Descarga reporte general de recibos en PDF"""
    recibos = Recibo.objects.select_related('pedido', 'metodo_pago', 'pedido__usuario').all().order_by('-id')
    config = ConfiguracionSistema.get_config()
    
    context = {
        'recibos': recibos,
        'fecha_generacion': timezone.now(),
        'config': config,
    }
    try:
        from xhtml2pdf import pisa
        import io

        html_string = render_to_string('recibo/reporte_recibos_pdf.html', context)
        result = io.BytesIO()
        pdf = pisa.CreatePDF(io.BytesIO(html_string.encode('utf-8')), dest=result, encoding='utf-8')
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="reporte_recibos.pdf"'
            return response
        messages.warning(
            request,
            'No se pudo generar el PDF del reporte. Se muestra la vista previa.',
        )
    except ImportError:
        messages.warning(request, "Librería xhtml2pdf no disponible. Mostrando vista HTML.")

    return render(request, 'recibo/reporte_recibos_pdf.html', context)

