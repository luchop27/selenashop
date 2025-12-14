#!/usr/bin/env python
"""
Script de prueba para la integración con WhatsApp Business API de Meta

Uso:
    python test_whatsapp.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
from core.whatsapp_utils import enviar_mensaje_whatsapp, generar_link_whatsapp_web
from core.models import Pedido

def test_credenciales():
    """Verifica que las credenciales estén configuradas"""
    print("\n" + "="*60)
    print("🔍 VERIFICANDO CREDENCIALES DE WHATSAPP")
    print("="*60 + "\n")
    
    verificaciones = {
        'WHATSAPP_PHONE_NUMBER_ID': settings.WHATSAPP_PHONE_NUMBER_ID,
        'WHATSAPP_BUSINESS_ACCOUNT_ID': settings.WHATSAPP_BUSINESS_ACCOUNT_ID,
        'WHATSAPP_ACCESS_TOKEN': settings.WHATSAPP_ACCESS_TOKEN,
        'WHATSAPP_ADMIN_NUMBER': settings.WHATSAPP_ADMIN_NUMBER,
    }
    
    todo_configurado = True
    
    for clave, valor in verificaciones.items():
        if not valor or valor.startswith('YOUR_'):
            print(f"❌ {clave}: NO CONFIGURADO")
            todo_configurado = False
        else:
            # Mostrar valor parcialmente por seguridad
            if 'TOKEN' in clave:
                valor_mostrado = valor[:20] + '...' if len(valor) > 20 else valor
            else:
                valor_mostrado = valor
            print(f"✅ {clave}: {valor_mostrado}")
    
    print()
    return todo_configurado


def test_envio_mensaje():
    """Envía un mensaje de prueba"""
    print("="*60)
    print("📤 ENVIANDO MENSAJE DE PRUEBA")
    print("="*60 + "\n")
    
    mensaje = """🧪 *MENSAJE DE PRUEBA* 🧪

Hola, este es un mensaje de prueba para verificar que la integración de WhatsApp está funcionando correctamente.

✅ Si recibes este mensaje, todo está configurado correctamente.

📱 *Vórtice Ecuador - Moda con estilo*"""
    
    print(f"📞 Enviando a: {settings.WHATSAPP_ADMIN_NUMBER}")
    print(f"📝 Mensaje:\n{mensaje}\n")
    
    resultado = enviar_mensaje_whatsapp(
        numero_destino=settings.WHATSAPP_ADMIN_NUMBER,
        mensaje=mensaje
    )
    
    if resultado.get('success'):
        print(f"✅ ¡ÉXITO! Mensaje enviado")
        print(f"   Message ID: {resultado.get('message_id')}")
        print(f"   {resultado.get('message')}")
        return True
    else:
        print(f"❌ ERROR al enviar: {resultado.get('message')}")
        if 'error_detail' in resultado:
            print(f"   Detalles: {resultado.get('error_detail')}")
        return False


def test_link_whatsapp():
    """Genera un link de WhatsApp Web como alternativa"""
    print("="*60)
    print("🔗 LINK DE WHATSAPP WEB (ALTERNATIVA)")
    print("="*60 + "\n")
    
    link = generar_link_whatsapp_web(
        numero_destino=settings.WHATSAPP_ADMIN_NUMBER,
        mensaje_preview='Mensaje de prueba desde Django'
    )
    
    print(f"📱 Abre este link para enviar un mensaje manualmente:")
    print(f"\n{link}\n")


def test_ultimo_pedido():
    """Prueba el formateo de un pedido real"""
    print("="*60)
    print("📦 PROBANDO CON ÚLTIMO PEDIDO")
    print("="*60 + "\n")
    
    try:
        pedido = Pedido.objects.latest('created_at')
        
        from core.whatsapp_utils import formatear_mensaje_pedido
        
        print(f"📋 Pedido encontrado: {pedido.numero_pedido}")
        print(f"👤 Cliente: {pedido.first_name} {pedido.last_name}")
        print(f"\n📝 VISTA PREVIA DEL MENSAJE:\n")
        print(formatear_mensaje_pedido(pedido))
        
    except Pedido.DoesNotExist:
        print("⚠️ No hay pedidos en la base de datos para probar")


def main():
    """Ejecuta todas las pruebas"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "🧪 TEST DE WHATSAPP BUSINESS API" + " "*16 + "║")
    print("╚" + "="*58 + "╝")
    
    # Test 1: Credenciales
    configurado = test_credenciales()
    
    if not configurado:
        print("\n⚠️  NOTA: Algunas credenciales no están configuradas.")
        print("   Por favor, revisa el archivo WHATSAPP_SETUP.md para obtener instrucciones.\n")
        return
    
    # Test 2: Enviar mensaje
    print("\n¿Deseas enviar un mensaje de prueba? (s/n): ", end='')
    respuesta = input().strip().lower()
    
    if respuesta == 's':
        test_envio_mensaje()
    
    # Test 3: Link de WhatsApp
    test_link_whatsapp()
    
    # Test 4: Último pedido
    test_ultimo_pedido()
    
    print("\n" + "="*60)
    print("✨ TEST COMPLETADO")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
