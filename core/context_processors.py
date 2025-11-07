from apps.productos.models import Categoria


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
