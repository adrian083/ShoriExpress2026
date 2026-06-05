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
    return (Path(__file__).resolve().parent / '.env').resolve(strict=False)


def switch_to_sqlite():
    """Configura el proyecto para usar SQLite"""
    env_file = _safe_env_file()
    env_content = ""

    if env_file.exists():
        env_content = env_file.read_text(encoding='utf-8')
    
    # Actualizar o agregar USE_SQLITE
    lines = env_content.split('\n')
    new_lines = []
    sqlite_line_added = False
    
    for line in lines:
        if line.startswith('USE_SQLITE='):
            new_lines.append('USE_SQLITE=true')
            sqlite_line_added = True
        elif line.strip() == '':
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    if not sqlite_line_added:
        new_lines.append('USE_SQLITE=true')

    env_file.write_text('\n'.join(new_lines), encoding='utf-8')

    # Establecer variable de entorno para la sesión actual
    os.environ['USE_SQLITE'] = 'true'
    
    print("OK: Cambiado a SQLite")
    print("Base de datos: db.sqlite3")
    print("Ejecuta 'python manage.py migrate' para aplicar migraciones")

def switch_to_mysql():
    """Configura el proyecto para usar MySQL"""
    env_file = _safe_env_file()
    env_content = ""

    if env_file.exists():
        env_content = env_file.read_text(encoding='utf-8')
    
    # Actualizar o agregar USE_SQLITE
    lines = env_content.split('\n')
    new_lines = []
    
    for line in lines:
        if line.startswith('USE_SQLITE='):
            new_lines.append('USE_SQLITE=false')
        elif line.strip() == '':
            new_lines.append(line)
        else:
            new_lines.append(line)

    env_file.write_text('\n'.join(new_lines), encoding='utf-8')

    # Establecer variable de entorno para la sesión actual
    os.environ['USE_SQLITE'] = 'false'
    
    print("OK: Cambiado a MySQL")
    print("Base de datos: shori_express (XAMPP)")
    print("Asegurate de que XAMPP MySQL esté corriendo")
    print("Ejecuta 'python manage.py migrate' para aplicar migraciones")

def main():
    if len(sys.argv) != 2:
        print("Uso: python switch_database.py [sqlite|mysql]")
        sys.exit(1)
    
    db_type = sys.argv[1].lower()
    
    if db_type == 'sqlite':
        switch_to_sqlite()
    elif db_type == 'mysql':
        switch_to_mysql()
    else:
        print("Error: Debes elegir 'sqlite' o 'mysql'")
        sys.exit(1)

if __name__ == '__main__':
    main()
