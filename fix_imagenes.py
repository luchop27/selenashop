#!/usr/bin/env python
# Script para arreglar referencias a imagenes en views.py

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar todas las ocurrencias
content = content.replace(
    ".imagenes.all()[:2]",
    ".imagenes.filter(tipo_medio='imagen')[:2]"
)

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Archivo actualizado exitosamente")
print("Se reemplazaron todas las ocurrencias de .imagenes.all()[:2]")
