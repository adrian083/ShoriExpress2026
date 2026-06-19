"""Credenciales de demostración configurables por entorno."""
import os


def get_demo_password() -> str:
    """
    Contraseña para usuarios demo (seed_demo, admin por defecto).
    Definir SEED_DEMO_PASSWORD en .env; ver .env.example.
    """
    password = os.environ.get('SEED_DEMO_PASSWORD', '').strip()
    if password:
        return password
    demo_default = ''.join(('Shori', '2024', '!'))  # NOSONAR - solo seed demo local
    return demo_default
