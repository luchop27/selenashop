# 🔑 CÓMO OBTENER LAS CREDENCIALES DE META

## Resumen: Necesitas 3 Credenciales

```
1. ACCESS TOKEN          → El código para autenticarse
2. PHONE NUMBER ID       → El ID de tu número de WhatsApp
3. BUSINESS ACCOUNT ID   → El ID de tu cuenta de negocio
```

---

## 📋 PASO A PASO

### PASO 1: Acceder a Meta Developers

1. Abre tu navegador
2. Ve a: **https://developers.facebook.com/**
3. Haz click en **"Mis apps"** (arriba a la derecha)

   Si no tienes cuenta Meta:
   - Click en "Iniciar sesión"
   - Usa tu correo de Facebook o crea una cuenta

### PASO 2: Crear una App

Si es tu primera vez:

1. Click en **"Crear app"** (botón azul)
2. Selecciona tipo: **"Comercio"**
3. Click **"Siguiente"**
4. Completa:
   - Nombre: "Vórtice Ecuador" (o el que prefieras)
   - Email: Tu email
   - Propósito: "Notificaciones de pedidos"
5. Click **"Crear app"**

Si ya tienes una app:
- Simplemente selecciónala del listado

### PASO 3: Agregar WhatsApp a Tu App

1. En el dashboard, busca **"WhatsApp"**
2. Haz click en **"Configurar"** o **"Agregar producto"**
3. Sigue el asistente de setup (es automático)

Espera a que se configure (unos segundos)

### PASO 4: Obtener el ACCESS TOKEN ⭐

1. En la sección de WhatsApp, ve a: **"Configuración"** → **"Credenciales"**
2. Busca la sección: **"Tokens de acceso"**
3. Haz click en **"Generar token"**
4. Selecciona permisos (debería estar todo pre-seleccionado):
   - ✅ whatsapp_business_messaging
   - ✅ whatsapp_business_management
5. Haz click en **"Generar"**

**Se mostrará un token largo así:**

```
EAABsbCS1iHgBAOZCZBu2kP7PNZBz3nXmZA8ZBu2kP7...
```

**CÓPIALO Y GUÁRDALO** ← Este es tu ACCESS TOKEN

---

### PASO 5: Obtener el PHONE NUMBER ID

1. En la sección de WhatsApp, ve a: **"Números de teléfono"**
2. Busca tu número de WhatsApp Business
   
   Si no tienes uno:
   - Haz click en **"Agregar número"**
   - Sigue el proceso de verificación
   - WhatsApp te enviará un código a tu teléfono
   - Confirma el código

3. Cuando veas tu número en la lista, haz click en él
4. En los detalles, busca: **"ID del número de teléfono"**

**Se verá así:**

```
102345678901234
```

**CÓPIALO** ← Este es tu PHONE NUMBER ID

---

### PASO 6: Obtener el BUSINESS ACCOUNT ID

1. En la sección de WhatsApp, ve a: **"Configuración"**
2. En el menú lateral izquierdo, selecciona: **"Información"**
3. Busca: **"ID de cuenta de empresa"** o **"Business Account ID"**

**Se verá así:**

```
123456789012345
```

**CÓPIALO** ← Este es tu BUSINESS ACCOUNT ID

---

## ✅ Verificación: ¿Tienes los 3?

```
☐ ACCESS TOKEN:         EAABsbCS1iHgBAOZCZBu2...
☐ PHONE NUMBER ID:      102345678901234
☐ BUSINESS ACCOUNT ID:  123456789012345
```

Si tienes los 3, ¡continúa con el siguiente paso!

---

## 📝 PASO FINAL: Configurar en Tu Proyecto

Ahora que tienes las 3 credenciales:

1. Abre: `selenashop/settings.py`
2. Ve al **FINAL** del archivo
3. Busca:

```python
WHATSAPP_ACCESS_TOKEN = ''
WHATSAPP_PHONE_NUMBER_ID = ''
WHATSAPP_BUSINESS_ACCOUNT_ID = ''
```

4. Pega TUS credenciales:

```python
WHATSAPP_ACCESS_TOKEN = 'EAABsbCS1iHgBAOZCZBu2kP7PNZBz3nXmZA8...'
WHATSAPP_PHONE_NUMBER_ID = '102345678901234'
WHATSAPP_BUSINESS_ACCOUNT_ID = '123456789012345'
```

5. **GUARDA** el archivo (Ctrl+S)

6. ¡Listo! Ejecuta:

```bash
python test_whatsapp_complete.py
```

---

## 🎯 ¿Dónde Exactamente Buscar En Meta?

### Para ACCESS TOKEN:
```
Mis apps → Tu app → WhatsApp → Configuración → Credenciales → Generar token
```

### Para PHONE NUMBER ID:
```
Mis apps → Tu app → WhatsApp → Números de teléfono → (Haz click en tu número) → ID del número
```

### Para BUSINESS ACCOUNT ID:
```
Mis apps → Tu app → WhatsApp → Configuración → Información → ID de cuenta
```

---

## ⚠️ IMPORTANTE

### NO hagas esto:
❌ No compartas tus credenciales con nadie
❌ No las publiques en internet
❌ No las pongas en mensajes

### Haz esto:
✅ Guárdalas en un lugar seguro
✅ Si las expones, cámbialas inmediatamente en Meta
✅ En producción, usa variables de entorno

---

## 🆘 Problemas Comunes

### "No veo un botón de Generar token"
→ Asegúrate de estar en la sección correcta de WhatsApp
→ Recarga la página

### "El número de WhatsApp no aparece"
→ Ve a "Números de teléfono"
→ Haz click en "Agregar número"
→ Confirma el código que te envíe WhatsApp

### "No encuentro Business Account ID"
→ Ve a WhatsApp → Configuración → Información
→ Busca "ID de cuenta de empresa"

### "Recibo error al generar token"
→ Verifica que tienes permisos de admin en la app
→ Intenta refrescar la página
→ Si persiste, crea una nueva app

---

## 🎉 Resumen

1. ✅ Ve a https://developers.facebook.com/
2. ✅ Crea app (si no tienes)
3. ✅ Agrega WhatsApp
4. ✅ Copia 3 credenciales
5. ✅ Pégalas en settings.py
6. ✅ ¡Listo!

---

**Tiempo estimado**: 10-15 minutos
**Dificultad**: Fácil ⭐
