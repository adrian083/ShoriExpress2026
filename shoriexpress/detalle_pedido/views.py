from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal, InvalidOperation

from cuentas.views import super_admin_required
from pedido.models import Pedido
from producto.models import Producto
from usuario.models import Usuario

from .models import DetallePedido


@super_admin_required
def lista_detalles(request):
    """
    Lista todos los detalles de pedido con opción de filtrado por:
    - Estado del pedido (pendiente, preparacion, listo, entregado, cancelado)
    - Disponibilidad del producto (disponible, no_disponible)
    
    Parámetros GET:
        - estado_pedido: estado del pedido a filtrar
        - disponibilidad: 'disponible' o 'no_disponible'
    """
    detalles = DetallePedido.objects.select_related(
        'pedido', 
        'pedido__usuario',
        'producto'
    ).all()
    
    # ===== FILTRO 1: Estado del Pedido =====
    estado_pedido = request.GET.get('estado_pedido', '').strip()
    estados_validos = {estado[0]: estado[1] for estado in Pedido.ESTADOS_PEDIDO}
    
    if estado_pedido and estado_pedido in estados_validos:
        detalles = detalles.filter(pedido__estado_pedido=estado_pedido)
    
    # ===== FILTRO 2: Disponibilidad del Producto =====
    disponibilidad = request.GET.get('disponibilidad', '').strip()
    
    if disponibilidad == 'disponible':
        detalles = detalles.filter(producto__esta_disponible=True)
    elif disponibilidad == 'no_disponible':
        detalles = detalles.filter(producto__esta_disponible=False)
    
    # Ordenamiento por fecha más reciente
    detalles = detalles.order_by('-pedido__fecha_pedido')
    
    # Contexto para la plantilla
    context = {
        'detalles': detalles,
        'estados_disponibles': Pedido.ESTADOS_PEDIDO,
        'filtro_estado': estado_pedido,
        'filtro_disponibilidad': disponibilidad,
        'contador_detalles': detalles.count(),
    }
    
    return render(request, 'detalle_pedido/lista_detalles_cards.html', context)


@super_admin_required
def crear_detalle(request):
    from inventario.services import InventoryService
    
    pedidos = Pedido.objects.all()
    productos = Producto.objects.all()

    if request.method == 'POST':
        ped_id = request.POST['id_pedido']
        prod_id = request.POST['id_producto']
        try:
            cantidad = int(str(request.POST.get('cantidad', '0')).strip())
            precio = Decimal(str(request.POST.get('precio', '0')).strip())
            
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor que 0.")
            if precio < 0:
                raise ValueError("El precio no puede ser negativo.")
            
            pedido = Pedido.objects.get(pk=ped_id)
            producto = Producto.objects.get(pk=prod_id)
            
            # Validar horario comercial
            dentro_horario, mensaje_horario = InventoryService.check_business_hours()
            if not dentro_horario:
                messages.error(request, f"No se puede realizar la venta: {mensaje_horario}")
                return render(request, 'detalle_pedido/form_detalle.html', {
                    'pedidos': pedidos,
                    'productos': productos
                })
            
            # Validar disponibilidad del producto
            puede_venderse, errores = Producto.objects.validar_venta(producto, cantidad)
            if not puede_venderse:
                error_msg = "No se puede vender el producto: "
                if 'horario' in errores:
                    error_msg += errores['horario']
                if 'ingredientes' in errores:
                    error_msg += "Ingredientes insuficientes: " + ", ".join([
                        f"{ing['insumo']} (necesita {ing['stock_necesario']}, tiene {ing['stock_actual']})"
                        for ing in errores['ingredientes']
                    ])
                if 'stock_insuficiente' in errores:
                    error_msg += "Stock insuficiente para la cantidad solicitada."
                
                messages.error(request, error_msg)
                return render(request, 'detalle_pedido/form_detalle.html', {
                    'pedidos': pedidos,
                    'productos': productos
                })
            
            uid = request.session.get("usuario_id")
            usuario_mov = pedido.usuario
            if uid:
                try:
                    usuario_mov = Usuario.objects.get(pk=uid)
                except Usuario.DoesNotExist:
                    pass

            resultado_descuento = InventoryService.deduct_inventory_by_recipe(
                producto, cantidad, registrar_movimiento=True, usuario=usuario_mov
            )

            detalles_desc = resultado_descuento.get("detalles_descuento") or []
            stock_snap = None
            if detalles_desc:
                try:
                    stock_snap = max(0, int(float(detalles_desc[0]["stock_nuevo"])))
                except (TypeError, ValueError):
                    stock_snap = None

            detalle = DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario_momento=precio,
                stock_remanente_post_venta=stock_snap,
            )

            pedido.total_pedido += detalle.subtotal
            pedido.save(update_fields=['total_pedido'])

            extra = ""
            if detalles_desc:
                d0 = detalles_desc[0]
                extra = f" Se descontaron {d0['cantidad_descontada']} unidades de {d0['insumo']}."
            messages.success(request, f"Detalle creado correctamente.{extra}")
            return redirect('lista_detalles')
            
        except (ValueError, InvalidOperation) as e:
            messages.error(request, f"Datos inválidos: {e}")
        except Exception as e:
            messages.error(request, f"No se pudo crear el detalle: {e}")

    return render(request, 'detalle_pedido/form_detalle.html', {
        'pedidos': pedidos,
        'productos': productos
    })


@super_admin_required
def editar_detalle(request, id):
    detalle = get_object_or_404(DetallePedido, pk=id)
    pedidos = Pedido.objects.all()
    productos = Producto.objects.all()

    if request.method == 'POST':
        try:
            cantidad = int(str(request.POST.get('cantidad', '0')).strip())
            precio = Decimal(str(request.POST.get('precio', '0')).strip())
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor que 0.")
            if precio < 0:
                raise ValueError("El precio no puede ser negativo.")

            detalle.pedido = Pedido.objects.get(pk=request.POST['id_pedido'])
            detalle.producto = Producto.objects.get(pk=request.POST['id_producto'])
            detalle.cantidad = cantidad
            detalle.precio_unitario_momento = precio
            detalle.save()
            messages.success(request, "Detalle actualizado.")
            return redirect('lista_detalles')
        except (ValueError, InvalidOperation) as e:
            messages.error(request, f"Datos inválidos: {e}")
        except Exception as e:
            messages.error(request, f"No se pudo actualizar el detalle: {e}")

    return render(request, 'detalle_pedido/form_detalle.html', {
        'detalle': detalle,
        'pedidos': pedidos,
        'productos': productos
    })


@super_admin_required
def eliminar_detalle(request, id):
    detalle = get_object_or_404(DetallePedido, pk=id)
    if request.method == 'POST':
        detalle.delete()
        messages.success(request, "Línea de pedido eliminada.")
        return redirect('lista_detalles')
    return render(request, 'detalle_pedido/eliminar_detalle.html', {'detalle': detalle})
