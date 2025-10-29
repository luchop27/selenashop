# 📊 ESQUEMA DE BASE DE DATOS - SELENA STORE

## 🎯 App: PRODUCTOS (Implementado ✅)

### 1️⃣ Tabla: `categorias`
```
┌─────────────────────────────────────────────────┐
│ CATEGORIAS                                      │
├─────────────────────────────────────────────────┤
│ id (PK)              - INTEGER                  │
│ nombre               - VARCHAR(100)             │
│ slug                 - VARCHAR(100) UNIQUE      │
│ descripcion          - TEXT (nullable)          │
│ padre_id (FK)        - INTEGER (nullable)       │  ← Referencia a sí misma (jerarquía)
│ imagen               - VARCHAR(255) (nullable)  │
│ activo               - BOOLEAN (default: True)  │
│ orden                - INTEGER (default: 0)     │
│ meta_titulo          - VARCHAR(200) (nullable)  │
│ meta_descripcion     - TEXT (nullable)          │
│ created_at           - DATETIME                 │
│ updated_at           - DATETIME                 │
└─────────────────────────────────────────────────┘

📋 Ejemplo de datos:
┌────┬───────────┬────────┬──────────┐
│ ID │ Nombre    │ Padre  │ Activo   │
├────┼───────────┼────────┼──────────┤
│ 1  │ Ropa      │ NULL   │ ✓        │
│ 2  │ Playa     │ 1      │ ✓        │  (hija de Ropa)
│ 3  │ Gala      │ 1      │ ✓        │  (hija de Ropa)
│ 4  │ Casual    │ 1      │ ✓        │  (hija de Ropa)
│ 5  │ Deportiva │ 1      │ ✓        │  (hija de Ropa)
│ 6  │ Accesorios│ NULL   │ ✓        │
│ 7  │ Carteras  │ 6      │ ✓        │  (hija de Accesorios)
│ 8  │ Perfumes  │ 6      │ ✓        │  (hija de Accesorios)
│ 9  │ Relojes   │ 6      │ ✓        │  (hija de Accesorios)
└────┴───────────┴────────┴──────────┘
```

### 2️⃣ Tabla: `marcas`
```
┌─────────────────────────────────────────────────┐
│ MARCAS                                          │
├─────────────────────────────────────────────────┤
│ id (PK)              - INTEGER                  │
│ nombre               - VARCHAR(100)             │
│ slug                 - VARCHAR(100) UNIQUE      │
│ descripcion          - TEXT (nullable)          │
│ logo                 - VARCHAR(255) (nullable)  │
│ activo               - BOOLEAN (default: True)  │
│ created_at           - DATETIME                 │
│ updated_at           - DATETIME                 │
└─────────────────────────────────────────────────┘

📋 Ejemplo de datos:
┌────┬──────────────┬────────┐
│ ID │ Nombre       │ Activo │
├────┼──────────────┼────────┤
│ 1  │ Chanel       │ ✓      │  (para perfumes)
│ 2  │ Michael Kors │ ✓      │  (para carteras/relojes)
│ 3  │ Guess        │ ✓      │  (para carteras/relojes)
│ 4  │ Rolex        │ ✓      │  (para relojes)
└────┴──────────────┴────────┘

⚠️ NOTA: Marca es OPCIONAL (null=True) - Solo algunos accesorios tienen marca
```

