"""
Script de diagnóstico para imágenes - Ejecutar en shell de Django
python manage.py shell < check_media.py
"""

from pathlib import Path
from django.conf import settings
from core.models import AboutUsImage
from apps.productos.models import Coleccion, Categoria, Producto

print("\n" + "="*80)
print("DIAGNÓSTICO DE IMÁGENES")
print("="*80)

# 1. Rutas configuradas
print("\n📁 RUTAS CONFIGURADAS:")
print(f"   MEDIA_URL: {settings.MEDIA_URL}")
print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"   DEBUG: {settings.DEBUG}")

# 2. Carpeta media existe
media_root = Path(settings.MEDIA_ROOT)
print(f"\n✓ Carpeta media existe: {media_root.exists()}")
if media_root.exists():
    print(f"   Permisos: {oct(media_root.stat().st_mode)[-3:]}")
    print(f"   Contenido:")
    try:
        for item in media_root.iterdir():
            print(f"      📂 {item.name}/")
            if item.is_dir():
                count = len(list(item.iterdir()))
                print(f"         ({count} archivos)")
    except Exception as e:
        print(f"      ❌ Error al leer: {e}")

# 3. Imágenes AboutUs
print(f"\n🖼️  IMÁGENES ABOUTUS:")
about_images = AboutUsImage.objects.all()
print(f"   Total: {about_images.count()}")
for img in about_images:
    print(f"\n   • {img.titulo or f'Imagen #{img.id}'}")
    print(f"     Campo: {img.imagen}")
    print(f"     URL: {img.imagen.url}")
    if img.imagen:
        full_path = Path(img.imagen.path) if hasattr(img.imagen, 'path') else Path(settings.MEDIA_ROOT) / img.imagen.name
        print(f"     Ruta completa: {full_path}")
        print(f"     ✓ Existe: {full_path.exists()}")
        if not full_path.exists():
            print(f"     ❌ ARCHIVO NO ENCONTRADO")

# 4. Colecciones con imagen
print(f"\n🏪 COLECCIONES CON IMAGEN:")
colecciones = Coleccion.objects.filter(imagen__isnull=False).exclude(imagen='')
print(f"   Total: {colecciones.count()}")
for col in colecciones[:3]:
    print(f"\n   • {col.nombre}")
    print(f"     URL: {col.imagen.url}")
    if col.imagen:
        full_path = Path(col.imagen.path) if hasattr(col.imagen, 'path') else Path(settings.MEDIA_ROOT) / col.imagen.name
        print(f"     ✓ Existe: {full_path.exists()}")

print("\n" + "="*80)
print("FIN DEL DIAGNÓSTICO")
print("="*80 + "\n")
