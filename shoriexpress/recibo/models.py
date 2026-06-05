from django.db import models

# REGLA DE ORO: Borramos las importaciones directas para evitar el error circular
# No importa Pedido ni MetodoPago aquí arriba.

class Recibo(models.Model):
    """
    Es el documento contable de la transacción.
    Contiene el desglose financiero final.
    """
    
    # Un pedido tiene un único recibo final. 
    # Usamos 'app_name.ModelName' entre comillas.
    pedido = models.OneToOneField(
        'pedido.Pedido', 
        on_delete=models.CASCADE, 
        related_name='recibo'
    )
    
    # Usamos 'metodo_pago.MetodoPago' entre comillas.
    metodo_pago = models.ForeignKey(
        'metodo_pago.MetodoPago', 
        on_delete=models.PROTECT
    )
    
    fecha_emision = models.DateTimeField(auto_now_add=True)
    
    # Desglose financiero
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    iva_total = models.DecimalField(max_digits=10, decimal_places=2)
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Para control de puntos de fidelidad
    puntos_ganados = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Recibo / Factura"
        verbose_name_plural = "Recibos / Facturas"
        db_table = "recibo_recibo"

    def __str__(self):
        # Django resolverá estas relaciones en tiempo de ejecución sin problemas
        return f"Recibo #{self.id} - Pedido #{self.pedido.id}"