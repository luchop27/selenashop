"""
Context processors para apps/ayudas
Proporciona datos globales a todos los templates
"""
from .models import DatosContacto

def datos_contacto(request):
    """Proporciona los datos de contacto a todos los templates"""
    try:
        contacto = DatosContacto.objects.first() or DatosContacto()
    except:
        contacto = DatosContacto()
    
    return {
        'datos_contacto': contacto
    }
