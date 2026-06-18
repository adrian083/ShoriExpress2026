from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rol', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rol',
            name='nombre_rol',
            field=models.CharField(max_length=30, unique=True, verbose_name='Nombre del Rol'),
        ),
    ]
