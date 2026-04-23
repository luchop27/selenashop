from django.db import migrations


def backfill_marca_basica(apps, schema_editor):
    Producto = apps.get_model('productos', 'Producto')

    for producto in Producto.objects.all().iterator():
        marca_limpia = (producto.marca or '').strip()
        if not marca_limpia:
            producto.marca = 'Básica'
            producto.save(update_fields=['marca'])
        elif marca_limpia != producto.marca:
            producto.marca = marca_limpia
            producto.save(update_fields=['marca'])


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0020_coleccion_imagen_mobile'),
    ]

    operations = [
        migrations.RunPython(backfill_marca_basica, migrations.RunPython.noop),
    ]
