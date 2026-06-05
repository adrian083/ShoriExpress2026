from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from cuentas.views import admin_shori_required
from movimiento_inventario.models import MovimientoInventario
from usuario.models import Usuario

from .lotes import ajustar_lote_entrada
from .models import Inventario


def _recalcular_estado(insumo):
    if insumo.stock_actual <= 0:
        insumo.stock_actual = max(insumo.stock_actual, Decimal("0.00"))
        insumo.estado_insumo = "agotado"
    elif insumo.stock_actual <= insumo.stock_minimo:
        insumo.estado_insumo = "pocos"
    else:
        insumo.estado_insumo = "disponible"


def _to_decimal_strict(val, label):
    try:
        return Decimal(str(val).strip())
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Valor inválido para {label}.")


@admin_shori_required
def lista_inventario(request):
    insumos = Inventario.objects.all().prefetch_related("lotes")
    total_valor_inventario = sum(
        float(i.stock_actual or 0) * float(i.precio_compra_referencia or 0)
        for i in insumos
    )
    return render(request, "inventario/lista_inventario.html", {
        "insumos": insumos,
        "total_valor_inventario": total_valor_inventario,
    })


@admin_shori_required
def crear_insumo(request):
    if request.method == "POST":
        uid = request.session.get("usuario_id")
        try:
            with transaction.atomic():
                cant_inicial = _to_decimal_strict(request.POST.get("stock", 0), "stock inicial")
                stock_minimo = _to_decimal_strict(request.POST.get("stock_minimo", 0), "stock mínimo")
                stock_maximo_raw = request.POST.get("stock_maximo")
                stock_maximo = _to_decimal_strict(stock_maximo_raw, "stock máximo") if stock_maximo_raw else None
                precio_compra = _to_decimal_strict(request.POST.get("precio_compra", 0), "precio compra")
                iva = _to_decimal_strict(request.POST.get("iva", 0), "IVA")

                if cant_inicial < 0 or stock_minimo < 0 or (stock_maximo is not None and stock_maximo < 0) or precio_compra < 0:
                    raise ValueError("Stock y precios no pueden ser negativos.")
                if iva < 0 or iva > 100:
                    raise ValueError("El IVA debe estar entre 0 y 100.")
                if stock_maximo is not None and stock_minimo > stock_maximo:
                    raise ValueError("El stock mínimo no puede ser mayor al stock máximo.")

                insumo = Inventario.objects.create(
                    nombre_insumo=request.POST["nombre"],
                    categoria_insumo=request.POST["categoria"],
                    unidad_medida=request.POST["unidad"],
                    stock_actual=Decimal("0"),
                    stock_minimo=stock_minimo,
                    stock_maximo=stock_maximo,
                    precio_compra_referencia=precio_compra,
                    iva_porcentaje=iva,
                    estado_insumo="agotado",
                )
                if cant_inicial > 0:
                    if not uid:
                        messages.error(
                            request,
                            "Inicia sesión en el panel para registrar stock inicial con movimiento. "
                            "El insumo quedó creado con stock 0.",
                        )
                    else:
                        usr = Usuario.objects.get(pk=uid)
                        lote_ini = request.POST.get("lote_inicial", "").strip()
                        fv = (
                            request.POST.get("fecha_vencimiento_inicial", "").strip()
                            or None
                        )
                        MovimientoInventario.objects.create(
                            insumo=insumo,
                            usuario=usr,
                            tipo_movimiento="entrada_inicial",
                            cantidad=cant_inicial,
                            lote=lote_ini,
                            fecha_vencimiento=fv,
                            observaciones="Stock inicial al crear insumo",
                        )
                        insumo.stock_actual += cant_inicial
                        ajustar_lote_entrada(
                            insumo, lote_ini, cant_inicial, fecha_vencimiento=fv
                        )
                _recalcular_estado(insumo)
                insumo.save()
            messages.success(request, "Insumo registrado correctamente.")
            return redirect("lista_inventario")
        except Exception as e:
            messages.error(request, f"Error al crear insumo: {e}")
    return render(request, "inventario/form_insumo.html", {"es_nuevo": True})


@admin_shori_required
def editar_insumo(request, id):
    insumo = get_object_or_404(Inventario, pk=id)
    if request.method == "POST":
        try:
            with transaction.atomic():
                insumo = Inventario.objects.select_for_update().get(pk=id)
                stock_nuevo = _to_decimal_strict(request.POST.get("stock", 0), "stock actual")
                stock_minimo = _to_decimal_strict(request.POST.get("stock_minimo", 0), "stock mínimo")
                stock_maximo_raw = request.POST.get("stock_maximo")
                stock_maximo = _to_decimal_strict(stock_maximo_raw, "stock máximo") if stock_maximo_raw else None
                precio_compra = _to_decimal_strict(request.POST.get("precio_compra", 0), "precio compra")
                iva = _to_decimal_strict(request.POST.get("iva", 0), "IVA")

                if stock_nuevo < 0 or stock_minimo < 0 or (stock_maximo is not None and stock_maximo < 0) or precio_compra < 0:
                    raise ValueError("Stock y precios no pueden ser negativos.")
                if iva < 0 or iva > 100:
                    raise ValueError("El IVA debe estar entre 0 y 100.")
                if stock_maximo is not None and stock_minimo > stock_maximo:
                    raise ValueError("El stock mínimo no puede ser mayor al stock máximo.")

                stock_anterior = insumo.stock_actual
                insumo.nombre_insumo = request.POST["nombre"]
                insumo.categoria_insumo = request.POST["categoria"]
                insumo.unidad_medida = request.POST["unidad"]
                insumo.stock_actual = stock_nuevo
                insumo.stock_minimo = stock_minimo
                insumo.stock_maximo = stock_maximo
                insumo.precio_compra_referencia = precio_compra
                insumo.iva_porcentaje = iva
                _recalcular_estado(insumo)
                insumo.save()

                if stock_nuevo != stock_anterior:
                    uid = request.session.get("usuario_id")
                    if uid:
                        usr = Usuario.objects.get(pk=uid)
                        MovimientoInventario.objects.create(
                            insumo=insumo,
                            usuario=usr,
                            tipo_movimiento="ajuste",
                            cantidad=stock_nuevo,
                            observaciones=f"Ajuste automático desde edición de insumo (antes: {stock_anterior}, ahora: {stock_nuevo})",
                        )

            messages.success(request, "Insumo actualizado correctamente.")
            return redirect("lista_inventario")
        except Exception as e:
            messages.error(request, f"Error al actualizar insumo: {e}")
    return render(request, "inventario/form_insumo.html", {"insumo": insumo})


@admin_shori_required
def eliminar_insumo(request, id):
    insumo = get_object_or_404(Inventario, pk=id)
    if request.method == "POST":
        insumo.delete()
        return redirect("lista_inventario")
    return render(request, "inventario/eliminar_insumo.html", {"insumo": insumo})


@admin_shori_required
def descargar_inventario_pdf(request):
    insumos = Inventario.objects.all().prefetch_related("lotes").order_by("nombre_insumo")
    context = {
        "insumos": insumos,
        "fecha_generacion": timezone.now(),
    }

    try:
        from xhtml2pdf import pisa
        import io

        html_string = render_to_string("inventario/reporte_inventario_pdf.html", context)
        result = io.BytesIO()
        pdf = pisa.CreatePDF(io.BytesIO(html_string.encode("utf-8")), dest=result, encoding="utf-8")
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="reporte_inventario.pdf"'
            return response
    except ImportError:
        pass

    return render(request, "inventario/reporte_inventario_pdf.html", context)
