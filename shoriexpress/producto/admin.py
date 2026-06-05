from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_producto',
        'precio_venta',
        'es_combo',
        'esta_habilitado',
        'esta_disponible',
        'disponibilidad_real',
        'imagen_preview'
    ]
    list_filter = [
        'es_combo',
        'esta_habilitado',
        'esta_disponible'
    ]
    search_fields = [
        'nombre_producto',
        'descripcion_producto'
    ]
    list_editable = [
        'esta_habilitado',
        'esta_disponible'
    ]
    readonly_fields = [
        'disponibilidad_real_info',
        'ingredientes_info',
        'imagen_preview'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'nombre_producto',
                'descripcion_producto',
                'precio_venta',
                'es_combo'
            )
        }),
        ('Control de Disponibilidad', {
            'fields': (
                'esta_habilitado',
                'esta_disponible',
                'disponibilidad_real_info',
                'ingredientes_info'
            ),
            'description': 'Control manual y automático de disponibilidad del producto.'
        }),
        ('Imágenes', {
            'fields': (
                'imagen',
                'imagen_preview',
                'imagen_catalogo'
            ),
            'classes': ('collapse',)
        }),
        ('Información de Auditoría', {
            'fields': (
                'registro_movimiento_inicial',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def disponibilidad_real(self, obj):
        """
        Muestra la disponibilidad real considerando el stock de ingredientes.
        """
        if obj.is_available_for_sale:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ Disponible</span>'
            )
        else:
            hay_stock, ingredientes_faltantes = obj.check_ingredient_stock()
            if not hay_stock:
                return format_html(
                    '<span style="color: red; font-weight: bold;">❌ Sin Ingredientes</span>'
                )
            else:
                return format_html(
                    '<span style="color: orange; font-weight: bold;">⚠️ Deshabilitado</span>'
                )
    disponibilidad_real.short_description = 'Disponibilidad Real'
    
    def disponibilidad_real_info(self, obj):
        """
        Muestra información detallada sobre la disponibilidad.
        """
        hay_stock, ingredientes_faltantes = obj.check_ingredient_stock()
        
        if hay_stock:
            return format_html(
                '<span style="color: green;">✅ Todos los ingredientes disponibles</span>'
            )
        else:
            faltantes_html = "<ul style='margin: 0; padding-left: 20px;'>"
            for ing in ingredientes_faltantes:
                faltantes_html += f"<li>{ing['insumo']}: {ing['stock_actual']}/{ing['stock_necesario']}</li>"
            faltantes_html += "</ul>"
            
            return format_html(
                '<span style="color: red;">❌ Ingredientes faltantes:</span>{}',
                faltantes_html
            )
    disponibilidad_real_info.short_description = 'Estado de Ingredientes'
    
    def ingredientes_info(self, obj):
        """
        Muestra información sobre los ingredientes/recetas del producto.
        """
        from receta.models import Receta
        
        recetas = Receta.objects.filter(producto=obj)
        if not recetas.exists():
            return format_html(
                '<span style="color: orange;">⚠️ Este producto no tiene recetas definidas</span>'
            )
        
        recetas_html = "<table style='width: 100%; border-collapse: collapse;'>"
        recetas_html += "<tr><th style='border: 1px solid #ddd; padding: 4px;'>Insumo</th>"
        recetas_html += "<th style='border: 1px solid #ddd; padding: 4px;'>Cantidad</th>"
        recetas_html += "<th style='border: 1px solid #ddd; padding: 4px;'>Stock Actual</th></tr>"
        
        for receta in recetas:
            insumo = receta.insumo
            stock_status = "✅" if insumo.stock_actual >= receta.cantidad_requerida else "❌"
            
            recetas_html += "<tr>"
            recetas_html += f"<td style='border: 1px solid #ddd; padding: 4px;'>{insumo.nombre_insumo}</td>"
            recetas_html += f"<td style='border: 1px solid #ddd; padding: 4px;'>{receta.cantidad_requerida} {insumo.get_unidad_medida_display()}</td>"
            recetas_html += f"<td style='border: 1px solid #ddd; padding: 4px;'>{stock_status} {insumo.stock_actual} {insumo.get_unidad_medida_display()}</td>"
            recetas_html += "</tr>"
        
        recetas_html += "</table>"
        return format_html(recetas_html)
    ingredientes_info.short_description = 'Recetas e Ingredientes'
    
    def imagen_preview(self, obj):
        """
        Muestra una vista previa de la imagen del producto.
        """
        if obj.imagen:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 4px;" />',
                obj.imagen.url
            )
        elif obj.imagen_catalogo:
            return format_html(
                '<img src="/static/{}" width="100" height="100" style="object-fit: cover; border-radius: 4px;" />',
                obj.imagen_catalogo
            )
        else:
            return format_html(
                '<span style="color: #999;">Sin imagen</span>'
            )
    imagen_preview.short_description = 'Vista Previa'
    
    actions = [
        'habilitar_seleccionados',
        'deshabilitar_seleccionados',
        'actualizar_disponibilidad_automatica'
    ]
    
    def habilitar_seleccionados(self, request, queryset):
        """
        Habilita los productos seleccionados manualmente.
        """
        count = queryset.update(esta_habilitado=True)
        self.message_user(request, f'{count} productos habilitados exitosamente.')
    habilitar_seleccionados.short_description = 'Habilitar productos seleccionados'
    
    def deshabilitar_seleccionados(self, request, queryset):
        """
        Deshabilita los productos seleccionados manualmente.
        """
        count = queryset.update(esta_habilitado=False)
        self.message_user(request, f'{count} productos deshabilitados exitosamente.')
    deshabilitar_seleccionados.short_description = 'Deshabilitar productos seleccionados'
    
    def actualizar_disponibilidad_automatica(self, request, queryset):
        """
        Actualiza la disponibilidad de los productos seleccionados basado en el stock de ingredientes.
        """
        actualizados = []
        for producto in queryset:
            estado_anterior = producto.esta_habilitado
            nuevo_estado = producto.update_availability_based_on_stock()
            
            if estado_anterior != nuevo_estado:
                actualizados.append(f'{producto.nombre_producto}: {"habilitado" if nuevo_estado else "deshabilitado"}')
        
        if actualizados:
            self.message_user(
                request, 
                f'Disponibilidad actualizada para {len(actualizados)} productos: ' + ', '.join(actualizados)
            )
        else:
            self.message_user(request, 'No se realizaron cambios en la disponibilidad.')
    actualizar_disponibilidad_automatica.short_description = 'Actualizar disponibilidad automática'
