from django import template
from django.db.models import Sum

register = template.Library()

@register.filter(name='sum_stock')
def sum_stock(variantes):
    """Suma el stock total de todas las variantes"""
    total = variantes.aggregate(total=Sum('stock'))['total']
    return total if total else 0
