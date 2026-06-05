from django.db import models

class Inventario(models.Model):
    """
    Representa los insumos o materias primas (ej. Pollo, Arroz, Aceite).
    """
    UNIDADES_MEDIDA = [
        ('GR', 'Gramos'),
        ('KG', 'Kilogramos'),
        ('ML', 'Mililitros'),
        ('LT', 'Litros'),
        ('UN', 'Unidad'),
    ]
    
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('agotado', 'Agotado'),
        ('pocos', 'Pocas Unidades'),
    ]

    # Datos básicos del insumo
    nombre_insumo = models.CharField(max_length=100)
    categoria_insumo = models.CharField(max_length=50) # Ej: Proteína, Vegetal, Abarrote
    unidad_medida = models.CharField(
        max_length=10, 
        choices=UNIDADES_MEDIDA, 
        default='GR'
    )
    
    # Control de Stock
    stock_actual = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )
    stock_minimo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Alerta cuando el stock baje de este valor"
    )
    stock_maximo = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True, 
        blank=True
    )
    
    # Costos e Impuestos
    precio_compra_referencia = models.DecimalField(max_digits=10, decimal_places=2)
    iva_porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00
    )
    
    estado_insumo = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='disponible'
    )

    class Meta:
        verbose_name = "Insumo de Inventario"
        verbose_name_plural = "Insumos de Inventario"
        db_table = "inventario_inventario"

    def __str__(self):
        return f"{self.nombre_insumo} ({self.stock_actual} {self.get_unidad_medida_display()})"


class InventarioLote(models.Model):
    """
    Stock por lote bajo cada insumo (vista tipo receta: un insumo → varias filas de lote).
    Se actualiza con movimientos de entrada/salida que indiquen código de lote.
    """

    insumo = models.ForeignKey(
        Inventario,
        on_delete=models.CASCADE,
        related_name="lotes",
    )
    codigo_lote = models.CharField(max_length=50)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Lote de inventario"
        verbose_name_plural = "Lotes de inventario"
        db_table = "inventario_inventariolote"
        unique_together = ("insumo", "codigo_lote")

    def __str__(self):
        return f"{self.insumo.nombre_insumo} — Lote {self.codigo_lote} ({self.cantidad})"