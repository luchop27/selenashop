from decimal import Decimal
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Avg, DecimalField, F, Max, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.usuarios.models import Usuario
from core.models import DetallePedido, Pedido


DASHBOARD_CACHE_KEY = "admin_dashboard:metrics:v1"
DASHBOARD_CACHE_TTL_SECONDS = 120


def _zero_decimal() -> Decimal:
    return Decimal("0.00")


def _percentage_change(current_value, previous_value) -> float:
    current_decimal = Decimal(current_value or 0)
    previous_decimal = Decimal(previous_value or 0)

    if previous_decimal > 0:
        return round(float(((current_decimal - previous_decimal) / previous_decimal) * 100), 2)

    if current_decimal > 0:
        return 100.0

    return 0.0


def _sum_amount(queryset, field_name: str) -> Decimal:
    return queryset.aggregate(
        total=Coalesce(
            Sum(field_name),
            Value(_zero_decimal(), output_field=DecimalField(max_digits=12, decimal_places=2)),
        )
    )["total"]


def get_admin_dashboard_context() -> dict:
    cached_context = cache.get(DASHBOARD_CACHE_KEY)
    if cached_context is not None:
        return cached_context

    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    last_60_days = now - timedelta(days=60)

    paid_orders = Pedido.objects.filter(pagado=True).exclude(estado="cancelado")
    all_orders = Pedido.objects.exclude(estado="cancelado")
    customer_users = Usuario.objects.filter(rol="cliente")

    total_earnings = _sum_amount(paid_orders, "total")
    total_discount_amount = _sum_amount(paid_orders, "discount_amount")
    net_balance = total_earnings - total_discount_amount

    total_orders = all_orders.count()
    total_customers = customer_users.count()

    earnings_last_30 = _sum_amount(paid_orders.filter(created_at__gte=last_30_days), "total")
    earnings_previous_30 = _sum_amount(
        paid_orders.filter(created_at__gte=last_60_days, created_at__lt=last_30_days),
        "total",
    )

    orders_last_30 = all_orders.filter(created_at__gte=last_30_days).count()
    orders_previous_30 = all_orders.filter(created_at__gte=last_60_days, created_at__lt=last_30_days).count()

    customers_last_30 = customer_users.filter(fecha_registro__gte=last_30_days).count()
    customers_previous_30 = customer_users.filter(fecha_registro__gte=last_60_days, fecha_registro__lt=last_30_days).count()

    top_products = list(
        DetallePedido.objects.filter(pedido__pagado=True)
        .exclude(pedido__estado="cancelado")
        .values("producto__id", "producto__nombre", "nombre_producto")
        .annotate(
            total_vendidos=Coalesce(Sum("cantidad"), Value(0)),
            total_ingresos=Coalesce(
                Sum(
                    F("cantidad") * F("precio_unitario"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                Value(_zero_decimal(), output_field=DecimalField(max_digits=12, decimal_places=2)),
            ),
            precio_promedio=Coalesce(
                Avg("precio_unitario"),
                Value(_zero_decimal(), output_field=DecimalField(max_digits=12, decimal_places=2)),
            ),
            imagen_url=Max("imagen_url"),
        )
        .order_by("-total_vendidos", "-total_ingresos")[:6]
    )

    context = {
        "total_earnings": total_earnings,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "my_balance": net_balance,
        "earnings_change": _percentage_change(earnings_last_30, earnings_previous_30),
        "orders_change": _percentage_change(orders_last_30, orders_previous_30),
        "customers_change": _percentage_change(customers_last_30, customers_previous_30),
        "balance_change": _percentage_change(
            earnings_last_30 - _sum_amount(paid_orders.filter(created_at__gte=last_30_days), "discount_amount"),
            earnings_previous_30
            - _sum_amount(
                paid_orders.filter(created_at__gte=last_60_days, created_at__lt=last_30_days),
                "discount_amount",
            ),
        ),
        "top_products": top_products,
    }

    cache.set(DASHBOARD_CACHE_KEY, context, DASHBOARD_CACHE_TTL_SECONDS)
    return context
