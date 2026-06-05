from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import time


class ConfiguracionSistema(models.Model):
    """
    Configuración centralizada del sistema POS.
    Actualmente maneja horario comercial y parámetros de negocio.
    """
    
    # Identificador único (singleton pattern)
    nombre_sistema = models.CharField(
        max_length=100,
        default="ShoriExpress",
        help_text="Nombre del negocio"
    )
    
    # ====== HORARIO COMERCIAL ======
    hora_apertura = models.TimeField(
        default=time(8, 0),
        help_text="Hora de apertura en formato 24h (ej: 08:00)"
    )
    hora_cierre = models.TimeField(
        default=time(19, 0),
        help_text="Hora de cierre en formato 24h (ej: 22:00 para 10 pm)"
    )
    
    # ====== PARÁMETROS DE NEGOCIO ======
    porcentaje_iva = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=19.00,
        help_text="Porcentaje de IVA a aplicar"
    )
    
    umbral_bonos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50000.00,
        help_text="Monto mínimo de compra para ganar bono de fidelidad"
    )
    
    # ====== AUDITORÍA ======
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuración del Sistema"
        db_table = "dashboard_configuracion"
    
    def __str__(self):
        return f"Config: {self.nombre_sistema}"
    
    def esta_dentro_horario(self, hora=None):
        """Determina si una hora dada está dentro del horario comercial."""
        if hora is None:
            ahora = timezone.localtime(timezone.now())
            hora = ahora.time()

        if self.hora_apertura == self.hora_cierre:
            return True

        if self.hora_apertura < self.hora_cierre:
            return self.hora_apertura <= hora <= self.hora_cierre

        return hora >= self.hora_apertura or hora <= self.hora_cierre

    def clean(self):
        """Validación: hora de cierre no puede ser igual a apertura."""
        if self.hora_cierre == self.hora_apertura:
            raise ValidationError(
                "La hora de cierre debe ser distinta a la de apertura."
            )
    
    @staticmethod
    def get_config():
        """Obtiene la configuración actual (singleton)"""
        config = ConfiguracionSistema.objects.first()
        if config is None:
            config = ConfiguracionSistema.objects.create(
                nombre_sistema='ShoriExpress',
                hora_apertura=time(8, 0),
                hora_cierre=time(19, 0),
                porcentaje_iva=19.00,
                umbral_bonos=50000.00,
            )
        return config
