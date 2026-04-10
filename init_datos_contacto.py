"""
Script para inicializar datos de contacto
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.ayudas.models import DatosContacto

# Crear o actualizar datos de contacto
datos, created = DatosContacto.objects.get_or_create(
    pk=1,
    defaults={
        'direccion': 'Av. 25 de Junio y Páez, Machala, El Oro.',
        'email': 'selenastore.oficial.ec@gmail.com',
        'telefono': '0979184413',
        'google_maps_url': 'https://maps.app.goo.gl/uRg725z6e2ViQjAh7',
        'facebook': 'https://www.facebook.com/selena.maite/',
        'instagram': 'https://www.instagram.com/selenaboutique_ec/',
        'tiktok': '',
        'twitter': '',
    }
)

if created:
    print("✓ Datos de contacto inicializados correctamente")
else:
    print("✓ Datos de contacto ya existían")

