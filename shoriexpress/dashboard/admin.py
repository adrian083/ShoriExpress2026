from django.contrib import admin
from .models import ConfiguracionSistema

@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ('nombre_sistema', 'hora_apertura', 'hora_cierre', 'porcentaje_iva', 'umbral_bonos')
    list_filter = ('hora_apertura', 'hora_cierre')
    search_fields = ('nombre_sistema',)

    def has_add_permission(self, request):
        """Evita crear múltiples configuraciones de sistema."""
        return not ConfiguracionSistema.objects.exists()
