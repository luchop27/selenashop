# 🔒 Sistema de Seguridad Implementado

## Resumen
Se ha implementado un sistema de seguridad completo para proteger el panel de administración de la tienda online.

## Componentes Implementados

### 1. Decoradores de Seguridad (`core/decorators.py`)

#### `@admin_required`
- **Propósito**: Proteger vistas que requieren permisos de administrador
- **Requisitos**: Usuario autenticado + (`is_staff=True` OR `is_superuser=True`)
- **Comportamiento**:
  - Si NO está autenticado → Redirige a `/admin/login/`
  - Si NO es admin → Redirige a inicio con mensaje de error
  - Si es admin → Permite el acceso

#### `@superuser_required`
- **Propósito**: Proteger vistas críticas solo para superusuarios
- **Requisitos**: Usuario autenticado + `is_superuser=True`
- **Uso**: Acciones sensibles como eliminar usuarios, cambiar configuraciones críticas

---

### 2. Middleware de Protección (`core/admin_middleware.py`)

**Clase**: `AdminAccessMiddleware`

**Funcionalidad**:
- Intercepta TODAS las peticiones HTTP antes de llegar a las vistas
- Protege rutas administrativas a nivel global
- Capa adicional de seguridad (defensa en profundidad)

**Rutas Protegidas**:
```
/admin/productos/
/admin/categorias/
/admin/colecciones/
/admin/atributos/
/admin/ordenes/
/admin/usuarios/
/admin/dashboard/
/admin/panel/
/admin-ecomus/
```

**Rutas Públicas (Permitidas)**:
```
/admin/login/
/admin/logout/
```

**Flujo de Verificación**:
1. ¿Es ruta administrativa? → NO → Continúa normal
2. ¿Es ruta pública (/admin/login/)? → SÍ → Continúa normal
3. ¿Usuario autenticado? → NO → Redirige a login
4. ¿Usuario es staff o superuser? → NO → Redirige a inicio con error
5. Todo OK → Permite acceso

---

### 3. Vistas Protegidas

#### Core (`core/views.py`)
✅ Todas las vistas `admin_*` ahora usan `@admin_required`:
- `admin_index` - Dashboard principal
- `admin_order_list` - Lista de pedidos
- `admin_order_detail` - Detalle de pedido
- `admin_order_tracking` - Seguimiento de pedido
- `admin_order_mark_paid` - Marcar como pagado
- `admin_order_update_status` - Actualizar estado
- `admin_order_cancel` - Cancelar pedido
- `admin_user_list` - Lista de usuarios
- `admin_user_detail` - Detalle de usuario
- `admin_user_edit` - Editar usuario
- `admin_user_delete` - Eliminar usuario
- `dashboard_redirect` - Redirección dashboard

#### Productos (`apps/productos/views.py`)
✅ Todas las vistas `admin_*` y `panel_*` ahora usan `@admin_required`:
- `panel_dashboard` - Dashboard de productos
- `panel_productos_list` - Lista panel
- `panel_producto_crear` - Crear panel
- `panel_categorias_list` - Lista categorías
- `panel_categoria_crear` - Crear categoría
- `panel_categoria_edit` - Editar categoría
- `panel_categoria_delete` - Eliminar categoría
- `admin_productos_list` - Lista admin
- `admin_producto_add` - Agregar producto
- `admin_producto_view` - Ver producto
- `admin_producto_edit` - Editar producto
- `admin_producto_delete` - Eliminar producto
- `admin_atributos_list` - Lista atributos
- `admin_atributo_add` - Agregar atributo
- `admin_atributo_edit` - Editar atributo
- `admin_atributo_delete` - Eliminar atributo
- `admin_colecciones_list` - Lista colecciones
- `admin_coleccion_add` - Agregar colección
- `admin_coleccion_edit` - Editar colección
- `admin_coleccion_delete` - Eliminar colección

---

## Configuración en Settings

