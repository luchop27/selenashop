"""
Context processors para apps/ayudas
Proporciona datos globales a todos los templates
"""
from .models import DatosContacto

def datos_contacto(request):
    """Proporciona los datos de contacto a todos los templates"""
    try:
        contacto = DatosContacto.objects.first()
        if contacto and contacto.email == 'info@selenashop.com':
            # Actualización automática de datos por defecto anteriores
            contacto.direccion = 'Av. 25 de Junio y Páez, Machala, El Oro'
            contacto.email = 'selenastore.oficial.ec@gmail.com'
            contacto.telefono = '0979184413'
            contacto.save()
        elif not contacto:
            contacto = DatosContacto()
            contacto.save()
    except:
        contacto = DatosContacto()
    
    return {
        'datos_contacto': contacto
    }
