from django.db import models
from usuario.models import Usuario

class Pedido(models.Model):
    """
    Representa la orden de compra del cliente. 
    Controla el flujo desde que se solicita hasta que se entrega.
    """
    TIPOS_PEDIDO = [
        ('local', 'Para comer aquí'),
        ('llevar', 'Para llevar'),
        ('domicilio', 'Domicilio'),
    ]
    
    ESTADOS_PEDIDO = [
        ('pendiente', 'Pendiente'),
        ('preparacion', 'En Preparación'),
        ('listo', 'Listo para Entrega'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    # Relación con el cliente o cajero que toma el pedido
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT, 
        related_name='pedidos'
    )
    
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    tipo_pedido = models.CharField(max_length=20, choices=TIPOS_PEDIDO, default='local')
    
    # Se deja como opcional para pedidos locales (mejora sugerida)
    direccion_pedido = models.CharField(max_length=255, null=True, blank=True)
    
    # Requerimiento Profe: Estado por defecto "pendiente"
    estado_pedido = models.CharField(
        max_length=20, 
        choices=ESTADOS_PEDIDO, 
        default='pendiente'
    )
    
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Bonos: opción de usar bonos para descuento
    usar_bonos = models.BooleanField(default=False)
    descuento_bonos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Tiempo de entrega: el cliente puede comparar la hora estimada con la real
    fecha_entrega_estimada = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Calculada al confirmar el pago (ej. hora actual + minutos de preparación)",
    )
    fecha_entrega_real = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Se registra automáticamente al marcar el pedido como entregado",
    )

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        db_table = "pedido_pedido"

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.primer_nombre} ({self.estado_pedido})"