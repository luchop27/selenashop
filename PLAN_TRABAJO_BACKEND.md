# 🚀 PLAN DE TRABAJO BACKEND - SELENASHOP
## (División de Trabajo en Equipo)

---

## 📌 FLUJO DE COMPRA DEFINIDO:
```
1. Cliente navega productos → 
2. Agrega al carrito → 
3. Revisa carrito → 
4. Click "Comprar por WhatsApp" → 
5. Abre WhatsApp con mensaje predeterminado + productos
```

**NO HAY**: Pagos con tarjeta, checkout tradicional, pasarelas de pago

---

## 🎯 APPS DJANGO NECESARIAS (SIMPLIFICADAS)

### ✅ Apps Principales:
1. **products/** - Catálogo de productos
2. **cart/** - Carrito de compras  
3. **customers/** - Usuarios y perfiles
4. **orders/** - Registro de pedidos (historial)
5. **core/** - Configuraciones generales

### ❌ NO necesitamos:
- ~~payments/~~ (no hay pagos online)
- ~~inventory/~~ (podemos integrarlo en products por ahora)

---

## 📊 MODELOS DE BASE DE DATOS - RELACIONES COMPLETAS

### 1️⃣ APP: **products/**

```python
# products/models.py

class Category(models.Model):
    """Categorías de productos (ej: Ropa, Accesorios, Calzado)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, 
                              on_delete=models.CASCADE, 
                              related_name='children')  # Categorías anidadas
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    """Marcas de productos"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Producto principal"""
    # Información básica
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=50, unique=True)  # Código único
    description = models.TextField()
    short_description = models.CharField(max_length=255, blank=True)
    
    # Relaciones
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, 
                                null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, 
                             null=True, blank=True, related_name='products')
    
    # Precios
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                       null=True, blank=True)  # Precio tachado
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                     null=True, blank=True)  # Costo (privado)
    
    # Inventario
    stock = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    track_inventory = models.BooleanField(default=True)
    
    # SEO
    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.TextField(blank=True)
    
    # Estados
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)  # Destacado
    is_new = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def discount_percentage(self):
        """Calcula el % de descuento si hay compare_price"""
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock > 0
    
    @property
    def is_low_stock(self):
        if not self.track_inventory:
            return False
        return self.stock <= self.low_stock_threshold


class ProductImage(models.Model):
    """Múltiples imágenes por producto"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(models.Model):
    """Variantes del producto (ej: Talla S, Color Rojo)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='variants')
    name = models.CharField(max_length=100)  # ej: "Talla S - Rojo"
    sku = models.CharField(max_length=50, unique=True)
    
    # Atributos de variante
    size = models.CharField(max_length=20, blank=True)  # XS, S, M, L, XL
    color = models.CharField(max_length=50, blank=True)
    color_hex = models.CharField(max_length=7, blank=True)  # #FF0000
    
    # Precio específico (opcional, si no usa el del producto)
    price = models.DecimalField(max_digits=10, decimal_places=2, 
                               null=True, blank=True)
    
    # Stock específico
    stock = models.IntegerField(default=0)
    
    # Imagen específica (opcional)
    image = models.ImageField(upload_to='variants/', blank=True)
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    @property
    def final_price(self):
        """Precio final (usa el de la variante o el del producto)"""
        return self.price if self.price else self.product.price


class ProductReview(models.Model):
    """Reseñas y calificaciones"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='reviews')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'customer']  # 1 review por cliente
    
    def __str__(self):
        return f"{self.customer.user.username} - {self.product.name} ({self.rating}★)"
```

---

### 2️⃣ APP: **customers/**

```python
# customers/models.py
from django.contrib.auth.models import User

class Customer(models.Model):
    """Perfil extendido del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                               related_name='customer')
    
    # Información personal
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)  # Importante!
    birth_date = models.DateField(null=True, blank=True)
    
    # Dirección predeterminada
    default_address = models.ForeignKey('Address', null=True, blank=True,
                                       on_delete=models.SET_NULL,
                                       related_name='+')
    
    # Configuración
    receive_newsletter = models.BooleanField(default=True)
    receive_whatsapp_notifications = models.BooleanField(default=True)
    
    # Stats
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, 
                                     default=0.00)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    
    @property
    def whatsapp_number(self):
        """Retorna el número de WhatsApp formateado"""
        return self.whatsapp or self.phone


class Address(models.Model):
    """Direcciones de envío"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, 
                                related_name='addresses')
    
    # Información de contacto
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    
    # Dirección
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Colombia')
    
    # Tipo
    address_type = models.CharField(max_length=20, 
                                   choices=[('home', 'Casa'), 
                                          ('work', 'Trabajo'), 
                                          ('other', 'Otro')],
                                   default='home')
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Addresses"
    
    def __str__(self):
        return f"{self.full_name} - {self.city}"


class Wishlist(models.Model):
    """Lista de deseos"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, 
                                related_name='wishlist_items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'product']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.customer} - {self.product.name}"
```

---

### 3️⃣ APP: **cart/**

```python
# cart/models.py

class Cart(models.Model):
    """Carrito de compras"""
    customer = models.ForeignKey('customers.Customer', null=True, blank=True,
                                on_delete=models.CASCADE, related_name='carts')
    session_key = models.CharField(max_length=255, blank=True)  # Para anónimos
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.customer:
            return f"Cart - {self.customer.user.username}"
        return f"Cart - Session {self.session_key[:8]}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total(self):
        # Aquí puedes agregar envío, impuestos, etc.
        return self.subtotal
    
    def get_whatsapp_message(self):
        """Genera el mensaje para WhatsApp"""
        message = "¡Hola! Me interesan estos productos:\n\n"
        
        for item in self.items.all():
            product_name = item.product.name
            if item.variant:
                product_name += f" ({item.variant.name})"
            message += f"• {product_name}\n"
            message += f"  Cantidad: {item.quantity}\n"
            message += f"  Precio: ${item.unit_price:,.0f}\n"
            message += f"  Subtotal: ${item.total_price:,.0f}\n\n"
        
        message += f"*TOTAL: ${self.total:,.0f}*\n\n"
        message += "¿Está disponible?"
        
        return message


class CartItem(models.Model):
    """Items en el carrito"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, 
                            related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    variant = models.ForeignKey('products.ProductVariant', null=True, blank=True,
                               on_delete=models.CASCADE)
    
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cart', 'product', 'variant']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity
    
    def save(self, *args, **kwargs):
        # Auto-calcular precio al guardar
        if self.variant and self.variant.price:
            self.unit_price = self.variant.price
        else:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)
```

---

### 4️⃣ APP: **orders/**

```python
# orders/models.py

class Order(models.Model):
    """Pedido/Orden - Registro de compras"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('whatsapp_sent', 'Enviado por WhatsApp'),
        ('confirmed', 'Confirmado'),
        ('processing', 'En Proceso'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Identificación
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT,
                                related_name='orders')
    
    # Estado
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                             default='pending')
    
    # Información del cliente (snapshot)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    customer_whatsapp = models.CharField(max_length=20, blank=True)
    
    # Dirección de envío (snapshot)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    
    # Totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, 
                                       default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Notas
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # WhatsApp
    whatsapp_message_sent = models.BooleanField(default=False)
    whatsapp_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generar número de orden único
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Items de la orden"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, 
                             related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    variant = models.ForeignKey('products.ProductVariant', null=True, blank=True,
                               on_delete=models.PROTECT)
    
    # Snapshot del producto al momento de la compra
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50)
    variant_name = models.CharField(max_length=100, blank=True)
    
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """Historial de cambios de estado"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, 
                             related_name='status_history')
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True,
                                  on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Order status histories"
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"
```

---

### 5️⃣ APP: **core/**

```python
# core/models.py

class SiteConfiguration(models.Model):
    """Configuración general de la tienda"""
    site_name = models.CharField(max_length=200, default='SelenaShop')
    site_description = models.TextField(blank=True)
    
    # Contacto
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20)  # IMPORTANTE!
    whatsapp_message_prefix = models.TextField(
        default="¡Hola! Me interesan estos productos:"
    )
    
    # Redes sociales
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    
    # Dirección física
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    
    # Configuración de envío
    free_shipping_threshold = models.DecimalField(max_digits=10, 
                                                  decimal_places=2, 
                                                  default=0.00)
    default_shipping_cost = models.DecimalField(max_digits=10, 
                                               decimal_places=2, 
                                               default=0.00)
    
    # SEO
    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"
    
    def __str__(self):
        return self.site_name
    
    @classmethod
    def get_config(cls):
        """Retorna la configuración (crea una si no existe)"""
        config, created = cls.objects.get_or_create(pk=1)
        return config
```

---

## 🔄 DIAGRAMA DE RELACIONES

```
User (Django Auth)
  ↓ OneToOne
Customer
  ├── OneToMany → Address
  ├── OneToMany → Cart
  │   └── OneToMany → CartItem
  │       ├── ForeignKey → Product
  │       └── ForeignKey → ProductVariant (opcional)
  ├── OneToMany → Order
  │   └── OneToMany → OrderItem
  ├── OneToMany → Wishlist
  └── OneToMany → ProductReview

Category
  ├── OneToMany → Product
  └── ForeignKey → Category (parent) [Recursivo]

Brand
  └── OneToMany → Product

Product
  ├── OneToMany → ProductImage
  ├── OneToMany → ProductVariant
  ├── OneToMany → ProductReview
  └── ForeignKey → Category, Brand
```

---

## 👥 DIVISIÓN DE TRABAJO (2 PERSONAS)

### 🔵 PERSONA 1 - "Backend Core"

#### Tarea 1: Configuración Inicial
- [ ] Instalar dependencias (Pillow, DRF, etc.)
- [ ] Configurar `MEDIA_ROOT` y `MEDIA_URL`
- [ ] Crear archivo `requirements.txt`
- [ ] Configurar Django Admin básico

#### Tarea 2: App `products/`
- [ ] Crear app `products`
- [ ] Crear modelos: `Category`, `Brand`, `Product`, `ProductImage`, `ProductVariant`
- [ ] Hacer migraciones
- [ ] Registrar modelos en admin
- [ ] Crear signals para slug automático
- [ ] Agregar datos de prueba (fixtures o admin)

#### Tarea 3: App `customers/`
- [ ] Crear app `customers`
- [ ] Crear modelos: `Customer`, `Address`, `Wishlist`
- [ ] Signal para crear Customer automático cuando se crea User
- [ ] Registrar en admin
- [ ] Vistas de registro y login

### 🟢 PERSONA 2 - "Cart & Orders"

#### Tarea 1: App `cart/`
- [ ] Crear app `cart`
- [ ] Crear modelos: `Cart`, `CartItem`
- [ ] Método `get_whatsapp_message()` en Cart
- [ ] Lógica para carrito de sesión (usuarios anónimos)
- [ ] Vistas para agregar/quitar/actualizar items
- [ ] Template de carrito

#### Tarea 2: App `orders/`
- [ ] Crear app `orders`
- [ ] Crear modelos: `Order`, `OrderItem`, `OrderStatusHistory`
- [ ] Función para crear orden desde carrito
- [ ] Signal para actualizar stock al crear orden
- [ ] Registrar en admin con inlines
- [ ] Vista de historial de órdenes

#### Tarea 3: App `core/`
- [ ] Crear app `core`
- [ ] Modelo `SiteConfiguration`
- [ ] Context processor para configuración global
- [ ] Vistas de home y páginas estáticas

---

## 🔧 TAREAS COMPARTIDAS

### Ambos deben hacer:
1. **Crear `serializers.py`** en cada app (para API REST)
2. **Crear `urls.py`** en cada app
3. **Tests básicos** (opcional pero recomendado)
4. **Documentar el código** con docstrings

---

## 📝 ORDEN DE IMPLEMENTACIÓN (PRIORIDAD)

### SPRINT 1 (Esta semana):
1. ✅ Persona 1: `products/` (modelos + admin)
2. ✅ Persona 2: `cart/` (modelos + lógica básica)
3. ✅ Persona 1: `customers/` (modelos + signals)

### SPRINT 2 (Próxima semana):
4. ✅ Persona 2: `orders/` (modelos + creación desde cart)
5. ✅ Persona 1: `products/` (vistas y templates)
6. ✅ Persona 2: Integración WhatsApp

### SPRINT 3 (Tercera semana):
7. ✅ Persona 1: Templates frontend (catálogo, detalle)
8. ✅ Persona 2: Templates cart y checkout
9. ✅ Ambos: Admin dashboard

---

## 🚀 COMANDOS INICIALES

```bash
# Persona 1 empieza con:
cd selenashop
python manage.py startapp products
python manage.py startapp customers

# Persona 2 empieza con:
python manage.py startapp cart
python manage.py startapp orders
```

---

## 📦 REQUIREMENTS.TXT

```txt
Django==4.2.7
Pillow==10.1.0
djangorestframework==3.14.0
django-cors-headers==4.3.0
python-decouple==3.8
```

---

## ⚙️ CONFIGURACIÓN EN settings.py

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'products',
    'customers',
    'cart',
    'orders',
    'core',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}
```

---

## 📱 INTEGRACIÓN WHATSAPP

### En el template del carrito:

```html
<!-- cart.html -->
<a href="https://wa.me/{{ whatsapp_number }}?text={{ cart.get_whatsapp_message|urlencode }}" 
   class="btn btn-success btn-lg">
   <i class="icon-whatsapp"></i> Comprar por WhatsApp
</a>
```

### En la vista:

```python
# cart/views.py
from core.models import SiteConfiguration

def cart_view(request):
    config = SiteConfiguration.get_config()
    cart = get_cart(request)
    
    context = {
        'cart': cart,
        'whatsapp_number': config.whatsapp_number,
    }
    return render(request, 'cart/cart.html', context)
```

---

## ✅ CHECKLIST GENERAL

### Backend Core:
- [ ] 5 apps creadas (products, customers, cart, orders, core)
- [ ] Todos los modelos con relaciones correctas
- [ ] Migraciones aplicadas sin errores
- [ ] Admin configurado para todas las apps
- [ ] Datos de prueba cargados

### Funcionalidad:
- [ ] Usuarios pueden registrarse/login
- [ ] Productos se muestran en catálogo
- [ ] Carrito funciona (agregar/quitar/actualizar)
- [ ] Botón WhatsApp genera mensaje correcto
- [ ] Órdenes se crean al enviar por WhatsApp
- [ ] Stock se actualiza automáticamente

### Testing:
- [ ] Crear producto con variantes
- [ ] Agregar al carrito
- [ ] Ver mensaje de WhatsApp generado
- [ ] Crear orden
- [ ] Verificar que stock disminuyó

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

1. **Yo te ayudo a crear la estructura base** (apps, modelos, settings)
2. **Tú y tu compañero dividen las tareas** según el plan
3. **Se reúnen para integrar** ambas partes
4. **Prueban el flujo completo** de compra

---

## ❓ ¿EMPEZAMOS?

Dime:
1. **¿Quieres que cree toda la estructura base ahora?** (apps, modelos, migrations)
2. **¿Qué número de WhatsApp usarán?** (para la configuración)
3. **¿Tú tomarás el rol de Persona 1 o Persona 2?**

¡Listo para empezar! 🚀
