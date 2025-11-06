# 📚 Guía: Colecciones, Categorías y Subcategorías

## 🎯 Estructura del Sistema

```
COLECCIÓN (ej: "Primavera 2024")
│
├── CATEGORÍA (ej: "Ropa")
│   ├── Subcategoría: Pantalones
│   ├── Subcategoría: Camisas
│   └── Subcategoría: Vestidos
│
└── CATEGORÍA (ej: "Accesorios")
    ├── Subcategoría: Carteras
    ├── Subcategoría: Cinturones
    └── Subcategoría: Joyas
```

---

## 🚀 Cómo Crear desde el Admin de Django

### 1️⃣ Crear una Colección

1. Ve a **Admin de Django** → **Productos** → **Colecciones**
2. Click en **"Agregar Colección"**
3. Completa los campos:
   - **Nombre**: `Primavera 2024`
   - **Slug**: Se genera automáticamente
   - **Descripción**: Breve descripción
   - **Imagen**: Sube una imagen (opcional)
   - **Activo**: ✓
   - **Destacada**: ✓ (para mostrar en homepage)
   - **Posición**: Orden de visualización (1, 2, 3...)

4. **VENTAJA**: Puedes agregar categorías directamente desde aquí usando el inline al final del formulario

---

### 2️⃣ Crear una Categoría Principal

1. Ve a **Admin de Django** → **Productos** → **Categorías**
2. Click en **"Agregar Categoría"**
3. Completa los campos:
   - **Nombre**: `Ropa`
   - **Slug**: Se genera automáticamente
   - **Descripción**: Descripción de la categoría
   - **Colección**: Selecciona `Primavera 2024` ← 🔗 **AQUÍ VA LA CONEXIÓN**
   - **Padre**: Déjalo vacío (es categoría principal)
   - **Tipo**: `ropa` (opcional, para clasificación)
   - **Estado**: ✓
   - **Posición**: 1

4. **VENTAJA**: Puedes agregar subcategorías directamente usando el inline

---

### 3️⃣ Crear Subcategorías

**Opción A: Desde la categoría padre**
1. Edita la categoría "Ropa"
2. Baja hasta el inline "Subcategorías"
3. Agrega:
   - Pantalones
   - Camisas
   - Vestidos

**Opción B: Crear nueva categoría**
1. Ve a **Categorías** → **Agregar Categoría**
2. Completa:
   - **Nombre**: `Pantalones`
   - **Colección**: `Primavera 2024`
   - **Padre**: Selecciona `Ropa` ← **Esto la hace subcategoría**
   - **Tipo**: `ropa`

---

## 📊 Lista Mejorada del Admin

### Colecciones - Vista de Lista
- ✅ Nombre y Slug
- ✅ Estado (Activo/Inactivo) - editable directamente
- ✅ Destacada - editable directamente
- ✅ Posición - editable directamente
- ✅ **Número de categorías** asociadas
- ✅ Fecha de creación

### Categorías - Vista de Lista
- ✅ Nombre y Slug
- ✅ Colección asociada
- ✅ Padre (para subcategorías)
- ✅ Tipo
- ✅ **Número de subcategorías**
- ✅ **Número de productos**
- ✅ Estado - editable directamente
- ✅ Posición - editable directamente

---

## 🎨 Ejemplo Completo

### Paso a Paso:

1. **Crear Colección**: "Primavera 2024"

2. **Crear Categorías Principales**:
   ```
   ✓ Ropa (colección: Primavera 2024)
   ✓ Accesorios (colección: Primavera 2024)
   ✓ Calzado (colección: Primavera 2024)
   ```

3. **Crear Subcategorías para "Ropa"**:
   ```
   ✓ Pantalones (padre: Ropa, colección: Primavera 2024)
   ✓ Camisas (padre: Ropa, colección: Primavera 2024)
   ✓ Vestidos (padre: Ropa, colección: Primavera 2024)
   ✓ Faldas (padre: Ropa, colección: Primavera 2024)
   ```

4. **Crear Subcategorías para "Accesorios"**:
   ```
   ✓ Carteras (padre: Accesorios, colección: Primavera 2024)
   ✓ Cinturones (padre: Accesorios, colección: Primavera 2024)
   ✓ Joyas (padre: Accesorios, colección: Primavera 2024)
   ```

---

## 🌐 Para el Navbar Desplegable

Cuando crees productos, asígnalos a:
- **Categoría**: Selecciona la principal (ej: Ropa)
- **Subcategoría**: Aquí seleccionarás Pantalones, Camisas, etc.

Luego en el frontend, el navbar mostrará:
```
Ropa ▼
  ├─ Pantalones
  ├─ Camisas
  ├─ Vestidos
  └─ Faldas

Accesorios ▼
  ├─ Carteras
  ├─ Cinturones
  └─ Joyas
```

---

## ✨ Características del Admin Mejorado

1. **Inlines**: Agrega subcategorías/categorías sin salir del formulario principal
2. **Autocomplete**: Búsqueda rápida para colecciones y padres
3. **Edición rápida**: Cambia estado, posición, destacada directamente desde la lista
4. **Contadores**: Ve cuántas subcategorías/productos tiene cada categoría
5. **Fieldsets organizados**: Campos agrupados lógicamente
6. **Filtros**: Filtra por colección, estado, tipo, fecha
7. **Búsqueda**: Busca por nombre, slug, descripción

---

## 🔗 Relaciones en la Base de Datos

```sql
productos_coleccion
├── id
├── nombre
├── slug
└── ...

productos_categoria
├── id
├── nombre
├── slug
├── coleccion_id → FK a productos_coleccion ✅
├── padre_id → FK a productos_categoria (self) ✅
└── ...

productos_producto
├── id
├── categoria_id → FK a productos_categoria
└── ...
```

---

## 🎯 Acceso Rápido

- Admin Django: `http://127.0.0.1:8000/admin/`
- Colecciones: `/admin/productos/coleccion/`
- Categorías: `/admin/productos/categoria/`
- Productos: `/admin/productos/producto/`
