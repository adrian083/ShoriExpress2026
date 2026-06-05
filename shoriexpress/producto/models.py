from django.db import models
from .managers import ProductoManager

class Producto(models.Model):
    """
    Representa los artículos que se venden al cliente final.
    """
    
    objects = ProductoManager()
    nombre_producto = models.CharField(
        max_length=100, 
        verbose_name="Nombre del Plato/Producto"
    )
    descripcion_producto = models.TextField(
        null=True, 
        blank=True, 
        help_text="Descripción que aparecerá en el carrito de compras"
    )
    
    # CAMBIO CRÍTICO: De URLField a ImageField
    imagen = models.ImageField(
        upload_to='productos/', 
        null=True, 
        blank=True,
        help_text="Sube una imagen desde tu dispositivo"
    )
    
    precio_venta = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Precio base al público"
    )
    
    es_combo = models.BooleanField(
        default=False, 
        help_text="Marcar si es un paquete que incluye varios sub-productos"
    )
    esta_disponible = models.BooleanField(
        default=True,
        verbose_name="¿Está en el menú actualmente?"
    )
    
    esta_habilitado = models.BooleanField(
        default=True,
        verbose_name="¿Está habilitado para venta?",
        help_text="Control manual para mostrar/ocultar productos. Se deshabilita automáticamente si faltan insumos."
    )

    # Registro opcional del abastecimiento o movimiento inicial (auditoría / trazabilidad)
    registro_movimiento_inicial = models.TextField(
        null=True,
        blank=True,
        help_text="Nota del movimiento o lote inicial asociado al alta del producto en carta",
    )

    imagen_catalogo = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Opcional. Ruta bajo static/ (ej. productos/perro-clasico.jpg). "
        "Se muestra en la tienda si no hay imagen subida a media.",
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        db_table = "producto_producto"

    def __str__(self):
        return self.nombre_producto
    
    def check_ingredient_stock(self):
        """
        Verifica si todos los ingredientes necesarios para este producto están disponibles.
        Returns: (bool, list) - (hay_stock_suficiente, lista_ingredientes_faltantes)
        """
        from receta.models import Receta
        
        ingredientes_faltantes = []
        
        for receta in Receta.objects.filter(producto=self):
            insumo = receta.insumo
            stock_necesario = receta.cantidad_requerida
            
            if insumo.stock_actual < stock_necesario:
                ingredientes_faltantes.append({
                    'insumo': insumo.nombre_insumo,
                    'stock_actual': insumo.stock_actual,
                    'stock_necesario': stock_necesario
                })
        
        hay_stock = len(ingredientes_faltantes) == 0
        return hay_stock, ingredientes_faltantes
    
    def update_availability_based_on_stock(self):
        """
        Actualiza automáticamente el estado esta_habilitado basado en el stock de ingredientes.
        Si un ingrediente está agotado, deshabilita el producto automáticamente.
        """
        hay_stock, _ = self.check_ingredient_stock()
        
        # Solo deshabilitar automáticamente si está habilitado manualmente
        # pero faltan ingredientes
        if self.esta_habilitado and not hay_stock:
            self.esta_habilitado = False
            self.save(update_fields=['esta_habilitado'])
            return False  # Producto deshabilitado
        
        # Si hay stock y está deshabilitado, podría ser por falta de ingredientes
        # así que lo volvemos a habilitar
        elif not self.esta_habilitado and hay_stock:
            self.esta_habilitado = True
            self.save(update_fields=['esta_habilitado'])
            return True  # Producto habilitado
        
        return self.esta_habilitado
    
    @property
    def is_available_for_sale(self):
        """
        Propiedad que combina la disponibilidad manual y el stock de ingredientes.
        True si el producto está habilitado manualmente Y tiene stock de ingredientes.
        """
        if not self.esta_habilitado:
            return False
        
        hay_stock, _ = self.check_ingredient_stock()
        return hay_stock