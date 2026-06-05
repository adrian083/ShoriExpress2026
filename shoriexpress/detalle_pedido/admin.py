from django.contrib import admin
from .models import DetallePedido

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario_momento', 'subtotal')
    list_filter = ('pedido__estado_pedido', 'producto__esta_disponible')
    search_fields = ('pedido__id', 'producto__nombre_producto')
