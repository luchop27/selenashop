"""
Script para arreglar productos sin slug
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.productos.models import Producto
from django.utils.text import slugify

def fix_products_without_slug():
    """
    Arreglar productos que no tienen slug
    """
    productos_sin_slug = Producto.objects.filter(slug__isnull=True) | Producto.objects.filter(slug='')
    
    if not productos_sin_slug.exists():
        print("✅ Todos los productos ya tienen slug.")
        return
    
    print(f"Arreglando {productos_sin_slug.count()} productos sin slug...\n")
    
    for producto in productos_sin_slug:
        # Generar slug basado en el nombre
        base_slug = slugify(producto.nombre)
        
        # Asegurar que el slug sea único
        slug = base_slug
        counter = 1
        while Producto.objects.filter(slug=slug).exclude(id=producto.id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Guardar el slug
        producto.slug = slug
        producto.save()
        
        print(f"✅ Producto ID {producto.id}: '{producto.nombre}'")
        print(f"   Slug generado: '{slug}'\n")
    
    print(f"✅ Se arreglaron {productos_sin_slug.count()} productos.")

if __name__ == '__main__':
    print("="*60)
    print("ARREGLANDO PRODUCTOS SIN SLUG")
    print("="*60 + "\n")
    
    fix_products_without_slug()
    
    print("\n" + "="*60)
    print("✅ PROCESO COMPLETADO")
    print("="*60)
