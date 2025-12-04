#!/usr/bin/env python
"""
Script automático para completar toda la configuración
Ejecutar: python setup_registro_ciudades.py

Este script:
1. Ejecuta las migraciones
2. Puebla la base de datos con ciudades del Ecuador
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
from apps.usuarios.models import Ciudad

print("\n" + "="*70)
print("CONFIGURACIÓN AUTOMÁTICA: REGISTRO CON CIUDADES DEL ECUADOR")
print("="*70)

# PASO 1: Ejecutar migraciones
print("\n📦 PASO 1: Ejecutando migraciones...")
try:
    call_command('migrate', 'usuarios', verbosity=2)
    print("✓ Migraciones ejecutadas correctamente")
except Exception as e:
    print(f"❌ Error en migraciones: {e}")
    sys.exit(1)

# PASO 2: Verificar si las ciudades ya existen
print("\n🏘️  PASO 2: Verificando ciudades...")
existing_count = Ciudad.objects.count()
print(f"Ciudades en la BD: {existing_count}")

if existing_count > 0:
    print("✓ Las ciudades ya están cargadas")
else:
    print("Cargando ciudades del Ecuador...")
    
    # Lista de ciudades
    ciudades_data = [
        # Azuay
        ('Cuenca', 'Azuay', '010101'),
        ('Gualaceo', 'Azuay', '010102'),
        ('Paute', 'Azuay', '010103'),
        ('Sígsig', 'Azuay', '010104'),
        ('Chordeleg', 'Azuay', '010105'),
        
        # Bolívar
        ('Guaranda', 'Bolívar', '020101'),
        ('Caluma', 'Bolívar', '020102'),
        ('Chillanes', 'Bolívar', '020103'),
        ('Echeandía', 'Bolívar', '020104'),
        
        # Cañar
        ('Azogues', 'Cañar', '030101'),
        ('La Troncal', 'Cañar', '030102'),
        ('Cañar', 'Cañar', '030103'),
        
        # Carchi
        ('Tulcán', 'Carchi', '040101'),
        ('San Gabriel', 'Carchi', '040102'),
        ('Espejo', 'Carchi', '040103'),
        
        # Chimborazo
        ('Riobamba', 'Chimborazo', '050101'),
        ('Latacunga', 'Chimborazo', '050102'),
        ('Penipe', 'Chimborazo', '050105'),
        
        # Cotopaxi
        ('Latacunga', 'Cotopaxi', '060101'),
        ('La Maná', 'Cotopaxi', '060102'),
        ('Salcedo', 'Cotopaxi', '060104'),
        
        # El Oro
        ('Machala', 'El Oro', '070101'),
        ('Santa Rosa', 'El Oro', '070102'),
        ('Huaquillas', 'El Oro', '070103'),
        ('Pasaje', 'El Oro', '070104'),
        
        # Esmeraldas
        ('Esmeraldas', 'Esmeraldas', '080101'),
        ('Atacames', 'Esmeraldas', '080102'),
        ('Quinindé', 'Esmeraldas', '080104'),
        
        # Guayas
        ('Guayaquil', 'Guayas', '090101'),
        ('Durán', 'Guayas', '090102'),
        ('Milagro', 'Guayas', '090105'),
        ('Daule', 'Guayas', '090104'),
        
        # Imbabura
        ('Ibarra', 'Imbabura', '100101'),
        ('Otavalo', 'Imbabura', '100102'),
        ('Antonio Ante', 'Imbabura', '100103'),
        ('Cotacachi', 'Imbabura', '100105'),
        
        # Loja
        ('Loja', 'Loja', '110101'),
        ('Catamayo', 'Loja', '110102'),
        ('Macará', 'Loja', '110103'),
        
        # Los Ríos
        ('Babahoyo', 'Los Ríos', '120101'),
        ('Quevedo', 'Los Ríos', '120102'),
        ('Vinces', 'Los Ríos', '120103'),
        
        # Manabí
        ('Manta', 'Manabí', '130101'),
        ('Portoviejo', 'Manabí', '130102'),
        ('Jipijapa', 'Manabí', '130104'),
        
        # Morona Santiago
        ('Macas', 'Morona Santiago', '140101'),
        ('Sucúa', 'Morona Santiago', '140102'),
        ('Palora', 'Morona Santiago', '140103'),
        
        # Napo
        ('Tena', 'Napo', '150101'),
        ('Archidona', 'Napo', '150102'),
        
        # Pastaza
        ('Puyo', 'Pastaza', '160101'),
        ('Mera', 'Pastaza', '160102'),
        
        # Pichincha
        ('Quito', 'Pichincha', '170101'),
        ('Cayambe', 'Pichincha', '170102'),
        ('Machachi', 'Pichincha', '170103'),
        ('Sangolquí', 'Pichincha', '170104'),
        
        # Santa Elena
        ('Santa Elena', 'Santa Elena', '240101'),
        ('La Libertad', 'Santa Elena', '240102'),
        ('Salinas', 'Santa Elena', '240103'),
        
        # Santo Domingo
        ('Santo Domingo', 'Santo Domingo de los Tsáchilas', '230101'),
        
        # Sucumbíos
        ('Nueva Loja', 'Sucumbíos', '210101'),
        ('Lago Agrio', 'Sucumbíos', '210102'),
        
        # Tungurahua
        ('Ambato', 'Tungurahua', '180101'),
        ('Baños', 'Tungurahua', '180102'),
        ('Pelileo', 'Tungurahua', '180104'),
        
        # Orellana
        ('Puerto Francisco de Orellana', 'Orellana', '220101'),
        ('Coca', 'Orellana', '220102'),
    ]
    
    created = 0
    for nombre, provincia, codigo in ciudades_data:
        ciudad, is_new = Ciudad.objects.get_or_create(
            nombre=nombre,
            defaults={
                'provincia': provincia,
                'codigo_postal': codigo,
                'activa': True
            }
        )
        if is_new:
            created += 1
    
    print(f"✓ {created} ciudades creadas")

# PASO 3: Verificación final
print("\n✅ PASO 3: Verificación final...")
total_ciudades = Ciudad.objects.count()
print(f"Total de ciudades en la BD: {total_ciudades}")

print("\n" + "="*70)
print("✨ ¡CONFIGURACIÓN COMPLETADA!")
print("="*70)
print("\nPróximos pasos:")
print("1. Reinicia el servidor: python manage.py runserver")
print("2. Ve a http://localhost:8000/register/")
print("3. Completa el formulario con teléfono y ciudad")
print("4. Las ciudades aparecerán en el dropdown")
print("\n")
