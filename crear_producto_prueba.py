#!/usr/bin/env python
"""
Script para crear producto de prueba: Blusa Tropical
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from apps.productos.models import (
    Producto, Categoria, Coleccion, Variante, 
    Atributo, ValorAtributo, VarianteAtributo
)

def crear_producto_prueba():
    # 1. Obtener la categoría Blusa (subcategoría de Ropa)
    try:
        categoria_blusa = Categoria.objects.get(nombre__iexact='Blusa')
        print(f"✓ Categoría encontrada: {categoria_blusa.nombre}")
    except Categoria.DoesNotExist:
        print("✗ No existe la categoría 'Blusa'")
        return
    
    # 2. Obtener la colección Playa
    try:
        coleccion_playa = Coleccion.objects.get(nombre__iexact='Playa')
        print(f"✓ Colección encontrada: {coleccion_playa.nombre}")
    except Coleccion.DoesNotExist:
        print("✗ No existe la colección 'Playa'")
        # Crear la colección si no existe
        coleccion_playa = Coleccion.objects.create(
            nombre='Playa',
            slug='playa',
            descripcion='Colección de ropa para la playa',
            activo=True,
            destacada=False,
            posicion=1
        )
        print(f"✓ Colección 'Playa' creada")
    
    # 3. Crear el producto
    import random
    random_num = random.randint(1000, 9999)
    producto = Producto.objects.create(
        nombre=f'Blusa Tropical {random_num}',
        slug=f'blusa-tropical-{random_num}',
        categoria=categoria_blusa,
        coleccion=coleccion_playa,
        tipo='simple',
        descripcion_corta='Blusa fresca y cómoda para el verano',
        descripcion_larga='Blusa tropical perfecta para días de playa y calor. Diseño ligero y cómodo.',
        precio_base=20.00,
        tiene_tallas=True,
        activo=True
    )
    print(f"✓ Producto creado: {producto.nombre} (ID: {producto.id})")
    
    # 4. Obtener atributo Talla y valor M
    try:
        atributo_talla = Atributo.objects.get(nombre__iexact='Talla')
        valor_m = ValorAtributo.objects.get(atributo=atributo_talla, valor__iexact='M')
        print(f"✓ Talla M encontrada (ID: {valor_m.id})")
    except (Atributo.DoesNotExist, ValorAtributo.DoesNotExist):
        print("✗ No existe el atributo Talla o el valor M")
        return
    
    # 5. Crear la variante
    variante = Variante.objects.create(
        producto=producto,
        sku=f'BLUSA-TROPICAL-M',
        precio=20.00,
        stock=5
    )
    print(f"✓ Variante creada: {variante.sku} - Stock: {variante.stock}")
    
    # 6. Asociar el atributo Talla M a la variante
    variante_atributo = VarianteAtributo.objects.create(
        variante=variante,
        valor_atributo=valor_m
    )
    print(f"✓ Atributo asociado: {valor_m.atributo.nombre} = {valor_m.valor}")
    
    # 7. Verificar datos
    print("\n" + "="*50)
    print("RESUMEN DEL PRODUCTO CREADO")
    print("="*50)
    print(f"Nombre: {producto.nombre}")
    print(f"Categoría: {producto.categoria.nombre}")
    print(f"Colección: {producto.coleccion.nombre if producto.coleccion else 'Sin colección'}")
    print(f"Precio base: ${producto.precio_base}")
    print(f"Total variantes: {producto.variantes.count()}")
    print(f"Stock total: {sum(v.stock for v in producto.variantes.all())}")
    print("\nVariantes:")
    for v in producto.variantes.all():
        atributos = VarianteAtributo.objects.filter(variante=v)
        attrs_str = ", ".join([f"{va.valor_atributo.atributo.nombre}: {va.valor_atributo.valor}" for va in atributos])
        print(f"  - {v.sku}: Stock={v.stock}, Precio=${v.precio} [{attrs_str}]")
    print("="*50)

if __name__ == '__main__':
    crear_producto_prueba()