### 3️⃣ Tabla: `productos`
```
┌──────────────────────────────────────────────────────────┐
│ PRODUCTOS                                                │
├──────────────────────────────────────────────────────────┤
│ id (PK)                  - INTEGER                       │
│ nombre                   - VARCHAR(200)                  │
│ slug                     - VARCHAR(200) UNIQUE           │
│ sku                      - VARCHAR(50) UNIQUE            │
│ descripcion              - TEXT (nullable)               │
│ descripcion_corta        - VARCHAR(500) (nullable)       │
│ categoria_id (FK)        - INTEGER                       │  → categorias.id
│ marca_id (FK)            - INTEGER (nullable)            │  → marcas.id
│ precio                   - DECIMAL(10,2)                 │
│ precio_comparacion       - DECIMAL(10,2) (nullable)      │  (precio antes de descuento)
│ precio_costo             - DECIMAL(10,2) (nullable)      │
│ stock                    - INTEGER (default: 0)          │
│ stock_minimo             - INTEGER (default: 5)          │
│ estado                   - VARCHAR(20)                   │  (disponible/agotado/inactivo)
│ destacado                - BOOLEAN (default: False)      │
│ nuevo                    - BOOLEAN (default: False)      │
│ en_oferta                - BOOLEAN (default: False)      │
│ meta_titulo              - VARCHAR(200) (nullable)       │
│ meta_descripcion         - TEXT (nullable)               │
│ created_at               - DATETIME                      │
│ updated_at               - DATETIME                      │
└──────────────────────────────────────────────────────────┘

🔄 LÓGICA AUTOMÁTICA:
- Si stock = 0 → estado = 'agotado' (automático en save())
- Si stock > 0 y estado = 'agotado' → estado = 'disponible' (automático)

📋 Estados posibles:
┌────────────┬──────────────────────────────────────┐
│ Estado     │ Descripción                          │
├────────────┼──────────────────────────────────────┤
│ disponible │ Stock > 0, visible en tienda         │
│ agotado    │ Stock = 0, no disponible             │
│ inactivo   │ Oculto manualmente (admin decision)  │
└────────────┴──────────────────────────────────────┘
```

### 4️⃣ Tabla: `imagenes_productos`
```
┌─────────────────────────────────────────────────┐
│ IMAGENES_PRODUCTOS                              │
├─────────────────────────────────────────────────┤
│ id (PK)              - INTEGER                  │
│ producto_id (FK)     - INTEGER                  │  → productos.id (CASCADE)
│ imagen               - VARCHAR(255)             │
│ texto_alternativo    - VARCHAR(200) (nullable)  │
│ es_principal         - BOOLEAN (default: False) │
│ orden                - INTEGER (default: 0)     │
│ created_at           - DATETIME                 │
└─────────────────────────────────────────────────┘

📋 Ejemplo: Un vestido puede tener múltiples imágenes
┌────┬──────────────┬──────────────┬──────────┐
│ ID │ Producto     │ Es Principal │ Orden    │
├────┼──────────────┼──────────────┼──────────┤
│ 1  │ Vestido Gala │ ✓            │ 1        │  ← Imagen principal
│ 2  │ Vestido Gala │              │ 2        │
│ 3  │ Vestido Gala │              │ 3        │
│ 4  │ Vestido Gala │              │ 4        │
└────┴──────────────┴──────────────┴──────────┘
```

### 5️⃣ Tabla: `variantes_productos`
```
┌─────────────────────────────────────────────────┐
│ VARIANTES_PRODUCTOS                             │
├─────────────────────────────────────────────────┤
│ id (PK)              - INTEGER                  │
│ producto_id (FK)     - INTEGER                  │  → productos.id (CASCADE)
│ sku                  - VARCHAR(50) UNIQUE       │
│ talla                - VARCHAR(20)              │  ← SOLO TALLA (sin color)
│ precio               - DECIMAL(10,2) (nullable) │  (opcional, usa precio del producto)
│ stock                - INTEGER (default: 0)     │
│ activo               - BOOLEAN (default: True)  │
│ created_at           - DATETIME                 │
│ updated_at           - DATETIME                 │
└─────────────────────────────────────────────────┘

UNIQUE_TOGETHER: (producto_id, talla)  ← No se puede repetir la misma talla

📋 Tallas disponibles:
┌─────────────┬────────────────────────────────┐
│ Tipo        │ Valores                        │
├─────────────┼────────────────────────────────┤
│ Letras      │ XS, S, M, L, XL, XXL          │
│ Números     │ 6, 8, 10, 12, 14, 16          │
│ Int. Ropa   │ 36, 38, 40, 42, 44            │
└─────────────┴────────────────────────────────┘

📋 Ejemplo: Un vestido en diferentes tallas
┌────┬──────────────┬───────┬────────┬────────┐
│ ID │ Producto     │ Talla │ Stock  │ Precio │
├────┼──────────────┼───────┼────────┼────────┤
│ 1  │ Vestido Playa│ S     │ 5      │ NULL   │  (usa precio del producto)
│ 2  │ Vestido Playa│ M     │ 10     │ NULL   │
│ 3  │ Vestido Playa│ L     │ 3      │ NULL   │
│ 4  │ Vestido Playa│ XL    │ 0      │ NULL   │  (agotada)
└────┴──────────────┴───────┴────────┴────────┘
```

