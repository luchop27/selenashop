"""
Script para poblar las páginas de información en la base de datos
Ejecutar: python manage.py shell < setup_info_pages.py
"""

from core.models import InfoPage

# 1. Términos y Condiciones
terms_html = """
<div class="box">
    <h4>Términos y Condiciones Generales</h4>
    <p>Bienvenido a SelenaShop. Al acceder y utilizar este sitio web, aceptas estar sujeto a estos términos y condiciones.</p>
</div>
<div class="box">
    <h4>Cambios en los Términos</h4>
    <p>Nos reservamos el derecho de actualizar o modificar estos términos y condiciones en cualquier momento. Tu continuación en el uso de este sitio web constituye tu aceptación de los cambios realizados.</p>
</div>
<div class="box">
    <h4>Uso del Sitio Web</h4>
    <p>Aceptas utilizar este sitio web únicamente para propósitos legales y de conformidad con todas las leyes y regulaciones aplicables. No debes usar este sitio de manera que pueda dañar, inhabilitar, sobrecargar o perjudicar el sitio web o interferir con su funcionamiento.</p>
</div>
<div class="box">
    <h4>Limitación de Responsabilidad</h4>
    <p>SelenaShop no será responsable por ningún daño directo, indirecto, incidental, especial o consecuente resultante del uso de nuestro sitio web o productos.</p>
</div>
<div class="box">
    <h4>Derechos de Autor</h4>
    <p>Todo el contenido en este sitio web, incluyendo textos, imágenes, gráficos, logos y software, está protegido por derechos de autor y es propiedad de SelenaShop. No se permite la reproducción o distribución sin autorización previa.</p>
</div>
"""

# 2. Política de Privacidad
privacy_html = """
<div class="box">
    <h4>Privacidad de Datos</h4>
    <p>En SelenaShop, valoramos tu privacidad. Esta política explica cómo recopilamos, utilizamos y protegemos tu información personal.</p>
</div>
<div class="box">
    <h4>Información que Recopilamos</h4>
    <p>Recopilamos información que nos proporcionas voluntariamente, como tu nombre, correo electrónico, dirección y detalles de pago cuando realizas una compra o te registras en nuestro sitio.</p>
</div>
<div class="box">
    <h4>Uso de tu Información</h4>
    <p>Utilizamos tu información para procesar pedidos, mejorar nuestros servicios, comunicarnos contigo sobre promociones y actualizaciones, y proteger contra el fraude.</p>
</div>
<div class="box">
    <h4>Seguridad de Datos</h4>
    <p>Implementamos medidas de seguridad estrictas para proteger tu información personal. Tu información está encriptada y almacenada de forma segura.</p>
</div>
<div class="box">
    <h4>Compartir Información</h4>
    <p>No compartimos tu información personal con terceros sin tu consentimiento, excepto cuando sea necesario para procesar tu pedido o cumplir con la ley.</p>
</div>
<div class="box">
    <h4>Contacto</h4>
    <p>Si tienes preguntas sobre nuestras prácticas de privacidad, por favor contáctanos en info@selenashop.com</p>
</div>
"""

