from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0004_auto_20260423_2151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='direccion',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