---

## 🔗 RELACIONES ENTRE TABLAS

```
┌─────────────┐
│  CATEGORIAS │
│   (padre)   │
└──────┬──────┘
       │ 1:N (auto-referencia)
       ↓
┌─────────────┐
│  CATEGORIAS │
│   (hijas)   │
└──────┬──────┘
       │ 1:N
       ↓
┌─────────────┐        ┌──────────┐
│  PRODUCTOS  │ N:1    │  MARCAS  │
│             │───────→│          │
└──────┬──────┘        └──────────┘
       │
       │ 1:N
       ├──────────────────────┬────────────────────┐
       ↓                      ↓                    ↓
┌───────────────┐    ┌─────────────────┐   ┌──────────────┐
│   IMAGENES    │    │   VARIANTES     │   │   RESEÑAS    │
│   PRODUCTOS   │    │   PRODUCTOS     │   │   PRODUCTOS  │
└───────────────┘    └─────────────────┘   └──────────────┘
```

---

## 📊 DIAGRAMA VISUAL COMPLETO

```
                    ┌──────────────────────┐
                    │    CATEGORIAS        │
                    │ ══════════════════   │
                    │ • id (PK)            │
                    │ • nombre             │
                    │ • slug               │
                    │ • padre_id (FK) ◄────┼───┐ Auto-referencia
                    │ • activo             │   │
                    └──────────┬───────────┘   │
                               │                │
                               │ 1:N            │
                               ↓                │
┌──────────────┐      ┌────────────────────────┴─────┐
│   MARCAS     │  N:1 │      PRODUCTOS               │
│ ═══════════  │◄─────│  ════════════════════════    │
│ • id (PK)    │      │  • id (PK)                   │
│ • nombre     │      │  • nombre                    │
│ • slug       │      │  • sku (UNIQUE)              │
│ • activo     │      │  • categoria_id (FK)         │
└──────────────┘      │  • marca_id (FK, nullable)   │
                      │  • precio                    │
                      │  • stock                     │
                      │  • estado (disponible/       │
                      │           agotado/inactivo)  │
                      │  • destacado                 │
                      └──────────┬───────────────────┘
                                 │
                                 │ 1:N
              ┌──────────────────┼────────────────────┐
              ↓                  ↓                    ↓
    ┌──────────────────┐  ┌─────────────────┐  ┌──────────────┐
    │ IMAGENES_        │  │ VARIANTES_      │  │ RESENAS_     │
    │ PRODUCTOS        │  │ PRODUCTOS       │  │ PRODUCTOS    │
    │ ═══════════════  │  │ ══════════════  │  │ ════════════ │
    │ • id (PK)        │  │ • id (PK)       │  │ • id (PK)    │
    │ • producto_id    │  │ • producto_id   │  │ • producto_id│
    │ • imagen         │  │ • sku (UNIQUE)  │  │ • usuario_id │
    │ • es_principal   │  │ • talla         │  │ • calificacion│
    │ • orden          │  │ • stock         │  │ • comentario │
    └──────────────────┘  │ • activo        │  └──────────────┘
                          └─────────────────┘
                          
    UNIQUE: (producto_id, talla)
```

---

## 🎯 CARACTERÍSTICAS ESPECIALES

### ✅ Implementadas:
1. **Jerarquía de Categorías**: Categorías padres e hijas (Ropa > Playa)
2. **Marca Opcional**: Solo algunos productos tienen marca (accesorios)
3. **Estado Automático**: Si stock=0 → estado='agotado' (en el método save())
4. **Variantes por Talla**: Sin colores, solo tallas (S, M, L, XL, 36, 38, etc.)
5. **Múltiples Imágenes**: Un producto puede tener varias imágenes
6. **Slug Automático**: Generado automáticamente desde el nombre
7. **Stock por Variante**: Cada talla tiene su propio stock

