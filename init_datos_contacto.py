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
        'direccion': 'Av. Principal 123, Quito, Ecuador',
        'email': 'info@selenashop.com',
        'telefono': '+593 99 999 9999',
        'google_maps_url': 'https://maps.app.goo.gl/uRg725z6e2ViQjAh7',
        'facebook': 'https://www.facebook.com/selenamaite.ec/?ref=pl_edit_xav_ig_profile_page_web#',
        'instagram': 'https://www.instagram.com/selenaonlineshop_ec?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw==',
        'tiktok': '',
        'twitter': '',
    }
)

if created:
    print("✓ Datos de contacto inicializados correctamente")
else:
    print("✓ Datos de contacto ya existían")

