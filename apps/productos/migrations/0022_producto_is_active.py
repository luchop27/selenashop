from django.db import migrations, models
from django.db.models import F


def backfill_producto_is_active(apps, schema_editor):
    Producto = apps.get_model("productos", "Producto")
    # Copiar el estado previo (`activo`) al nuevo campo (`is_active`)
    Producto.objects.all().update(is_active=F("activo"))


class Migration(migrations.Migration):
    dependencies = [
        ("productos", "0021_backfill_marca_basica"),
    ]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(backfill_producto_is_active, migrations.RunPython.noop),
    ]

