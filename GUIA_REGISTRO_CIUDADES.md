# 📝 GUÍA COMPLETA: REGISTRO CON TELÉFONO Y CIUDAD

## ✅ CAMBIOS REALIZADOS

### 1. **Modelo `Usuario` actualizado**
   - Se agregó campo `telefono` (ya existía, pero lo usamos)
   - Se cambió campo `ciudad` de CharField a **ForeignKey** hacia el modelo `Ciudad`

### 2. **Nuevo modelo `Ciudad`**
   - Almacena todas las ciudades del Ecuador
   - Incluye: nombre, provincia, código postal, estado activo

### 3. **Plantilla `register.html` actualizada**
   - Agregar campo de input para **teléfono**
   - Agregar campo select (combobox) para **ciudad**
   - Se muestran todas las ciudades ordenadas por nombre

### 4. **Vista `registrar_usuario` actualizada**
   - Valida teléfono (opcional)
   - Valida ciudad (opcional)
   - Guarda todos los datos en la base de datos

### 5. **Admin de Django actualizado**
   - Se registró el modelo `Ciudad`
   - Se actualicó `UsuarioAdmin` para mostrar teléfono y ciudad

---

## 🚀 PASOS PARA APLICAR CAMBIOS

### PASO 1: Ejecutar migraciones
```bash
python manage.py migrate
```
Esto creará:
- Tabla `usuarios_ciudad`
- Actualizará tabla `usuarios_usuario` con nueva relación

### PASO 2: Poblar las ciudades del Ecuador
```bash
python manage.py shell < setup_all_ciudades.py
```
Esto insertará ~60 ciudades del Ecuador en la BD.

### PASO 3: Reiniciar servidor Django
```bash
# Detén el servidor (Ctrl+C)
python manage.py runserver
```

### PASO 4: Probar el formulario
1. Ve a `http://localhost:8000/register/`
2. Completa el formulario con:
   - Nombre
   - Apellido
   - Email
   - **Teléfono** (nuevo)
   - **Ciudad** (nuevo - dropdown)
   - Contraseña
   - Confirmar contraseña
3. Haz clic en "Register"
4. Verifica que los datos se guardaron en el admin

---

## 📋 ESTRUCTURA DE ARCHIVOS MODIFICADOS

```
apps/usuarios/
├── models.py                          ✅ Actualizado
├── views.py                           ✅ Actualizado
├── admin.py                           ✅ Actualizado
├── migrations/
│   └── 0002_ciudad_usuario_ciudad.py ✅ Nuevo
└── scripts/
    └── populate_ciudades.py           ✅ Disponible

templates/
└── register.html                      ✅ Actualizado
```

---

## 🔍 VERIFICACIÓN EN EL ADMIN

1. Accede a `http://localhost:8000/admin/`
2. En "Usuarios":
   - Haz clic en "Ciudades" → Verás ~60 ciudades del Ecuador
   - Haz clic en un Usuario → Verás campos de teléfono y ciudad

---

## 📊 ESTRUCTURA DE LA BD

### Tabla: `usuarios_ciudad`
```sql
id       INTEGER PRIMARY KEY
nombre   VARCHAR(100) UNIQUE
provincia VARCHAR(100)
codigo_postal VARCHAR(10)
activa   BOOLEAN
```

### Tabla: `usuarios_usuario` (modificada)
```sql
ciudad_id  INTEGER FOREIGN KEY (usuarios_ciudad.id)
telefono   VARCHAR(20)
```

---

## ✨ CARACTERÍSTICAS

- ✅ Teléfono es opcional
- ✅ Ciudad es opcional
- ✅ Se guardan correctamente en la BD
- ✅ Se validan antes de guardar
- ✅ Están disponibles en el admin
- ✅ Se muestran en el perfil del usuario

---

## 🛠️ COMANDOS ÚTILES

### Ver todas las ciudades cargadas
```bash
python manage.py shell
```
```python
from apps.usuarios.models import Ciudad
print(Ciudad.objects.count())  # Debe mostrar ~60
```

### Ver usuarios con teléfono y ciudad
```bash
python manage.py shell
```
```python
from apps.usuarios.models import Usuario
for user in Usuario.objects.all():
    print(f"{user.email}: {user.telefono} - {user.ciudad}")
```

### Resetear todo (si algo falla)
```bash
# 1. Elimina la migración más reciente:
rm apps/usuarios/migrations/0002_*.py

# 2. Revierte la BD a estado anterior:
python manage.py migrate usuarios 0001

# 3. Realiza cambios nuevamente:
python manage.py migrate
python manage.py shell < setup_all_ciudades.py
```

---

## ⚠️ TROUBLESHOOTING

### Error: "No such table: usuarios_ciudad"
→ Ejecuta: `python manage.py migrate`

### Error: "No such column: usuarios_usuario.ciudad_id"
→ Ejecuta: `python manage.py migrate`

### Ciudades no aparecen en el dropdown
→ Ejecuta: `python manage.py shell < setup_all_ciudades.py`

### Ciudades desaparecen después de reiniciar
→ Eso significa que no fueron guardadas. Ejecuta nuevamente el script.

---

## 📞 DATOS DEL FORMULARIO

| Campo | Tipo | Obligatorio | Validación |
|-------|------|-------------|-----------|
| Nombre | Text | No | - |
| Apellido | Text | No | - |
| Email | Email | **Sí** | Único |
| Teléfono | Tel | No | Max 20 caracteres |
| Ciudad | Select | No | Selección de dropdown |
| Contraseña | Password | **Sí** | Min 6 caracteres |
| Confirmar | Password | **Sí** | Debe coincidir |

---

## 🎉 ¡LISTO!
El formulario de registro ahora tiene:
- ✅ Campo de teléfono
- ✅ Dropdown de ciudades del Ecuador
- ✅ Se guardan correctamente
- ✅ Se muestran en el admin
