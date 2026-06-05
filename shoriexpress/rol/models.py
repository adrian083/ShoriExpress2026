from django.db import models

class Rol(models.Model):
    """
    Define los niveles de acceso al sistema.
    Ejemplos: 'Administrador', 'Cajero', 'Cliente', 'Cocinero'.
    """
    nombre_rol = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Nombre del Rol"
    )

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre_rol']

    def __str__(self):
        return self.nombre_rol