from django.contrib import admin
from .models import Recibo

@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'metodo_pago', 'total_pagado', 'fecha_emision', 'puntos_ganados')
    list_filter = ('metodo_pago__esta_activo', 'fecha_emision')
    search_fields = ('pedido__id', 'metodo_pago__nombre_metodo')
