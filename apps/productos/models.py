# apps/productos/models.py
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
import os


def validate_video_extension(value):
    """Validar que el archivo sea un video válido"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.mp4', '.webm', '.mov', '.avi', '.mkv']
    if ext not in valid_extensions:
        raise ValidationError(f'Archivo no permitido. Solo se aceptan: {", ".join(valid_extensions)}')


def validate_image_extension(value):
    """Validar que el archivo sea una imagen válida"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.heic', '.heif']
    if ext not in valid_extensions:
        raise ValidationError(f'Archivo no permitido. Solo se aceptan: {", ".join(valid_extensions)}')


# -----------------------------
# COLECCIÓN
# -----------------------------
class Coleccion(models.Model):
    """
    Colecciones que agrupan categorías completas.
    Ejemplo: "Primavera 2024", "Verano Casual", "Formal Elegante"
    """
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    # Imagen de la colección
    imagen = models.ImageField(
        upload_to='colecciones/',
        blank=True,
        null=True,
        help_text="Imagen representativa de la colección"
    )
    
    activo = models.BooleanField(default=True)
    destacada = models.BooleanField(default=False, help_text="Mostrar en página principal")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = "Colección"
        verbose_name_plural = "Colecciones"

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('productos:lista_por_coleccion', args=[self.slug])


# -----------------------------
# CATEGORÍA
# -----------------------------
class Categoria(models.Model):
    """
    Agrupa productos (Ropa, Accesorios, Perfumes, etc.)
    Soporta jerarquía con padre -> subcategorías.
    CONECTADA A COLECCIÓN mediante FK.
    """
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    # Imagen de la categoría
    imagen = models.ImageField(
        upload_to='categorias/',
        blank=True,
        null=True,
        help_text="Imagen representativa de la categoría"
    )
    
    # 🔗 CONEXIÓN A COLECCIÓN
    coleccion = models.ForeignKey(
        Coleccion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='categorias',
        help_text="Colección a la que pertenece esta categoría"
    )

    padre = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategorias'
    )
    
    estado = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('productos:lista_por_categoria', args=[self.slug])


# ------------------------------
# ESTILO
# ------------------------------
class Estilo(models.Model):
    """
    Para navegar por estilo: gala, playa, casual, oficina, sport...
    """
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    posicion = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['posicion']
        verbose_name = "Estilo"
        verbose_name_plural = "Estilos"

    def __str__(self):
        return self.nombre


# ------------------------------
# PRODUCTO
# ------------------------------
class Producto(models.Model):
    """
    Producto base que se muestra en la tienda.
    Las tallas y colores viven en Variantes.
    """
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos'
    )
    coleccion = models.ForeignKey(
        'Coleccion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos',
        help_text="Colección a la que pertenece este producto"
    )
    tipo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Ej: vestido, perfume, reloj..."
    )

    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    descripcion_corta = models.TextField(blank=True, null=True)
    descripcion_larga = models.TextField(blank=True, null=True)

    marca = models.CharField(max_length=100, blank=True, null=True)
    precio_base = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tiene_tallas = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    
    # Sistema de productos bajo pedido
    bajo_pedido = models.BooleanField(
        default=False,
        help_text="Si está activado, el producto seguirá visible aunque no tenga stock. Si está desactivado, se eliminará automáticamente al agotarse."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        """Retorna la URL absoluta del producto usando slug"""
        from django.urls import reverse
        try:
            return reverse('core:product_detail', args=[self.slug])
        except Exception:
            # Fallback: build a simple path if URL reversal fails
            return f"/producto/{self.slug}/"
    
    def stock_total(self):
        """Calcula el stock total sumando todas las variantes"""
        return sum(v.stock for v in self.variantes.all())
    
    def tiene_stock(self):
        """Verifica si el producto tiene stock disponible"""
        return self.stock_total() > 0
    
    def permite_pedido(self):
        """Indica si el producto permite hacer pedidos (tiene stock O está bajo pedido)"""
        return self.tiene_stock() or self.bajo_pedido
    
    def estado_stock(self):
        """Retorna el estado del stock del producto para mostrar en la UI"""
        if self.tiene_stock():
            return "disponible"
        elif self.bajo_pedido:
            return "bajo_pedido"
        else:
            return "sin_stock"


# ------------------------------
# TALLA
# ------------------------------
class Talla(models.Model):
    """
    Catálogo general de tallas (S, M, L, 36, 38, Única...).
    """
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['codigo']
        verbose_name = "Talla"
        verbose_name_plural = "Tallas"

    def __str__(self):
        return self.codigo


# ------------------------------
# VARIANTE
# ------------------------------
class Variante(models.Model):
    """
    Variante del producto -> combina producto + talla + color.
    Aquí también va el stock y el precio específico.
    """
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='variantes'
    )
    talla = models.ForeignKey(
        Talla,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='variantes'
    )
    color = models.CharField(max_length=50, blank=True, null=True)
    sku = models.CharField(max_length=100, unique=True)
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Si lo dejas vacío, el sistema puede usar precio_base del producto."
    )
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Variante"
        verbose_name_plural = "Variantes"
        constraints = [
            models.UniqueConstraint(
                fields=['producto', 'talla', 'color'],
                name='productos_uq_variante_producto_talla_color'
            )
        ]

    def __str__(self):
        base = f"{self.producto.nombre}"
        if self.color:
            base += f" - {self.color}"
        if self.talla:
            base += f" - {self.talla.codigo}"
        return base


