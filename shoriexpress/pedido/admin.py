from django.contrib import admin
from .models import Pedido

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'estado_pedido', 'total_pedido', 'fecha_pedido', 'tipo_pedido')
    list_filter = ('estado_pedido', 'tipo_pedido', 'fecha_pedido')
    search_fields = ('usuario__nombre_usuario', 'usuario__primer_nombre', 'id')
