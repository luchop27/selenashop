from django.shortcuts import render, get_object_or_404
from .models import PaginaAyuda, CategoriaFAQ


def pagina_ayuda(request, tipo):
    """
    Vista genérica para mostrar páginas de ayuda
    Tipos válidos: 'terminos', 'devoluciones', 'envios', 'privacidad'
    """
    tipos_validos = ['terminos', 'devoluciones', 'envios', 'privacidad']
    
    if tipo not in tipos_validos:
        return render(request, '404.html', status=404)
    
    pagina = get_object_or_404(PaginaAyuda, tipo=tipo, activo=True)
    
    context = {
        'pagina': pagina,
        'titulo': pagina.titulo,
    }
    
    return render(request, 'terms-conditions.html', context)


def faq_list(request):
    """
    Vista para mostrar todas las preguntas frecuentes organizadas por categoría
    """
    categorias = CategoriaFAQ.objects.filter(activo=True).prefetch_related(
        'preguntas'
    ).order_by('orden')
    
    # Filtrar preguntas activas en cada categoría
    for categoria in categorias:
        categoria.preguntas_activas = categoria.preguntas.filter(activo=True).order_by('orden')
    
    context = {
        'categorias': categorias,
    }
    
    return render(request, 'faq-1.html', context)


# Vistas específicas (opcional, por si prefieres rutas más claras)
def terms_conditions(request):
    return pagina_ayuda(request, 'terminos')


def delivery_return(request):
    return pagina_ayuda(request, 'devoluciones')


def shipping(request):
    return pagina_ayuda(request, 'envios')


def privacy_policy(request):
    return pagina_ayuda(request, 'privacidad')

