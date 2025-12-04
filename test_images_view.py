"""
Vista de prueba para diagnóstico de imágenes
Agregaesta vista a tu proyecto y accede a: /test-images/
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from pathlib import Path
from django.conf import settings

@require_http_methods(["GET"])
def test_images(request):
    """Vista para diagnosticar problemas con imágenes"""
    
    from core.models import AboutUsImage
    from apps.productos.models import Coleccion, Categoria, Producto
    
    # Información de configuración
    config = {
        'DEBUG': settings.DEBUG,
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': str(settings.MEDIA_ROOT),
        'MEDIA_ROOT_EXISTS': Path(settings.MEDIA_ROOT).exists(),
    }
    
    # Recopilar datos sobre imágenes
    data = {
        'config': config,
        'aboutus_images': [],
        'colecciones': [],
        'categorias': [],
        'productos': [],
        'media_folders': [],
    }
    
    # AboutUs Images
    for img in AboutUsImage.objects.all()[:10]:
        data['aboutus_images'].append({
            'id': img.id,
            'titulo': img.titulo,
            'imagen': str(img.imagen),
            'url': img.imagen.url if img.imagen else None,
            'existe': Path(settings.MEDIA_ROOT / str(img.imagen)).exists() if img.imagen else False,
        })
    
    # Colecciones
    for col in Coleccion.objects.filter(imagen__isnull=False).exclude(imagen='')[:10]:
        data['colecciones'].append({
            'id': col.id,
            'nombre': col.nombre,
            'imagen': str(col.imagen),
            'url': col.imagen.url,
            'existe': Path(settings.MEDIA_ROOT / str(col.imagen)).exists(),
        })
    
    # Categorías
    for cat in Categoria.objects.filter(imagen__isnull=False).exclude(imagen='')[:10]:
        data['categorias'].append({
            'id': cat.id,
            'nombre': cat.nombre,
            'imagen': str(cat.imagen),
            'url': cat.imagen.url,
            'existe': Path(settings.MEDIA_ROOT / str(cat.imagen)).exists(),
        })
    
    # Productos
    for prod in Producto.objects.filter(imagen_principal__isnull=False).exclude(imagen_principal='')[:10]:
        data['productos'].append({
            'id': prod.id,
            'nombre': prod.nombre,
            'imagen': str(prod.imagen_principal),
            'url': prod.imagen_principal.url,
            'existe': Path(settings.MEDIA_ROOT / str(prod.imagen_principal)).exists(),
        })
    
    # Carpetas en media
    try:
        for item in Path(settings.MEDIA_ROOT).iterdir():
            if item.is_dir():
                files = list(item.iterdir())
                data['media_folders'].append({
                    'nombre': item.name,
                    'cantidad_archivos': len(files),
                    'archivos': [f.name for f in files[:5]]
                })
    except:
        pass
    
    return JsonResponse(data, indent=2)
