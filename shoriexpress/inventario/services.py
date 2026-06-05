from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime
from .models import Inventario
from receta.models import Receta
from producto.models import Producto


class InventoryService:
    """
    Servicio centralizado para la gestión de inventario y descuento por recetas.
    """
    
    @staticmethod
    def validate_recipe_ingredients(producto, cantidad=1):
        """
        Valida si hay stock suficiente de todos los ingredientes para un producto.
        
        Args:
            producto: Producto a validar
            cantidad: Cantidad de unidades del producto a preparar
            
        Returns:
            tuple: (es_valido, lista_ingredientes_insuficientes)
        """
        ingredientes_insuficientes = []
        
        for receta in Receta.objects.filter(producto=producto):
            insumo = receta.insumo
            cantidad_necesaria = receta.cantidad_requerida * cantidad
            
            if insumo.stock_actual < cantidad_necesaria:
                ingredientes_insuficientes.append({
                    'insumo': insumo.nombre_insumo,
                    'stock_actual': float(insumo.stock_actual),
                    'stock_necesario': float(cantidad_necesaria),
                    'unidad_medida': insumo.get_unidad_medida_display()
                })
        
        return len(ingredientes_insuficientes) == 0, ingredientes_insuficientes
    
    @staticmethod
    @transaction.atomic
    def deduct_inventory_by_recipe(producto, cantidad=1, registrar_movimiento=True, usuario=None):
        """
        Descuenta el inventario basado en la receta de un producto.

        Args:
            producto: Producto vendido
            cantidad: Cantidad de unidades vendidas
            registrar_movimiento: Si debe registrar el movimiento en el historial
            usuario: Responsable del movimiento (obligatorio si registrar_movimiento=True)

        Returns:
            dict: Resultado de la operación con detalles del descuento
        """
        # Primero validar que hay stock suficiente
        es_valido, ingredientes_insuficientes = InventoryService.validate_recipe_ingredients(
            producto, cantidad
        )
        
        if not es_valido:
            raise ValidationError(
                f"Stock insuficiente para preparar {cantidad} unidad(es) de {producto.nombre_producto}. "
                f"Ingredientes faltantes: {ingredientes_insuficientes}"
            )
        
        detalles_descuento = []
        
        # Realizar el descuento de cada ingrediente
        for receta in Receta.objects.filter(producto=producto):
            insumo = receta.insumo
            cantidad_a_descontar = receta.cantidad_requerida * cantidad
            
            # Guardar stock anterior para auditoría
            stock_anterior = insumo.stock_actual
            
            # Actualizar stock del insumo
            insumo.stock_actual -= cantidad_a_descontar
            insumo.save(update_fields=['stock_actual'])
            
            # Actualizar estado del insumo si es necesario
            InventoryService.update_ingredient_status(insumo)
            
            if registrar_movimiento and usuario is not None:
                InventoryService.record_salida_venta(
                    insumo=insumo,
                    usuario=usuario,
                    cantidad=cantidad_a_descontar,
                    observaciones=(
                        f"Venta detalle/admin: {cantidad}x {producto.nombre_producto} "
                        f"(stock {stock_anterior} → {insumo.stock_actual})"
                    ),
                )
            
            detalles_descuento.append({
                'insumo': insumo.nombre_insumo,
                'cantidad_descontada': float(cantidad_a_descontar),
                'stock_anterior': float(stock_anterior),
                'stock_nuevo': float(insumo.stock_actual),
                'unidad_medida': insumo.get_unidad_medida_display()
            })
        
        # Actualizar disponibilidad del producto basado en el stock restante
        producto.update_availability_based_on_stock()
        
        return {
            'exito': True,
            'producto': producto.nombre_producto,
            'cantidad_vendida': cantidad,
            'detalles_descuento': detalles_descuento
        }
    
    @staticmethod
    def update_ingredient_status(insumo):
        """
        Actualiza el estado de un insumo basado en su stock actual.
        """
        if insumo.stock_actual <= 0:
            insumo.estado_insumo = 'agotado'
        elif insumo.stock_actual < insumo.stock_minimo:
            insumo.estado_insumo = 'pocos'
        else:
            insumo.estado_insumo = 'disponible'
        
        insumo.save(update_fields=['estado_insumo'])
    
    @staticmethod
    def record_salida_venta(insumo, usuario, cantidad, observaciones):
        """Registra una salida por venta coherente con el modelo MovimientoInventario."""
        from movimiento_inventario.models import MovimientoInventario

        MovimientoInventario.objects.create(
            insumo=insumo,
            usuario=usuario,
            tipo_movimiento="salida_venta",
            cantidad=cantidad,
            observaciones=observaciones,
        )
    
    @staticmethod
    def check_business_hours():
        """
        Verifica si el sistema está dentro del horario comercial.
        
        Returns:
            tuple: (esta_dentro_horario, config_sistema)
        """
        from dashboard.models import ConfiguracionSistema
        from datetime import datetime, time
        
        config = ConfiguracionSistema.get_config()
        ahora = localtime(timezone.now()).time()
        
        esta_dentro = config.esta_dentro_horario(ahora)
        
        return esta_dentro, config
    
    @staticmethod
    def get_available_products():
        """
        Obtiene todos los productos que están disponibles para venta.
        Considera tanto el estado manual como el stock de ingredientes.
        
        Returns:
            QuerySet: Productos disponibles para venta
        """
        productos = Producto.objects.filter(
            esta_habilitado=True,
            esta_disponible=True
        )
        
        productos_disponibles = []
        for producto in productos:
            if producto.is_available_for_sale:
                productos_disponibles.append(producto)
        
        return productos_disponibles
    
    @staticmethod
    def update_all_products_availability():
        """
        Actualiza la disponibilidad de todos los productos basado en el stock de ingredientes.
        Útil para ejecutar después de actualizaciones masivas de inventario.
        """
        productos_actualizados = []
        
        for producto in Producto.objects.all():
            estado_anterior = producto.esta_habilitado
            nuevo_estado = producto.update_availability_based_on_stock()
            
            if estado_anterior != nuevo_estado:
                productos_actualizados.append({
                    'producto': producto.nombre_producto,
                    'estado_anterior': estado_anterior,
                    'nuevo_estado': nuevo_estado
                })
        
        return productos_actualizados
