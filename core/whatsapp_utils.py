"""
Utilidades para enviar mensajes a traves de WhatsApp Business API de Meta.
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def _credencial_configurada(valor):
    """Valida que una credencial no sea vacia ni placeholder."""
    if not valor:
        return False

    valor_normalizado = str(valor).strip()
    if not valor_normalizado:
        return False

    return not valor_normalizado.upper().startswith('YOUR_')


def enviar_notificacion_pedido(pedido):
    """
    Envía una notificación automática a WhatsApp del admin cuando se realiza un pedido.
    
    Args:
        pedido: Objeto Pedido con los datos del pedido realizado
    
    Returns:
        dict: Resultado del envío {'success': True/False, 'message': str, 'message_id': str}
    """
    
    # Verificar que tenemos los datos necesarios
    if not all([
        _credencial_configurada(settings.WHATSAPP_PHONE_NUMBER_ID),
        _credencial_configurada(settings.WHATSAPP_ACCESS_TOKEN),
        _credencial_configurada(settings.WHATSAPP_ADMIN_NUMBER),
    ]):
        logger.warning('WhatsApp: Credenciales no configuradas completamente')
        return {
            'success': False,
            'message': 'Credenciales de WhatsApp no configuradas'
        }
    
    # Formatear el mensaje
    mensaje = formatear_mensaje_pedido(pedido)
    
    # Enviar a través de la API de Meta
    resultado = enviar_mensaje_whatsapp(
        numero_destino=settings.WHATSAPP_ADMIN_NUMBER,
        mensaje=mensaje
    )
    
    return resultado


def formatear_mensaje_pedido(pedido):
    """
    Formatea el mensaje del pedido en formato compatible con WhatsApp.
    
    Args:
        pedido: Objeto Pedido
    
    Returns:
        str: Mensaje formateado
    """
    
    # Encabezado
    mensaje = f"""✨ *NUEVO PEDIDO #{pedido.numero_pedido}* ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 *DATOS DEL CLIENTE:*
👤 Nombre: {pedido.first_name} {pedido.last_name}
📧 Correo: {pedido.email}
📱 Teléfono: {pedido.phone}
🏠 Dirección: {pedido.address}
🏙️ Ciudad: {pedido.city}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 *DETALLES DEL PEDIDO:*"""
    
    # Agregar cada producto
    for i, item in enumerate(pedido.items.all(), 1):
        mensaje += f"""

🔹 *Producto {i}:* {item.nombre_producto}
   📏 Talla: {item.talla or 'N/A'}
   🎨 Color: {item.color or 'N/A'}
   📊 Cantidad: {item.cantidad}
   💵 Precio unitario: ${item.precio_unitario:.2f}
   📋 Subtotal: ${item.subtotal:.2f}"""
    
    # Notas si existen
    if pedido.order_note:
        mensaje += f"""

📝 *Notas adicionales:*
{pedido.order_note}"""
    
    # Resumen de totales
    mensaje += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 *RESUMEN DEL PEDIDO:*
🛍️ Subtotal: ${pedido.subtotal:.2f}
🚚 Costo de envío: ${pedido.shipping_cost:.2f}"""
    
    # Regalo si existe
    if pedido.gift_wrap:
        mensaje += f"\n🎁 Envoltura de regalo: ${pedido.gift_wrap_cost:.2f}"
    
    # Descuento si existe
    if pedido.discount_amount > 0:
        mensaje += f"\n💳 Descuento ({pedido.discount_code}): -${pedido.discount_amount:.2f}"
    
    # Total
    mensaje += f"""

✅ *TOTAL A PAGAR: ${pedido.total:.2f}*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💳 *Método de pago:*
{pedido.get_metodo_pago_display()}

🛍️ *Vórtice Ecuador - Moda con estilo*
✨ ¡Gracias por tu compra! ✨"""
    
    return mensaje


def enviar_mensaje_whatsapp(numero_destino, mensaje):
    """
    Envía un mensaje a través de WhatsApp Business API de Meta.
    
    Args:
        numero_destino (str): Número en formato internacional (ej: +593979607739)
        mensaje (str): Contenido del mensaje
    
    Returns:
        dict: {'success': True/False, 'message': str, 'message_id': str}
    """
    
    try:
        import requests
    except ImportError:
        logger.warning('WhatsApp: paquete requests no instalado. Se omite envio.')
        return {
            'success': False,
            'message': 'Notificacion de WhatsApp deshabilitada temporalmente'
        }

    try:
        # URL del endpoint de la API
        url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        # Headers
        headers = {
            'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
        }
        
        # Estructura del payload
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': numero_destino,
            'type': 'text',
            'text': {
                'preview_url': False,
                'body': mensaje
            }
        }
        
        # Realizar la solicitud
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Verificar respuesta
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', 'unknown')
            
            logger.info('WhatsApp: Mensaje enviado exitosamente. ID: %s', message_id)
            
            return {
                'success': True,
                'message': 'Notificación enviada a WhatsApp del administrador',
                'message_id': message_id
            }
        else:
            error_msg = response.text
            logger.error('WhatsApp: Error %s. %s', response.status_code, error_msg)
            
            return {
                'success': False,
                'message': 'No se pudo enviar la notificacion de WhatsApp',
                'error_detail': error_msg
            }
    
    except requests.exceptions.Timeout:
        logger.error('WhatsApp: Timeout al enviar el mensaje')
        return {
            'success': False,
            'message': 'Timeout al conectar con WhatsApp API'
        }
    
    except requests.exceptions.RequestException as exc:
        logger.error('WhatsApp: Error de conexion o solicitud. %s', str(exc))
        return {
            'success': False,
            'message': 'Error de conexión con WhatsApp API'
        }
    
    except Exception:
        logger.exception('WhatsApp: Error inesperado al enviar mensaje')
        return {
            'success': False,
            'message': 'Error inesperado al enviar la notificacion'
        }


