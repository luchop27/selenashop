# 📋 EXPLICACIÓN COMPLETA: ESTRUCTURA DE BASE DE DATOS PARA SELENASHOP

## 🎯 TU TIENDA: ROPA FEMENINA + ACCESORIOS

### Productos que venderás:
1. **ROPA** (por estilos/ocasiones):
   - 👗 Ropa de Playa
   - 👠 Ropa de Gala
   - 👕 Casual/Diario
   - 🏃‍♀️ Deportiva
   - 💼 Formal/Oficina
   - 🌙 Ropa de noche
   - etc.

2. **ACCESORIOS** (con/sin marca):
   - 👜 Carteras (algunas de marca)
   - 💍 Joyas/Bisutería
   - 🌸 Perfumes (de marca)
   - ⌚ Relojes (algunos de marca)
   - 🕶️ Gafas
   - 🧣 Bufandas, gorros
   - etc.

---

## 📚 ¿QUÉ ES UN SLUG?

### Definición Simple:
Un **slug** es una versión "amigable" del nombre para URLs.

### Ejemplos:
```
Nombre del producto: "Vestido de Gala Rojo"
Slug generado:       "vestido-de-gala-rojo"

Categoría: "Ropa de Playa"
Slug:      "ropa-de-playa"

Marca: "Victoria's Secret"
Slug:  "victorias-secret"
```

### ¿Para qué sirve?
```
❌ URL FEA:  https://selenashop.com/producto?id=123
✅ URL BONITA: https://selenashop.com/producto/vestido-de-gala-rojo

❌ URL FEA:  https://selenashop.com/categoria?id=5
✅ URL BONITA: https://selenashop.com/categoria/ropa-de-playa
```

### Beneficios:
- ✅ Mejor SEO (Google lo prefiere)
- ✅ URLs fáciles de recordar
- ✅ URLs que se pueden compartir
- ✅ Se ve profesional

---

## 🗂️ ESTRUCTURA DE BASE DE DATOS PROPUESTA

### Basándome en los HTMLs, necesitas:

## 📊 TABLAS Y RELACIONES

### **5 TABLAS PRINCIPALES:**

```
1. categorias
2. marcas
3. productos
4. imagenes_productos
5. variantes_productos
```

---

## 🔍 TABLA 1: `categorias`

### ¿Para qué sirve?
Organizar productos por **tipo** y **ocasión**

### Campos:
```sql
id                BIGSERIAL (automático)
nombre            TEXT                      - "Ropa de Playa"
slug              TEXT (único)              - "ropa-de-playa"
descripcion       TEXT                      - Descripción de la categoría
imagen            TEXT                      - Ruta de la imagen
padre_id          BIGINT (nullable)         - Para subcategorías
activo            BOOLEAN                   - ¿Se muestra?
orden             INTEGER                   - Orden de visualización
created_at        TIMESTAMPTZ
updated_at        TIMESTAMPTZ
```

### Ejemplos de categorías:
```
CATEGORÍAS PRINCIPALES:
├─ Ropa
│  ├─ Ropa de Playa
│  ├─ Ropa de Gala
│  ├─ Casual
│  ├─ Deportiva
│  └─ Formal
│
└─ Accesorios
   ├─ Carteras
   ├─ Perfumes
   ├─ Relojes
   ├─ Joyas
   └─ Gafas
```

### ¿Cómo funciona `padre_id`?
```
Categoría: "Ropa" (padre_id = NULL)
  └─ Subcategoría: "Ropa de Playa" (padre_id = 1)
  └─ Subcategoría: "Ropa de Gala" (padre_id = 1)

Categoría: "Accesorios" (padre_id = NULL)
  └─ Subcategoría: "Carteras" (padre_id = 2)
  └─ Subcategoría: "Perfumes" (padre_id = 2)
```

---

## 🏷️ TABLA 2: `marcas`

