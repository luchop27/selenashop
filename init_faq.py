"""
Script para inicializar preguntas frecuentes de ejemplo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.ayudas.models import CategoriaFAQ, PreguntaFrecuente

# Limpiar datos previos (opcional)
# CategoriaFAQ.objects.all().delete()

# Crear categorías
categoria_compras = CategoriaFAQ.objects.get_or_create(
    nombre="Información de Compra",
    defaults={"orden": 1, "activo": True}
)[0]

categoria_pago = CategoriaFAQ.objects.get_or_create(
    nombre="Formas de Pago",
    defaults={"orden": 2, "activo": True}
)[0]

categoria_envios = CategoriaFAQ.objects.get_or_create(
    nombre="Envíos y Entregas",
    defaults={"orden": 3, "activo": True}
)[0]

categoria_devoluciones = CategoriaFAQ.objects.get_or_create(
    nombre="Devoluciones y Cambios",
    defaults={"orden": 4, "activo": True}
)[0]

categoria_cuenta = CategoriaFAQ.objects.get_or_create(
    nombre="Mi Cuenta",
    defaults={"orden": 5, "activo": True}
)[0]

# Preguntas para Información de Compra
PreguntaFrecuente.objects.get_or_create(
    pregunta="¿Cómo realizo una compra en Selena Shop?",
    categoria=categoria_compras,
    defaults={
        "respuesta": "<p>El proceso es muy sencillo:</p><ol><li>Busca los productos que deseas</li><li>Agrega al carrito</li><li>Procede al pago</li><li>Completa tus datos de envío</li><li>Confirma tu pedido</li></ol>",
        "activo": True,
        "orden": 1
    }
)

PreguntaFrecuente.objects.get_or_create(
    pregunta="¿Puedo cambiar mi pedido después de hacerlo?",
    categoria=categoria_compras,
    defaults={
        "respuesta": "<p>Si el pedido aún no ha sido procesado por nuestro equipo, podemos modificarlo. Contáctanos lo antes posible a través de nuestro formulario de contacto o WhatsApp.</p>",
        "activo": True,
        "orden": 2
    }
)

# Preguntas para Formas de Pago
PreguntaFrecuente.objects.get_or_create(
    pregunta="¿Qué métodos de pago aceptan?",
    categoria=categoria_pago,
    defaults={
        "respuesta": "<p>Aceptamos:</p><ul><li>Tarjeta de crédito (Visa, Mastercard)</li><li>Tarjeta de débito</li><li>Transferencia bancaria</li><li>PayPal</li></ul>",
        "activo": True,
        "orden": 1
    }
)

PreguntaFrecuente.objects.get_or_create(
    pregunta="¿Es seguro pagar con mi tarjeta?",
    categoria=categoria_pago,
    defaults={
        "respuesta": "<p>Sí, utilizamos encriptación SSL de 256 bits y protocolos de seguridad estándar de la industria. Tus datos de pago nunca se almacenan en nuestros servidores.</p>",
        "activo": True,
        "orden": 2
    }
)

# Preguntas para Envíos
PreguntaFrecuente.objects.get_or_create(
    pregunta="¿Cuánto tiempo demora la entrega?",
    categoria=categoria_envios,
    defaults={
        "respuesta": "<p>El tiempo de entrega varía según tu ubicación:</p><ul><li><strong>Zona metropolitana:</strong> 2-3 días hábiles</li><li><strong>Provincia:</strong> 5-7 días hábiles</li><li><strong>Envíos a diferentes regiones:</strong> Consultar disponibilidad</li></ul>",
        "activo": True,
        "orden": 1
    }
)

PreguntaFrecuente.objects.get_or_create(
    pregunta="¿Realizan envíos a todo el país?",
    categoria=categoria_envios,
    defaults={
        "respuesta": "<p>Sí, realizamos envíos a nivel nacional. Contamos con alianzas con las principales empresas de logística para garantizar entregas seguras en todo el país.</p>",
        "activo": True,
        "orden": 2
    }
)

PreguntaFrecuente.objects.get_or_create(
    pregunta="¿Puedo rastrear mi pedido?",
    categoria=categoria_envios,
    defaults={
        "respuesta": "<p>Sí, recibirás un número de seguimiento por email una vez que tu pedido sea despachado. Podrás rastrear tu paquete en tiempo real desde nuestra plataforma.</p>",
        "activo": True,
        "orden": 3
    }
)

# Preguntas para Devoluciones
PreguntaFrecuente.objects.get_or_create(
    pregunta="¿Cuál es la política de devoluciones?",
    categoria=categoria_devoluciones,
    defaults={
        "respuesta": "<p>Contamos con una política de 30 días para devoluciones. El producto debe estar en perfecto estado y con su embalaje original. Los gastos de devolución corren por cuenta del cliente.</p>",
        "activo": True,
        "orden": 1
    }
)

PreguntaFrecuente.objects.get_or_create(
    pregunta="¿Cómo solicito una devolución?",
    categoria=categoria_devoluciones,
    defaults={
        "respuesta": "<p>Contacta con nuestro equipo de servicio al cliente proporcionando tu número de pedido y el motivo de la devolución. Te enviaremos las instrucciones para proceder con el retorno del producto.</p>",
        "activo": True,
        "orden": 2
    }
)

# Preguntas para Mi Cuenta
PreguntaFrecuente.objects.get_or_create(
    pregunta="¿Cómo creo una cuenta?",
    categoria=categoria_cuenta,
    defaults={
        "respuesta": "<p>Haz clic en 'Registrarse' en la esquina superior derecha. Completa el formulario con tu email, nombre y contraseña. ¡Eso es todo!</p>",
        "activo": True,
        "orden": 1
    }
)

PreguntaFrecuente.objects.get_or_create(
    pregunta="¿Olvidé mi contraseña, qué hago?",
    categoria=categoria_cuenta,
    defaults={
        "respuesta": "<p>Haz clic en 'Olvidé mi contraseña' en la página de inicio de sesión. Ingresa tu email y recibirás un enlace para restablecer tu contraseña en unos minutos.</p>",
        "activo": True,
        "orden": 2
    }
)

print("✓ Categorías de FAQ inicializadas correctamente")
print("✓ Preguntas frecuentes agregadas exitosamente")