def generar_mensaje_factura_cliente(pedido, request=None):
    """
    Genera un mensaje estilo FACTURA PROFESIONAL para que el cliente
    lo envíe por WhatsApp a la tienda al finalizar su compra.

    Incluye:
    - Encabezado de orden de compra con ID
    - Datos del cliente
    - Listado detallado de productos (talla, color, cantidad, precio)
    - Desglose de totales (subtotal, envío, descuento, total)
    - Link de seguimiento personalizado (vista web del pedido)
    - Instrucciones para enviar el comprobante de pago

    Args:
        pedido: Objeto Pedido ya guardado en la DB
        request: HttpRequest (opcional) para construir URLs absolutas

    Returns:
        str: Mensaje formateado listo para encodeURIComponent
    """

    # ── Encabezado ──────────────────────────────────────────────────────────
    mensaje = (
        "*ORDEN DE COMPRA - SELENA BOUTIQUE*\n"
        "--------------------------------\n\n"
        f"*Pedido:* #{pedido.numero_pedido}\n"
        f"*Cliente:* {pedido.first_name} {pedido.last_name}\n"
        f"*Ciudad:* {pedido.city}, {pedido.country}\n"
        f"*Telefono:* {pedido.phone}\n"
    )

    # ── Detalle de productos ─────────────────────────────────────────────────
    mensaje += "\n*DETALLE:*\n"
    for item in pedido.items.all():
        partes = []
        if item.talla:
            partes.append(item.talla)
        if item.color:
            partes.append(item.color)
        variantes_str = f" [{' / '.join(partes)}]" if partes else ""
        mensaje += f"  - {item.cantidad}x {item.nombre_producto}{variantes_str} - ${item.precio_unitario:.2f}\n"

    # ── Totales ──────────────────────────────────────────────────────────────
    mensaje += "\n--------------------------------\n"
    mensaje += f"Subtotal: ${pedido.subtotal:.2f}\n"

    if pedido.shipping_cost and pedido.shipping_cost > 0:
        mensaje += f"Envio: ${pedido.shipping_cost:.2f}\n"
    else:
        mensaje += "Envio: $0.00 (Gratis)\n"

    if pedido.gift_wrap and pedido.gift_wrap_cost:
        mensaje += f"Envoltura de regalo: ${pedido.gift_wrap_cost:.2f}\n"

    if pedido.discount_amount and pedido.discount_amount > 0:
        codigo = f" ({pedido.discount_code})" if pedido.discount_code else ""
        mensaje += f"Descuento{codigo}: -${pedido.discount_amount:.2f}\n"

    mensaje += f"\n*TOTAL A PAGAR: ${pedido.total:.2f}*\n"

    # ── Donde ver el pedido (sin link) ───────────────────────────────────────
    mensaje += (
        "\n--------------------------------\n"
        "Para ver tu pedido con las fotos de los productos:\n"
        "Ingresa a tu cuenta > Mis Pedidos\n"
    )

    # ── Instrucciones de pago ────────────────────────────────────────────────
    mensaje += (
        "\n*INSTRUCCIONES DE PAGO:*\n"
        "1. Realiza la transferencia al numero de cuenta indicado.\n"
        "2. Envia el comprobante a este WhatsApp.\n"
        "3. Tu pedido se procesara al confirmar el pago.\n"
        "\nGracias por comprar en Selena Boutique!"
    )

    return mensaje


def generar_link_whatsapp_web(numero_destino, mensaje_preview=''):
    """
    Genera un enlace para abrir WhatsApp Web o App con un mensaje predeterminado.
    
    Útil como fallback si la API falla, o para redirigir al usuario.
    
    Args:
        numero_destino (str): Número sin + (ej: 593979607739)
        mensaje_preview (str): Mensaje inicial (opcional)
    
    Returns:
        str: URL para abrir WhatsApp
    """
    
    # Remover caracteres especiales del número
    numero_limpio = numero_destino.replace('+', '').replace(' ', '').replace('-', '')
    
    # Crear URL
    if mensaje_preview:
        # Codificar el mensaje para la URL
        from urllib.parse import quote
        mensaje_encoded = quote(mensaje_preview)
        url = f"https://wa.me/{numero_limpio}?text={mensaje_encoded}"
    else:
        url = f"https://wa.me/{numero_limpio}"
    
    return url