### ¿Para qué sirve?
Registrar marcas de productos (especialmente accesorios)

### Campos:
```sql
id                BIGSERIAL
nombre            TEXT                      - "Victoria's Secret"
slug              TEXT (único)              - "victorias-secret"
logo              TEXT                      - Ruta del logo
descripcion       TEXT
activo            BOOLEAN
created_at        TIMESTAMPTZ
updated_at        TIMESTAMPTZ
```

### Ejemplos:
```
- Victoria's Secret (perfumes, ropa interior)
- Carolina Herrera (perfumes)
- Michael Kors (carteras, relojes)
- Coach (carteras)
- Fossil (relojes)
- Zara (ropa sin marca específica = NULL)
- Genérico (productos sin marca = NULL)
```

### ⚠️ IMPORTANTE:
**NO todos los productos tienen marca**, solo algunos accesorios.
La relación es **OPCIONAL** (nullable).

---

## 🛍️ TABLA 3: `productos`

### ¿Para qué sirve?
El producto en sí (vestido, cartera, perfume, etc.)

### Campos:
```sql
id                      BIGSERIAL
nombre                  TEXT                    - "Vestido de Gala Largo"
slug                    TEXT (único)            - "vestido-de-gala-largo"
sku                     TEXT (único)            - "VGL-001"
descripcion             TEXT                    - Descripción larga
descripcion_corta       TEXT                    - Descripción corta

-- RELACIONES
categoria_id            BIGINT (FK)             - ¿A qué categoría pertenece?
marca_id                BIGINT (FK, nullable)   - ¿Tiene marca? (opcional)

-- PRECIOS
precio                  DECIMAL(10,2)           - $150000
precio_comparacion      DECIMAL(10,2)           - $200000 (precio tachado)
precio_costo            DECIMAL(10,2)           - $80000 (solo admin)

-- INVENTARIO
stock                   INTEGER                 - 10 unidades
stock_minimo            INTEGER                 - 3 (alerta)
gestionar_inventario    BOOLEAN                 - ¿Controlar stock?

-- SEO
meta_titulo             TEXT
meta_descripcion        TEXT

-- ESTADOS
activo                  BOOLEAN                 - ¿Se muestra?
destacado               BOOLEAN                 - ¿En home?
nuevo                   BOOLEAN                 - Etiqueta "Nuevo"
en_oferta               BOOLEAN                 - Etiqueta "Oferta"

-- TIMESTAMPS
created_at              TIMESTAMPTZ
updated_at              TIMESTAMPTZ
```

### Ejemplo de producto:
```
Nombre: "Vestido de Gala Rojo con Lentejuelas"
Categoría: Ropa de Gala
Marca: NULL (sin marca)
Precio: $250.000
Precio comparación: $350.000 (oferta del 28%)
Stock: 5 unidades
Variantes: Talla S, M, L, XL
Imágenes: 4 fotos
```

---

## 🖼️ TABLA 4: `imagenes_productos`

### ¿Para qué sirve?
Un producto puede tener **MÚLTIPLES IMÁGENES** (vista frontal, trasera, detalle, etc.)

### Campos:
```sql
id                      BIGSERIAL
producto_id             BIGINT (FK)             - ¿De qué producto es?
imagen                  TEXT                    - Ruta de la imagen
texto_alternativo       TEXT                    - Para SEO/accesibilidad
es_principal            BOOLEAN                 - ¿Imagen principal?
orden                   INTEGER                 - Orden de visualización
created_at              TIMESTAMPTZ
```

### Ejemplo:
```
Producto: "Vestido de Gala Rojo"
  └─ Imagen 1: "vestido-frontal.jpg"       (es_principal=true, orden=1)
  └─ Imagen 2: "vestido-trasera.jpg"       (es_principal=false, orden=2)
  └─ Imagen 3: "vestido-detalle.jpg"       (es_principal=false, orden=3)
  └─ Imagen 4: "vestido-modelo.jpg"        (es_principal=false, orden=4)
```

