from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre_usuario', 'primer_nombre', 'apellido', 'correo', 'estado', 'rol', 'bonos_fidelidad')
    list_filter = ('estado', 'rol', 'tipo_documento')
    search_fields = ('nombre_usuario', 'primer_nombre', 'apellido', 'correo', 'documento')
