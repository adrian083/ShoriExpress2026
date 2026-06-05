from django.contrib import admin
from .models import MovimientoInventario

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('insumo', 'tipo_movimiento', 'cantidad', 'usuario', 'fecha_movimiento')
    list_filter = ('tipo_movimiento', 'fecha_movimiento', 'usuario')
    search_fields = ('insumo__nombre_insumo', 'observaciones')
