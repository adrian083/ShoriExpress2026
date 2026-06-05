import os
import MySQLdb

# Configuración de la base de datos
db_config = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3307")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "567422"),
    "database": os.environ.get("MYSQL_DATABASE", "shori_express"),
}

try:
    conn = MySQLdb.connect(**db_config)
    print("✅ Conexión exitosa a MySQL")
    conn.close()
except MySQLdb.OperationalError as e:
    print(f"❌ Error de conexión: {e}")
    print("Posibles causas:")
    print("- MySQL no está corriendo en XAMPP")
    print("- Puerto incorrecto (revisa my.ini en XAMPP)")
    print("- Contraseña incorrecta")
    print("- Base de datos no existe")
    print("- Firewall bloqueando el puerto")