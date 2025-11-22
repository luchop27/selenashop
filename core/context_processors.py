from apps.productos.models import Categoria, Producto
from django.db.models import Avg, Q
from .cart import Cart
from .models import DeliveryReturnInfo


def categorias_menu(request):
    """
    Context processor para hacer las categorías disponibles en todas las plantillas.
    Retorna categorías principales con sus subcategorías y productos mejor puntuados.
    """
    # Obtener categorías principales con Ropa primero
    from django.db.models import Case, When, Value, IntegerField
    
    categorias_principales = Categoria.objects.filter(
        estado=True, 
        padre__isnull=True
    ).prefetch_related('subcategorias').annotate(
        orden_custom=Case(
            When(nombre__iexact='Ropa', then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('orden_custom', 'nombre')
    
    # 3 productos recientes SOLO de la categoría principal "Ropa" y sus subcategorías
    try:
        categoria_ropa = Categoria.objects.get(nombre__iexact='Ropa', padre__isnull=True)
        subcategorias_ids = list(categoria_ropa.subcategorias.filter(estado=True).values_list('id', flat=True))
        categoria_ids = [categoria_ropa.id] + subcategorias_ids
        productos_mejor_puntuados = (
            Producto.objects
            .filter(activo=True, categoria_id__in=categoria_ids)
            .annotate(promedio_rating=Avg('resenas__calificacion'))
            .select_related('categoria', 'coleccion')
            .prefetch_related('imagenes', 'variantes', 'variantes__talla', 'resenas')
            .order_by('-created_at')[:3]
        )
    except Categoria.DoesNotExist:
        productos_mejor_puntuados = (
            Producto.objects
            .filter(activo=True)
            .annotate(promedio_rating=Avg('resenas__calificacion'))
            .select_related('categoria', 'coleccion')
            .prefetch_related('imagenes', 'variantes', 'variantes__talla', 'resenas')
            .order_by('-created_at')[:3]
        )
    
    return {
        'categorias_menu': categorias_principales,
        'productos_mejor_puntuados': productos_mejor_puntuados
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
