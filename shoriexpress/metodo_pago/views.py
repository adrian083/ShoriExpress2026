from django.contrib import messages
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods

from cuentas.views import admin_shori_required

from .models import MetodoPago


@admin_shori_required
@require_GET
def lista_metodos(request):
    metodos = MetodoPago.objects.all()
    return render(request, 'metodo_pago/lista_metodos.html', {'metodos': metodos})


@admin_shori_required
@require_http_methods(["GET", "POST"])
def crear_metodo(request):
    if request.method == 'POST':
        nombre = (request.POST.get('nombre') or '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()[:100]
        activo = request.POST.get('esta_activo') == '1'
        if len(nombre) < 3:
            messages.error(request, "El nombre debe tener al menos 3 caracteres.")
            return render(request, 'metodo_pago/form_metodo.html')
        try:
            MetodoPago.objects.create(
                nombre_metodo=nombre,
                descripcion=descripcion or '',
                esta_activo=activo,
            )
        except IntegrityError:
            messages.error(request, "Ya existe un método con ese nombre.")
            return render(request, 'metodo_pago/form_metodo.html')
        messages.success(request, "Método de pago creado.")
        return redirect('lista_metodos')
    return render(request, 'metodo_pago/form_metodo.html')


@admin_shori_required
@require_http_methods(["GET", "POST"])
def editar_metodo(request, id):
    metodo = get_object_or_404(MetodoPago, pk=id)
    if request.method == 'POST':
        nombre = (request.POST.get('nombre') or '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()[:100]
        if len(nombre) < 3:
            messages.error(request, "El nombre debe tener al menos 3 caracteres.")
            return render(request, 'metodo_pago/form_metodo.html', {'metodo': metodo})
        metodo.nombre_metodo = nombre
        metodo.descripcion = descripcion
        metodo.esta_activo = request.POST.get('esta_activo') == '1'
        try:
            metodo.save()
        except IntegrityError:
            messages.error(request, "Ya existe un método con ese nombre.")
            return render(request, 'metodo_pago/form_metodo.html', {'metodo': metodo})
        messages.success(request, "Método actualizado.")
        return redirect('lista_metodos')
    return render(request, 'metodo_pago/form_metodo.html', {'metodo': metodo})


@admin_shori_required
@require_http_methods(["GET", "POST"])
def eliminar_metodo(request, id):
    metodo = get_object_or_404(MetodoPago, pk=id)
    if request.method == 'POST':
        try:
            metodo.delete()
        except ProtectedError:
            messages.warning(
                request,
                "No se puede eliminar este método de pago porque está siendo utilizado por uno o más recibos."
            )
            return redirect('lista_metodos')
        messages.success(request, "Método eliminado.")
        return redirect('lista_metodos')
    return render(request, 'metodo_pago/eliminar_metodo.html', {'metodo': metodo})