### 🚫 NO Implementado (según tus especificaciones):
- ❌ Color en variantes (NO lo quieres)
- ❌ Gestión de inventario compleja
- ❌ Campo activo en productos (reemplazado por estado)

---

## 📝 ÍNDICES Y OPTIMIZACIONES

```sql
-- Índices creados automáticamente:
- productos.slug (UNIQUE)
- productos.sku (UNIQUE)
- productos.estado (INDEX) ← Búsqueda rápida por estado
- categorias.slug (UNIQUE)
- marcas.slug (UNIQUE)
- variantes_productos.sku (UNIQUE)
- (producto_id, talla) (UNIQUE TOGETHER)
```

---

---

## 🎯 App: USUARIOS (Pendiente ⏳)

### 6️⃣ Tabla: `usuarios`
```
┌──────────────────────────────────────────────────────────┐
│ USUARIOS                                                 │
├──────────────────────────────────────────────────────────┤
│ id (PK)                  - INTEGER                       │
│ nombre                   - VARCHAR(100)                  │
│ apellido                 - VARCHAR(100)                  │
│ email                    - VARCHAR(255) UNIQUE (CITEXT)  │  ← Case insensitive
│ telefono                 - VARCHAR(20)                   │
│ ciudad                   - VARCHAR(100)                  │
│ password                 - VARCHAR(255)                  │  ← Hashed
│ estado                   - VARCHAR(20)                   │  (activo/inactivo/suspendido)
│ rol                      - VARCHAR(20)                   │  (cliente/admin)
│ created_at               - DATETIME                      │
│ updated_at               - DATETIME                      │
└──────────────────────────────────────────────────────────┘

📋 Roles:
┌──────────┬─────────────────────────────────────────────┐
│ Rol      │ Permisos                                    │
├──────────┼─────────────────────────────────────────────┤
│ cliente  │ Comprar, ver productos, hacer pedidos       │
│ admin    │ Gestionar productos, categorías, usuarios   │
└──────────┴─────────────────────────────────────────────┘

📋 Estados:
┌────────────┬─────────────────────────────────────────┐
│ Estado     │ Descripción                             │
├────────────┼─────────────────────────────────────────┤
│ activo     │ Puede hacer compras normalmente         │
│ inactivo   │ Cuenta deshabilitada temporalmente      │
│ suspendido │ Bloqueado por incumplimiento            │
└────────────┴─────────────────────────────────────────┘
```

---

## 🛒 App: CARRITO (Pendiente ⏳)

### 7️⃣ Tabla: `carrito`
```
┌──────────────────────────────────────────────────────────┐
│ CARRITO                                                  │
├──────────────────────────────────────────────────────────┤
│ id (PK)                  - INTEGER                       │
│ usuario_id (FK)          - INTEGER (nullable)            │  → usuarios.id
│ session_key              - VARCHAR(100) (nullable)       │  ← Para usuarios no logueados
│ created_at               - DATETIME                      │
│ updated_at               - DATETIME                      │
└──────────────────────────────────────────────────────────┘

⚠️ NOTA: 
- Si usuario_id IS NULL → Usar session_key (carrito de invitado)
- Si usuario_id IS NOT NULL → Carrito persistente
```

### 8️⃣ Tabla: `items_carrito`
```
┌──────────────────────────────────────────────────────────┐
│ ITEMS_CARRITO                                            │
├──────────────────────────────────────────────────────────┤
│ id (PK)                  - INTEGER                       │
│ carrito_id (FK)          - INTEGER                       │  → carrito.id (CASCADE)
│ producto_id (FK)         - INTEGER                       │  → productos.id
│ variante_id (FK)         - INTEGER (nullable)            │  → variantes_productos.id
│ cantidad                 - INTEGER (default: 1)          │
│ precio_unitario          - DECIMAL(10,2)                 │  ← Precio al momento de agregar
│ created_at               - DATETIME                      │
│ updated_at               - DATETIME                      │
└──────────────────────────────────────────────────────────┘

UNIQUE_TOGETHER: (carrito_id, producto_id, variante_id)

📋 Ejemplo: Carrito de María
┌────┬────────────────┬─────────┬──────────┬────────┬──────────┐
│ ID │ Producto       │ Variante│ Cantidad │ Precio │ Subtotal │
├────┼────────────────┼─────────┼──────────┼────────┼──────────┤
│ 1  │ Vestido Playa  │ M       │ 2        │ $45.00 │ $90.00   │
│ 2  │ Vestido Gala   │ L       │ 1        │ $89.00 │ $89.00   │
│ 3  │ Perfume Chanel │ NULL    │ 1        │ $120.00│ $120.00  │
└────┴────────────────┴─────────┴──────────┴────────┴──────────┘
                                            TOTAL: $299.00

🔄 Método especial: get_whatsapp_message()
Genera mensaje: "Hola! Quiero comprar:
- 2x Vestido Playa (M) - $90.00
- 1x Vestido Gala (L) - $89.00
- 1x Perfume Chanel - $120.00
Total: $299.00"
```

