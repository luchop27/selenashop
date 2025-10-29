from django.db import models
from django.utils.text import slugify
from django.conf import settings


class Categoria(models.Model):
    """
    Tabla: categorias
    Función: Organizar productos por tipo (Ropa, Accesorios) y estilo
    Ejemplos: Ropa > Playa, Ropa > Gala, Accesorios > Carteras
    """
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    imagen = models.ImageField(upload_to='categorias/', blank=True, verbose_name='Imagen')
    padre = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subcategorias',
        verbose_name='Categoría padre',
        help_text='Categoría principal (Ej: Ropa, Accesorios)'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    orden = models.IntegerField(default=0, verbose_name='Orden')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['orden', 'nombre']

    def __str__(self):
        if self.padre:
            return f"{self.padre.nombre} > {self.nombre}"
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Marca(models.Model):
    """
    Tabla: marcas
    Función: Marcas de productos
    """
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    logo = models.ImageField(upload_to='marcas/', blank=True, verbose_name='Logo')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Producto(models.Model):
    """
    Tabla: productos
    Función: Producto principal de la tienda (ropa, carteras, perfumes, etc.)
    """
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('agotado', 'Agotado'),
        ('inactivo', 'Inactivo'),
    ]
    
    # Información básica
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    descripcion = models.TextField(verbose_name='Descripción')
    descripcion_corta = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Descripción corta'
    )

    # Relaciones
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        related_name='productos',
        verbose_name='Categoría/Estilo'
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos',
        verbose_name='Marca',
        help_text='Solo para accesorios de marca'
    )

    # Precios
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio'
    )
    precio_comparacion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Precio de comparación',
        help_text='Precio antes del descuento (se muestra tachado)'
    )
    precio_costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Precio de costo',
        help_text='Solo visible para administradores'
    )

    # Inventario
    stock = models.IntegerField(default=0, verbose_name='Stock total')
    stock_minimo = models.IntegerField(
        default=5,
        verbose_name='Stock mínimo',
        help_text='Alerta cuando el stock llegue a este nivel'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='disponible',
        verbose_name='Estado del producto'
    )

    # SEO
    meta_titulo = models.CharField(max_length=160, blank=True, verbose_name='Meta título')
    meta_descripcion = models.TextField(blank=True, verbose_name='Meta descripción')

    # Estados adicionales
    destacado = models.BooleanField(default=False, verbose_name='Destacado')
    nuevo = models.BooleanField(default=False, verbose_name='Nuevo')
    en_oferta = models.BooleanField(default=False, verbose_name='En oferta')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        
        # Auto-cambiar estado según stock
        if self.stock <= 0:
            self.estado = 'agotado'
        elif self.estado == 'agotado' and self.stock > 0:
            self.estado = 'disponible'
            
        super().save(*args, **kwargs)

    @property
    def porcentaje_descuento(self):
        """Calcula el porcentaje de descuento"""
        if self.precio_comparacion and self.precio_comparacion > self.precio:
            return int(((self.precio_comparacion - self.precio) / self.precio_comparacion) * 100)
        return 0

    @property
    def esta_disponible(self):
        """Verifica si el producto está disponible para venta"""
        return self.estado == 'disponible' and self.stock > 0

    @property
    def stock_bajo(self):
        """Verifica si el stock está bajo"""
        return 0 < self.stock <= self.stock_minimo


class ImagenProducto(models.Model):
    """
    Tabla: imagenes_productos
    Función: Múltiples imágenes por producto
    """
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='imagenes',
        verbose_name='Producto'
    )
    imagen = models.ImageField(upload_to='productos/', verbose_name='Imagen')
    texto_alternativo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Texto alternativo'
    )
    es_principal = models.BooleanField(default=False, verbose_name='Es principal')
    orden = models.IntegerField(default=0, verbose_name='Orden')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        verbose_name = 'Imagen de producto'
        verbose_name_plural = 'Imágenes de productos'
        ordering = ['orden', 'id']

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"


class VarianteProducto(models.Model):
    """
    Tabla: variantes_productos
    Función: Variantes del producto por TALLA únicamente
    Ejemplo: Un vestido puede tener tallas S, M, L, XL
    """
    TALLAS_LETRA = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Extra Extra Large'),
    ]
    
    TALLAS_NUMERO = [
        ('6', 'Talla 6'),
        ('8', 'Talla 8'),
        ('10', 'Talla 10'),
        ('12', 'Talla 12'),
        ('14', 'Talla 14'),
        ('16', 'Talla 16'),
        ('36', 'Talla 36'),
        ('38', 'Talla 38'),
        ('40', 'Talla 40'),
        ('42', 'Talla 42'),
        ('44', 'Talla 44'),
    ]
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='variantes',
        verbose_name='Producto'
    )
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    
    # Talla (puede ser letra o número)
    talla = models.CharField(
        max_length=20,
        verbose_name='Talla',
        help_text='Ej: S, M, L, XL o 36, 38, 40'
    )
    
    # Precio específico (opcional, usa el del producto si no tiene)
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Precio específico',
        help_text='Dejar vacío para usar el precio del producto'
    )
    
    # Stock por talla
    stock = models.IntegerField(default=0, verbose_name='Stock de esta talla')
    
    activo = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    class Meta:
        verbose_name = 'Variante de producto'
        verbose_name_plural = 'Variantes de productos'
        ordering = ['talla']
        unique_together = ['producto', 'talla']

    def __str__(self):
        return f"{self.producto.nombre} - Talla {self.talla}"

    @property
    def precio_final(self):
        """Retorna el precio de la variante o del producto"""
        return self.precio if self.precio else self.producto.precio
    
    @property
    def esta_disponible(self):
        """Verifica si esta variante tiene stock"""
        return self.activo and self.stock > 0


class ResenaProducto(models.Model):
    """
    Tabla: resenas_productos
    Función: Reseñas y calificaciones de productos
    """
    CALIFICACIONES = [(i, f'{i} estrellas') for i in range(1, 6)]

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='resenas',
        verbose_name='Producto'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuario'
    )
    calificacion = models.IntegerField(
        choices=CALIFICACIONES,
        verbose_name='Calificación'
    )
    titulo = models.CharField(max_length=200, blank=True, verbose_name='Título')
    comentario = models.TextField(verbose_name='Comentario')
    compra_verificada = models.BooleanField(
        default=False,
        verbose_name='Compra verificada'
    )
    aprobado = models.BooleanField(default=True, verbose_name='Aprobado')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')

    class Meta:
        verbose_name = 'Reseña de producto'
        verbose_name_plural = 'Reseñas de productos'
        ordering = ['-created_at']
        unique_together = ['producto', 'usuario']

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre} ({self.calificacion}★)"

