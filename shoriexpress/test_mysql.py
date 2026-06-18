import os

try:
    import MySQLdb as mysql_driver
except ModuleNotFoundError:
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
        import MySQLdb as mysql_driver
    except ModuleNotFoundError as exc:
        raise SystemExit(f"No se encontró un driver de MySQL: {exc}") from exc


# Configuración de la base de datos
def _load_env_file(path):
    if not os.path.exists(path):
        return
    for raw_line in open(path, encoding='utf-8').read().splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file('.env')


db_config = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3307")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "shori_express"),
}

try:
    conn = mysql_driver.connect(**db_config)
    print("✅ Conexión exitosa a MySQL")
    conn.close()
except mysql_driver.OperationalError as e:
    print(f"❌ Error de conexión: {e}")
    print("Posibles causas:")
    print("- MySQL no está corriendo en XAMPP")
    print("- Puerto incorrecto (revisa my.ini en XAMPP)")
    print("- Contraseña incorrecta")
    print("- Base de datos no existe")
    print("- Firewall bloqueando el puerto")