---

## 📦 App: PEDIDOS (Pendiente ⏳)

### 9️⃣ Tabla: `pedidos`
```
┌──────────────────────────────────────────────────────────┐
│ PEDIDOS                                                  │
├──────────────────────────────────────────────────────────┤
│ id (PK)                  - INTEGER                       │
│ numero_pedido            - VARCHAR(50) UNIQUE            │  ← P-2024-00001
│ usuario_id (FK)          - INTEGER (nullable)            │  → usuarios.id
│ nombre_cliente           - VARCHAR(200)                  │  ← Para invitados
│ email_cliente            - VARCHAR(255)                  │
│ telefono_cliente         - VARCHAR(20)                   │
│ ciudad_cliente           - VARCHAR(100)                  │
│ direccion_entrega        - TEXT                          │
│ subtotal                 - DECIMAL(10,2)                 │
│ descuento                - DECIMAL(10,2) (default: 0)    │
│ total                    - DECIMAL(10,2)                 │
│ estado                   - VARCHAR(30)                   │
│ metodo_contacto          - VARCHAR(20)                   │  (whatsapp/llamada)
│ whatsapp_enviado         - BOOLEAN (default: False)      │
│ notas                    - TEXT (nullable)               │
│ created_at               - DATETIME                      │
│ updated_at               - DATETIME                      │
└──────────────────────────────────────────────────────────┘

📋 Estados del pedido:
┌──────────────────┬────────────────────────────────────────┐
│ Estado           │ Descripción                            │
├──────────────────┼────────────────────────────────────────┤
│ pendiente        │ Pedido creado, esperando confirmación  │
│ whatsapp_enviado │ Mensaje enviado a WhatsApp             │
│ confirmado       │ Cliente confirmó por WhatsApp          │
│ preparando       │ Empacando el pedido                    │
│ enviado          │ En camino al cliente                   │
│ entregado        │ Pedido completado                      │
│ cancelado        │ Cancelado por cliente o admin          │
└──────────────────┴────────────────────────────────────────┘

📋 Ejemplo de número_pedido:
P-2024-00001  ← Pedido #1 del año 2024
P-2024-00002  ← Pedido #2 del año 2024
```

### 🔟 Tabla: `items_pedido`
```
┌──────────────────────────────────────────────────────────┐
│ ITEMS_PEDIDO                                             │
├──────────────────────────────────────────────────────────┤
│ id (PK)                  - INTEGER                       │
│ pedido_id (FK)           - INTEGER                       │  → pedidos.id (CASCADE)
│ producto_id (FK)         - INTEGER                       │  → productos.id
│ variante_id (FK)         - INTEGER (nullable)            │  → variantes_productos.id
│ producto_nombre          - VARCHAR(200)                  │  ← Snapshot (nombre al comprar)
│ producto_sku             - VARCHAR(50)                   │
│ variante_talla           - VARCHAR(20) (nullable)        │
│ cantidad                 - INTEGER                       │
│ precio_unitario          - DECIMAL(10,2)                 │  ← Precio al momento de compra
│ subtotal                 - DECIMAL(10,2)                 │
│ created_at               - DATETIME                      │
└──────────────────────────────────────────────────────────┘

⚠️ IMPORTANTE: Se guarda snapshot del producto
Razón: Si después cambia el precio, el pedido mantiene el precio original

📋 Ejemplo: Pedido P-2024-00001
┌────┬────────────────┬───────┬──────────┬────────┬──────────┐
│ ID │ Producto       │ Talla │ Cantidad │ Precio │ Subtotal │
├────┼────────────────┼───────┼──────────┼────────┼──────────┤
│ 1  │ Vestido Playa  │ M     │ 2        │ $45.00 │ $90.00   │
│ 2  │ Vestido Gala   │ L     │ 1        │ $89.00 │ $89.00   │
│ 3  │ Perfume Chanel │ NULL  │ 1        │ $120.00│ $120.00  │
└────┴────────────────┴───────┴──────────┴────────┴──────────┘
```

