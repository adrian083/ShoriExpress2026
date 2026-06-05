from django.contrib import messages
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from cuentas.password_utils import hash_password, password_coincide
from cuentas.views import admin_shori_required, login_shori_required

from .models import Usuario
from rol.models import Rol


@login_shori_required
@require_http_methods(["GET", "POST"])
def mi_cuenta(request, id):
    """Vista de perfil/cuenta personal para el usuario."""
    sesion_id = request.session.get("usuario_id")
    if not sesion_id or int(sesion_id) != int(id):
        messages.error(request, "No puedes editar la cuenta de otro usuario.")
        return redirect("landing")

    usuario = get_object_or_404(Usuario, pk=id)
    mensaje_exito = None
    mensaje_error = None

    try:
        from pedido.models import Pedido
        total_pedidos = Pedido.objects.filter(usuario=usuario).count()
    except Exception:
        total_pedidos = 0

    if request.method == 'POST':
        seccion = request.POST.get('seccion', '')

        if seccion == 'info_personal':
            correo = (request.POST.get('correo') or '').strip()
            telefono = (request.POST.get('telefono') or '').strip() or None
            direccion = (request.POST.get('direccion') or '').strip()
            if not correo or not direccion:
                mensaje_error = 'Correo y dirección son obligatorios.'
            elif Usuario.objects.filter(correo__iexact=correo).exclude(pk=usuario.pk).exists():
                mensaje_error = 'Ese correo ya está registrado en otra cuenta.'
            else:
                usuario.correo = correo
                usuario.telefono = telefono
                usuario.direccion = direccion
                try:
                    usuario.save(update_fields=['correo', 'telefono', 'direccion'])
                    mensaje_exito = 'Datos de contacto y entrega actualizados correctamente.'
                except Exception as e:
                    mensaje_error = f'Error al guardar: {e}'

        elif seccion == 'cambiar_password':
            if usuario.rol and usuario.rol.nombre_rol.strip().lower() == 'cliente':
                mensaje_error = 'Los clientes no pueden cambiar la contraseña desde aquí. Contacta al local.'
            else:
                password_actual = request.POST.get('password_actual', '')
                password_nueva = request.POST.get('password_nueva', '')
                password_confirmar = request.POST.get('password_confirmar', '')

                if not password_coincide(usuario, password_actual):
                    mensaje_error = 'La contraseña actual no es correcta.'
                elif password_nueva != password_confirmar:
                    mensaje_error = 'Las contraseñas nuevas no coinciden.'
                elif len(password_nueva) < 8:
                    mensaje_error = 'La contraseña nueva debe tener al menos 8 caracteres.'
                else:
                    usuario.contrasena = hash_password(password_nueva)
                    usuario.ultima_actualizacion_password = timezone.now()
                    try:
                        usuario.save(update_fields=['contrasena', 'ultima_actualizacion_password'])
                        mensaje_exito = 'Contraseña actualizada correctamente.'
                    except Exception as e:
                        mensaje_error = f'Error al cambiar contraseña: {e}'

        elif seccion == 'cambiar_username':
            if usuario.rol and usuario.rol.nombre_rol.strip().lower() == 'cliente':
                mensaje_error = 'Los clientes no pueden cambiar el nombre de usuario desde aquí.'
            else:
                nuevo_username = request.POST.get('nuevo_username', '').strip()
                if not nuevo_username:
                    mensaje_error = 'El username no puede estar vacío.'
                elif Usuario.objects.filter(nombre_usuario=nuevo_username).exclude(pk=usuario.pk).exists():
                    mensaje_error = f'El username "{nuevo_username}" ya está en uso.'
                else:
                    usuario.nombre_usuario = nuevo_username
                    try:
                        usuario.save()
                        request.session['usuario_username'] = nuevo_username
                        mensaje_exito = f'Username actualizado a "{nuevo_username}".'
                    except Exception as e:
                        mensaje_error = f'Error al cambiar username: {e}'

    es_cliente = bool(
        usuario.rol and usuario.rol.nombre_rol.strip().lower() == 'cliente'
    )
    base_template = 'base_tienda.html' if es_cliente else 'base.html'
    return render(request, 'usuario/mi_cuenta.html', {
        'usuario': usuario,
        'total_pedidos': total_pedidos,
        'mensaje_exito': mensaje_exito,
        'mensaje_error': mensaje_error,
        'es_cliente': es_cliente,
        'base_template': base_template,
    })


