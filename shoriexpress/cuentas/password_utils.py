"""Contraseñas: hash con el sistema de Django (PBKDF2) y compatibilidad con texto plano legado."""
from django.contrib.auth.hashers import check_password, identify_hasher, make_password


def _es_hash_django(almacenado: str) -> bool:
    if not almacenado:
        return False
    try:
        identify_hasher(almacenado)
        return True
    except ValueError:
        return False


def hash_password(plain: str) -> str:
    return make_password(plain)


def password_coincide(usuario, plain: str) -> bool:
    """True si la contraseña es correcta (hash Django o legado en texto plano)."""
    almacenado = usuario.contrasena or ""
    if _es_hash_django(almacenado):
        return check_password(plain, almacenado)
    return almacenado == plain


def rehash_si_legado(usuario, plain_correcta: str) -> None:
    """Si aún está en texto plano, guarda hash y persiste."""
    if _es_hash_django(usuario.contrasena or ""):
        return
    usuario.contrasena = make_password(plain_correcta)
    usuario.save(update_fields=["contrasena"])
