# apps/productos/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Variante, Producto
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Variante)
@receiver(post_delete, sender=Variante)
def verificar_stock_producto(sender, instance, **kwargs):
    """
    Después de guardar o eliminar una variante, verifica el stock total del producto.
    Si el producto NO está marcado como 'bajo_pedido' y su stock total es 0,
    lo elimina automáticamente del sistema.
    """
    producto = instance.producto
    
    # Calcular stock total de todas las variantes del producto
    stock_total = sum(v.stock for v in producto.variantes.all())
    
    logger.info(f"📦 Verificando stock de '{producto.nombre}': {stock_total} unidades")
    
    # Si el stock es 0 y el producto NO está bajo pedido, eliminarlo
    if stock_total == 0 and not producto.bajo_pedido:
        logger.warning(f"🗑️  Eliminando producto '{producto.nombre}' - Stock: 0, Bajo pedido: No")
        producto.delete()
    elif stock_total == 0 and producto.bajo_pedido:
        logger.info(f"✅ Producto '{producto.nombre}' sin stock pero marcado como 'bajo pedido' - Se mantiene visible")
    else:
        logger.info(f"✅ Producto '{producto.nombre}' con stock suficiente")
