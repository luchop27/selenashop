# Generated migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_ciudad_usuario_ciudad'),
    ]

    operations = [
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('codigo', models.CharField(blank=True, max_length=10, null=True)),
                ('activa', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Provincia',
                'verbose_name_plural': 'Provincias',
                'ordering': ['nombre'],
            },
        ),
        migrations.RemoveField(
            model_name='ciudad',
            name='codigo_postal',
        ),
        migrations.RemoveField(
            model_name='ciudad',
            name='nombre',
        ),
        migrations.AddField(
            model_name='ciudad',
            name='nombre',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ciudad',
            name='codigo_postal',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='ciudad',
            name='provincia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ciudades', to='usuarios.provincia'),
        ),
        migrations.AlterUniqueTogether(
            name='ciudad',
            unique_together={('nombre', 'provincia')},
        ),
        migrations.AddField(
            model_name='usuario',
            name='provincia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usuarios', to='usuarios.provincia'),
        ),
    ]
