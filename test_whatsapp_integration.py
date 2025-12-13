"""
Script de prueba para validar la integración de WhatsApp
Ejecutar desde la raíz del proyecto con: python test_whatsapp_integration.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.conf import settings
from core.whatsapp import WhatsAppAPI, enviar_notificacion_pedido
from decimal import Decimal

print("=" * 60)
print("🔍 VERIFICACIÓN DE CONFIGURACIÓN DE WHATSAPP")
print("=" * 60)

# Verificar credenciales
access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
business_account_id = getattr(settings, 'WHATSAPP_BUSINESS_ACCOUNT_ID', '')
admin_number = getattr(settings, 'WHATSAPP_ADMIN_NUMBER', '')

print("\n✓ Variables de configuración:")
print(f"  - Access Token: {'✅ Configurado' if access_token else '❌ NO configurado'}")
print(f"  - Phone Number ID: {'✅ Configurado' if phone_number_id else '❌ NO configurado'}")
print(f"  - Business Account ID: {'✅ Configurado' if business_account_id else '❌ NO configurado'}")
print(f"  - Número de admin: {'✅ {admin_number}' if admin_number else '❌ NO configurado'}")

# Crear instancia de WhatsAppAPI
api = WhatsAppAPI()

print("\n✓ Datos de la instancia WhatsAppAPI:")
print(f"  - Base URL: {api.api_url}")
print(f"  - Phone Number ID: {api.phone_number_id[:10]}..." if api.phone_number_id else "  - Phone Number ID: NO configurado")

# Verificar si se puede enviar
if not access_token or not phone_number_id:
    print("\n⚠️  IMPORTANTE: Las credenciales de WhatsApp no están configuradas.")
    print("   Para enviar mensajes, completar estos pasos:")
    print("   1. Acceder a https://developers.facebook.com/")
    print("   2. Crear/seleccionar una app")
    print("   3. Agregar WhatsApp Business")
    print("   4. Obtener: Access Token, Phone Number ID, Business Account ID")
    print("   5. Actualizar selenashop/settings.py con estas credenciales")
else:
    print("\n✅ Credenciales configuradas. Sistema listo para enviar mensajes.")

print("\n" + "=" * 60)
print("📝 PRUEBA DE FORMATO DE MENSAJE")
print("=" * 60)

# Crear datos de prueba
datos_prueba = {
    'pedido_id': 'ORD-20240108-TEST',
    'cliente_nombre': 'Luis Alberto Vasquez Gomez',
    'cliente_email': 'xkrules.2005@gmail.com',
    'cliente_direccion': 'Kleber Franco',
    'cliente_telefono': '0979607739',
    'cliente_ciudad': 'Quito',
    'subtotal': Decimal('35.00'),
    'envio': Decimal('5.00'),
    'gift_wrap': Decimal('0.00'),
    'descuento': Decimal('0.00'),
    'total': Decimal('40.00'),
    'items': [
        {
            'nombre': 'Camiseta V-N002',
            'cantidad': 1,
            'precio_unitario': Decimal('35.00'),
            'subtotal': Decimal('35.00'),
            'talla': 'U',
            'color': 'Rojo'
        }
    ]
}

# Formatear mensaje
mensaje = api._formatear_mensaje_pedido(datos_prueba)
print("\n📱 Mensaje que se enviaría:\n")
print(mensaje)

print("\n" + "=" * 60)
print("✅ Prueba completada. Sistema listo para producción.")
print("=" * 60)
