from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from decimal import Decimal, InvalidOperation
from .models import MovimientoInventario
from inventario.models import Inventario
from inventario.lotes import ajustar_lote_entrada, ajustar_lote_salida
from usuario.models import Usuario
from cuentas.views import admin_shori_required


def _usuario_responsable_movimiento(request, post_usuario_id):
    """Siempre el usuario de la sesión (panel); ignora manipulación del campo en el POST."""
    sid = request.session.get("usuario_id")
    if sid:
        return Usuario.objects.get(pk=sid)
    return Usuario.objects.get(pk=post_usuario_id)


def _recalcular_estado(insumo):
    if insumo.stock_actual <= 0:
        insumo.stock_actual = max(insumo.stock_actual, Decimal('0.00'))
        insumo.estado_insumo = 'agotado'
    elif insumo.stock_actual <= insumo.stock_minimo:
        insumo.estado_insumo = 'pocos'
    else:
        insumo.estado_insumo = 'disponible'


def _validar_y_parsear_cantidad(raw):
    try:
        cantidad = Decimal(str(raw).strip())
    except (InvalidOperation, ValueError):
        raise ValueError("Cantidad inválida.")
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0.")
    return cantidad

@admin_shori_required
def lista_movimientos(request):
    movimientos = MovimientoInventario.objects.select_related('insumo', 'usuario').all().order_by('-fecha_movimiento')
    return render(request, 'movimiento_inventario/lista_movimientos.html', {'movimientos': movimientos})


@admin_shori_required
def crear_movimiento(request):
    insumos = Inventario.objects.all()
    usuarios = Usuario.objects.all()
    preselect_insumo = request.GET.get('insumo_id', '')
    preselect_tipo = request.GET.get('tipo', '')
    usuario_sesion_id = request.session.get('usuario_id')
    usuario_sesion = None
    if usuario_sesion_id:
        try:
            usuario_sesion = Usuario.objects.get(pk=usuario_sesion_id)
        except Usuario.DoesNotExist:
            usuario_sesion = None

    if request.method == 'POST':
        try:
            # Usamos una transacción para que si algo falla, no se guarde nada a medias
            with transaction.atomic():
                insumo_id = request.POST['id_insumo']
                usuario_id = request.POST['id_usuario']
                tipo = request.POST['tipo_movimiento']
                cantidad_decimal = _validar_y_parsear_cantidad(request.POST.get('cantidad', ''))
                
                fecha_vencimiento = request.POST.get('fecha_vencimiento', '').strip() or None

                insumo = Inventario.objects.select_for_update().get(pk=insumo_id)
                if tipo in ('salida_venta', 'salida_desperdicio') and cantidad_decimal > insumo.stock_actual:
                    raise ValueError(
                        f"No hay stock suficiente para salida. Stock actual: {insumo.stock_actual}, salida solicitada: {cantidad_decimal}."
                    )

                movimiento = MovimientoInventario.objects.create(
                    insumo=insumo,
                    usuario=_usuario_responsable_movimiento(request, usuario_id),
                    tipo_movimiento=tipo,
                    cantidad=cantidad_decimal,
                    lote=request.POST.get('lote', ''),
                    fecha_vencimiento=fecha_vencimiento,
                    observaciones=request.POST.get('observaciones', '')
                )

                # ACTUALIZACIÓN DEL STOCK
                if tipo in ('entrada', 'entrada_inicial'):
                    insumo.stock_actual += cantidad_decimal
                    ajustar_lote_entrada(
                        insumo,
                        movimiento.lote,
                        cantidad_decimal,
                        fecha_vencimiento=movimiento.fecha_vencimiento,
                    )
                elif tipo in ('salida_venta', 'salida_desperdicio'):
                    insumo.stock_actual -= cantidad_decimal
                    ajustar_lote_salida(insumo, movimiento.lote, cantidad_decimal)
                elif tipo == 'ajuste':
                    insumo.stock_actual = cantidad_decimal

                # Evitar estados inconsistentes
                _recalcular_estado(insumo)
                insumo.save()

            messages.success(request, f"Movimiento registrado. Nuevo stock: {insumo.stock_actual}")
            return redirect('lista_movimientos')
            
        except Exception as e:
            messages.error(request, f"Error al registrar movimiento: {e}")

    return render(request, 'movimiento_inventario/form_movimiento.html', {
        'insumos': insumos, 'usuarios': usuarios,
        'preselect_insumo': preselect_insumo, 'preselect_tipo': preselect_tipo,
        'usuario_sesion_id': usuario_sesion_id,
        'usuario_sesion': usuario_sesion,
    })


