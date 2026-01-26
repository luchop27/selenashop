"""
Script para inicializar contenido en las Páginas de Ayuda
Ejecutar: python manage.py shell < scripts/init_paginas_ayuda.py
"""

from apps.ayudas.models import PaginaAyuda

# Limpiar registros anteriores
PaginaAyuda.objects.all().delete()

# Crear páginas de ayuda con contenido de ejemplo
paginas_ayuda = [
    {
        'tipo': 'terminos',
        'titulo': 'Términos y Condiciones',
        'contenido': '''
            <div class="box">
                <h4>Estos Términos y Condiciones Pueden Cambiar</h4>
                <p>Nos reservamos el derecho de actualizar o modificar estos términos y condiciones en cualquier momento sin previo aviso. 
                Tu uso de SelenaShop después de cualquier cambio constituye tu acuerdo de seguir y estar vinculado por los términos y 
                condiciones tal como han sido modificados. Por esta razón, te recomendamos que revises estos términos y condiciones 
                siempre que utilices este sitio web.</p>
            </div>
            
            <div class="box">
                <h4>Limitaciones de Responsabilidad</h4>
                <p>SelenaShop no asume ninguna responsabilidad y no será responsable por los daños o virus que puedan infectar tu 
                computadora, equipo de telecomunicaciones u otra propiedad causados por o que surjan de tu acceso, uso o navegación 
                en este sitio web.</p>
            </div>
            
            <div class="box">
                <h4>Derechos de Autor y Marcas Registradas</h4>
                <p>A menos que se indique lo contrario, el material en este sitio web, incluyendo textos, imágenes, ilustraciones, 
                software, clips de audio y video, está sujeto a los derechos de autor y marcas registradas de SelenaShop. 
                En consecuencia, el material en este sitio web no puede ser copiado, reproducido, modificado, publicado, transmitido 
                o distribuido, en todo o en parte, de cualquier forma, sin el consentimiento previo por escrito de SelenaShop.</p>
            </div>
            
            <div class="box">
                <h4>Productos, Contenido y Especificaciones</h4>
                <p>Todas las características, contenido, especificaciones, productos y precios descritos en este sitio web están 
                sujetos a cambio en cualquier momento sin previo aviso. Es tu responsabilidad verificar y obedecer todas las leyes 
                locales, estatales e internacionales aplicables con respecto a la posesión, uso y venta de cualquier artículo 
                comprado de este sitio web.</p>
            </div>
        '''
    },
    {
        'tipo': 'privacidad',
        'titulo': 'Política de Privacidad',
        'contenido': '''
            <div class="box">
                <h4>Información que Recopilamos</h4>
                <p>SelenaShop recopila información que nos proporcionas directamente, como cuando realizas una compra, creas una cuenta 
                o te comunicas con nosotros. Esta información puede incluir nombre, dirección de correo electrónico, número de teléfono, 
                dirección postal y detalles de pago.</p>
            </div>
            
            <div class="box">
                <h4>Cómo Utilizamos Tu Información</h4>
                <p>Utilizamos la información que recopilamos para procesar tus pedidos, comunicarnos contigo sobre tus compras, 
                personalizar tu experiencia de compra y mejorar nuestros servicios. También podemos usar tu información para enviar 
                promociones y actualizaciones, siempre respetando tus preferencias de privacidad.</p>
            </div>
            
            <div class="box">
                <h4>Protección de Datos</h4>
                <p>Nos comprometemos a proteger tu información personal. Utilizamos medidas de seguridad estándar de la industria 
                para proteger tus datos contra acceso no autorizado, alteración, divulgación o destrucción.</p>
            </div>
            
            <div class="box">
                <h4>Compartir Información</h4>
                <p>No compartimos tu información personal con terceros sin tu consentimiento, excepto en los casos necesarios para 
                procesar tus pedidos (como con nuestros socios de envío). Nos comprometemos a mantener tu privacidad y seguridad.</p>
            </div>
        '''
    },
    {
        'tipo': 'devoluciones',
        'titulo': 'Devoluciones y Cambios',
        'contenido': '''
            <div class="box">
                <h4>Política de Devoluciones</h4>
                <p>En SelenaShop, queremos que estés completamente satisfecho con tu compra. Si por alguna razón no estás satisfecho, 
                aceptamos devoluciones dentro de 30 días desde la fecha de compra. El artículo debe estar sin usar, en su empaque 
                original y en perfecto estado.</p>
            </div>
            
            <div class="box">
                <h4>Cómo Solicitar una Devolución</h4>
                <p>Para solicitar una devolución, ponte en contacto con nosotros a través de tu cuenta en SelenaShop o envía un 
                correo electrónico a info@selenashop.com. Proporciona el número de pedido y una breve descripción del motivo de la 
                devolución. Te enviaremos instrucciones sobre cómo devolver el artículo.</p>
            </div>
            
            <div class="box">
                <h4>Reembolsos</h4>
                <p>Una vez que recibamos y inspeccionemos tu artículo devuelto, procesaremos el reembolso en un plazo de 7-10 días 
                hábiles. El reembolso se acreditará en el método de pago original utilizado para la compra.</p>
            </div>
            
            <div class="box">
                <h4>Cambios</h4>
                <p>Si deseas cambiar un artículo por otro, también podemos ayudarte. Simplemente sigue el proceso de devolución y 
                realiza una nueva compra con el artículo que deseas. Alternativamente, contacta con nosotros para coordinar un cambio 
                directo.</p>
            </div>
            
            <div class="box">
                <h4>Exclusiones</h4>
                <p>Las devoluciones no son aceptables para artículos que hayan sido utilizados, lavados o modificados de cualquier 
                manera. Los artículos con defectos de fabricación pueden ser reemplazados sin costo adicional.</p>
            </div>
        '''
    },
    {
        'tipo': 'envios',
        'titulo': 'Envíos y Entregas',
        'contenido': '''
            <div class="box">
                <h4>Opciones de Envío</h4>
                <p>SelenaShop ofrece varias opciones de envío para satisfacer tus necesidades:</p>
                <ul style="margin-left: 20px; margin-top: 10px;">
                    <li><strong>Envío Estándar:</strong> 5-7 días hábiles - Gratis en compras mayores a $75</li>
                    <li><strong>Envío Expresado:</strong> 2-3 días hábiles - Costo adicional aplicable</li>
                    <li><strong>Envío Prioritario:</strong> 1 día hábil - Costo adicional aplicable</li>
                </ul>
            </div>
            
            <div class="box">
                <h4>Costos de Envío</h4>
                <p>Los costos de envío se calculan según el peso del paquete, la distancia de entrega y la opción de envío seleccionada. 
                Verás una estimación de los costos de envío antes de completar tu compra.</p>
            </div>
            
            <div class="box">
                <h4>Tracking de Pedidos</h4>
                <p>Una vez que tu pedido sea enviado, recibirás un número de seguimiento por correo electrónico. Puedes usar este número 
                para rastrear el estado de tu envío en tiempo real a través de nuestro sitio web o directamente en el sitio del 
                transportista.</p>
            </div>
            
            <div class="box">
                <h4>Entregas Internacionales</h4>
                <p>Realizamos envíos a muchos países. Los tiempos de entrega para entregas internacionales varían según el destino, 
                pero generalmente oscilan entre 10-21 días hábiles. Ten en cuenta que pueden aplicarse aranceles y impuestos de 
                aduana según las leyes del país de destino.</p>
            </div>
            
            <div class="box">
                <h4>Paquetes Dañados o Perdidos</h4>
                <p>Si tu paquete llega dañado o se pierde durante el envío, contáctanos inmediatamente. Trabajaremos con el transportista 
                para resolver el problema y reemplazar tu artículo o emitir un reembolso completo.</p>
            </div>
        '''
    }
]

# Insertar páginas de ayuda
for pagina_data in paginas_ayuda:
    pagina, created = PaginaAyuda.objects.get_or_create(
        tipo=pagina_data['tipo'],
        defaults={
            'titulo': pagina_data['titulo'],
            'contenido': pagina_data['contenido'],
            'activo': True
        }
    )
    if created:
        print(f"✓ Creada página: {pagina_data['titulo']}")
    else:
        print(f"✓ Ya existe página: {pagina_data['titulo']}")

print("\n✅ Inicialización completada. Puedes editar el contenido desde el admin de Django.")
