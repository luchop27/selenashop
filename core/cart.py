# core/cart.py
from decimal import Decimal
from django.conf import settings
from apps.productos.models import Producto, Variante


class Cart:
    """
    Clase para manejar el carrito de compras en la sesión
    """
    
    def __init__(self, request):
        """
        Inicializar el carrito
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Guardar un carrito vacío en la sesión
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, producto, variante_id=None, quantity=1, override_quantity=False):
        """
        Agregar un producto al carrito o actualizar su cantidad
        
        Args:
            producto: Instancia del modelo Producto
            variante_id: ID de la variante seleccionada
            quantity: Cantidad a agregar
            override_quantity: Si True, reemplaza la cantidad. Si False, incrementa.
        """
        # Crear una clave única para el producto (incluye variante si existe)
        if variante_id:
            product_id = f"{producto.id}_{variante_id}"
        else:
            product_id = str(producto.id)
        
        # Si el producto no está en el carrito, agregarlo
        if product_id not in self.cart:
            # Obtener información de la variante si existe
            variante_info = {}
            precio = producto.precio_base
            
            if variante_id:
                try:
                    variante = Variante.objects.select_related('talla').get(id=variante_id)
                    variante_info = {
                        'color': variante.color if variante.color else None,
                        'talla': variante.talla.codigo if variante.talla else None,
                        'talla_nombre': variante.talla.nombre if variante.talla else None,
                    }
                    precio = variante.precio if variante.precio else producto.precio_base
                except Variante.DoesNotExist:
                    pass
            
            # Obtener la primera imagen del producto
            primera_imagen = producto.imagenes.first()
            imagen_url = primera_imagen.imagen.url if primera_imagen and primera_imagen.imagen else None
            
            self.cart[product_id] = {
                'producto_id': producto.id,
                'variante_id': variante_id,
                'nombre': producto.nombre,
                'precio': str(precio),
                'quantity': 0,
                'imagen': imagen_url,
                **variante_info
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()
    
    def save(self):
        """
        Marcar la sesión como "modificada" para asegurar que se guarde
        """
        self.session.modified = True
    
    def remove(self, product_id):
        """
        Eliminar un producto del carrito
        
        Args:
            product_id: Clave del producto en el carrito (puede incluir variante)
        """
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def __iter__(self):
        """
        Iterar sobre los items en el carrito y obtener los productos de la BD
        """
        product_ids = [int(item['producto_id']) for item in self.cart.values()]
        
        # Obtener los productos de la base de datos
        productos = Producto.objects.filter(id__in=product_ids).prefetch_related('imagenes')
        
        cart = self.cart.copy()
        for item in cart.values():
            # Encontrar el producto correspondiente
            item['producto'] = next((p for p in productos if p.id == item['producto_id']), None)
            item['precio_decimal'] = Decimal(item['precio'])
            item['total_precio'] = item['precio_decimal'] * item['quantity']
            yield item
    
    def __len__(self):
        """
        Contar todos los items en el carrito
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        """
        Calcular el precio total de todos los items en el carrito
        """
        return sum(Decimal(item['precio']) * item['quantity'] for item in self.cart.values())
    
    def clear(self):
        """
        Eliminar el carrito de la sesión
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
    
    def update_quantity(self, product_id, quantity):
        """
        Actualizar la cantidad de un producto en el carrito
        
        Args:
            product_id: Clave del producto en el carrito
            quantity: Nueva cantidad
        """
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.remove(product_id)
            self.save()
