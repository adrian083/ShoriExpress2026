from django.db import migrations


def crear_efectivo(apps, schema_editor):
    MetodoPago = apps.get_model("metodo_pago", "MetodoPago")
    MetodoPago.objects.get_or_create(
        nombre_metodo="Efectivo",
        defaults={
            "descripcion": "Pago en efectivo (domicilio o punto de venta)",
            "esta_activo": True,
        },
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("metodo_pago", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_efectivo, noop_reverse),
    ]
