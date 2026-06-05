from django.contrib import admin
from .models import MetodoPago

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre_metodo', 'descripcion', 'esta_activo')
    list_filter = ('esta_activo',)
    search_fields = ('nombre_metodo', 'descripcion')
