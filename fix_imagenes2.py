#!/usr/bin/env python
# Script para arreglar referencias a imagenes en views.py - verificar que imagen no sea None

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar el filtro para excluir imágenes sin archivo
content = content.replace(
    ".imagenes.filter(tipo_medio='imagen')[:2]",
    ".imagenes.filter(tipo_medio='imagen').exclude(imagen='')[:2]"
)

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Archivo actualizado exitosamente")
print("Se agregó .exclude(imagen='') para filtrar imágenes vacías")
