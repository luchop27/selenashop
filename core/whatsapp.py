"""
Módulo para enviar notificaciones por WhatsApp usando la API de Meta
"""
import requests
import logging
from django.conf import settings
from decimal import Decimal

logger = logging.getLogger(__name__)


class WhatsAppAPI:
    """Clase para manejar la integración con WhatsApp Business API"""
    
    def __init__(self):
        self.api_url = "https://graph.instagram.com/v18.0"
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
        self.access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
        self.business_account_id = getattr(settings, 'WHATSAPP_BUSINESS_ACCOUNT_ID', '')
    
    def enviar_mensaje_pedido(self, numero_destinatario, datos_pedido):
        """
        Envía un mensaje formateado con los detalles del pedido
        
        Args:
            numero_destinatario: Número de teléfono en formato internacional (ej: 593979607739)
            datos_pedido: Diccionario con los datos del pedido
        
        Returns:
            dict: Respuesta de la API o None si falla
        """
        try:
            if not self.access_token or not self.phone_number_id:
                logger.warning('WhatsApp API credentials no configuradas')
                return None
            
            mensaje = self._formatear_mensaje_pedido(datos_pedido)
            
            return self._enviar_mensaje_texto(numero_destinatario, mensaje)
        
        except Exception as e:
            logger.error(f'Error al enviar mensaje WhatsApp: {str(e)}')
            return None
    
    def _formatear_mensaje_pedido(self, datos_pedido):
        """Formatea el mensaje con los detalles del pedido"""
        
        pedido_id = datos_pedido.get('pedido_id', 'N/A')
        cliente_nombre = datos_pedido.get('cliente_nombre', 'Cliente')
        cliente_email = datos_pedido.get('cliente_email', '')
        cliente_direccion = datos_pedido.get('cliente_direccion', '')
        cliente_telefono = datos_pedido.get('cliente_telefono', '')
        cliente_ciudad = datos_pedido.get('cliente_ciudad', '')
        
        subtotal = datos_pedido.get('subtotal', Decimal('0'))
        envio = datos_pedido.get('envio', Decimal('0'))
        gift_wrap = datos_pedido.get('gift_wrap', Decimal('0'))
        descuento = datos_pedido.get('descuento', Decimal('0'))
        total = datos_pedido.get('total', Decimal('0'))
        
        items = datos_pedido.get('items', [])
        
        # Encabezado
        mensaje = "✨ *Pedido " + str(pedido_id) + " - Vórtice Ecuador* ✨\n"
        mensaje += "--------------------------------------\n"
        
        # Datos del cliente
        mensaje += "📋 *Datos del Cliente:*\n"
        mensaje += f"👤 Nombre: {cliente_nombre}\n"
        if cliente_email:
            mensaje += f"📧 Correo: {cliente_email}\n"
        if cliente_telefono:
            mensaje += f"📱 Teléfono: {cliente_telefono}\n"
        if cliente_ciudad:
            mensaje += f"🏙️ Ciudad: {cliente_ciudad}\n"
        if cliente_direccion:
            mensaje += f"🏠 Dirección: {cliente_direccion}\n"
        
        mensaje += "--------------------------------------\n"
        
        # Detalles del pedido
        mensaje += "📦 *Detalles del pedido:*\n"
        for item in items:
            nombre_producto = item.get('nombre', 'Producto sin nombre')
            cantidad = item.get('cantidad', 1)
            precio_unitario = item.get('precio_unitario', Decimal('0'))
            subtotal_item = item.get('subtotal', Decimal('0'))
            talla = item.get('talla', '')
            color = item.get('color', '')
            
            mensaje += f"\n🔹 *{nombre_producto}*\n"
            if talla:
                mensaje += f"   🔸 Talla: {talla}\n"
            if color:
                mensaje += f"   🔸 Color: {color}\n"
            mensaje += f"   🔸 Cantidad: {cantidad}\n"
            mensaje += f"   🔸 Precio unitario: ${float(precio_unitario):.2f}\n"
            mensaje += f"   🔸 Subtotal: ${float(subtotal_item):.2f}\n"
        
        mensaje += "\n--------------------------------------\n"
        
        # Resumen
        mensaje += "💰 *Resumen del pedido:*\n"
        mensaje += f"🛍️ Subtotal: ${float(subtotal):.2f}\n"
        
        if gift_wrap > 0:
            mensaje += f"🎁 Envoltura de regalo: ${float(gift_wrap):.2f}\n"
        
        if envio > 0:
            mensaje += f"🚚 Costo de envío: ${float(envio):.2f}\n"
        
        if descuento > 0:
            mensaje += f"🎟️ Descuento: -${float(descuento):.2f}\n"
        
        mensaje += f"✅ *Total a pagar: ${float(total):.2f}*\n"
        mensaje += "--------------------------------------\n\n"
        
        # Despedida
        mensaje += "¡Gracias! 😊\n\n"
        mensaje += "🛍️ *Vórtice Ecuador - Moda con estilo*"
        
        return mensaje
    
    def _enviar_mensaje_texto(self, numero_destinatario, texto):
        """Envía un mensaje de texto a través de WhatsApp API"""
        
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": numero_destinatario,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": texto
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Mensaje WhatsApp enviado exitosamente a {numero_destinatario}")
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar mensaje WhatsApp: {str(e)}")
            return None


def enviar_notificacion_pedido(pedido, detalles_pedido):
    """
    Función principal para enviar notificación de pedido por WhatsApp
    
    Args:
        pedido: Instancia del modelo Pedido
        detalles_pedido: Lista de diccionarios con los detalles de los items del pedido
    
    Returns:
        bool: True si se envió exitosamente, False en caso contrario
    """
    try:
        # Obtener el número del admin (puedes configurarlo en settings o buscarlo en BD)
        numero_admin = getattr(settings, 'WHATSAPP_ADMIN_NUMBER', '')
        
        if not numero_admin:
            logger.warning('Número de admin WhatsApp no configurado')
            return False
        
        # Preparar datos del pedido (usando los campos correctos del modelo Pedido)
        datos_pedido = {
            'pedido_id': pedido.numero_pedido,  # Usar el número de pedido único
            'cliente_nombre': f"{pedido.first_name} {pedido.last_name}",
            'cliente_email': pedido.email,
            'cliente_direccion': pedido.address,
            'cliente_telefono': pedido.phone,
            'cliente_ciudad': pedido.city,
            'subtotal': pedido.subtotal,
            'envio': Decimal('0'),  # Calcular envío si es necesario
            'gift_wrap': pedido.gift_wrap_cost,
            'descuento': pedido.discount_amount,
            'total': pedido.total,
            'items': detalles_pedido
        }
        
        # Enviar mensaje
        api = WhatsAppAPI()
        resultado = api.enviar_mensaje_pedido(numero_admin, datos_pedido)
        
        return resultado is not None
    
    except Exception as e:
        logger.error(f'Error en enviar_notificacion_pedido: {str(e)}')
        return False