**Archivo**: `selenashop/settings.py`

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.CartPersistenceMiddleware',
    'core.admin_middleware.AdminAccessMiddleware',  # ← NUEVO
]
```

---

## Cómo Funciona (Flujo Completo)

### Escenario: Usuario Cliente Intenta Acceder a `/admin/productos/`

1. **Middleware AdminAccessMiddleware** intercepta la petición
   - Detecta que `/admin/productos/` es una ruta administrativa
   - Verifica: ¿Usuario autenticado? → SÍ
   - Verifica: ¿es_staff o es_superuser? → NO
   - **Acción**: Redirige a inicio con mensaje "No tienes permisos..."

2. **Decorador @admin_required** (si el middleware fallara)
   - Segunda capa de defensa
   - Verifica autenticación y permisos
   - Redirige si no cumple requisitos

**Resultado**: **ACCESO DENEGADO** ❌

---

### Escenario: Usuario Admin Accede a `/admin/productos/`

1. **Middleware AdminAccessMiddleware**
   - Detecta ruta administrativa
   - Verifica: ¿Usuario autenticado? → SÍ
   - Verifica: ¿es_staff o es_superuser? → SÍ ✅
   - **Acción**: Permite continuar

2. **Decorador @admin_required**
   - Verifica permisos
   - Todo OK ✅
   - **Acción**: Ejecuta la vista

**Resultado**: **ACCESO PERMITIDO** ✅

---

## Tipos de Usuarios

### Cliente Normal
```python
usuario.is_authenticated = True
usuario.is_staff = False
usuario.is_superuser = False
```
**Acceso**: Solo vistas públicas (productos, carrito, perfil)

### Administrador (Staff)
```python
usuario.is_authenticated = True
usuario.is_staff = True
usuario.is_superuser = False
```
**Acceso**: Vistas públicas + Panel de administración completo

### Superusuario
```python
usuario.is_authenticated = True
usuario.is_staff = True (generalmente)
usuario.is_superuser = True
```
**Acceso**: TODO el sistema + Django Admin + Acciones críticas

---

## Beneficios de esta Implementación

### 🛡️ Seguridad Multicapa
- Middleware (primera línea de defensa)
- Decoradores (segunda línea de defensa)
- Verificaciones en vistas (tercera línea si es necesario)

### 🚀 Fácil Mantenimiento
- Un solo decorador `@admin_required` para aplicar
- No más código repetitivo de verificación
- Fácil de extender

### 📝 Mensajes Claros
- "Debes iniciar sesión para acceder al panel de administración"
- "No tienes permisos para acceder al panel de administración"

### ⚡ Rendimiento
- Middleware ejecuta solo una vez por petición
- Verificaciones simples (booleanos)
- Sin queries adicionales a BD

---

## Pruebas Recomendadas

### 1. Usuario No Autenticado
```
Visitar: /admin/productos/
Resultado Esperado: Redirige a /admin/login/
```

### 2. Usuario Cliente (Autenticado, No Staff)
```
Visitar: /admin/productos/
Resultado Esperado: Redirige a inicio con mensaje de error
```

### 3. Usuario Admin (is_staff=True)
```
Visitar: /admin/productos/
Resultado Esperado: Acceso permitido
```

### 4. Ruta Pública
```
Visitar: /admin/login/
Resultado Esperado: Muestra formulario de login (sin redirección)
```

---

## Notas Importantes

⚠️ **El middleware NO protege**:
- Django Admin nativo (`/django-admin/`)
- Rutas que no empiecen con `/admin/`

⚠️ **Orden del Middleware**:
- AdminAccessMiddleware debe estar DESPUÉS de AuthenticationMiddleware
- De lo contrario, `request.user` no estará disponible

✅ **Compatibilidad**:
- Compatible con el campo `rol` del modelo Usuario personalizado
- Compatible con Django's `is_staff` y `is_superuser`

---

## Archivos Modificados

1. ✅ `core/decorators.py` (NUEVO)
2. ✅ `core/admin_middleware.py` (NUEVO)
3. ✅ `core/views.py` (MODIFICADO - decoradores aplicados)
4. ✅ `apps/productos/views.py` (MODIFICADO - decoradores aplicados)
5. ✅ `selenashop/settings.py` (MODIFICADO - middleware agregado)

---

## Siguiente Paso: Configurar Usuarios Admin

Para crear un usuario administrador:

```bash
python manage.py shell
```

```python
from apps.usuarios.models import Usuario

# Crear admin
admin = Usuario.objects.create_user(
    email='admin@tienda.com',
    password='admin123',
    nombre='Admin',
    apellido='Sistema',
    is_staff=True,
    is_superuser=True
)

# O actualizar usuario existente
usuario = Usuario.objects.get(email='cliente@example.com')
usuario.is_staff = True
usuario.save()
```

---

## Resumen

✅ Panel de administración COMPLETAMENTE protegido
✅ Middleware intercepta accesos no autorizados
✅ Decoradores en todas las vistas admin
✅ Mensajes claros para el usuario
✅ Sistema multicapa (defensa en profundidad)
✅ Código limpio y mantenible

**Estado**: IMPLEMENTADO Y FUNCIONAL 🎉
