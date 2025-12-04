#!/usr/bin/env python
"""
Script automático para completar toda la configuración de provincias y ciudades
Ejecutar: python setup_provincias_ciudades_auto.py

Este script:
1. Ejecuta las migraciones
2. Puebla provincias y ciudades del Ecuador
3. Verificación
"""

import os
import sys
import django
from pathlib import Path

# Agregar la raíz del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from django.core.management import call_command
from apps.usuarios.models import Provincia, Ciudad

print("\n" + "="*70)
print("CONFIGURACIÓN AUTOMÁTICA: REGISTRO CON PROVINCIAS Y CIUDADES")
print("="*70)

# PASO 1: Ejecutar migraciones
print("\n📦 PASO 1: Ejecutando migraciones...")
try:
    call_command('migrate', 'usuarios', verbosity=2)
    print("✓ Migraciones ejecutadas correctamente")
except Exception as e:
    print(f"❌ Error en migraciones: {e}")
    sys.exit(1)

# PASO 2: Poblar provincias y ciudades
print("\n🏘️  PASO 2: Poblando provincias y ciudades...")

provincias_ciudades = {
    'Azuay': ['Cuenca', 'Gualaceo', 'Paute', 'Sígsig', 'Chordeleg'],
    'Bolívar': ['Guaranda', 'Caluma', 'Chillanes', 'Echeandía', 'San Miguel'],
    'Cañar': ['Azogues', 'La Troncal', 'Cañar', 'El Tambo', 'Biblián'],
    'Carchi': ['Tulcán', 'San Gabriel', 'Espejo', 'Montúfar', 'Huaca'],
    'Chimborazo': ['Riobamba', 'Latacunga', 'Penipe', 'Guamote', 'Cumandá'],
    'Cotopaxi': ['Latacunga', 'La Maná', 'Pangua', 'Salcedo', 'Pujilí'],
    'El Oro': ['Machala', 'Santa Rosa', 'Huaquillas', 'Pasaje', 'Piñas'],
    'Esmeraldas': ['Esmeraldas', 'Atacames', 'Muisne', 'Quinindé', 'San Lorenzo'],
    'Guayas': ['Guayaquil', 'Durán', 'Milagro', 'Daule', 'Samborondón', 'Balzar'],
    'Imbabura': ['Ibarra', 'Otavalo', 'Antonio Ante', 'Cotacachi', 'Urcuquí'],
    'Loja': ['Loja', 'Catamayo', 'Macará', 'Vilcabamba', 'Saraguro'],
    'Los Ríos': ['Babahoyo', 'Quevedo', 'Vinces', 'Baba', 'Mocache'],
    'Manabí': ['Manta', 'Portoviejo', 'Jipijapa', 'El Carmen', 'Chone', 'Bahía de Caráquez'],
    'Morona Santiago': ['Macas', 'Sucúa', 'Palora', 'Tena', 'Puyo'],
    'Napo': ['Tena', 'Archidona', 'Puerto Misahuallí', 'Puyo', 'Quijos'],
    'Pastaza': ['Puyo', 'Mera', 'Santa Clara', 'Arajuno', 'Shell'],
    'Pichincha': ['Quito', 'Cayambe', 'Machachi', 'Sangolquí', 'Latacunga', 'Puembo'],
    'Santa Elena': ['Santa Elena', 'La Libertad', 'Salinas', 'Olón', 'Manglaralto'],
    'Santo Domingo': ['Santo Domingo'],
    'Sucumbíos': ['Nueva Loja', 'Lago Agrio', 'Cascales', 'Putumayo', 'Cuyabeno'],
    'Tungurahua': ['Ambato', 'Baños', 'Latacunga', 'Pelileo', 'Píllaro'],
    'Orellana': ['Puerto Francisco de Orellana', 'Coca', 'Joya de los Sachas', 'Loreto'],
}

provincias_creadas = 0
ciudades_creadas = 0

for provincia_nombre, ciudades_nombres in provincias_ciudades.items():
    provincia, p_created = Provincia.objects.get_or_create(
        nombre=provincia_nombre,
        defaults={'activa': True}
    )
    
    if p_created:
        provincias_creadas += 1
    
    for ciudad_nombre in ciudades_nombres:
        ciudad, c_created = Ciudad.objects.get_or_create(
            nombre=ciudad_nombre,
            provincia=provincia,
            defaults={'activa': True}
        )
        if c_created:
            ciudades_creadas += 1

print(f"✓ {provincias_creadas} provincias creadas/verificadas")
print(f"✓ {ciudades_creadas} ciudades creadas/verificadas")

# PASO 3: Verificación final
print("\n✅ PASO 3: Verificación final...")
total_provincias = Provincia.objects.count()
total_ciudades = Ciudad.objects.count()

print(f"Total de provincias en la BD: {total_provincias}")
print(f"Total de ciudades en la BD: {total_ciudades}")

print("\n" + "="*70)
print("✨ ¡CONFIGURACIÓN COMPLETADA!")
print("="*70)
print("\nPróximos pasos:")
print("1. Reinicia el servidor: python manage.py runserver")
print("2. Ve a http://localhost:8000/register/")
print("3. Selecciona una provincia en el primer combobox")
print("4. Las ciudades de esa provincia aparecerán en el segundo combobox")
print("\n")