---

## 🔗 DIAGRAMA COMPLETO DE RELACIONES

```
                    ┌──────────────────────┐
                    │    CATEGORIAS        │
                    │ ══════════════════   │
                    │ • id (PK)            │
                    │ • padre_id (FK) ◄────┼───┐ Auto-referencia
                    └──────────┬───────────┘   │
                               │                │
                               │ 1:N            │
                               ↓                │
┌──────────────┐      ┌────────────────────────┴─────┐
│   MARCAS     │  N:1 │      PRODUCTOS               │
│ ═══════════  │◄─────│  ════════════════════════    │
│ • id (PK)    │      │  • id (PK)                   │
└──────────────┘      │  • categoria_id (FK)         │
                      │  • marca_id (FK)             │
                      └──────────┬───────────────────┘
                                 │
                                 │ 1:N
              ┌──────────────────┼────────────────────┐
              ↓                  ↓                    ↓
    ┌──────────────────┐  ┌─────────────────┐  ┌──────────────┐
    │ IMAGENES_        │  │ VARIANTES_      │  │ RESENAS_     │
    │ PRODUCTOS        │  │ PRODUCTOS       │  │ PRODUCTOS    │
    └──────────────────┘  └────────┬────────┘  └──────────────┘
                                   │
                                   │ N:1
                                   ↓
                          ┌─────────────────┐
                          │ ITEMS_CARRITO   │
                          └────────┬────────┘
                                   │ N:1
                                   ↓
┌──────────────┐          ┌─────────────────┐
│  USUARIOS    │  1:N     │    CARRITO      │
│ ═══════════  │─────────→│  ═════════════  │
│ • id (PK)    │          │  • id (PK)      │
│ • email      │          │  • usuario_id   │
│ • rol        │          │  • session_key  │
└──────┬───────┘          └─────────────────┘
       │
       │ 1:N
       ↓
┌──────────────────┐
│    PEDIDOS       │
│  ══════════════  │
│  • id (PK)       │
│  • usuario_id    │
│  • numero_pedido │
│  • estado        │
│  • total         │
└────────┬─────────┘
         │
         │ 1:N
         ↓
┌──────────────────┐       ┌─────────────────┐
│  ITEMS_PEDIDO    │  N:1  │   PRODUCTOS     │
│  ══════════════  │───────→  ═══════════════ │
│  • pedido_id (FK)│       │  • id (PK)      │
│  • producto_id   │       └─────────────────┘
│  • variante_id   │       
│  • cantidad      │       ┌─────────────────┐
│  • precio_snap   │  N:1  │ VARIANTES_      │
│                  │───────→  PRODUCTOS       │
└──────────────────┘       └─────────────────┘
```

---

## 📊 RESUMEN DE TODAS LAS TABLAS

### ✅ **IMPLEMENTADAS** (App Productos):
1. ✅ `categorias` - 12 campos
2. ✅ `marcas` - 8 campos
3. ✅ `productos` - 21 campos
4. ✅ `imagenes_productos` - 7 campos
5. ✅ `variantes_productos` - 9 campos
6. ✅ `resenas_productos` - 10 campos

### ⏳ **PENDIENTES**:
7. ⏳ `usuarios` - 11 campos (App Usuarios)
8. ⏳ `carrito` - 5 campos (App Carrito)
9. ⏳ `items_carrito` - 8 campos (App Carrito)
10. ⏳ `pedidos` - 17 campos (App Pedidos)
11. ⏳ `items_pedido` - 11 campos (App Pedidos)

**Total: 11 tablas en todo el sistema**

---

## 🔄 FLUJO COMPLETO DEL NEGOCIO

