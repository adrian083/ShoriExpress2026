from django.db import models

class MetodoPago(models.Model):
    """
    Define las formas en que el cliente puede pagar.
    Ejemplos: 'Efectivo', 'Tarjeta de Débito', 'Transferencia', 'Puntos'.
    """
    nombre_metodo = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=100, null=True, blank=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        db_table = "metodo_pago_metodopago"

    def __str__(self):
        return self.nombre_metodo