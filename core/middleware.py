# core/middleware.py
from django.conf import settings
from apps.productos.models import CarritoItem, Producto, Variante
from decimal import Decimal


class CartPersistenceMiddleware:
    """
    Middleware para sincronizar el carrito de sesión a la BD cuando el usuario se autentica.
    También carga el carrito guardado de la BD cuando el usuario inicia sesión.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Sincronizar carrito si el usuario está autenticado
        if request.user.is_authenticated:
            self._sync_cart_to_db(request)
        
        response = self.get_response(request)
        return response
    
    def _sync_cart_to_db(self, request):
        """
        Sincronizar items del carrito de sesión a la BD si es necesario.
        Esto es útil cuando el usuario se acaba de autenticar.
        """
        cart_session = request.session.get(settings.CART_SESSION_ID, {})
        
        if not cart_session:
            return
        
        # Filtrar items válidos (ignorar metadatos que comienzan con _)
        valid_items = {k: v for k, v in cart_session.items() if not k.startswith('_') and isinstance(v, dict)}
        
        if not valid_items:
            return
        
        # Sincronizar cada item al carrito de BD
        for product_key, item_data in valid_items.items():
            try:
                producto_id = item_data.get('producto_id')
                variante_id = item_data.get('variante_id')
                cantidad = item_data.get('quantity', 1)
                precio = Decimal(item_data.get('precio', '0'))
                
                # Validar que el producto existe
                producto = Producto.objects.get(id=producto_id)
                
                # Obtener o crear el item en la BD
                carrito_item, created = CarritoItem.objects.get_or_create(
                    usuario=request.user,
                    producto_id=producto_id,
                    variante_id=variante_id,
                    defaults={
                        'cantidad': cantidad,
                        'precio': precio,
                        'color': item_data.get('color'),
                        'talla_codigo': item_data.get('talla'),
                        'talla_nombre': item_data.get('talla_nombre'),
                        'imagen_url': item_data.get('imagen'),
                    }
                )
                
                # Si ya existía, actualizar la cantidad (sumar a la existente)
                if not created:
                    carrito_item.cantidad += cantidad
                    carrito_item.precio = precio
                    carrito_item.save()
            
            except (Producto.DoesNotExist, ValueError, TypeError):
                # Ignorar items inválidos
                continue
        
        # Limpiar la sesión de carrito (ya que está en la BD)
        if settings.CART_SESSION_ID in request.session:
            # Preservar metadatos si existen
            cart_data = request.session[settings.CART_SESSION_ID]
            metadata = {k: v for k, v in cart_data.items() if k.startswith('_')}
            request.session[settings.CART_SESSION_ID] = metadata
            request.session.modified = True