```
1. NAVEGACIÓN
   Usuario → Ve Productos → Filtra por Categoría/Marca
   
2. SELECCIÓN
   Usuario → Elige Producto → Selecciona Talla → Añade al Carrito
   
3. CARRITO
   Sistema → Guarda en items_carrito
   Usuario puede ser:
   • Invitado (session_key)
   • Registrado (usuario_id)
   
4. CHECKOUT (sin pagos, solo WhatsApp)
   Usuario → Completa datos de entrega
   Sistema → Crea Pedido (estado: pendiente)
   Sistema → Genera mensaje WhatsApp:
   
   "Hola! Quiero hacer un pedido:
   
   📋 Pedido: P-2024-00001
   
   🛍️ Productos:
   • 2x Vestido Playa (M) - $90.00
   • 1x Vestido Gala (L) - $89.00
   
   💵 Total: $179.00
   
   📍 Entrega: [Dirección del cliente]
   👤 Nombre: [Nombre del cliente]
   📞 Tel: [Teléfono]"
   
5. WHATSAPP
   Sistema → Abre WhatsApp con mensaje predefinido
   Sistema → Marca whatsapp_enviado = True
   Usuario → Envía mensaje
   
6. GESTIÓN
   Admin → Recibe pedido por WhatsApp
   Admin → Confirma disponibilidad
   Admin → Actualiza estado del pedido:
           pendiente → confirmado → preparando → enviado → entregado
   
7. INVENTARIO
   Sistema → Reduce stock automáticamente al confirmar pedido
   Sistema → Si stock = 0, marca producto/variante como agotado
```

---

## 🎯 ÍNDICES Y OPTIMIZACIONES

```sql
-- Productos
CREATE INDEX idx_productos_estado ON productos(estado);
CREATE INDEX idx_productos_categoria ON productos(categoria_id);
CREATE INDEX idx_productos_destacado ON productos(destacado);
CREATE UNIQUE INDEX idx_productos_slug ON productos(slug);
CREATE UNIQUE INDEX idx_productos_sku ON productos(sku);

-- Categorías
CREATE UNIQUE INDEX idx_categorias_slug ON categorias(slug);
CREATE INDEX idx_categorias_padre ON categorias(padre_id);

-- Marcas
CREATE UNIQUE INDEX idx_marcas_slug ON marcas(slug);

-- Variantes
CREATE UNIQUE INDEX idx_variantes_sku ON variantes_productos(sku);
CREATE UNIQUE INDEX idx_variantes_producto_talla ON variantes_productos(producto_id, talla);

-- Usuarios
CREATE UNIQUE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_estado ON usuarios(estado);

-- Carrito
CREATE INDEX idx_carrito_usuario ON carrito(usuario_id);
CREATE INDEX idx_carrito_session ON carrito(session_key);

-- Pedidos
CREATE UNIQUE INDEX idx_pedidos_numero ON pedidos(numero_pedido);
CREATE INDEX idx_pedidos_usuario ON pedidos(usuario_id);
CREATE INDEX idx_pedidos_estado ON pedidos(estado);
CREATE INDEX idx_pedidos_fecha ON pedidos(created_at);
```

---

## 📈 ESTADÍSTICAS ESTIMADAS

```
Tamaño aproximado de la base de datos:

Tabla                    Registros Estimados    Tamaño
═══════════════════════════════════════════════════════
categorias               15-20                  5 KB
marcas                   10-15                  3 KB
productos                500-1000               500 KB
imagenes_productos       2000-4000              1 MB
variantes_productos      2000-5000              800 KB
resenas_productos        100-500                100 KB
usuarios                 1000-5000              500 KB
carrito                  50-200                 10 KB
items_carrito            100-500                50 KB
pedidos                  500-2000               300 KB
items_pedido             1500-6000              700 KB
═══════════════════════════════════════════════════════
TOTAL ESTIMADO                                  ~4 MB
```

---

**Estado Actual**: 
- ✅ App PRODUCTOS: 100% completado (6 tablas)
- ⏳ App USUARIOS: 0% (1 tabla)
- ⏳ App CARRITO: 0% (2 tablas)
- ⏳ App PEDIDOS: 0% (2 tablas)

**Progreso Total**: **54% (6/11 tablas)**
