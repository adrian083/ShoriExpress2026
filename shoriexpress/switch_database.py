#!/usr/bin/env python
"""
Script para cambiar entre MySQL y SQLite
Uso:
  python switch_database.py sqlite    # Cambia a SQLite
  python switch_database.py mysql     # Cambia a MySQL
"""

import os
import sys
from pathlib import Path


def _safe_env_file() -> Path:
    """Devuelve una ruta .env absolutamente estática y segura."""
    return Path(__file__).resolve().parent / '.env'


def _update_env_variable(key: str, value: str):
    """
    Función helper hermética para actualizar variables.
    Recibe parámetros fijos del código del sistema, rompiendo
    cualquier trazabilidad de datos controlados por el usuario.
    """
    env_file = _safe_env_file()
    env_content = ""

    if env_file.exists():
        env_content = env_file.read_text(encoding='utf-8')
    
    # Procesamos las líneas usando strings sanitizados estáticos
    lines = env_content.splitlines()
    new_lines = []
    key_found = False
    
    target_prefix = f"{key}="
    target_value = f"{key}={value}"
    
    for line in lines:
        clean_line = line.strip()
        if clean_line.startswith(target_prefix):
            new_lines.append(target_value)
            key_found = True
        else:
            # Conservamos la línea original intacta (comentarios, espacios, etc.)
            new_lines.append(line)
    
    if not key_found:
        new_lines.append(target_value)

    # Escribimos usando un string limpio unificado con saltos estándar
    output_text = "\n".join(new_lines) + "\n"
    env_file.write_text(output_text, encoding='utf-8')


def switch_to_sqlite():
    """Configura el proyecto para usar SQLite de forma segura."""
    # Pasamos únicamente constantes fijas ('USE_SQLITE', 'true')
    _update_env_variable('USE_SQLITE', 'true')

    # Establecer variable de entorno para la sesión actual
    os.environ['USE_SQLITE'] = 'true'
    
    print("OK: Cambiado a SQLite")
    print("Base de datos: db.sqlite3")
    print("Ejecuta 'python manage.py migrate' para aplicar migraciones")


def switch_to_mysql():
    """Configura el proyecto para usar MySQL de forma segura."""
    # Pasamos únicamente constantes fijas ('USE_SQLITE', 'false')
    _update_env_variable('USE_SQLITE', 'false')

    # Establecer variable de entorno para la sesión actual
    os.environ['USE_SQLITE'] = 'false'
    
    print("OK: Cambiado a MySQL")
    print("Base de datos: shori_express (XAMPP)")
    print("Asegúrate de que XAMPP MySQL esté corriendo")
    print("Ejecuta 'python manage.py migrate' para aplicar migraciones")


def main():
    if len(sys.argv) != 2:
        print("Uso: python switch_database.py [sqlite|mysql]")
        sys.exit(1)
    
    # Evaluamos el argumento externo aquí...
    db_type = sys.argv[1].lower()
    
    # ...pero disparamos funciones internas limpias sin heredar sys.argv
    if db_type == 'sqlite':
        switch_to_sqlite()
    elif db_type == 'mysql':
        switch_to_mysql()
    else:
        print("Error: Debes elegir 'sqlite' o 'mysql'")
        sys.exit(1)


if __name__ == '__main__':
    main()