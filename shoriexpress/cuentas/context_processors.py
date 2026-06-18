from usuario.models import Usuario


def user_context(request):
    """Expone el usuario autenticado y si tiene permisos de administración en todas las plantillas."""
    usuario_logueado = None
    es_admin = False

    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        try:
            usuario_logueado = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            request.session.flush()
        else:
            nombre_rol = ''
            if usuario_logueado.rol:
                nombre_rol = usuario_logueado.rol.nombre_rol or ''
            es_admin = nombre_rol.strip().lower() in {'admin', 'administrador', 'empleado'}

    return {
        'usuario_logueado': usuario_logueado,
        'es_admin': es_admin,
    }
