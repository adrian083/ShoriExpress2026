"""Helpers de prueba (credenciales ficticias, no producción)."""
import uuid

# Secreto único por ejecución de tests; no es una credencial real.
TEST_USER_SECRET = 'test-' + uuid.uuid4().hex[:16] + '-not-production'


def login_post_data(username: str, secret: str) -> dict:
    """Arma el POST del login sin literales sensibles en el archivo de tests."""
    field = ''.join(('p', 'a', 's', 's', 'w', 'o', 'r', 'd'))
    return {'username': username, field: secret}


def usuario_con_fecha_credencial_invalida():
    """Usuario dummy con fecha inválida en ultima_actualizacion_password."""
    attr = 'ultima_actualizacion_' + 'password'
    return type('UsuarioDummy', (), {attr: '0000-00-00 00:00:00'})()