@admin_shori_required
@require_GET
def lista_usuarios(request):
    usuarios = Usuario.objects.select_related('rol').all()
    return render(request, 'usuario/lista_usuarios.html', {'usuarios': usuarios})


@admin_shori_required
@require_http_methods(["GET", "POST"])
def crear_usuario(request):
    roles = Rol.objects.all()

    if request.method == 'POST':
        pwd = (request.POST.get('pass') or '').strip()
        if len(pwd) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'usuario/form_usuario.html', {'roles': roles})
        try:
            puntos = int(request.POST.get('puntos') or 0)
        except (TypeError, ValueError):
            puntos = 0
        puntos = max(0, puntos)
        try:
            Usuario.objects.create(
                tipo_documento=request.POST['tipo_doc'],
                documento=request.POST['documento'].strip(),
                nombre_usuario=request.POST['username'].strip(),
                contrasena=hash_password(pwd),
                primer_nombre=request.POST['nombre'].strip(),
                apellido=request.POST['apellido'].strip(),
                correo=request.POST['correo'].strip().lower(),
                telefono=(request.POST.get('telefono') or '').strip() or None,
                direccion=request.POST['direccion'].strip(),
                puntos_acumulados=puntos,
                estado=request.POST['estado'],
                rol=Rol.objects.get(pk=request.POST['id_rol']),
                ultima_actualizacion_password=timezone.now(),
            )
        except IntegrityError:
            messages.error(
                request,
                'No se pudo crear el usuario: documento, correo o nombre de usuario duplicado.',
            )
            return render(request, 'usuario/form_usuario.html', {'roles': roles})
        except (KeyError, ValueError, Rol.DoesNotExist):
            messages.error(request, 'Revisa los datos: faltan campos obligatorios o el rol no es válido.')
            return render(request, 'usuario/form_usuario.html', {'roles': roles})
        messages.success(request, 'Usuario creado correctamente.')
        return redirect('lista_usuarios')

    return render(request, 'usuario/form_usuario.html', {'roles': roles})


@admin_shori_required
@require_http_methods(["GET", "POST"])
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    roles = Rol.objects.all()

    if request.method == 'POST':
        new_pass = (request.POST.get('pass') or '').strip()
        if new_pass and len(new_pass) < 8:
            messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres.')
            return render(request, 'usuario/form_usuario.html', {
                'usuario': usuario,
                'roles': roles,
            })
        usuario.tipo_documento = request.POST['tipo_doc']
        usuario.documento = request.POST['documento'].strip()
        usuario.nombre_usuario = request.POST['username'].strip()
        if new_pass:
            usuario.contrasena = hash_password(new_pass)
            usuario.ultima_actualizacion_password = timezone.now()
        usuario.primer_nombre = request.POST['nombre'].strip()
        usuario.apellido = request.POST['apellido'].strip()
        usuario.correo = request.POST['correo'].strip().lower()
        usuario.telefono = (request.POST.get('telefono') or '').strip() or None
        usuario.direccion = request.POST['direccion'].strip()
        try:
            usuario.puntos_acumulados = max(0, int(request.POST.get('puntos') or 0))
        except (TypeError, ValueError):
            usuario.puntos_acumulados = 0
        usuario.estado = request.POST['estado']
        usuario.rol = Rol.objects.get(pk=request.POST['id_rol'])
        try:
            usuario.save()
        except IntegrityError:
            messages.error(
                request,
                'No se pudo guardar: documento, correo o nombre de usuario duplicado.',
            )
            return render(request, 'usuario/form_usuario.html', {
                'usuario': usuario,
                'roles': roles,
            })
        messages.success(request, 'Usuario actualizado.')
        return redirect('lista_usuarios')

    return render(request, 'usuario/form_usuario.html', {
        'usuario': usuario,
        'roles': roles
    })


@admin_shori_required
@require_http_methods(["GET", "POST"])
def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    if request.method == 'POST':
        sid = request.session.get('usuario_id')
        if sid and int(sid) == int(id):
            messages.error(request, 'No puedes eliminar tu propia cuenta desde el panel.')
            return redirect('lista_usuarios')
        try:
            usuario.delete()
            messages.success(request, 'Usuario eliminado.')
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el usuario porque tiene pedidos, recibos u otros registros asociados. "
                "Reasigna o elimina esos registros primero.",
            )
            return redirect('lista_usuarios')
        return redirect('lista_usuarios')
    return render(request, 'usuario/eliminar_usuario.html', {'usuario': usuario})
