from apps.productos.models import Categoria
from .cart import Cart
from .models import DeliveryReturnInfo


def categorias_menu(request):
    """
    Context processor para hacer las categorías disponibles en todas las plantillas.
    Retorna categorías principales con sus subcategorías.
    """
    categorias_principales = Categoria.objects.filter(
        estado=True, 
        padre__isnull=True
    ).prefetch_related('subcategorias').order_by('nombre')
    
    return {
        'categorias_menu': categorias_principales
    }


def cart(request):
    """
    Context processor para hacer el carrito disponible en todas las plantillas
    """
    return {'cart': Cart(request)}


def delivery_return_info(request):
    """
    Context processor para hacer la información de Delivery & Return disponible en todas las plantillas
    """
    try:
        info = DeliveryReturnInfo.objects.filter(activo=True).first()
    except:
        info = None
    
    return {'delivery_return_info': info}
