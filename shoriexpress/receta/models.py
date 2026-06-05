from django.db import models
from producto.models import Producto
from inventario.models import Inventario

class Receta(models.Model):
    """
    Relaciona un Producto con los Insumos necesarios para su preparación.
    Permite el descuento automático de inventario por porción.
    """
    
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        related_name='ingredientes'
    )
    insumo = models.ForeignKey(
        Inventario, 
        on_delete=models.CASCADE
    )
    
    # Cantidad exacta que se gasta por cada unidad de producto vendido
    cantidad_requerida = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Cantidad a descontar (ej: 0.5 si son 500g y el insumo está en KG)"
    )

    class Meta:
        verbose_name = "Receta / Escandallo"
        verbose_name_plural = "Recetas / Escandallos"
        # Evita que el mismo insumo se agregue dos veces al mismo producto
        unique_together = ('producto', 'insumo')
        db_table = "receta_receta"

    def __str__(self):
        return f"{self.producto.nombre_producto} utiliza {self.cantidad_requerida} de {self.insumo.nombre_insumo}"