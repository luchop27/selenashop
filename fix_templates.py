#!/usr/bin/env python
# Script para reemplazar .imagen.url por .src en todos los templates

import os
import glob

templates_dir = 'templates'
changes_made = 0
files_modified = 0

# Buscar todos los archivos HTML
html_files = glob.glob(f'{templates_dir}/**/*.html', recursive=True)

for filepath in html_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Reemplazos específicos
        replacements = [
            ('.imagenes.all.0.imagen.url', '.imagenes.all.0.src'),
            ('.imagenes.all.1.imagen.url', '.imagenes.all.1.src'),
            ('.imagenes.first.imagen.url', '.imagenes.first.src'),
            ('imagenes.0.imagen.url', 'imagenes.0.src'),
            ('imagenes.1.imagen.url', 'imagenes.1.src'),
            ('item.product.imagenes.first.imagen.url', 'item.product.imagenes.first.src'),
            ('producto.imagenes.first.imagen.url', 'producto.imagenes.first.src'),
            ('producto.imagenes.all.0.imagen.url', 'producto.imagenes.all.0.src'),
            ('producto.imagenes.all.1.imagen.url', 'producto.imagenes.all.1.src'),
            ('coleccion.imagen.url', 'coleccion.imagen.url'),  # No cambiar - es diferente
            ('categoria.imagen.url', 'categoria.imagen.url'),  # No cambiar - es diferente
            ('imagen.imagen.url', 'imagen.src'),  # Este es el objeto Imagen
        ]
        
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                changes_made += content.count(new) - original_content.count(new)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            files_modified += 1
            print(f"✓ Modificado: {filepath}")
    
    except Exception as e:
        print(f"✗ Error en {filepath}: {e}")

print(f"\n{'='*50}")
print(f"✓ Proceso completado")
print(f"  Archivos modificados: {files_modified}")
print(f"  Total de cambios: {changes_made}")
print(f"{'='*50}")
