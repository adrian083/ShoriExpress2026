from django.contrib import admin
from .models import Receta


class ProductoDisponibleFilter(admin.SimpleListFilter):
    title = 'Disponibilidad del Producto'
    parameter_name = 'producto_disponible'

    def lookups(self, request, model_admin):
        return (
            ('disponible', 'Productos Disponibles'),
            ('no_disponible', 'Productos No Disponibles'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'disponible':
            return queryset.filter(producto__esta_disponible=True)
        if self.value() == 'no_disponible':
            return queryset.filter(producto__esta_disponible=False)


class InsumoEstadoFilter(admin.SimpleListFilter):
    title = 'Estado del Insumo'
    parameter_name = 'insumo_estado'

    def lookups(self, request, model_admin):
        return (
            ('disponible', 'Insumos Disponibles'),
            ('agotado', 'Insumos Agotados'),
            ('pocos', 'Insumos con Pocas Unidades'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'disponible':
            return queryset.filter(insumo__estado_insumo='disponible')
        if self.value() == 'agotado':
            return queryset.filter(insumo__estado_insumo='agotado')
        if self.value() == 'pocos':
            return queryset.filter(insumo__estado_insumo='pocos')


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'insumo', 'cantidad_requerida')
    list_filter = (ProductoDisponibleFilter, InsumoEstadoFilter)
    search_fields = ('producto__nombre_producto', 'insumo__nombre_insumo')
