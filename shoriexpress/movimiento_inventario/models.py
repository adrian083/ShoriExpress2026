from django.db import models
from inventario.models import Inventario
from usuario.models import Usuario

class MovimientoInventario(models.Model):
    """
    Registra cada entrada o salida de insumos. 
    Aquí se controla el Lote y la fecha de vencimiento.
    """
    TIPOS_MOVIMIENTO = [
        ('entrada', 'Entrada por Compra'),
        ('entrada_inicial', 'Entrada inicial (alta de insumo / stock inicial)'),
        ('salida_venta', 'Salida por Venta'),
        ('salida_desperdicio', 'Salida por Desperdicio/Merma'),
        ('ajuste', 'Ajuste de Inventario'),
    ]

    # Relaciones
    insumo = models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='movimientos')
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    
    # Nuevo: El Lote se registra directamente aquí para diferenciar entradas
    lote = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        help_text="Código del lote provisto por el proveedor o interno"
    )
    
    # Datos del movimiento
    tipo_movimiento = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Fechas (Trazabilidad)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(
        null=True, 
        blank=True, 
        help_text="Obligatorio para productos perecederos"
    )
    
    # Auditoría
    observaciones = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        db_table = "movimiento_inventario_movimientoinventario"

    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} - {self.insumo.nombre_insumo} (Lote: {self.lote})"