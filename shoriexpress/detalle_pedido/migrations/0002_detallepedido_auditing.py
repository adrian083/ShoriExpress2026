# Generated migration for DetallePedido enhancements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detalle_pedido', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='detallepedido',
            name='stock_remanente_post_venta',
            field=models.PositiveIntegerField(blank=True, help_text='Stock restante del insumo principal después de esta venta', null=True),
        ),
        migrations.AddField(
            model_name='detallepedido',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
