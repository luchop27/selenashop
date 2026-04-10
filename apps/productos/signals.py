# apps/productos/signals.py
import logging
import os
import threading
from urllib.parse import urljoin

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.html import escape
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import MarketingCampaignState, Producto, Variante, Imagen, Coleccion, Categoria

logger = logging.getLogger(__name__)


def _delete_file_field(file_field):
    if not file_field:
        return
    try:
        # Borra el archivo del storage (S3) sin volver a guardar el modelo.
        file_field.delete(save=False)
    except Exception:
        logger.exception('❌ Error al eliminar archivo de storage: %s', getattr(file_field, 'name', file_field))


def _delete_old_file_if_changed(instance, field_name, current_file):
    if not instance.pk:
        return
    try:
        existing = instance.__class__.objects.get(pk=instance.pk)
    except instance.__class__.DoesNotExist:
        return
    old_file = getattr(existing, field_name)
    if old_file and old_file != current_file:
        _delete_file_field(old_file)


CAMPAIGN_BATCH_SIZE = 30
CAMPAIGN_SUBJECT = '¡Algo nuevo ha llegado para ti! ✨'


@receiver(post_delete, sender=Imagen)
def eliminar_archivos_imagen(sender, instance, **kwargs):
    """Eliminar archivos en storage cuando se borra una Imagen."""
    _delete_file_field(instance.imagen)
    _delete_file_field(instance.video)


@receiver(pre_save, sender=Imagen)
def eliminar_archivos_imagen_antiguos(sender, instance, **kwargs):
    """Eliminar archivos antiguos de storage cuando se actualiza una Imagen."""
    _delete_old_file_if_changed(instance, 'imagen', instance.imagen)
    _delete_old_file_if_changed(instance, 'video', instance.video)


@receiver(post_delete, sender=Coleccion)
def eliminar_imagen_coleccion(sender, instance, **kwargs):
    _delete_file_field(instance.imagen)


@receiver(pre_save, sender=Coleccion)
def eliminar_imagen_coleccion_antigua(sender, instance, **kwargs):
    _delete_old_file_if_changed(instance, 'imagen', instance.imagen)


@receiver(post_delete, sender=Categoria)
def eliminar_imagen_categoria(sender, instance, **kwargs):
    _delete_file_field(instance.imagen)


@receiver(pre_save, sender=Categoria)
def eliminar_imagen_categoria_antigua(sender, instance, **kwargs):
    _delete_old_file_if_changed(instance, 'imagen', instance.imagen)


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


def _build_site_base_url():
    base_url = getattr(settings, 'MARKETING_SITE_URL', '').strip()
    if not base_url:
        base_url = os.environ.get('MARKETING_SITE_URL', '').strip()
    if not base_url:
        base_url = 'http://localhost:8000'
    if not base_url.endswith('/'):
        base_url += '/'
    return base_url


def _absolute_url(base_url, raw_url):
    if not raw_url:
        return ''
    if raw_url.startswith('http://') or raw_url.startswith('https://'):
        return raw_url
    return urljoin(base_url, raw_url.lstrip('/'))


def _build_products_cards_html(productos, base_url):
    if not productos:
        return '<p style="margin: 0; color: #6b7280;">Pronto tendremos novedades disponibles.</p>'

    cards = []
    for producto in productos:
        first_image = producto.imagenes.order_by('posicion', 'created_at').first()
        image_src = first_image.src if first_image else ''
        image_url = _absolute_url(base_url, image_src)
        product_url = _absolute_url(base_url, producto.get_absolute_url())

        try:
            price_text = f"${producto.precio_base:.2f}"
        except Exception:
            price_text = f"${producto.precio_base}"

        product_name = escape(producto.nombre)

        cards.append(
            f'''
            <div style="width: 31%; min-width: 190px; border: 1px solid #ececec; border-radius: 12px; overflow: hidden; background: #fff;">
                <a href="{product_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div style="height: 180px; background: #f7f7f7; display: flex; align-items: center; justify-content: center;">
                        {f'<img src="{image_url}" alt="{product_name}" style="max-width: 100%; max-height: 100%; object-fit: cover;">' if image_url else '<span style="color:#9ca3af;font-size:13px;">Sin imagen</span>'}
                    </div>
                    <div style="padding: 12px 14px;">
                        <div style="font-size: 14px; font-weight: 600; color: #111827; margin-bottom: 6px;">{product_name}</div>
                        <div style="font-size: 14px; color: #111827;">{price_text}</div>
                    </div>
                </a>
            </div>
            '''
        )

    return ''.join(cards)


