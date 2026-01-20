# core/cart.py
from decimal import Decimal
from django.conf import settings
from apps.productos.models import Producto, Variante, CarritoItem


class Cart:
    """
    Clase para manejar el carrito de compras en la sesión y BD.
    Si el usuario está autenticado, sincroniza con CarritoItem en la BD.
    Si no está autenticado, usa sessionStorage (sesión de servidor).
    """
    
    def __init__(self, request):
        """
        Inicializar el carrito
        """
        self.request = request
        self.session = request.session
        self.user = request.user
        
        # Si el usuario está autenticado, cargar carrito de la BD
        if self.user.is_authenticated:
            self._load_from_db()
        else:
            # Si no está autenticado, usar sesión
            cart = self.session.get(settings.CART_SESSION_ID)
            if not cart:
                # Guardar un carrito vacío en la sesión
                cart = self.session[settings.CART_SESSION_ID] = {}
            self.cart = cart
    
    def _load_from_db(self):
        """
        Cargar el carrito desde la BD para usuarios autenticados.
        La sesión se usa solo como caché.
        """
        # Cargar items de la BD con el producto relacionado
        items_db = CarritoItem.objects.filter(usuario=self.user).select_related('producto')
        
        # Construir el carrito en formato de sesión
        self.cart = {}
        for item in items_db:
            # Crear una clave única (igual que en add())
            if item.variante_id:
                product_key = f"{item.producto_id}_{item.variante_id}"
            else:
                product_key = str(item.producto_id)
            
            self.cart[product_key] = {
                'producto_id': item.producto_id,
                'variante_id': item.variante_id,
                'nombre': item.producto.nombre,
                'producto_slug': item.producto.slug,  # Agregar el slug del producto
                'precio': str(item.precio),
                'quantity': item.cantidad,
                'imagen': item.imagen_url,
                'color': item.color,
                'talla': item.talla_codigo,
                'talla_nombre': item.talla_nombre,
                '_db_id': item.id  # Guardar ID para actualizaciones
            }
    
    def _save_to_db(self):
        """
        Sincronizar el carrito de sesión a la BD para usuarios autenticados.
        """
        if not self.user.is_authenticated:
            return
        
        # Obtener items válidos del carrito (ignorar metadatos)
        valid_items = {k: v for k, v in self.cart.items() if not k.startswith('_') and isinstance(v, dict)}
        
        # Obtener IDs de DB que ya existen
        existing_db_ids = {item['_db_id'] for item in valid_items.values() if '_db_id' in item}
        
        # Eliminar items que no están en el carrito actual
        CarritoItem.objects.filter(usuario=self.user).exclude(id__in=existing_db_ids).delete()
        
        # Actualizar o crear items en la BD
        for product_key, item_data in valid_items.items():
            producto_id = item_data['producto_id']
            variante_id = item_data.get('variante_id')
            cantidad = item_data['quantity']
            precio = Decimal(item_data['precio'])
            
            # Preparar datos adicionales
            color = item_data.get('color')
            talla_codigo = item_data.get('talla')
            talla_nombre = item_data.get('talla_nombre')
            imagen_url = item_data.get('imagen')
            
            if '_db_id' in item_data:
                # Actualizar item existente
                try:
                    carrito_item = CarritoItem.objects.get(id=item_data['_db_id'])
                    carrito_item.cantidad = cantidad
                    carrito_item.save()
                except CarritoItem.DoesNotExist:
                    # Si el item fue eliminado desde otra sesión, recréalo
                    CarritoItem.objects.get_or_create(
                        usuario=self.user,
                        producto_id=producto_id,
                        variante_id=variante_id,
                        defaults={
                            'cantidad': cantidad,
                            'precio': precio,
                            'color': color,
                            'talla_codigo': talla_codigo,
                            'talla_nombre': talla_nombre,
                            'imagen_url': imagen_url,
                        }
                    )
            else:
                # Crear nuevo item
                CarritoItem.objects.get_or_create(
                    usuario=self.user,
                    producto_id=producto_id,
                    variante_id=variante_id,
                    defaults={
                        'cantidad': cantidad,
                        'precio': precio,
                        'color': color,
                        'talla_codigo': talla_codigo,
                        'talla_nombre': talla_nombre,
                        'imagen_url': imagen_url,
                    }
                )
    
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
                'producto_slug': producto.slug,
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
        Marcar la sesión como "modificada" para asegurar que se guarde.
        Si el usuario está autenticado, también sincroniza con la BD.
        """
        self.session.modified = True
        
        # Sincronizar con BD si está autenticado
        if self.user.is_authenticated:
            self._save_to_db()
    
    def remove(self, product_id):
        """
        Eliminar un producto del carrito
        
        Args:
            product_id: Clave del producto en el carrito (puede incluir variante)
        """
        if product_id in self.cart:
            # Si está autenticado y el item tiene ID de BD, eliminar de BD también
            if self.user.is_authenticated and '_db_id' in self.cart[product_id]:
                try:
                    CarritoItem.objects.get(id=self.cart[product_id]['_db_id']).delete()
                except CarritoItem.DoesNotExist:
                    pass
            
            del self.cart[product_id]
            self.save()
    
    def __iter__(self):
        """
        Iterar sobre los items en el carrito y obtener los productos de la BD
        """
        # Filtrar solo items válidos (diccionarios, no metadatos)
        valid_items = {k: v for k, v in self.cart.items() if not k.startswith('_') and isinstance(v, dict)}
        
        product_ids = [int(item['producto_id']) for item in valid_items.values()]
        
        # Obtener los productos de la base de datos
        productos = Producto.objects.filter(id__in=product_ids).prefetch_related('imagenes')
        
        # Hacer una copia profunda para no modificar el carrito en sesión
        for key, item_data in valid_items.items():
            # Crear una copia del item para no modificar el original
            item = item_data.copy()
            
            # Encontrar el producto correspondiente
            producto = next((p for p in productos if p.id == item['producto_id']), None)
            item['producto'] = producto
            
            # Asegurar que el slug esté disponible (por si no está en la sesión)
            if 'producto_slug' not in item and producto:
                item['producto_slug'] = producto.slug
            
            item['precio_decimal'] = Decimal(item['precio'])
            item['total_precio'] = item['precio_decimal'] * item['quantity']
            yield item
    
    def __len__(self):
        """
        Contar todos los items en el carrito
        """
        return sum(item['quantity'] for key, item in self.cart.items() if not key.startswith('_') and isinstance(item, dict))
    
    def get_total_price(self):
        """
        Calcular el precio total de todos los items en el carrito
        """
        subtotal = sum(Decimal(item['precio']) * item['quantity'] for key, item in self.cart.items() if not key.startswith('_') and isinstance(item, dict))
        
        # Agregar costo de gift wrap si está habilitado
        if self.has_gift_wrap():
            subtotal += Decimal('5.00')
        
        return subtotal
    
    def clear(self):
        """
        Eliminar el carrito de la sesión y de la BD si está autenticado.
        Se asegura de que el carrito esté completamente limpio en ambos lugares.
        """
        # Eliminar de la BD si está autenticado
        if self.user.is_authenticated:
            CarritoItem.objects.filter(usuario=self.user).delete()
        
        # Vaciar el diccionario del carrito
        self.cart = {}
        
        # Limpiar la sesión completamente
        if settings.CART_SESSION_ID in self.session:
            self.session[settings.CART_SESSION_ID] = {}
        else:
            self.session[settings.CART_SESSION_ID] = {}
        
        # Marcar sesión como modificada y guardar
        self.session.modified = True
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
    
    def set_note(self, note):
        """
        Guardar una nota para el pedido
        """
        cart_data = self.session.get(settings.CART_SESSION_ID, {})
        cart_data['_note'] = note
        self.session[settings.CART_SESSION_ID] = cart_data
        self.save()
    
    def get_note(self):
        """
        Obtener la nota del pedido
        """
        cart_data = self.session.get(settings.CART_SESSION_ID, {})
        return cart_data.get('_note', '')
    
    def set_gift_wrap(self, enabled=True):
        """
        Habilitar/deshabilitar gift wrap
        """
        cart_data = self.session.get(settings.CART_SESSION_ID, {})
        cart_data['_gift_wrap'] = enabled
        self.session[settings.CART_SESSION_ID] = cart_data
        self.save()
    
    def has_gift_wrap(self):
        """
        Verificar si el gift wrap está habilitado
        """
        cart_data = self.session.get(settings.CART_SESSION_ID, {})
        return cart_data.get('_gift_wrap', False)
