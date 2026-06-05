"""
Utilidades para validación de horario comercial y restricciones en el carrito
"""
from django.utils import timezone
from django.utils.timezone import localtime
from dashboard.models import ConfiguracionSistema


class HorarioComercialValidator:
    """Validador de horario comercial"""
    
    @staticmethod
    def es_dentro_horario():
        """
        Verifica si la hora actual está dentro del horario comercial
        """
        try:
            config = ConfiguracionSistema.get_config()
            ahora = localtime(timezone.now())
            hora_actual = ahora.time()
            
            return config.esta_dentro_horario(hora_actual)
        except Exception as e:
            # Si hay error con la configuración, permitir por defecto
            print(f"Error al validar horario: {e}")
            return True
    
    @staticmethod
    def obtener_mensaje_fuera_horario():
        """
        Obtiene mensaje cuando está fuera de horario
        """
        try:
            config = ConfiguracionSistema.get_config()
            return (
                f"Lo sentimos, estamos fuera de nuestro horario de atención. "
                f"Abiertos de {config.hora_apertura.strftime('%H:%M')} a "
                f"{config.hora_cierre.strftime('%H:%M')}"
            )
        except:
            return "Lo sentimos, estamos fuera de horario en este momento."
    
    @staticmethod
    def obtener_config_horario():
        """
        Retorna configuración de horario para AJAX/API
        """
        try:
            config = ConfiguracionSistema.get_config()
            ahora = localtime(timezone.now())
            hora_actual = ahora.time()
            
            dentro_horario = config.esta_dentro_horario(hora_actual)
            return {
                'dentro_horario': dentro_horario,
                'hora_apertura': config.hora_apertura.strftime('%H:%M'),
                'hora_cierre': config.hora_cierre.strftime('%H:%M'),
                'hora_actual': hora_actual.strftime('%H:%M'),
                'mensaje': HorarioComercialValidator.obtener_mensaje_fuera_horario()
                           if not dentro_horario
                           else None
            }
        except:
            return {
                'dentro_horario': True,
                'mensaje': None
            }
