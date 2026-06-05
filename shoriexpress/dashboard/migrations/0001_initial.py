# Generated migration for ConfiguracionSistema model

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracionSistema',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_sistema', models.CharField(default='ShoriExpress', help_text='Nombre del negocio', max_length=100)),
                ('hora_apertura', models.TimeField(default=datetime.time(8, 0), help_text='Hora de apertura (ej: 08:00)')),
                ('hora_cierre', models.TimeField(default=datetime.time(19, 0), help_text='Hora de cierre (ej: 19:00)')),
                ('porcentaje_iva', models.DecimalField(decimal_places=2, default=19.0, help_text='Porcentaje de IVA a aplicar', max_digits=5)),
                ('umbral_bonos', models.DecimalField(decimal_places=2, default=50000.0, help_text='Monto mínimo de compra para ganar bono de fidelidad', max_digits=10)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Configuración del Sistema',
                'verbose_name_plural': 'Configuración del Sistema',
                'db_table': 'dashboard_configuracion',
            },
        ),
    ]
