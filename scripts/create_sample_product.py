"""
Crea un producto de ejemplo: "Vestido de Gala" (estilo Gala, talla S)
Ejecutar con el Python del venv:
D:/Proyectos_Django_Trabajos/TiendaOnline/.venv/Scripts/python.exe scripts/create_sample_product.py
"""
import os
import django
from django.utils.text import slugify

import sys
# Asegurarnos de que la raíz del proyecto esté en sys.path para importar settings
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()


from apps.productos.models import Categoria, Estilo, Producto, Talla, Variante, Imagen

# Crear o obtener categoría principal y subcategoría
cat_ropa, created = Categoria.objects.get_or_create(nombre='Ropa', slug='ropa')

# Intento con subcategoría Vestidos
categoria_vestidos, created = Categoria.objects.get_or_create(
    nombre='Vestidos',
    slug='vestidos',
    padre=cat_ropa
)

# Crear estilo Gala
estilo_gala, created = Estilo.objects.get_or_create(nombre='Gala', slug='gala')

# Crear talla S
talla_s, created = Talla.objects.get_or_create(codigo='S', defaults={'nombre':'Small'})

# Crear producto
nombre = 'Vestido de Gala Elegante'
slug = slugify(nombre)
producto, created = Producto.objects.get_or_create(
    nombre=nombre,
    defaults={
        'slug': slug,
        'tipo': 'vestido',
        'descripcion_corta': 'Vestido de gala elegante, ideal para eventos formales.',
        'descripcion_larga': 'Vestido confeccionado con telas premium, corte ceñido y detalles bordados.',
        'marca': 'Selena',
        'material': 'Seda',
        'precio_base': 149.99,
        'tiene_tallas': True,
        'activo': True,
        'categoria': categoria_vestidos,
        'estilo': estilo_gala,
    }
)

# Crear variante talla S
sku = f"VG-{talla_s.codigo}-001"
variante, v_created = Variante.objects.get_or_create(
    producto=producto,
    talla=talla_s,
    color='Rojo',
    defaults={
        'sku': sku,
        'precio': 149.99,
        'stock': 5,
    }
)

# Crear imagen de ejemplo
imagen_url = 'https://via.placeholder.com/800x1200?text=Vestido+de+Gala'
imagen, i_created = Imagen.objects.get_or_create(producto=producto, url=imagen_url)

print('Creado/Obtenido:')
print('Categoria Ropa ID:', cat_ropa.id)
print('Categoria Vestidos ID:', categoria_vestidos.id)
print('Estilo Gala ID:', estilo_gala.id)
print('Talla S ID:', talla_s.id)
print('Producto ID:', producto.id, 'Nombre:', producto.nombre)
print('Variante ID:', variante.id, 'SKU:', variante.sku, 'Talla:', variante.talla.codigo, 'Stock:', variante.stock)
print('Imagen ID:', imagen.id, 'URL:', imagen.url)
print('\nPuedes ver esto en el admin: http://127.0.0.1:8000/admin/productos/producto/{}/change/'.format(producto.id))
