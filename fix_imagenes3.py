#!/usr/bin/env python
# Script para usar la propiedad .src en lugar de .imagen.url

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar todas las referencias a imagen.url por src
replacements = [
    ('imagenes[0].imagen.url if imagenes[0].imagen else None', 'imagenes[0].src'),
    ('imagenes[1].imagen.url if len(imagenes) > 1 and imagenes[1].imagen else producto.main_image_src', 'imagenes[1].src if len(imagenes) > 1 else producto.main_image_src'),
    ('imagenes[0].imagen.url if imagenes[0].imagen else \'\'', 'imagenes[0].src'),
    ('imagenes[1].imagen.url if len(imagenes) > 1 and imagenes[1].imagen else producto.main_image_src', 'imagenes[1].src if len(imagenes) > 1 else producto.main_image_src'),
    ('imagenes[0].imagen.url', 'imagenes[0].src'),
    ('imagenes[1].imagen.url if len(imagenes) > 1 else producto.main_image_src', 'imagenes[1].src if len(imagenes) > 1 else producto.main_image_src'),
    ('imagenes[1].imagen.url if len(imagenes) > 1 else None', 'imagenes[1].src if len(imagenes) > 1 else None'),
]

for old, new in replacements:
    content = content.replace(old, new)

# También eliminar el filtro .exclude(imagen='') ya que .src maneja esto
content = content.replace(
    ".imagenes.filter(tipo_medio='imagen').exclude(imagen='')[:2]",
    ".imagenes.filter(tipo_medio='imagen')[:2]"
)

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Archivo actualizado exitosamente")
print("Se reemplazaron todas las referencias a .imagen.url por .src")
print("La propiedad .src maneja automáticamente imágenes/videos/URLs vacías")