### ¿Por qué tabla separada?
Porque **1 producto = muchas fotos**. Relación **1:N** (uno a muchos).

---

## 👗 TABLA 5: `variantes_productos`

### ¿Para qué sirve?
El mismo producto puede tener **VARIANTES** (tallas, colores)

### Campos:
```sql
id                      BIGSERIAL
producto_id             BIGINT (FK)             - ¿De qué producto es?
nombre                  TEXT                    - "Talla M - Rojo"
sku                     TEXT (único)            - "VGL-001-M-RED"

-- ATRIBUTOS
talla                   TEXT                    - "M"
color                   TEXT                    - "Rojo"
color_hex               TEXT                    - "#FF0000"

-- PRECIO (opcional, usa el del producto si no tiene)
precio                  DECIMAL(10,2)           - NULL (usa precio del producto)

-- STOCK ESPECÍFICO
stock                   INTEGER                 - 3 unidades de talla M roja

-- IMAGEN (opcional)
imagen                  TEXT                    - Foto específica de esta variante

activo                  BOOLEAN
created_at              TIMESTAMPTZ
updated_at              TIMESTAMPTZ
```

### Ejemplo Real:
```
Producto: "Vestido de Gala Rojo"
Precio base: $250.000

Variantes:
├─ Talla S - Rojo   (stock: 2, precio: $250.000, SKU: VGL-001-S-RED)
├─ Talla M - Rojo   (stock: 5, precio: $250.000, SKU: VGL-001-M-RED)
├─ Talla L - Rojo   (stock: 3, precio: $250.000, SKU: VGL-001-L-RED)
└─ Talla XL - Rojo  (stock: 0, precio: $250.000, SKU: VGL-001-XL-RED) ❌ AGOTADO
```

### ¿Por qué tabla separada?
Porque necesitas **controlar stock POR VARIANTE**, no solo por producto.

---

## 🔗 DIAGRAMA DE RELACIONES

```
categorias (1) ──────< (N) productos
   ↑                          ↓
   │                          ├──> (N) imagenes_productos
   └─── (padre_id)            └──> (N) variantes_productos
                              ↑
marcas (1) ──────< (N) productos (opcional)


LECTURA:
- 1 categoría tiene MUCHOS productos
- 1 marca tiene MUCHOS productos (o ninguno)
- 1 producto tiene MUCHAS imágenes
- 1 producto tiene MUCHAS variantes
- 1 categoría puede tener MUCHAS subcategorías
```

---

## 📝 CASOS DE USO REALES

### Caso 1: Vestido de Gala
```
TABLA: productos
- Nombre: "Vestido Largo de Gala Rojo"
- Categoría: "Ropa de Gala"
- Marca: NULL (sin marca)
- Precio: $250.000
- Stock: (controlado por variantes)

TABLA: imagenes_productos
- 4 imágenes del vestido

TABLA: variantes_productos
- S, M, L, XL (cada una con su stock)
```

### Caso 2: Perfume de Marca
```
TABLA: productos
- Nombre: "Good Girl Carolina Herrera 80ml"
- Categoría: "Perfumes" (subcategoría de Accesorios)
- Marca: "Carolina Herrera" ✅
- Precio: $450.000
- Stock: 10 unidades

TABLA: imagenes_productos
- 2 imágenes del perfume

TABLA: variantes_productos
- NULL (no tiene variantes, solo una presentación)
```

### Caso 3: Cartera sin Marca
```
TABLA: productos
- Nombre: "Cartera Cruzada Cuero Sintético"
- Categoría: "Carteras"
- Marca: NULL (sin marca)
- Precio: $80.000
- Stock: (controlado por variantes)

TABLA: variantes_productos
- Color Negro (stock: 5)
- Color Café (stock: 3)
- Color Beige (stock: 2)
```

---

