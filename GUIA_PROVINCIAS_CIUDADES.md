# 📝 GUÍA: REGISTRO CON PROVINCIAS Y CIUDADES DINÁMICAS

## ✅ CAMBIOS REALIZADOS

### 1. **Modelos de Base de Datos**
   - ✅ **Nuevo modelo `Provincia`**: Almacena todas las provincias del Ecuador
   - ✅ **Modelo `Ciudad` actualizado**: Ahora usa ForeignKey a Provincia
   - ✅ **Modelo `Usuario` actualizado**: Agregar ForeignKey a Provincia

### 2. **Formulario de Registro (register.html)**
   - ✅ **Combobox 1**: Seleccionar Provincia
   - ✅ **Combobox 2**: Seleccionar Ciudad (se filtra por provincia seleccionada)
   - ✅ **JavaScript AJAX**: Carga ciudades dinámicamente sin recargar la página

### 3. **Vista de Registro (registrar_usuario)**
   - ✅ Procesa provincia
   - ✅ Procesa ciudad
   - ✅ Valida ambos campos
   - ✅ Guarda correctamente en BD

### 4. **API AJAX**
   - ✅ Nueva vista: `api_ciudades_por_provincia/<provincia_id>/`
   - ✅ Retorna JSON con ciudades de una provincia

### 5. **Admin Django**
   - ✅ Nuevo admin: `ProvinciaAdmin`
   - ✅ Actualizado: `CiudadAdmin`
   - ✅ Actualizado: `UsuarioAdmin`

---

## 🚀 PASOS PARA EJECUTAR

### OPCIÓN 1 (RECOMENDADA - Una sola línea):
```bash
python setup_provincias_ciudades_auto.py
```

Esto automáticamente:
- Ejecuta las migraciones
- Puebla todas las provincias y ciudades
- Verifica que todo esté correcto

### OPCIÓN 2 (Manual paso a paso):
```bash
# Paso 1: Ejecutar migraciones
python manage.py migrate

# Paso 2: Abrir shell
python manage.py shell

# Paso 3: Ejecutar el script de población
exec(open('setup_provincias_ciudades.py').read())

# Paso 4: Salir del shell
exit()
```

---

## ✨ CÓMO FUNCIONA

### En el formulario de registro:
1. Usuario selecciona **Provincia** en el primer combobox
2. Al cambiar provincia, se dispara un evento AJAX
3. Se obtienen las ciudades de esa provincia desde el servidor
4. El segundo combobox se llena automáticamente con esas ciudades
5. Usuario selecciona una **Ciudad**
6. Se envía el formulario

```
Provincia (Combobox)
       ↓
    AJAX (/api/ciudades-por-provincia/1/)
       ↓
    Retorna JSON: {ciudades: [{id: 1, nombre: "Cuenca"}, ...]}
       ↓
Ciudad (Combobox) ← Se llena dinámicamente
```

---

## 📋 ESTRUCTURA DE LA BASE DE DATOS

### Tabla: `usuarios_provincia`
```
id       INTEGER PRIMARY KEY
nombre   VARCHAR(100) UNIQUE
codigo   VARCHAR(10)
activa   BOOLEAN
```

### Tabla: `usuarios_ciudad`
```
id           INTEGER PRIMARY KEY
nombre       VARCHAR(100)
provincia_id INTEGER FOREIGN KEY
codigo_postal VARCHAR(10)
activa       BOOLEAN
unique (nombre, provincia_id)
```

### Tabla: `usuarios_usuario` (modificada)
```
provincia_id INTEGER FOREIGN KEY (nullable)
ciudad_id    INTEGER FOREIGN KEY (nullable)
```

---

## 🌍 PROVINCIAS Y CIUDADES INCLUIDAS

Se incluyen las 22 provincias del Ecuador con ~100 ciudades principales:

- **Azuay**: Cuenca, Gualaceo, Paute, Sígsig, Chordeleg
- **Bolívar**: Guaranda, Caluma, Chillanes, Echeandía, San Miguel
- **Cañar**: Azogues, La Troncal, Cañar, El Tambo, Biblián
- **Carchi**: Tulcán, San Gabriel, Espejo, Montúfar, Huaca
- **Chimborazo**: Riobamba, Latacunga, Penipe, Guamote, Cumandá
- **Cotopaxi**: Latacunga, La Maná, Pangua, Salcedo, Pujilí
- **El Oro**: Machala, Santa Rosa, Huaquillas, Pasaje, Piñas
- **Esmeraldas**: Esmeraldas, Atacames, Muisne, Quinindé, San Lorenzo
- **Guayas**: Guayaquil, Durán, Milagro, Daule, Samborondón, Balzar
- **Imbabura**: Ibarra, Otavalo, Antonio Ante, Cotacachi, Urcuquí
- **Loja**: Loja, Catamayo, Macará, Vilcabamba, Saraguro
- **Los Ríos**: Babahoyo, Quevedo, Vinces, Baba, Mocache
- **Manabí**: Manta, Portoviejo, Jipijapa, El Carmen, Chone, Bahía de Caráquez
- **Morona Santiago**: Macas, Sucúa, Palora, Tena, Puyo
- **Napo**: Tena, Archidona, Puerto Misahuallí, Puyo, Quijos
- **Pastaza**: Puyo, Mera, Santa Clara, Arajuno, Shell
- **Pichincha**: Quito, Cayambe, Machachi, Sangolquí, Latacunga, Puembo
- **Santa Elena**: Santa Elena, La Libertad, Salinas, Olón, Manglaralto
- **Santo Domingo**: Santo Domingo
- **Sucumbíos**: Nueva Loja, Lago Agrio, Cascales, Putumayo, Cuyabeno
- **Tungurahua**: Ambato, Baños, Latacunga, Pelileo, Píllaro
- **Orellana**: Puerto Francisco de Orellana, Coca, Joya de los Sachas, Loreto

