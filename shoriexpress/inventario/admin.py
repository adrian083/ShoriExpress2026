from django.contrib import admin
from django.db import models
from .models import Inventario, InventarioLote


class StockFilter(admin.SimpleListFilter):
    title = 'Estado de Stock'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return (
            ('bajo', 'Bajo Stock'),
            ('normal', 'Stock Normal'),
            ('exceso', 'Exceso de Stock'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'bajo':
            return queryset.filter(stock_actual__lt=models.F('stock_minimo'))
        if self.value() == 'normal':
            return queryset.filter(
                Q(stock_actual__gte=models.F('stock_minimo')) &
                Q(Q(stock_maximo__isnull=True) | Q(stock_actual__lte=models.F('stock_maximo')))
            )
        if self.value() == 'exceso':
            return queryset.filter(stock_actual__gt=models.F('stock_maximo')).exclude(stock_maximo__isnull=True)


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ("nombre_insumo", "categoria_insumo", "stock_actual", "estado_insumo")
    list_filter = ("categoria_insumo", "estado_insumo", "unidad_medida", StockFilter)
    search_fields = ("nombre_insumo", "categoria_insumo")


@admin.register(InventarioLote)
class InventarioLoteAdmin(admin.ModelAdmin):
    list_display = ("insumo", "codigo_lote", "cantidad", "fecha_registro", "fecha_vencimiento")
    list_filter = ("fecha_registro", "fecha_vencimiento")
    search_fields = ("insumo__nombre_insumo", "codigo_lote")
