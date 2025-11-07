# apps/productos/models.py
from django.db import models
from django.urls import reverse


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        # URL pattern in `apps.productos.urls` uses the name 'producto_detail' and
        # expects the product slug. Use that to build the absolute URL.
        try:
            return reverse('productos:producto_detail', args=[self.slug])
        except Exception:
            # Fallback: build a simple path if URL reversal fails
            return f"/producto/{self.slug}/"


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
    Imagen asociada a un producto o a una variante específica.
    """
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
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    url = models.TextField(default='', blank=True, help_text="URL alternativa si no se usa archivo")
    posicion = models.PositiveIntegerField(default=0, help_text="Orden de visualización")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['posicion', 'created_at']
        verbose_name = "Imagen"
        verbose_name_plural = "Imágenes"
        constraints = [
            models.CheckConstraint(
                check=(models.Q(producto__isnull=False) | models.Q(variante__isnull=False)),
                name='productos_imagen_producto_o_variante_not_null',
            ),
        ]

    def __str__(self):
        if self.producto:
            return f"Imagen de {self.producto.nombre}"
        if self.variante:
            return f"Imagen de variante {self.variante}"
        return self.url or ""

    @property
    def src(self):
        if self.imagen:
            return self.imagen.url
        return self.url or ""


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