@admin_shori_required
def editar_movimiento(request, id):
    movimiento = get_object_or_404(MovimientoInventario, pk=id)
    insumos = Inventario.objects.all()
    usuarios = Usuario.objects.all()
    usuario_sesion_id = request.session.get('usuario_id')
    usuario_sesion = None
    if usuario_sesion_id:
        try:
            usuario_sesion = Usuario.objects.get(pk=usuario_sesion_id)
        except Usuario.DoesNotExist:
            usuario_sesion = None

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Los ajustes no se pueden editar porque no guardamos stock previo para revertirlos de forma segura.
                if movimiento.tipo_movimiento == 'ajuste':
                    raise ValueError("Los movimientos de ajuste no se pueden editar. Elimina y crea uno nuevo.")

                nueva_cantidad = _validar_y_parsear_cantidad(request.POST.get('cantidad', ''))

                # Revertir el movimiento anterior antes de aplicar el nuevo
                insumo_anterior = Inventario.objects.select_for_update().get(pk=movimiento.insumo_id)
                tipo_anterior = movimiento.tipo_movimiento
                cantidad_anterior = movimiento.cantidad

                if tipo_anterior in ('entrada', 'entrada_inicial'):
                    insumo_anterior.stock_actual -= cantidad_anterior
                    ajustar_lote_salida(insumo_anterior, movimiento.lote, cantidad_anterior)
                elif tipo_anterior in ('salida_venta', 'salida_desperdicio'):
                    insumo_anterior.stock_actual += cantidad_anterior
                    ajustar_lote_entrada(
                        insumo_anterior,
                        movimiento.lote,
                        cantidad_anterior,
                        fecha_vencimiento=movimiento.fecha_vencimiento,
                    )
                _recalcular_estado(insumo_anterior)
                insumo_anterior.save()

                nuevo_insumo = Inventario.objects.select_for_update().get(pk=request.POST['id_insumo'])
                nuevo_tipo = request.POST['tipo_movimiento']
                if nuevo_tipo == 'ajuste':
                    raise ValueError("No puedes convertir un movimiento existente en ajuste. Crea un ajuste nuevo.")

                movimiento.insumo = nuevo_insumo
                movimiento.usuario = _usuario_responsable_movimiento(
                    request, request.POST['id_usuario']
                )
                movimiento.tipo_movimiento = nuevo_tipo
                movimiento.cantidad = nueva_cantidad
                movimiento.lote = request.POST.get('lote', '')
                fecha_vencimiento = request.POST.get('fecha_vencimiento', '').strip() or None
                movimiento.fecha_vencimiento = fecha_vencimiento
                movimiento.observaciones = request.POST.get('observaciones', '')

                # Aplicar nuevo movimiento al stock
                if nuevo_tipo in ('entrada', 'entrada_inicial'):
                    nuevo_insumo.stock_actual += nueva_cantidad
                    ajustar_lote_entrada(
                        nuevo_insumo,
                        movimiento.lote,
                        nueva_cantidad,
                        fecha_vencimiento=fecha_vencimiento,
                    )
                elif nuevo_tipo in ('salida_venta', 'salida_desperdicio'):
                    if nueva_cantidad > nuevo_insumo.stock_actual:
                        raise ValueError(
                            f"No hay stock suficiente para salida. Stock actual: {nuevo_insumo.stock_actual}, salida solicitada: {nueva_cantidad}."
                        )
                    nuevo_insumo.stock_actual -= nueva_cantidad
                    ajustar_lote_salida(nuevo_insumo, movimiento.lote, nueva_cantidad)

                movimiento.save()
                _recalcular_estado(nuevo_insumo)
                nuevo_insumo.save()

            messages.success(request, f"Movimiento actualizado. Stock de '{nuevo_insumo.nombre_insumo}' ajustado.")
            return redirect('lista_movimientos')
        except Exception as e:
            messages.error(request, f"No se pudo actualizar el movimiento: {e}")

    return render(request, 'movimiento_inventario/form_movimiento.html', {
        'movimiento': movimiento,
        'insumos': insumos,
        'usuarios': usuarios,
        'usuario_sesion_id': usuario_sesion_id,
        'usuario_sesion': usuario_sesion,
    })


@admin_shori_required
def eliminar_movimiento(request, id):
    movimiento = get_object_or_404(MovimientoInventario, pk=id)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                if movimiento.tipo_movimiento == 'ajuste':
                    raise ValueError("Los movimientos de ajuste no se pueden eliminar para evitar inconsistencias de stock.")

                # Revertir el efecto del movimiento en el stock
                insumo = Inventario.objects.select_for_update().get(pk=movimiento.insumo_id)
                if movimiento.tipo_movimiento in ('entrada', 'entrada_inicial'):
                    if movimiento.cantidad > insumo.stock_actual:
                        raise ValueError("No se puede revertir la entrada porque el stock actual ya es menor que ese movimiento.")
                    insumo.stock_actual -= movimiento.cantidad
                    ajustar_lote_salida(insumo, movimiento.lote, movimiento.cantidad)
                elif movimiento.tipo_movimiento in ('salida_venta', 'salida_desperdicio'):
                    insumo.stock_actual += movimiento.cantidad
                    ajustar_lote_entrada(
                        insumo,
                        movimiento.lote,
                        movimiento.cantidad,
                        fecha_vencimiento=movimiento.fecha_vencimiento,
                    )

                _recalcular_estado(insumo)
                insumo.save()
                movimiento.delete()

            messages.success(request, f"Movimiento eliminado. Stock de '{insumo.nombre_insumo}' revertido.")
            return redirect('lista_movimientos')
        except Exception as e:
            messages.error(request, f"No se pudo eliminar el movimiento: {e}")
            return redirect('lista_movimientos')
    return render(request, 'movimiento_inventario/eliminar_movimiento.html', {'movimiento': movimiento})