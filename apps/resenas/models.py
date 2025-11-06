# apps/resenas/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Resena(models.Model):
    """
    Reseñas y calificaciones de las clientas sobre productos.
    Una usuaria puede reseñar un producto solo una vez.
    """
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.CASCADE,
        related_name='resenas'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resenas'
    )
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación de 1 a 5 estrellas"
    )
    titulo = models.CharField(max_length=200, blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ['-creado_en']
        constraints = [
            models.UniqueConstraint(
                fields=['producto', 'usuario'],
                name='resenas_uq_producto_usuario'
            )
        ]
        indexes = [
            models.Index(fields=['producto', '-creado_en']),
            models.Index(fields=['calificacion']),
        ]

    def __str__(self):
        return f"Reseña de {self.usuario.email} para {self.producto.nombre} ({self.calificacion}⭐)"
