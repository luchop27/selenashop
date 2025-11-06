# 🎯 GUÍA RÁPIDA: Cómo Agregar Categorías y Subcategorías

## ✅ PASO 1: Crear Colección (Si no existe)

1. Ve a **Admin Django** → **Productos** → **Colecciones**
2. Click "Agregar Colección"
3. Llena solo:
   - **Nombre**: `Primavera 2024`
   - **Slug**: (se genera solo)
   - **Activo**: ✓
   - **Destacada**: ✓ (opcional)
4. Guardar

---

## ✅ PASO 2: Crear Categoría PRINCIPAL (Ejemplo: Ropa)

1. Ve a **Productos** → **Categorías** → **Agregar Categoría**
2. Llena:
   - **Nombre**: `Ropa`
   - **Slug**: (se genera solo)
   - **Colección**: Selecciona `Primavera 2024` ✅
   - **Padre**: ❌ DEJAR VACÍO (es categoría principal)
   - **Tipo**: `ropa` (opcional, puedes escribir lo que quieras o dejarlo vacío)
   - **Estado**: ✓
   - **Posición**: 1
3. Guardar

---

## ✅ PASO 3: Crear SUBCATEGORÍAS (Ejemplo: Pantalones, Camisas)

### Opción A: Desde el inline (MÁS FÁCIL) ⭐

1. Edita la categoría "Ropa" que creaste
2. Baja hasta el final donde dice **"SUBCATEGORÍAS"**
3. Click en "Agregar otra Subcategoría"
4. Llena solo:
   - **Nombre**: `Pantalones`
   - **Slug**: (se genera solo)
   - **Estado**: ✓
   - **Posición**: 1

5. **NO LLENES:**
   - ❌ Colección (se hereda automáticamente de "Ropa")
   - ❌ Tipo (se hereda automáticamente de "Ropa")

6. Guardar

### Opción B: Crear nueva categoría

1. Ve a **Categorías** → **Agregar Categoría**
2. Llena:
   - **Nombre**: `Pantalones`
   - **Slug**: (se genera solo)
   - **Padre**: Selecciona `Ropa` ✅
   - **Colección**: Se llenará automáticamente al guardar
   - **Tipo**: Opcional (se hereda del padre si no lo llenas)
3. Guardar

---

## 📋 Resumen Simple:

| Tipo | Colección | Padre | Tipo |
|------|-----------|-------|------|
| **Categoría Principal** | ✅ Seleccionar | ❌ Vacío | Opcional |
| **Subcategoría** | Auto | ✅ Seleccionar | Auto |

---

## ⚠️ Campos Explicados:

- **COLECCIÓN**: Solo se llena para categorías principales
- **PADRE**: Solo se llena para subcategorías
- **TIPO**: Totalmente opcional (puedes escribir: ropa, accesorio, calzado, o dejarlo vacío)

---

## 🎯 Ejemplo Completo:

```
1. Crear Colección: "Primavera 2024"

2. Crear Categoría Principal:
   - Nombre: Ropa
   - Colección: Primavera 2024 ✓
   - Padre: (vacío)
   - Tipo: ropa (o vacío)

3. Crear Subcategorías (desde el inline de Ropa):
   - Pantalones (solo nombre y slug)
   - Camisas (solo nombre y slug)
   - Vestidos (solo nombre y slug)

Todo lo demás (colección, tipo) se hereda automáticamente!
```

---

## 🔥 LO MÁS IMPORTANTE:

✅ **Categoría Principal**: Llena COLECCIÓN, deja PADRE vacío
✅ **Subcategoría**: Llena PADRE, deja COLECCIÓN vacío (se llena solo)
✅ **Tipo**: Siempre opcional, puedes dejarlo vacío

La colección y el tipo se heredan automáticamente del padre! 🎉