# ------------------------------
# IMAGEN
# ------------------------------
class Imagen(models.Model):
    """
    Imagen o video asociado a un producto o a una variante específica.
    """
    TIPO_CHOICES = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
    ]
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='imagenes'
    )
    variante = models.ForeignKey(
        Variante,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='imagenes'
    )
    tipo_medio = models.CharField(max_length=10, choices=TIPO_CHOICES, default='imagen', help_text="Tipo de medio")
    imagen = models.ImageField(
        upload_to='productos/imagenes/', 
        blank=True, 
        null=True,
        validators=[validate_image_extension],
        help_text="Archivo de imagen (JPG, PNG, GIF, WebP, HEIC/iPhone) - Resolución original mantenida"
    )
    video = models.FileField(
        upload_to='productos/videos/', 
        blank=True, 
        null=True,
        validators=[validate_video_extension],
        help_text="Archivo de video (MP4, WebM, MOV) - Resolución original mantenida"
    )
    url = models.TextField(default='', blank=True, help_text="URL alternativa si no se usa archivo")
    posicion = models.PositiveIntegerField(default=0, help_text="Orden de visualización")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['posicion', 'created_at']
        verbose_name = "Imagen/Video"
        verbose_name_plural = "Imágenes/Videos"
        constraints = [
            models.CheckConstraint(
                check=(models.Q(producto__isnull=False) | models.Q(variante__isnull=False)),
                name='productos_imagen_producto_o_variante_not_null',
            ),
        ]

    def __str__(self):
        tipo = "Video" if self.tipo_medio == 'video' else "Imagen"
        if self.producto:
            return f"{tipo} de {self.producto.nombre}"
        if self.variante:
            return f"{tipo} de variante {self.variante}"
        return self.url or ""
    
    def clean(self):
        """Validar que el tipo de medio coincida con el archivo subido"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"=== CLEAN IMAGEN ===")
        logger.info(f"Tipo medio: {self.tipo_medio}")
        logger.info(f"Tiene imagen: {bool(self.imagen)}")
        logger.info(f"Tiene video: {bool(self.video)}")
        logger.info(f"Tiene URL: {bool(self.url)}")
        
        super().clean()
        
        if self.tipo_medio == 'video':
            if self.imagen and not self.video:
                logger.error("ERROR: Tipo video pero solo hay imagen")
                raise ValidationError({
                    'tipo_medio': 'Has seleccionado "Video" pero subiste una imagen. Cambia el tipo a "Imagen" o sube un video.'
                })
            if not self.video and not self.url:
                logger.error("ERROR: Tipo video pero no hay video ni URL")
                raise ValidationError({
                    'video': 'Debes subir un archivo de video o proporcionar una URL.'
                })
            logger.info("✓ Validación video OK")
        elif self.tipo_medio == 'imagen':
            if self.video and not self.imagen:
                logger.error("ERROR: Tipo imagen pero solo hay video")
                raise ValidationError({
                    'tipo_medio': 'Has seleccionado "Imagen" pero subiste un video. Cambia el tipo a "Video" o sube una imagen.'
                })
            if not self.imagen and not self.url:
                logger.error("ERROR: Tipo imagen pero no hay imagen ni URL")
                raise ValidationError({
                    'imagen': 'Debes subir una imagen o proporcionar una URL.'
                })
            logger.info("✓ Validación imagen OK")
    
    def save(self, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"=== SAVE IMAGEN ===")
        logger.info(f"Tipo medio: {self.tipo_medio}")
        logger.info(f"Tiene imagen: {bool(self.imagen)}")
        logger.info(f"Tiene video: {bool(self.video)}")
        
        try:
            super().save(*args, **kwargs)
            logger.info("✓ Guardado exitoso")
        except Exception as e:
            logger.error(f"ERROR al guardar: {e}")
            raise
    


    @property
    def src(self):
        if self.tipo_medio == 'video' and self.video:
            return self.video.url
        if self.imagen:
            return self.imagen.url
        return self.url or ""
    
    @property
    def es_video(self):
        return self.tipo_medio == 'video'
    
    @property
    def es_imagen(self):
        return self.tipo_medio == 'imagen'


# ------------------------------
# ATRIBUTO (Nuevo sistema)
# ------------------------------
class Atributo(models.Model):
    """
    Define tipos de atributos personalizables: Color, Talla, Marca, Material, etc.
    Ejemplo: nombre="Color", tipo="color"
    """
    TIPO_CHOICES = [
        ('color', 'Color'),
        ('talla', 'Talla/Tamaño'),
        ('texto', 'Texto'),
        ('numero', 'Número'),
    ]
    
    nombre = models.CharField(max_length=100, unique=True, help_text="Ej: Color, Talla, Marca")
    slug = models.SlugField(max_length=120, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='texto')
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    posicion = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['posicion', 'nombre']
        verbose_name = "Atributo"
        verbose_name_plural = "Atributos"

    def __str__(self):
        return self.nombre


# ------------------------------
# VALOR ATRIBUTO
# ------------------------------
class ValorAtributo(models.Model):
    """
    Valores específicos de cada atributo.
    Ejemplo: atributo=Color, valor="Rojo", codigo_color="#FF0000"
    """
    atributo = models.ForeignKey(
        Atributo,
        on_delete=models.CASCADE,
        related_name='valores'
    )
    valor = models.CharField(max_length=100, help_text="Ej: Rojo, S, Nike")
    codigo_color = models.CharField(
        max_length=7, 
        blank=True, 
        null=True,
        help_text="Para colores: código HEX (#FF0000)"
    )
    posicion = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['atributo', 'posicion', 'valor']
        verbose_name = "Valor de Atributo"
        verbose_name_plural = "Valores de Atributos"
        unique_together = [['atributo', 'valor']]

    def __str__(self):
        return f"{self.atributo.nombre}: {self.valor}"


# ------------------------------
# VARIANTE ATRIBUTO (Relación N:M)
# ------------------------------
class VarianteAtributo(models.Model):
    """
    Relaciona una variante con sus atributos.
    Ejemplo: Variante X tiene Color=Rojo, Talla=M
    """
    variante = models.ForeignKey(
        Variante,
        on_delete=models.CASCADE,
        related_name='atributos'
    )
    valor_atributo = models.ForeignKey(
        ValorAtributo,
        on_delete=models.CASCADE,
        related_name='variantes'
    )

    class Meta:
        verbose_name = "Atributo de Variante"
        verbose_name_plural = "Atributos de Variantes"
        unique_together = [['variante', 'valor_atributo']]

    def __str__(self):
        return f"{self.variante} - {self.valor_atributo}"


# ------------------------------
# GLOBAL CONTENT SETTINGS
# ------------------------------
class GlobalProductContent(models.Model):
    """
    Contenido global para las páginas de producto (Features, Materials Care, etc.)
    Solo debe existir UNA instancia de este modelo.
    """
    # Features Section
    features_content = models.TextField(
        blank=True,
        help_text="HTML para la sección Features. Ej: <li>Front button placket</li>"
    )
    
    # Materials Care Section  
    materials_content = models.TextField(
        blank=True,
        help_text="HTML para Materials Care. Ej: <li>Content: 100% Cotton</li>"
    )
    
    # Care Instructions Icons (mantener los íconos y descripciones)
    care_icon_1 = models.CharField(max_length=50, default="icon-machine", help_text="Clase CSS del ícono 1")
    care_text_1 = models.CharField(max_length=200, default="Machine wash max. 30ºC. Short spin.")
    
    care_icon_2 = models.CharField(max_length=50, default="icon-iron", help_text="Clase CSS del ícono 2")
    care_text_2 = models.CharField(max_length=200, default="Iron maximum 110ºC.")
    
    care_icon_3 = models.CharField(max_length=50, default="icon-bleach", help_text="Clase CSS del ícono 3")
    care_text_3 = models.CharField(max_length=200, default="Do not bleach/bleach.")
    
    care_icon_4 = models.CharField(max_length=50, default="icon-dry-clean", help_text="Clase CSS del ícono 4")
    care_text_4 = models.CharField(max_length=200, default="Do not dry clean.")
    
    care_icon_5 = models.CharField(max_length=50, default="icon-tumble-dry", help_text="Clase CSS del ícono 5")
    care_text_5 = models.CharField(max_length=200, default="Tumble dry, medium hear.")
    
    # Bottom text with icons
    product_code_text = models.CharField(
        max_length=300,
        default="LT01: 70% wool, 15% polyester, 10% polyamide, 5% acrylic 900 Grms/mt",
        help_text="Texto que aparece debajo de los íconos SVG"
    )
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Contenido Global de Productos"
        verbose_name_plural = "Contenido Global de Productos"
    
    def __str__(self):
        return "Global Product Content Settings"
    
    def save(self, *args, **kwargs):
        # Asegurar que solo exista una instancia (Singleton pattern)
        if not self.pk and GlobalProductContent.objects.exists():
            raise ValueError('Solo puede existir una instancia de GlobalProductContent')
        return super().save(*args, **kwargs)


# ------------------------------
# SHIPPING & DELIVERY
# ------------------------------
class ShippingInfo(models.Model):
    """
    Información de envío general o por producto.
    """
    titulo = models.CharField(max_length=200, default="Shipping & Delivery")
    descripcion = models.TextField(
        help_text="Descripción general de la política de envío"
    )
    tiempo_nacional = models.CharField(
        max_length=100,
        blank=True,
        help_text="Ej: 3-6 días"
    )
    tiempo_internacional = models.CharField(
        max_length=100,
        blank=True,
        help_text="Ej: 12-26 días"
    )
    costo_envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Costo de envío estándar"
    )
    envio_gratis_desde = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monto mínimo para envío gratis"
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Información de Envío"
        verbose_name_plural = "Información de Envío"
    
    def __str__(self):
        return self.titulo


# ------------------------------
# RETURN POLICIES
# ------------------------------
class ReturnPolicy(models.Model):
    """
    Políticas de devolución con íconos opcionales.
    """
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    icono = models.CharField(
        max_length=50,
        blank=True,
        help_text="Clase CSS del ícono (opcional)"
    )
    dias_devolucion = models.PositiveIntegerField(
        default=30,
        help_text="Días permitidos para devolución"
    )
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['orden']
        verbose_name = "Política de Devolución"
        verbose_name_plural = "Políticas de Devolución"
    
    def __str__(self):
        return self.titulo

# ==================== CARRITO PERSISTENTE ====================
class CarritoItem(models.Model):
    """
    Modelo para almacenar los items del carrito de forma persistente en la BD.
    Permite que los usuarios mantengan su carrito incluso después de cerrar sesión.
    """
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='carrito_items'
    )
    producto = models.ForeignKey(
        'Producto',
        on_delete=models.CASCADE
    )
    variante = models.ForeignKey(
        'Variante',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Metadatos para mostrar el item sin necesidad de queries adicionales
    color = models.CharField(max_length=50, blank=True, null=True)
    talla_codigo = models.CharField(max_length=10, blank=True, null=True)
    talla_nombre = models.CharField(max_length=50, blank=True, null=True)
    imagen_url = models.URLField(blank=True, null=True)
    
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    fecha_actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_agregado']
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"
        unique_together = ('usuario', 'producto', 'variante')
    
    def __str__(self):
        return f"{self.usuario.email} - {self.producto.nombre} x {self.cantidad}"
    
    @property
    def total_precio(self):
        """Calcular el precio total del item"""
        return self.precio * self.cantidad