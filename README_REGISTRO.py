#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RESUMEN RÁPIDO: LO QUE CAMBIÓ EN TU PROYECTO

Este archivo documenta todos los cambios hechos para agregar:
- Campo de teléfono en registro
- Dropdown de ciudades del Ecuador
"""

print("""

╔════════════════════════════════════════════════════════════════╗
║   RESUMEN: REGISTRO CON TELÉFONO Y CIUDAD                     ║
╚════════════════════════════════════════════════════════════════╝

📋 CAMBIOS REALIZADOS:

1. MODELO DE DATOS
   ✓ Nuevo modelo: Ciudad (con todas las ciudades del Ecuador)
   ✓ Modificado: Usuario.ciudad (de CharField a ForeignKey)
   ✓ Utilizado: Usuario.telefono (ya existía, ahora activo)

2. BASE DE DATOS
   ✓ Nueva tabla: usuarios_ciudad
   ✓ Modificada tabla: usuarios_usuario
   → Ejecutar: python manage.py migrate

3. FORMULARIO (register.html)
   ✓ Agregado: Input de teléfono
   ✓ Agregado: Select (dropdown) de ciudades
   ✓ Validación: Teléfono (opcional, max 20 car.)
   ✓ Validación: Ciudad (opcional)

4. VISTA (registrar_usuario)
   ✓ Procesa teléfono
   ✓ Procesa ciudad
   ✓ Valida ambos campos
   ✓ Guarda en BD

5. ADMIN DJANGO
   ✓ Nuevo: Gestor de Ciudades
   ✓ Actualizado: UsuarioAdmin (muestra teléfono y ciudad)


🚀 PASOS PARA EJECUTAR:

OPCIÓN 1 (RECOMENDADA):
   $ python setup_registro_ciudades.py
   
   Esto hará TODO automáticamente:
   - Migraciones
   - Población de ciudades
   - Verificación

OPCIÓN 2 (MANUAL):
   $ python manage.py migrate
   $ python manage.py shell < setup_all_ciudades.py


✅ VERIFICACIÓN:

1. Reinicia el servidor:
   $ python manage.py runserver

2. Ve a: http://localhost:8000/register/

3. Deberías ver:
   ✓ Campo de Teléfono (nuevo)
   ✓ Dropdown de Ciudades (nuevo) con ~50 ciudades
   
4. Completa el formulario y registrate

5. Verifica en admin: http://localhost:8000/admin/usuarios/usuario/


📁 ARCHIVOS IMPORTANTES:

Modificados:
- apps/usuarios/models.py (+ modelo Ciudad, modificado Usuario)
- apps/usuarios/views.py (nueva lógica de registro)
- apps/usuarios/admin.py (registro de Ciudad)
- templates/register.html (nuevos campos en formulario)
- apps/usuarios/migrations/0002_ciudad_usuario_ciudad.py (nueva)

Nuevos:
- setup_registro_ciudades.py (script automático)
- setup_all_ciudades.py (poblador de ciudades)
- GUIA_REGISTRO_CIUDADES.md (documentación completa)
- INSTRUCCIONES_REGISTRO.txt (pasos a seguir)
- RESUMEN_CAMBIOS_CIUDADES.md (resumen detallado)


🌍 CIUDADES INCLUIDAS:

Se incluyen ~50 ciudades principales del Ecuador de todas las provincias:
- Azuay: Cuenca, Gualaceo, Paute, Sígsig
- Bolívar: Guaranda, Caluma
- Cañar: Azogues, La Troncal
- Carchi: Tulcán, San Gabriel
- ... y más de todas las provincias


💡 DATOS DEL FORMULARIO:

Campo      | Tipo     | Obligatorio | Validación
-----------|----------|-------------|-------------------
Nombre     | Text     | No          | -
Apellido   | Text     | No          | -
Email      | Email    | SÍ          | Único en BD
Teléfono   | Tel      | No          | Max 20 caracteres
Ciudad     | Select   | No          | Dropdown de ~50 ciudades
Contraseña | Password | SÍ          | Min 6 caracteres
Confirmar  | Password | SÍ          | Debe coincidir


🔍 VER DATOS EN EL ADMIN:

# Ver todas las ciudades
python manage.py shell
>>> from apps.usuarios.models import Ciudad
>>> print(Ciudad.objects.count())

# Ver usuario recién creado
>>> from apps.usuarios.models import Usuario
>>> user = Usuario.objects.latest('id')
>>> print(f"Teléfono: {user.telefono}")
>>> print(f"Ciudad: {user.ciudad}")


⚠️  EN CASO DE ERROR:

- Error "No such table": python manage.py migrate
- Error "No such column": python manage.py migrate
- Ciudades vacías: python setup_all_ciudades.py
- Necesitas resetear todo: 
  1. rm apps/usuarios/migrations/0002_*.py
  2. python manage.py migrate usuarios 0001
  3. python manage.py migrate
  4. python setup_all_ciudades.py


✨ ¡LISTO PARA USAR!

El formulario de registro ahora está completo con:
✓ Teléfono
✓ Dropdown de ciudades del Ecuador
✓ Validación completa
✓ Almacenamiento correcto en BD
✓ Visible en el admin


📖 Documentación completa en:
- GUIA_REGISTRO_CIUDADES.md
- INSTRUCCIONES_REGISTRO.txt
- RESUMEN_CAMBIOS_CIUDADES.md

""")