## 🎨 LO QUE VI EN LOS HTMLs

### Del frontend (shop-filter-sidebar.html):
```html
✅ Filtros por categoría
✅ Filtros por marca
✅ Filtros por precio
✅ Filtros por color
✅ Filtros por talla
✅ Sistema de ordenamiento (precio alto/bajo)
✅ Productos con múltiples colores
✅ Etiquetas: "New", "Sale", "%Off"
```

### Del admin (add-product.html):
```html
✅ Formulario completo de producto
✅ Selector de categoría
✅ Selector de marca
✅ Múltiples imágenes
✅ Gestión de stock
✅ Precios (normal, comparación, costo)
✅ Variantes (tallas, colores)
```

---

## ✅ RESUMEN: ¿CUÁNTAS TABLAS?

### **5 TABLAS** para productos:

1. **categorias** (Ropa de Gala, Playa, Carteras, Perfumes)
2. **marcas** (Carolina Herrera, Michael Kors, etc.)
3. **productos** (Producto principal)
4. **imagenes_productos** (Múltiples fotos por producto)
5. **variantes_productos** (Tallas, colores con stock individual)

---

## 🚀 LO QUE VOY A HACER SI APRUEBAS:

### 1. **Actualizar `models.py`** con:
   - ✅ Campos en español
   - ✅ Categorías con jerarquía (padre-hijo)
   - ✅ Marca opcional (nullable)
   - ✅ Variantes con stock individual
   - ✅ Sistema de ofertas
   - ✅ Control de inventario
   - ✅ SEO fields

### 2. **Configurar Admin** con:
   - ✅ Inlines para imágenes y variantes
   - ✅ Filtros por categoría, marca, estado
   - ✅ Búsqueda por nombre, SKU
   - ✅ Vista previa de imágenes

### 3. **Crear Migraciones** para:
   - ✅ Aplicar cambios a la base de datos

---

## ❓ PREGUNTAS PARA TI:

1. **¿Esta estructura te parece bien?**
   - 5 tablas: categorias, marcas, productos, imagenes_productos, variantes_productos

2. **¿Categorías adicionales?**
   Además de:
   - Ropa de Playa
   - Ropa de Gala
   - Carteras
   - Perfumes
   - Relojes
   
   ¿Hay otras ocasiones/estilos?

3. **¿Sistema de tallas?**
   - ¿XS, S, M, L, XL, XXL?
   - ¿Tallas numéricas (36, 38, 40)?
   - ¿Ambas?

4. **¿Control de stock?**
   - ¿Por variante? (Talla M Rojo: 5 unidades) ✅ RECOMENDADO
   - ¿Por producto? (Total: 15 unidades)

5. **¿Te quedó claro lo del SLUG?**

---

## 💡 RECOMENDACIONES:

### ✅ QUÉ MANTENER:
- 5 tablas es perfecto para tu negocio
- Marca opcional (solo algunos accesorios la tienen)
- Variantes con stock individual
- Categorías jerárquicas
- Múltiples imágenes

### ⚠️ QUÉ AGREGAR DESPUÉS (opcional):
- Tabla de colores (si quieres estandarizar)
- Tabla de tallas (si quieres estandarizar)
- Tabla de materiales (cuero, sintético, etc.)

### 🎯 PARA EMPEZAR:
Estas 5 tablas son SUFICIENTES y se adaptan perfectamente a los HTMLs que tienes.

---

## 🤔 ¿APRUEBAS ESTA ESTRUCTURA?

**SI DICES QUE SÍ, VOY A:**
1. Actualizar los modelos
2. Crear las migraciones
3. Aplicar a la base de datos
4. Configurar el admin
5. Mostrarte ejemplos de cómo agregar productos

**SI QUIERES CAMBIOS, DIME:**
- ¿Qué modificar?
- ¿Qué agregar?
- ¿Qué quitar?

---

**¿Procedemos con esta estructura? 🚀**