---

## 🔍 VERIFICACIÓN EN EL ADMIN

1. Accede a `http://localhost:8000/admin/`
2. En "Usuarios":
   - Haz clic en "Provincias" → Ver ~22 provincias
   - Haz clic en "Ciudades" → Ver ~100 ciudades
   - Haz clic en un Usuario → Ver campos provincia y ciudad

---

## 📝 FORMULARIO ACTUALIZADO

| Campo | Tipo | Obligatorio | Comportamiento |
|-------|------|-------------|-----------------|
| Nombre | Text | No | - |
| Apellido | Text | No | - |
| Email | Email | **Sí** | Único |
| Teléfono | Tel | No | Max 20 caracteres |
| **Provincia** | **Select** | **No** | **Dispara AJAX al cambiar** |
| **Ciudad** | **Select** | **No** | **Se llena dinámicamente** |
| Contraseña | Password | **Sí** | Min 6 caracteres |
| Confirmar | Password | **Sí** | Debe coincidir |

---

## 🛠️ ARCHIVOS MODIFICADOS/CREADOS

### Modificados:
- `apps/usuarios/models.py` (agregado Provincia, modificado Ciudad y Usuario)
- `apps/usuarios/views.py` (nuevas vistas y helpers)
- `apps/usuarios/urls.py` (nueva ruta de API)
- `apps/usuarios/admin.py` (nuevo ProvinciaAdmin)
- `templates/register.html` (nuevos combobox y JavaScript AJAX)

### Nuevos:
- `apps/usuarios/migrations/0003_provincia_ciudades.py`
- `setup_provincias_ciudades_auto.py` ⭐ (automático)
- `setup_provincias_ciudades.py` (manual)

---

## ⚙️ JAVASCRIPT AJAX

El formulario incluye JavaScript que:
1. Escucha cambios en el select de Provincia
2. Obtiene el ID de la provincia seleccionada
3. Hace una petición AJAX a `/api/ciudades-por-provincia/<id>/`
4. Recibe JSON con las ciudades
5. Llena el select de Ciudad dinámicamente

```javascript
function cargarCiudades() {
    const provinciaId = document.getElementById('provincia').value;
    
    if (provinciaId) {
        fetch(`/api/ciudades-por-provincia/${provinciaId}/`)
            .then(response => response.json())
            .then(data => {
                // Llenar select de ciudades
                data.ciudades.forEach(ciudad => {
                    // crear opciones...
                });
            });
    }
}
```

---

## 🔒 VALIDACIONES

- Email: Único en BD, obligatorio
- Contraseña: Mínimo 6 caracteres, obligatorio
- Provincia: Opcional, solo acepta provincias activas
- Ciudad: Opcional, solo acepta ciudades activas de la provincia seleccionada
- Teléfono: Opcional, máximo 20 caracteres

---

## 📊 EJEMPLO DE FLUJO

```
Usuario accede a /register/
↓
Ve formulario con 2 combobox vacíos (selecciona provincia)
↓
Selecciona "Pichincha" en provincia
↓
JavaScript detecta cambio → Dispara AJAX
↓
API retorna: {ciudades: [
    {id: 1, nombre: "Quito"},
    {id: 2, nombre: "Cayambe"},
    {id: 3, nombre: "Machachi"},
    ...
]}
↓
Combobox de ciudad se llena automáticamente
↓
Usuario selecciona "Quito"
↓
Usuario completa otros datos y envía formulario
↓
Se guarda: provincia=Pichincha, ciudad=Quito
```

---

## 🚀 PRÓXIMOS PASOS

1. Ejecuta: `python setup_provincias_ciudades_auto.py`
2. Reinicia Django: `python manage.py runserver`
3. Ve a: `http://localhost:8000/register/`
4. Prueba seleccionar una provincia y verifica que aparecen ciudades
5. Completa el registro y verifica en admin

¡Todo está listo para usar!
