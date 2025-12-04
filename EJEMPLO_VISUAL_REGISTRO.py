"""
EJEMPLO VISUAL: CÓMO FUNCIONA EL REGISTRO CON PROVINCIAS Y CIUDADES
"""

print("""

╔════════════════════════════════════════════════════════════════════╗
║              EJEMPLO: REGISTRO CON PROVINCIAS Y CIUDADES           ║
╚════════════════════════════════════════════════════════════════════╝


PASO 1: Usuario accede a /register/
════════════════════════════════════════════════════════════════════

Formulario inicial:
┌─────────────────────────────────────────┐
│  REGISTRO                               │
├─────────────────────────────────────────┤
│ Nombre: [________________]              │
│ Apellido: [________________]            │
│ Email: [________________] *             │
│ Teléfono: [________________]            │
│                                         │
│ Provincia:                              │
│ ┌─────────────────────────────────────┐ │
│ │ -- Select Province --               │ │  ← Combobox 1
│ │ Azuay                               │ │
│ │ Bolívar                             │ │
│ │ Cañar                               │ │
│ │ Carchi                              │ │
│ │ ... más ...                         │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Ciudad:                                 │
│ ┌─────────────────────────────────────┐ │
│ │ -- Select City --                   │ │  ← Combobox 2 (vacío)
│ └─────────────────────────────────────┘ │
│                                         │
│ Contraseña: [________________] *        │
│ Confirmar: [________________] *         │
│                                         │
│ [REGISTER]                              │
│ [Log in aquí]                           │
└─────────────────────────────────────────┘


PASO 2: Usuario selecciona una Provincia (ej: "Guayas")
════════════════════════════════════════════════════════════════════

El usuario hace clic en el combobox de Provincia y selecciona "Guayas"

JavaScript detecta el cambio:
  ✓ Obtiene el valor seleccionado: provincia_id = 9
  ✓ Dispara petición AJAX a: /api/ciudades-por-provincia/9/


PASO 3: AJAX Request (transparente para el usuario)
════════════════════════════════════════════════════════════════════

Petición HTTP:
  GET /api/ciudades-por-provincia/9/
  
Respuesta JSON:
  {
    "success": true,
    "ciudades": [
      {"id": 1, "nombre": "Guayaquil"},
      {"id": 2, "nombre": "Durán"},
      {"id": 3, "nombre": "Milagro"},
      {"id": 4, "nombre": "Daule"},
      {"id": 5, "nombre": "Samborondón"},
      {"id": 6, "nombre": "Balzar"}
    ]
  }


PASO 4: El combobox de Ciudad se llena automáticamente
════════════════════════════════════════════════════════════════════

Formulario actualizado (sin recargar la página):

┌─────────────────────────────────────────┐
│  REGISTRO                               │
├─────────────────────────────────────────┤
│ Nombre: [Luis________________]          │
│ Apellido: [Vasquez__________]           │
│ Email: [luis@example.com___] *          │
│ Teléfono: [0987654321________]          │
│                                         │
│ Provincia:                              │
│ ┌─────────────────────────────────────┐ │
│ │ Guayas                    ↓         │ │  ✓ "Guayas" seleccionado
│ └─────────────────────────────────────┘ │
│                                         │
│ Ciudad:                                 │
│ ┌─────────────────────────────────────┐ │
│ │ -- Select City --                   │ │
│ │ Guayaquil                           │ │  ✓ Se llenó automáticamente
│ │ Durán                               │ │
│ │ Milagro                             │ │
│ │ Daule                               │ │
│ │ Samborondón                         │ │
│ │ Balzar                              │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Contraseña: [***********] *            │
│ Confirmar: [***********] *             │
│                                         │
│ [REGISTER]                              │
│ [Log in aquí]                           │
└─────────────────────────────────────────┘


PASO 5: Usuario selecciona una Ciudad (ej: "Guayaquil")
════════════════════════════════════════════════════════════════════

Usuario hace clic en el combobox de Ciudad y selecciona "Guayaquil"

┌─────────────────────────────────────────┐
│  REGISTRO                               │
├─────────────────────────────────────────┤
│ Nombre: [Luis________________]          │
│ Apellido: [Vasquez__________]           │
│ Email: [luis@example.com___] *          │
│ Teléfono: [0987654321________]          │
│ Provincia: [Guayas________]             │
│ Ciudad: [Guayaquil_________]            │ ✓ Seleccionado
│ Contraseña: [***********] *            │
│ Confirmar: [***********] *             │
│ [REGISTER]                              │
└─────────────────────────────────────────┘


PASO 6: Usuario hace clic en REGISTER
════════════════════════════════════════════════════════════════════

El formulario se envía con todos los datos:
  - nombre: "Luis"
  - apellido: "Vasquez"
  - email: "luis@example.com"
  - telefono: "0987654321"
  - provincia: 9 (Guayas)
  - ciudad: 1 (Guayaquil)
  - password: "***password***"
  - password_confirm: "***password***"


PASO 7: Datos se guardan en la BD
════════════════════════════════════════════════════════════════════

Base de Datos:

usuarios_usuario:
┌────┬──────────┬───────┬──────────┬────────────────┬───────────┐
│ id │ email    │ nombre│ apellido │ provincia_id   │ ciudad_id │
├────┼──────────┼───────┼──────────┼────────────────┼───────────┤
│ 1  │ luis@... │ Luis  │ Vasquez  │ 9 (Guayas)    │ 1 (Gye)   │
└────┴──────────┴───────┴──────────┴────────────────┴───────────┘

usuarios_provincia:
┌────┬──────────────────┐
│ id │ nombre           │
├────┼──────────────────┤
│ 9  │ Guayas           │
└────┴──────────────────┘

usuarios_ciudad:
┌────┬────────────┬───────────────┐
│ id │ nombre     │ provincia_id  │
├────┼────────────┼───────────────┤
│ 1  │ Guayaquil  │ 9 (Guayas)   │
└────┴────────────┴───────────────┘


PASO 8: Usuario puede ver sus datos en el Admin
════════════════════════════════════════════════════════════════════

Admin de Django:
http://localhost:8000/admin/usuarios/usuario/1/

┌─────────────────────────────────────────────────┐
│ USUARIO: luis@example.com                       │
├─────────────────────────────────────────────────┤
│ Email: luis@example.com                         │
│ Nombre: Luis                                    │
│ Apellido: Vasquez                               │
│ Teléfono: 0987654321                           │
│ Provincia: Guayas                              │
│ Ciudad: Guayaquil                              │
│ Rol: Cliente                                    │
│ Activo: Sí                                      │
│ Fecha de Registro: 2025-12-02 14:30:45         │
└─────────────────────────────────────────────────┘


════════════════════════════════════════════════════════════════════
FLUJO TÉCNICO COMPLETO:
════════════════════════════════════════════════════════════════════

GET /register/
    ↓
Render template con provincias (ciudades = [])
    ↓
Usuario abre página ← Ve Provincia combobox lleno, Ciudad combobox vacío
    ↓
Usuario selecciona provincia
    ↓
JavaScript onchange → fetch('/api/ciudades-por-provincia/9/')
    ↓
Views: api_ciudades_por_provincia(request, 9)
    ↓
QuerySet: Ciudad.objects.filter(provincia_id=9)
    ↓
JsonResponse: {"success": true, "ciudades": [...]}
    ↓
JavaScript llena el combobox de ciudades
    ↓
Usuario selecciona ciudad y completa formulario
    ↓
POST /register/ con todos los datos
    ↓
Views: registrar_usuario(request)
    ↓
Validaciones → create_user() → login() → redirect to my_account
    ↓
Usuario registrado ✓


════════════════════════════════════════════════════════════════════
VENTAJAS DE ESTE SISTEMA:
════════════════════════════════════════════════════════════════════

✓ Sin recargar página
✓ Experiencia de usuario fluida
✓ Solo se muestran ciudades de la provincia seleccionada
✓ Se valida correctamente en el servidor
✓ Se guarda estructuradamente en la BD
✓ Escalable (si se agregan más provincias/ciudades)
✓ Datos organizados y normalizados
✓ Fácil de mantener y actualizar


════════════════════════════════════════════════════════════════════
¡Así funciona el sistema completo! 🚀
════════════════════════════════════════════════════════════════════

""")
