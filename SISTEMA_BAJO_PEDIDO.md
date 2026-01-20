# Sistema de Productos Bajo Pedido

## 📋 Descripción General

Se ha implementado un sistema de gestión de productos que permite dos comportamientos diferentes cuando un producto se queda sin stock:

### ✅ Producto "Bajo Pedido" (Activado)
- El producto **seguirá visible** en la tienda aunque no tenga stock
- Mostrará un mensaje indicando "No disponible - Bajo pedido"
- Los clientes podrán realizar pedidos del producto
- **NO se elimina** automáticamente del sistema

### ❌ Producto Normal (Desactivado)
- Cuando el stock llega a **0 en todas las tallas/variantes**
- El producto se **elimina automáticamente** del sistema
- Ya no aparecerá en la tienda ni en el admin

---

## 🔧 Cambios Implementados

### 1. Base de Datos
**Archivo**: `apps/productos/models.py`

Se agregó el campo `bajo_pedido` al modelo Producto:

```python
bajo_pedido = models.BooleanField(
    default=False,
    help_text="Si está activado, el producto seguirá visible aunque no tenga stock..."
)
```

**Métodos nuevos**:
- `stock_total()` - Calcula stock total del producto
- `tiene_stock()` - Verifica si hay stock disponible
- `permite_pedido()` - Indica si permite hacer pedidos
- `estado_stock()` - Retorna: "disponible", "bajo_pedido" o "sin_stock"

**Migración**: `apps/productos/migrations/0015_producto_bajo_pedido.py`

---

### 2. Admin Django
**Archivo**: `apps/productos/admin.py`

- Campo `bajo_pedido` agregado a `list_display` (visible en la lista)
- Agregado a `list_filter` (filtrar por este campo)
- Agregado a `list_editable` (editable desde la lista)
- Incluido en fieldsets de "Venta"

---

### 3. Panel Admin (Ecomus)

#### Archivo: `admin-ecomus/add-product.html`
Checkbox agregado en la sección "Estado":

```html
<input type="checkbox" name="bajo_pedido" id="id_bajo_pedido">
<label for="id_bajo_pedido">
    <span>Producto bajo pedido</span>
    <p>Si está activado, el producto seguirá visible aunque no tenga stock...</p>
</label>
```

#### Archivo: `admin-ecomus/edit-product.html`
Mismo checkbox con el estado actual del producto:

```html
<input type="checkbox" name="bajo_pedido" {% if producto.bajo_pedido %}checked{% endif %}>
```

---

### 4. Vistas de Procesamiento
**Archivo**: `apps/productos/views.py`

#### Vista `admin_producto_add`:
```python
producto = form.save(commit=False)
producto.bajo_pedido = request.POST.get('bajo_pedido') == 'on'
producto.save()
```

#### Vista `admin_producto_edit`:
```python
producto = form.save(commit=False)
producto.bajo_pedido = request.POST.get('bajo_pedido') == 'on'
producto.save()
```

---

### 5. Sistema de Eliminación Automática
**Archivo**: `apps/productos/signals.py` (NUEVO)

Se creó un sistema de señales que:

1. **Monitorea** cada vez que se guarda o elimina una variante
2. **Calcula** el stock total del producto
3. **Verifica** si el producto tiene `bajo_pedido` activado
4. **Elimina** automáticamente el producto si:
   - Stock total = 0
   - bajo_pedido = False

```python
@receiver(post_save, sender=Variante)
@receiver(post_delete, sender=Variante)
def verificar_stock_producto(sender, instance, **kwargs):
    producto = instance.producto
    stock_total = sum(v.stock for v in producto.variantes.all())
    
    if stock_total == 0 and not producto.bajo_pedido:
        logger.warning(f"🗑️ Eliminando producto '{producto.nombre}'")
        producto.delete()
```

**Registro de señales**: `apps/productos/apps.py`

```python
def ready(self):
    import apps.productos.signals
```

---

## 📖 Guía de Uso

### Para el Administrador:

#### Crear un Producto Bajo Pedido:
1. Ir a **Admin → Productos → Agregar Producto**
2. Llenar todos los campos normalmente
3. En la sección **Estado**, marcar ✅ **"Producto bajo pedido"**
4. Guardar

#### Editar un Producto Existente:
1. Ir a **Admin → Productos → Lista de Productos**
2. Clic en **Editar** en el producto deseado
3. Marcar/desmarcar el checkbox **"Producto bajo pedido"**
4. Guardar

#### Desde la Lista de Productos:
- Puedes editar el campo `bajo_pedido` directamente desde la lista
- También puedes filtrar productos por este campo

---

### Comportamiento Automático:

#### Escenario 1: Producto Normal (bajo_pedido = No)
```
Stock inicial: 10 unidades
↓
Se venden 10 unidades
↓
Stock = 0
↓
🗑️ Producto ELIMINADO automáticamente
```

#### Escenario 2: Producto Bajo Pedido (bajo_pedido = Sí)
```
Stock inicial: 10 unidades
↓
Se venden 10 unidades
↓
Stock = 0
↓
✅ Producto SE MANTIENE visible
📦 Muestra "Bajo pedido"
🛒 Permite hacer pedidos
```

---

## 🎨 Integración Frontend (Pendiente)

Para mostrar el estado en las páginas de producto, usa los métodos del modelo:

```django
{% if producto.tiene_stock %}
    <button>Agregar al carrito</button>
{% elif producto.bajo_pedido %}
    <button>Hacer pedido - Sin stock</button>
    <p class="text-warning">⚠️ Este producto está bajo pedido</p>
{% else %}
    <button disabled>No disponible</button>
{% endif %}
```

O usando el método `estado_stock()`:

```django
{% if producto.estado_stock == 'disponible' %}
    <span class="badge bg-success">Disponible</span>
{% elif producto.estado_stock == 'bajo_pedido' %}
    <span class="badge bg-warning">Bajo pedido</span>
{% else %}
    <span class="badge bg-danger">Sin stock</span>
{% endif %}
```

---

## 📊 Logs del Sistema

El sistema genera logs informativos:

```
📦 Verificando stock de 'Vestido Floral': 0 unidades
🗑️ Eliminando producto 'Vestido Floral' - Stock: 0, Bajo pedido: No
```

```
📦 Verificando stock de 'Blusa Premium': 0 unidades
✅ Producto 'Blusa Premium' sin stock pero marcado como 'bajo pedido' - Se mantiene visible
```

---

## ⚠️ Notas Importantes

1. **La eliminación es PERMANENTE**: Cuando un producto se elimina por falta de stock, se borra de la base de datos junto con sus imágenes y variantes.

2. **Recomendación**: Para productos que pueden volver a tener stock en el futuro, **activa "Bajo pedido"** en lugar de dejar que se eliminen.

3. **Alternativa**: Si no quieres eliminar productos pero tampoco mostrarlos, puedes usar el campo `activo = False` en lugar del sistema de eliminación automática.

4. **Productos sin variantes**: Si un producto no tiene variantes, el cálculo de stock será 0, por lo que se eliminará automáticamente (a menos que tenga `bajo_pedido = True`).

---

## 🔄 Testing

Para probar la funcionalidad:

1. Crea un producto con stock bajo
2. NO marques "bajo pedido"
3. Reduce el stock a 0 en todas las variantes
4. **Resultado**: El producto desaparece del admin

5. Crea otro producto con stock bajo
6. SÍ marca "bajo pedido"
7. Reduce el stock a 0
8. **Resultado**: El producto permanece visible

---

**Fecha de implementación**: 19 de enero de 2026
**Versión**: 1.0
