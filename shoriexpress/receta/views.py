from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404

from cuentas.views import admin_shori_required
from inventario.models import Inventario
from producto.models import Producto

from .models import Receta


@admin_shori_required
def lista_recetas(request):
    recetas = Receta.objects.select_related('producto', 'insumo').all()

    productos_con_recetas = {}
    for r in recetas:
        prod_id = r.producto.id
        if prod_id not in productos_con_recetas:
            productos_con_recetas[prod_id] = {
                'producto': r.producto,
                'ingredientes': []
            }
        productos_con_recetas[prod_id]['ingredientes'].append(r)

    total_productos_con_recetas = len(productos_con_recetas)
    total_ingredientes = len(recetas)

    return render(request, 'receta/lista_recetas.html', {
        'recetas': recetas,
        'productos_con_recetas': productos_con_recetas,
        'total_productos_con_recetas': total_productos_con_recetas,
        'total_ingredientes': total_ingredientes,
    })


@admin_shori_required
def crear_receta(request):
    productos = Producto.objects.all()
    insumos = Inventario.objects.all()
    preselect_producto = request.GET.get('producto_id', '')

    if request.method == 'POST':
        prod_id = request.POST.get('id_producto')
        insu_id = request.POST.get('id_insumo')
        cantidad = request.POST.get('cantidad')
        if cantidad is None or str(cantidad).strip() == "":
            messages.error(request, "Indica la cantidad requerida.")
            return render(request, 'receta/form_receta.html', {
                'productos': productos,
                'insumos': insumos,
                'preselect_producto': preselect_producto,
            })

        try:
            cant = Decimal(str(cantidad).strip().replace(",", "."))
        except (InvalidOperation, TypeError, AttributeError):
            messages.error(request, "La cantidad requerida no es válida.")
            return render(request, 'receta/form_receta.html', {
                'productos': productos,
                'insumos': insumos,
                'preselect_producto': preselect_producto,
            })
        if cant <= 0:
            messages.error(request, "La cantidad debe ser mayor que cero.")
            return render(request, 'receta/form_receta.html', {
                'productos': productos,
                'insumos': insumos,
                'preselect_producto': preselect_producto,
            })

        try:
            producto = get_object_or_404(Producto, pk=prod_id)
            insumo = get_object_or_404(Inventario, pk=insu_id)

            Receta.objects.create(
                producto=producto,
                insumo=insumo,
                cantidad_requerida=cant
            )

            messages.success(request, f"Ingrediente '{insumo.nombre_insumo}' agregado a {producto.nombre_producto}.")

            if request.POST.get('agregar_otro'):
                return redirect(f"/recetas/crear/?producto_id={prod_id}")

            return redirect('lista_recetas')

        except IntegrityError:
            messages.error(request, "Error: Este insumo ya está registrado en la receta de este producto. Prueba editando la cantidad en la lista.")
        except Exception as e:
            messages.error(request, f"Hubo un error inesperado: {e}")

    return render(request, 'receta/form_receta.html', {
        'productos': productos,
        'insumos': insumos,
        'preselect_producto': preselect_producto,
    })


@admin_shori_required
def editar_receta(request, id):
    receta = get_object_or_404(Receta, pk=id)
    productos = Producto.objects.all()
    insumos = Inventario.objects.all()
    if request.method == 'POST':
        try:
            cant = Decimal(str(request.POST.get('cantidad', '')).strip().replace(",", "."))
        except (InvalidOperation, TypeError, AttributeError):
            messages.error(request, "La cantidad requerida no es válida.")
            return render(request, 'receta/form_receta.html', {
                'receta': receta,
                'productos': productos,
                'insumos': insumos,
            })
        if cant <= 0:
            messages.error(request, "La cantidad debe ser mayor que cero.")
            return render(request, 'receta/form_receta.html', {
                'receta': receta,
                'productos': productos,
                'insumos': insumos,
            })
        receta.producto = Producto.objects.get(pk=request.POST['id_producto'])
        receta.insumo = Inventario.objects.get(pk=request.POST['id_insumo'])
        receta.cantidad_requerida = cant
        receta.save()
        messages.success(request, "Receta actualizada.")
        return redirect('lista_recetas')
    return render(request, 'receta/form_receta.html', {
        'receta': receta,
        'productos': productos,
        'insumos': insumos
    })


@admin_shori_required
def eliminar_receta(request, id):
    receta = get_object_or_404(Receta, pk=id)
    if request.method == 'POST':
        receta.delete()
        messages.success(request, "Ingrediente eliminado de la receta.")
        return redirect('lista_recetas')
    return render(request, 'receta/eliminar_receta.html', {'receta': receta})
