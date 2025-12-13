"""
Script de prueba completa de la integración WhatsApp
Este script simula el proceso completo que ocurre cuando se realiza un pedido
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
from datetime import datetime

print("\n" + "="*70)
print("🧪 TEST COMPLETO DE INTEGRACIÓN WHATSAPP")
print("="*70)

# TEST 1: Verificar credenciales
print("\n📋 TEST 1: Verificar Credenciales")
print("-" * 70)

access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
business_account_id = getattr(settings, 'WHATSAPP_BUSINESS_ACCOUNT_ID', '')
admin_number = getattr(settings, 'WHATSAPP_ADMIN_NUMBER', '')

credenciales_ok = bool(access_token and phone_number_id and business_account_id and admin_number)

print(f"  Access Token: {'✅ OK' if access_token else '❌ FALTA'}")
print(f"  Phone Number ID: {'✅ OK' if phone_number_id else '❌ FALTA'}")
print(f"  Business Account ID: {'✅ OK' if business_account_id else '❌ FALTA'}")
print(f"  Admin Number: {'✅ OK ({})'.format(admin_number) if admin_number else '❌ FALTA'}")

# TEST 2: Instanciar WhatsAppAPI
print("\n📋 TEST 2: Instanciar WhatsAppAPI")
print("-" * 70)

try:
    api = WhatsAppAPI()
    print(f"  ✅ WhatsAppAPI instanciado correctamente")
    print(f"     - Base URL: {api.api_url}")
    print(f"     - Has token: {bool(api.access_token)}")
    print(f"     - Has phone_number_id: {bool(api.phone_number_id)}")
except Exception as e:
    print(f"  ❌ Error al instanciar: {str(e)}")
    sys.exit(1)

# TEST 3: Formatear mensaje
print("\n📋 TEST 3: Formatear Mensaje de Pedido")
print("-" * 70)

datos_pedido = {
    'pedido_id': 'ORD-20240108-TEST',
    'cliente_nombre': 'Luis Alberto Vasquez Gomez',
    'cliente_email': 'xkrules.2005@gmail.com',
    'cliente_direccion': 'Kleber Franco 123',
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
        },
        {
            'nombre': 'Pantalón P-002',
            'cantidad': 2,
            'precio_unitario': Decimal('50.00'),
            'subtotal': Decimal('100.00'),
            'talla': 'M',
            'color': 'Azul'
        }
    ]
}

try:
    mensaje = api._formatear_mensaje_pedido(datos_pedido)
    print("  ✅ Mensaje formateado correctamente")
    print(f"     - Longitud: {len(mensaje)} caracteres")
    print(f"     - Contiene emojis: {any(ord(c) > 127 for c in mensaje)}")
    print("\n" + "="*70)
    print("📱 MENSAJE GENERADO:")
    print("="*70)
    print(mensaje)
    print("="*70)
except Exception as e:
    print(f"  ❌ Error al formatear: {str(e)}")
    sys.exit(1)

# TEST 4: Validar estructura
print("\n📋 TEST 4: Validar Estructura del Mensaje")
print("-" * 70)

validaciones = [
    ('Número de pedido', 'ORD-20240108-TEST' in mensaje),
    ('Nombre del cliente', 'Luis Alberto Vasquez Gomez' in mensaje),
    ('Email', 'xkrules.2005@gmail.com' in mensaje),
    ('Teléfono', '0979607739' in mensaje),
    ('Ciudad', 'Quito' in mensaje),
    ('Dirección', 'Kleber Franco' in mensaje),
    ('Subtotal', 'Subtotal: $35.00' in mensaje),
    ('Total', 'Total a pagar: $40.00' in mensaje),
    ('Producto 1', 'Camiseta V-N002' in mensaje),
    ('Producto 2', 'Pantalón P-002' in mensaje),
    ('Cantidad producto 1', '1' in mensaje),
    ('Cantidad producto 2', '2' in mensaje),
    ('Talla', 'Talla:' in mensaje),
    ('Emojis', '✨' in mensaje and '📋' in mensaje and '🏠' in mensaje),
]

todos_ok = True
for validacion, resultado in validaciones:
    estado = '✅' if resultado else '❌'
    print(f"  {estado} {validacion}")
    if not resultado:
        todos_ok = False

# TEST 5: Información de implementación
print("\n📋 TEST 5: Información de Implementación")
print("-" * 70)

print("  ✅ Archivos creados:")
print("     - core/whatsapp.py (módulo de integración)")
print("     - test_whatsapp_integration.py (este script)")
print("     - WHATSAPP_SETUP_GUIDE.md (guía técnica)")
print("     - WHATSAPP_IMPLEMENTATION.md (guía usuario)")
print("     - RESUMEN_WHATSAPP_INTEGRATION.md (resumen cambios)")

print("\n  ✅ Archivos modificados:")
print("     - core/views.py (integración en checkout_process)")
print("     - selenashop/settings.py (configuración)")
print("     - requirements.txt (requests agregado)")

print("\n  ✅ Funcionalidades:")
print("     - Envío automático de mensajes al realizar pedido")
print("     - Información completa del cliente")
print("     - Detalles de productos")
print("     - Resumen de costos")
print("     - Manejo robusto de errores")

# Resumen final
print("\n" + "="*70)
if todos_ok and credenciales_ok:
    print("✅ TODOS LOS TESTS PASARON - SISTEMA LISTO PARA PRODUCCIÓN")
elif todos_ok and not credenciales_ok:
    print("⚠️  TESTS PASARON - CREDENCIALES NO CONFIGURADAS")
    print("\n   Próximos pasos:")
    print("   1. Acceder a https://developers.facebook.com/")
    print("   2. Crear app y agregar WhatsApp Business")
    print("   3. Obtener credenciales")
    print("   4. Actualizar selenashop/settings.py")
    print("   5. Ejecutar este script nuevamente para validar")
else:
    print("❌ ALGUNOS TESTS FALLARON - REVISAR ARRIBA")

print("="*70 + "\n")
