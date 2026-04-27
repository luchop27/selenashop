from datetime import timedelta

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.productos.models import Variante
from core.models import Pedido


class Command(BaseCommand):
    help = (
        'Cancela pedidos pendientes por transferencia no pagados con mas de N horas '
        'y restaura su stock.'
    )

    def add_arguments(self, parser):
        default_hours = int(getattr(settings, 'UNPAID_ORDER_CANCEL_HOURS', 2) or 2)
        parser.add_argument(
            '--hours',
            type=int,
            default=default_hours,
            help='Cantidad de horas para considerar un pedido como expirado (default: settings.UNPAID_ORDER_CANCEL_HOURS).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la ejecucion sin modificar pedidos ni stock.',
        )

    def handle(self, *args, **options):
        hours = max(1, options['hours'])
        dry_run = options['dry_run']
        cutoff = timezone.now() - timedelta(hours=hours)

        pedidos_qs = Pedido.objects.filter(
            estado='pendiente',
            pagado=False,
            metodo_pago='bank_transfer',
            created_at__lte=cutoff,
        )

        total_candidatos = pedidos_qs.count()
        if total_candidatos == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Sin pedidos para cancelar (estado=pendiente, transferencias sin pago, >{hours}h).'
                )
            )
            return

        cancelados = 0
        restaurados = 0
        advertencias = 0

        with transaction.atomic():
            pedidos = list(
                pedidos_qs
                .select_for_update()
                .prefetch_related('items__variante', 'items__producto')
            )

            for pedido in pedidos:
                restauradas_pedido, warnings_pedido = self._restaurar_stock_pedido(
                    pedido,
                    dry_run=dry_run,
                )
                restaurados += restauradas_pedido
                advertencias += warnings_pedido

                if not dry_run:
                    pedido.estado = 'cancelado'
                    pedido.save(update_fields=['estado', 'updated_at'])

                cancelados += 1

        mode = 'dry-run' if dry_run else 'aplicado'
        style = self.style.WARNING if dry_run else self.style.SUCCESS
        self.stdout.write(
            style(
                'cancel_unpaid_orders | '
                f'candidatos={total_candidatos} '
                f'cancelados={cancelados} '
                f'unidades_restauradas={restaurados} '
                f'advertencias={advertencias} '
                f'modo={mode}'
            )
        )

    def _restaurar_stock_pedido(self, pedido, dry_run=False):
        cantidades_por_variante = {}
        warnings_count = 0

        for item in pedido.items.all():
            variante_id = item.variante_id

            if not variante_id and item.producto_id:
                variante_id = (
                    Variante.objects
                    .filter(producto_id=item.producto_id)
                    .order_by('id')
                    .values_list('id', flat=True)
                    .first()
                )

            if not variante_id:
                warnings_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'Pedido {pedido.numero_pedido}: item "{item.nombre_producto}" sin variante para restaurar stock.'
                    )
                )
                continue

            cantidades_por_variante[variante_id] = (
                cantidades_por_variante.get(variante_id, 0) + item.cantidad
            )

        unidades_restauradas = 0
        for variante_id, cantidad in cantidades_por_variante.items():
            try:
                variante = Variante.objects.select_for_update().get(id=variante_id)
            except Variante.DoesNotExist:
                warnings_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'Pedido {pedido.numero_pedido}: variante {variante_id} no existe, no se pudo restaurar {cantidad} unidad(es).'
                    )
                )
                continue

            if not dry_run:
                variante.stock += cantidad
                variante.save(update_fields=['stock', 'updated_at'])

            unidades_restauradas += cantidad

        return unidades_restauradas, warnings_count
