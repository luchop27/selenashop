#!/usr/bin/env python
"""
Script para diagnosticar problemas con imágenes en Django
"""
import os
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from django.conf import settings
from core.models import AboutUsImage
from apps.productos.models import Coleccion, Categoria, Producto

print("=" * 80)
print("DIAGNÓSTICO DE IMÁGENES EN DJANGO")
print("=" * 80)

# 1. Verificar configuración de MEDIA
print("\n1. CONFIGURACIÓN DE MEDIA:")
print(f"   MEDIA_URL: {settings.MEDIA_URL}")
print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"   DEBUG: {settings.DEBUG}")

# 2. Verificar que la carpeta media existe
print("\n2. CARPETA MEDIA:")
media_path = Path(settings.MEDIA_ROOT)
print(f"   ¿Existe? {media_path.exists()}")
if media_path.exists():
    print(f"   Contenido:")
    for item in media_path.iterdir():
        print(f"      - {item.name}")
        if item.is_dir():
            for subitem in item.iterdir():
                print(f"         - {subitem.name}")

# 3. Verificar AboutUsImage
print("\n3. IMÁGENES ABOUTUS:")
about_images = AboutUsImage.objects.all()
print(f"   Total de imágenes: {about_images.count()}")
for img in about_images:
    print(f"\n   Imagen: {img.titulo}")
    print(f"      - ID: {img.id}")
    print(f"      - Campo imagen: {img.imagen}")
    print(f"      - URL: {img.imagen.url}")
    print(f"      - Path completo: {img.imagen.path if img.imagen else 'N/A'}")
    print(f"      - ¿Archivo existe? {img.imagen.storage.exists(img.imagen.name) if img.imagen else False}")
    print(f"      - Activo: {img.activo}")

# 4. Verificar Colecciones con imagen
print("\n4. COLECCIONES CON IMAGEN:")
colecciones = Coleccion.objects.filter(imagen__isnull=False).exclude(imagen='')
print(f"   Total: {colecciones.count()}")
for col in colecciones[:5]:
    print(f"\n   Colección: {col.nombre}")
    print(f"      - Campo imagen: {col.imagen}")
    print(f"      - URL: {col.imagen.url}")
    print(f"      - ¿Archivo existe? {col.imagen.storage.exists(col.imagen.name) if col.imagen else False}")

# 5. Verificar Categorías con imagen
print("\n5. CATEGORÍAS CON IMAGEN:")
categorias = Categoria.objects.filter(imagen__isnull=False).exclude(imagen='')
print(f"   Total: {categorias.count()}")
for cat in categorias[:5]:
    print(f"\n   Categoría: {cat.nombre}")
    print(f"      - Campo imagen: {cat.imagen}")
    print(f"      - URL: {cat.imagen.url}")
    print(f"      - ¿Archivo existe? {cat.imagen.storage.exists(cat.imagen.name) if cat.imagen else False}")

# 6. Verificar Productos con imagen
print("\n6. PRODUCTOS CON IMAGEN:")
productos = Producto.objects.filter(imagen_principal__isnull=False).exclude(imagen_principal='')
print(f"   Total: {productos.count()}")
for prod in productos[:5]:
    print(f"\n   Producto: {prod.nombre}")
    print(f"      - Campo imagen: {prod.imagen_principal}")
    if prod.imagen_principal:
        print(f"      - URL: {prod.imagen_principal.url}")
        print(f"      - ¿Archivo existe? {prod.imagen_principal.storage.exists(prod.imagen_principal.name)}")

print("\n" + "=" * 80)
print("FIN DEL DIAGNÓSTICO")
print("=" * 80)
