from django.db import models
from pedido.models import Pedido
from producto.models import Producto


class DetallePedido(models.Model):
    """
    Representa cada ítem dentro de un pedido. 
    Aquí se gestionan las personalizaciones y el costo real de la venta.
    Incluye auditoría de stock post-venta para trazabilidad.
    """
    
    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE, 
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.PROTECT
    )
    
    cantidad = models.PositiveIntegerField(default=1)
    
    # Auditoría: El precio puede cambiar en el maestro de productos, 
    # pero el recibo debe mostrar cuánto pagó el cliente en ese momento.
    precio_unitario_momento = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )
    
    # ====== NUEVO: AUDITORÍA DE INVENTARIO ======
    # Cantidad de unidades disponibles en inventario DESPUÉS de esta venta
    # Útil para auditoría rápida y análisis de stock crítico
    stock_remanente_post_venta = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Stock restante del insumo principal después de esta venta"
    )
    
    # Mejora para "Punto de Venta": Notas para la cocina (ej: "Sin cebolla")
    notas_especiales = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Instrucciones especiales de preparación"
    )
    
    # Timestamp para auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Detalle del Pedido"
        verbose_name_plural = "Detalles del Pedido"
        db_table = "detalle_pedido_detallepedido"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre_producto} (Pedido #{self.pedido.id})"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario_momento
    
    @property
    def subtotal_con_iva(self):
        """Calcula subtotal con IVA basado en configuración"""
        from dashboard.models import ConfiguracionSistema
        config = ConfiguracionSistema.get_config()
        tasa_iva = config.porcentaje_iva / 100
        return self.subtotal * (1 + tasa_iva)