# 3. Devoluciones y Cambios
delivery_html = """
<div class="box">
    <h4>Política de Devoluciones</h4>
    <p>Queremos que estés completamente satisfecho con tu compra. Si no lo estás, ofrecemos una política de devolución fácil.</p>
</div>
<div class="box">
    <h4>Plazo de Devolución</h4>
    <p>Tienes 14 días a partir de la fecha de entrega para devolver tu artículo. El producto debe estar en condiciones de venta, sin usar y con todas las etiquetas originales.</p>
</div>
<div class="box">
    <h4>Proceso de Devolución</h4>
    <p>Para iniciar una devolución, contacta a nuestro equipo de servicio al cliente. Te proporcionaremos una etiqueta de envío prepagada. Una vez que recibamos tu artículo, procesaremos tu reembolso en 5-7 días hábiles.</p>
</div>
<div class="box">
    <h4>Cambios</h4>
    <p>Ofrecemos cambios sin costo si deseas un tamaño o color diferente. Simplemente contáctanos con los detalles de tu pedido y procesaremos el cambio rápidamente.</p>
</div>
<div class="box">
    <h4>Artículos en Oferta</h4>
    <p>Los artículos marcados como "En Oferta" o con descuento especial no son elegibles para devolución. Sin embargo, puedes cambiarlos por otro tamaño o color.</p>
</div>
<div class="box">
    <h4>Artículos Defectuosos</h4>
    <p>Si recibes un artículo defectuoso o dañado, contáctanos inmediatamente. Reemplazaremos el artículo o procesaremos un reembolso completo, incluyendo el envío.</p>
</div>
"""

# 4. Envíos
shipping_html = """
<div class="box">
    <h4>Opciones de Envío</h4>
    <p>En SelenaShop ofrecemos varias opciones de envío para que puedas elegir la que mejor se adapte a tus necesidades.</p>
</div>
<div class="box">
    <h4>Envío Estándar</h4>
    <p>El envío estándar toma entre 5-7 días hábiles. Los costos se calcularán según la ubicación y el peso del paquete.</p>
</div>
<div class="box">
    <h4>Envío Express</h4>
    <p>El envío express garantiza entrega en 2-3 días hábiles. Ideal para cuando necesitas tu pedido rápidamente. Se aplica costo adicional.</p>
</div>
<div class="box">
    <h4>Envío Gratis</h4>
    <p>Disfruta de envío gratis en compras mayores a $75 USD. Esta promoción se aplica automáticamente al carrito cuando alcances el monto mínimo.</p>
</div>
<div class="box">
    <h4>Rastreo de Pedido</h4>
    <p>Una vez que tu pedido sea despachado, recibirás un número de rastreo por correo electrónico. Puedes usarlo para seguir tu paquete en tiempo real.</p>
</div>
<div class="box">
    <h4>Entregas Internacionales</h4>
    <p>Enviamos a muchos países. Los tiempos de entrega varían según el destino. Se pueden aplicar aranceles y impuestos de importación.</p>
</div>
<div class="box">
    <h4>Entregas No Entregadas</h4>
    <p>Si tu paquete no puede ser entregado, nos pondremos en contacto contigo para hacer arreglos. Trabajamos contigo para asegurar que recibas tu pedido.</p>
</div>
"""

# Crear o actualizar los registros
pages_data = [
    {
        'slug': 'terms-conditions',
        'titulo': 'Términos y Condiciones',
        'contenido': terms_html,
        'seo_meta_description': 'Lee nuestros términos y condiciones de uso para SelenaShop'
    },
    {
        'slug': 'privacy-policy',
        'titulo': 'Política de Privacidad',
        'contenido': privacy_html,
        'seo_meta_description': 'Conoce cómo protegemos tu privacidad en SelenaShop'
    },
    {
        'slug': 'delivery-return',
        'titulo': 'Devoluciones y Cambios',
        'contenido': delivery_html,
        'seo_meta_description': 'Información sobre nuestra política de devoluciones y cambios'
    },
    {
        'slug': 'shipping',
        'titulo': 'Envíos',
        'contenido': shipping_html,
        'seo_meta_description': 'Conoce nuestras opciones de envío y costos de envío'
    },
]

for data in pages_data:
    page, created = InfoPage.objects.update_or_create(
        slug=data['slug'],
        defaults={
            'titulo': data['titulo'],
            'contenido': data['contenido'],
            'seo_meta_description': data['seo_meta_description'],
            'activo': True
        }
    )
    action = "creada" if created else "actualizada"
    print(f"✓ Página '{data['slug']}' {action} correctamente")

print("\n✓ Todas las páginas de información han sido configuradas exitosamente")
