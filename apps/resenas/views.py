from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.productos.models import Producto
from .models import Resena, RespuestaResena


@login_required
@require_http_methods(["POST"])
def submit_review(request, producto_id):
    """
    Vista para enviar una nueva reseña
    """
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Verificar si el usuario ya reseñó este producto
    if Resena.objects.filter(producto=producto, usuario=request.user).exists():
        return JsonResponse({
            'success': False,
            'message': 'Ya has reseñado este producto'
        }, status=400)
    
    try:
        calificacion = int(request.POST.get('rating', 0))
        if calificacion < 1 or calificacion > 5:
            raise ValueError("Calificación inválida")
        
        titulo = request.POST.get('title', '').strip()
        comentario = request.POST.get('comment', '').strip()
        
        if not comentario:
            return JsonResponse({
                'success': False,
                'message': 'El comentario es requerido'
            }, status=400)
        
        # Crear la reseña
        resena = Resena.objects.create(
            producto=producto,
            usuario=request.user,
            calificacion=calificacion,
            titulo=titulo,
            comentario=comentario
        )
        
        # Calcular nuevo promedio de calificaciones
        resenas = Resena.objects.filter(producto=producto)
        promedio = sum(r.calificacion for r in resenas) / resenas.count()
        
        return JsonResponse({
            'success': True,
            'message': 'Reseña enviada correctamente',
            'review': {
                'id': resena.id,
                'rating': resena.calificacion,
                'title': resena.titulo,
                'comment': resena.comentario,
                'user_name': request.user.get_full_name() or request.user.email,
                'created_at': resena.get_tiempo_transcurrido(),
            },
            'average_rating': round(promedio, 1),
            'total_reviews': resenas.count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def reply_review(request, resena_id):
    """
    Vista para responder a una reseña (solo staff/admin)
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'No tienes permisos para responder reseñas'
        }, status=403)
    
    resena = get_object_or_404(Resena, id=resena_id)
    comentario = request.POST.get('comment', '').strip()
    
    if not comentario:
        return JsonResponse({
            'success': False,
            'message': 'El comentario es requerido'
        }, status=400)
    
    try:
        respuesta = RespuestaResena.objects.create(
            resena=resena,
            usuario=request.user,
            comentario=comentario
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Respuesta enviada correctamente',
            'reply': {
                'id': respuesta.id,
                'comment': respuesta.comentario,
                'user_name': request.user.get_full_name() or 'Modave',
                'created_at': 'Just now'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_reviews(request, producto_id):
    """
    Vista para obtener todas las reseñas de un producto
    """
    producto = get_object_or_404(Producto, id=producto_id)
    sort_by = request.GET.get('sort', 'recent')  # recent, rating_high, rating_low
    
    resenas = Resena.objects.filter(producto=producto).select_related('usuario').prefetch_related('respuestas__usuario')
    
    # Aplicar ordenamiento
    if sort_by == 'rating_high':
        resenas = resenas.order_by('-calificacion', '-creado_en')
    elif sort_by == 'rating_low':
        resenas = resenas.order_by('calificacion', '-creado_en')
    else:  # recent (default)
        resenas = resenas.order_by('-creado_en')
    
    # Calcular estadísticas
    total = resenas.count()
    if total > 0:
        promedio = sum(r.calificacion for r in resenas) / total
        rating_counts = {i: 0 for i in range(1, 6)}
        for resena in resenas:
            rating_counts[resena.calificacion] += 1
    else:
        promedio = 0
        rating_counts = {i: 0 for i in range(1, 6)}
    
    # Verificar si el usuario actual ya reseñó (si está autenticado)
    user_has_reviewed = False
    if hasattr(request, 'user') and request.user.is_authenticated:
        user_has_reviewed = Resena.objects.filter(
            producto=producto,
            usuario=request.user
        ).exists()
    
    # Construir respuesta
    reviews_data = []
    for resena in resenas:
        reviews_data.append({
            'id': resena.id,
            'rating': resena.calificacion,
            'title': resena.titulo,
            'comment': resena.comentario,
            'user_name': resena.usuario.get_full_name() or resena.usuario.email.split('@')[0],
            'created_at': resena.get_tiempo_transcurrido(),
            'verified': resena.verificado,
            'replies': [
                {
                    'id': resp.id,
                    'comment': resp.comentario,
                    'user_name': resp.usuario.get_full_name() or 'Modave',
                    'created_at': resp.get_tiempo_transcurrido() if hasattr(resp, 'get_tiempo_transcurrido') else resp.creado_en.strftime('%Y-%m-%d')
                }
                for resp in resena.respuestas.all()
            ]
        })
    
    return JsonResponse({
        'success': True,
        'reviews': reviews_data,
        'user_has_reviewed': user_has_reviewed,
        'stats': {
            'average': round(promedio, 1),
            'total': total,
            'rating_counts': rating_counts
        }
    })
