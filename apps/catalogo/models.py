# apps/catalogo/models.py
from django.db import models


class Categoria(models.Model):
    """
    Agrupa productos (Ropa, Accesorios, Perfumes, etc.)
    Soporta jerarquía con padre -> subcategorías.
    """
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    padre = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategorias'
    )
    tipo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Opcional: ropa, accesorio, perfume..."
    )
    posicion = models.PositiveIntegerField(default=0)
    estado = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['posicion', 'nombre']
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


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
        ordering = ['posicion', 'nombre']
        verbose_name = "Estilo"
        verbose_name_plural = "Estilos"

    def __str__(self):
        return self.nombre


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
    estilo = models.ForeignKey(
        Estilo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos'
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
    material = models.CharField(max_length=100, blank=True, null=True)

    activo = models.BooleanField(default=True)
    precio_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Se usa cuando no hay variante o la variante no define precio."
    )
    tiene_tallas = models.BooleanField(
        default=False,
        help_text="Si es true, el cliente elegirá talla/variante."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.nombre


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
        # esto emula tu UNIQUE lógico (producto, talla, color)
        constraints = [
            models.UniqueConstraint(
                fields=['producto', 'talla', 'color'],
                name='uq_variante_producto_talla_color'
            )
        ]

    def __str__(self):
        base = f"{self.producto.nombre}"
        if self.color:
            base += f" - {self.color}"
        if self.talla:
            base += f" - {self.talla.codigo}"
        return base


class Imagen(models.Model):
    """
    Imagen asociada a un producto o a una variante específica.
    Al menos uno de los dos debe estar presente.
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
    url = models.URLField()
    alt = models.CharField(max_length=200, blank=True, null=True)
    posicion = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['posicion']
        verbose_name = "Imagen"
        verbose_name_plural = "Imágenes"

    def __str__(self):
        if self.producto:
            return f"Imagen de {self.producto.nombre}"
        if self.variante:
            return f"Imagen de variante {self.variante}"
        return self.url
