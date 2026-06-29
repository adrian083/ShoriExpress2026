"""
Script manual para verificar conexión a MySQL (XAMPP).
Uso: python scripts/check_mysql_connection.py
No es una prueba unitaria de Django.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main() -> int:
    try:
        import MySQLdb as mysql_driver
    except ModuleNotFoundError:
        try:
            import pymysql
            pymysql.install_as_MySQLdb()
            import MySQLdb as mysql_driver
        except ModuleNotFoundError as exc:
            print(f'No se encontró un driver de MySQL: {exc}')
            return 1

    _load_env_file(ROOT / '.env')

    db_config = {
        'host': os.environ.get('MYSQL_HOST', '127.0.0.1'),
        'port': int(os.environ.get('MYSQL_PORT', '3306')),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', ''),
        'database': os.environ.get('MYSQL_DATABASE', 'shori_express'),
    }

    try:
        conn = mysql_driver.connect(**db_config)
        print('Conexion exitosa a MySQL')
        conn.close()
        return 0
    except mysql_driver.OperationalError as exc:
        print(f'Error de conexion: {exc}')
        print('Posibles causas:')
        print('- MySQL no esta corriendo en XAMPP')
        print('- Puerto incorrecto')
        print('- Contrasena incorrecta')
        print('- Base de datos no existe')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
