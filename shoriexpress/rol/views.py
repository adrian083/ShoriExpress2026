from django.contrib import messages
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods

from cuentas.delete_utils import eliminar_con_mensaje
from cuentas.views import admin_shori_required

from .models import Rol

_MAX_NOMBRE_ROL = 30


@admin_shori_required
@require_GET
def lista_roles(request):
    roles = Rol.objects.all()
    return render(request, 'rol/lista_roles.html', {'roles': roles})


@admin_shori_required
@require_http_methods(["GET", "POST"])
def crear_rol(request):
    if request.method == 'POST':
        nombre = (request.POST.get('nombre_rol') or '').strip()
        if len(nombre) < 3:
            messages.error(request, "El nombre del rol debe tener al menos 3 caracteres.")
            return render(request, 'rol/form_rol.html')
        if len(nombre) > _MAX_NOMBRE_ROL:
            messages.error(
                request,
                f"El nombre del rol no puede superar {_MAX_NOMBRE_ROL} caracteres.",
            )
            return render(request, 'rol/form_rol.html')
        try:
            Rol.objects.create(nombre_rol=nombre)
        except IntegrityError:
            messages.error(request, "Ya existe un rol con ese nombre.")
            return render(request, 'rol/form_rol.html')
        messages.success(request, "Rol creado.")
        return redirect('lista_roles')
    return render(request, 'rol/form_rol.html')


@admin_shori_required
@require_http_methods(["GET", "POST"])
def editar_rol(request, id):
    rol = get_object_or_404(Rol, pk=id)
    if request.method == 'POST':
        nombre = (request.POST.get('nombre_rol') or '').strip()
        if len(nombre) < 3:
            messages.error(request, "El nombre del rol debe tener al menos 3 caracteres.")
            return render(request, 'rol/form_rol.html', {'rol': rol})
        if len(nombre) > _MAX_NOMBRE_ROL:
            messages.error(
                request,
                f"El nombre del rol no puede superar {_MAX_NOMBRE_ROL} caracteres.",
            )
            return render(request, 'rol/form_rol.html', {'rol': rol})
        rol.nombre_rol = nombre
        try:
            rol.save()
        except IntegrityError:
            messages.error(request, "Ya existe un rol con ese nombre.")
            return render(request, 'rol/form_rol.html', {'rol': rol})
        messages.success(request, "Rol actualizado.")
        return redirect('lista_roles')
    return render(request, 'rol/form_rol.html', {'rol': rol})


@admin_shori_required
@require_http_methods(["GET", "POST"])
def eliminar_rol(request, id):
    rol = get_object_or_404(Rol, pk=id)
    if request.method == 'POST':
        return eliminar_con_mensaje(
            request,
            rol,
            mensaje_ok='Rol eliminado.',
            url_redirect='lista_roles',
            mensaje_error=(
                'No se puede eliminar el rol porque hay usuarios u otros registros que lo usan. '
                'Reasigna esos usuarios a otro rol e intenta de nuevo.'
            ),
        )
    return render(request, 'rol/eliminar_rol.html', {'rol': rol})