def _send_marketing_campaign_email():
    from apps.usuarios.models import Usuario

    recipients = list(
        Usuario.objects.filter(
            rol='cliente',
            is_active=True,
            is_subscribed=True,
        )
        .exclude(email='')
        .values_list('email', flat=True)
    )

    if not recipients:
        logger.info('📭 Campaña no enviada: no hay usuarios suscritos activos.')
        return

    latest_products = list(
        Producto.objects.filter(activo=True)
        .prefetch_related('imagenes')
        .order_by('-created_at')[:3]
    )

    base_url = _build_site_base_url()
    products_html = _build_products_cards_html(latest_products, base_url)
    novedades_url = _absolute_url(base_url, '/')

    text_body = (
        '¡No te lo puedes perder! Hemos renovado nuestro catálogo con piezas exclusivas para ti. '
        'Ingresa ahora y descubre las novedades.'
    )

    html_body = f'''
    <div style="font-family: Arial, sans-serif; max-width: 760px; margin: 0 auto; background: #ffffff; border: 1px solid #ececec; border-radius: 14px; overflow: hidden;">
        <div style="background: #111827; color: #ffffff; padding: 22px 24px; text-align: center;">
            <h2 style="margin: 0; font-size: 24px;">¡Algo nuevo ha llegado para ti! ✨</h2>
        </div>
        <div style="padding: 24px;">
            <p style="margin: 0 0 14px; font-size: 16px; color: #111827;">
                ¡No te lo puedes perder! Hemos renovado nuestro catálogo con piezas exclusivas para ti.
            </p>
            <p style="margin: 0 0 24px; font-size: 15px; color: #4b5563;">
                Estas son 3 de nuestras últimas novedades:
            </p>
            <div style="display: flex; gap: 12px; flex-wrap: wrap; justify-content: space-between;">
                {products_html}
            </div>
            <div style="text-align: center; margin-top: 26px;">
                <a href="{novedades_url}" style="display: inline-block; background: #111827; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 999px; font-weight: 600;">
                    Ver novedades
                </a>
            </div>
        </div>
    </div>
    '''

    from_email = settings.DEFAULT_FROM_EMAIL
    connection = get_connection(fail_silently=True)
    messages = []

    for recipient in recipients:
        message = EmailMultiAlternatives(
            subject=CAMPAIGN_SUBJECT,
            body=text_body,
            from_email=from_email,
            to=[recipient],
            connection=connection,
        )
        message.attach_alternative(html_body, 'text/html')
        messages.append(message)

    try:
        sent_count = connection.send_messages(messages)
        logger.info(f'📨 Campaña enviada a {sent_count} destinatarios.')
    except Exception:
        logger.exception('❌ Error enviando campaña de productos nuevos.')


def _send_marketing_campaign_async():
    thread = threading.Thread(target=_send_marketing_campaign_email, daemon=True)
    thread.start()


@receiver(post_save, sender=Producto)
def trigger_marketing_campaign(sender, instance, created, **kwargs):
    """
    Acumula productos nuevos y dispara campaña publicitaria cada 30 altas.
    Se ejecuta en background para no bloquear el request del admin.
    """
    if not created:
        return

    should_send = False

    try:
        with transaction.atomic():
            state = MarketingCampaignState.get_default()
            state.pending_new_products += 1

            if state.pending_new_products >= CAMPAIGN_BATCH_SIZE:
                state.pending_new_products = 0
                state.last_sent_at = timezone.now()
                should_send = True

            state.save()

        logger.info(
            f"📊 Contador de campaña actualizado. Pendientes: {state.pending_new_products}/{CAMPAIGN_BATCH_SIZE}"
        )

        if should_send:
            transaction.on_commit(_send_marketing_campaign_async)
    except Exception:
        logger.exception('❌ Error actualizando campaña automática de marketing.')
