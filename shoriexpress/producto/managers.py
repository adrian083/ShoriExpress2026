from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import time


class ProductoManager(models.Manager):
    """
    Manager personalizado para el modelo Producto con filtros de disponibilidad.
    """
    
    def disponibles(self):
        """
        Retorna productos que están habilitados manualmente y tienen stock de ingredientes.
        """
        productos = super().filter(
            esta_habilitado=True,
            esta_disponible=True
        )
        
        # Filtrar por stock de ingredientes
        productos_disponibles = []
        for producto in productos:
            if producto.is_available_for_sale:
                productos_disponibles.append(producto.pk)
        
        return super().filter(pk__in=productos_disponibles)
    
    def habilitados(self):
        """
        Retorna productos que están habilitados manualmente (sin validar stock de ingredientes).
        """
        return super().filter(esta_habilitado=True)
    
    def dentro_horario_comercial(self):
        """
        Verifica si el sistema está dentro del horario comercial.
        
        Returns:
            tuple: (esta_dentro_horario, mensaje)
        """
        from dashboard.models import ConfiguracionSistema
        
        try:
            config = ConfiguracionSistema.get_config()
            ahora = localtime(timezone.now()).time()
            
            if config.esta_dentro_horario(ahora):
                return True, "Dentro del horario comercial"
            else:
                return False, f"Fuera de horario. Horario: {config.hora_apertura} - {config.hora_cierre}"
                
        except Exception:
            # Si no hay configuración, asumimos que está disponible
            return True, "Configuración no encontrada, asumiendo disponibilidad"
    
    def validar_venta(self, producto, cantidad=1):
        """
        Valida si un producto se puede vender considerando todas las restricciones.
        
        Args:
            producto: Producto a validar
            cantidad: Cantidad a vender
            
        Returns:
            tuple: (puede_venderse, dict_con_errores)
        """
        errores = {}
        
        # Validar horario comercial
        dentro_horario, mensaje_horario = self.dentro_horario_comercial()
        if not dentro_horario:
            errores['horario'] = mensaje_horario
        
        # Validar disponibilidad manual
        if not producto.esta_habilitado:
            errores['habilitado'] = "El producto está deshabilitado manualmente"
        
        if not producto.esta_disponible:
            errores['disponible'] = "El producto no está disponible en el menú"
        
        # Validar stock de ingredientes
        hay_stock, ingredientes_faltantes = producto.check_ingredient_stock()
        if not hay_stock:
            errores['ingredientes'] = ingredientes_faltantes
        
        # Validar stock suficiente para la cantidad solicitada
        from inventario.services import InventoryService
        stock_valido, ingredientes_insuficientes = InventoryService.validate_recipe_ingredients(
            producto, cantidad
        )
        if not stock_valido:
            errores['stock_insuficiente'] = ingredientes_insuficientes
        
        return len(errores) == 0, errores
