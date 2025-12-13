# ✨ NOTIFICACIONES POR WHATSAPP EN VÓRTICE ECUADOR

## 🎯 ¿QUÉ SE IMPLEMENTÓ?

Ahora cuando un cliente realiza un pedido en el checkout, automáticamente se envía un mensaje de WhatsApp al admin (número: 0979607739) con todos los detalles:

- ✅ Número de pedido
- ✅ Datos del cliente (nombre, email, teléfono, dirección)
- ✅ Productos solicitados (nombre, cantidad, precio)
- ✅ Resumen de costos (subtotal, envío, descuento, total)
- ✅ Ciudad de envío

**Todo con emojis bonitos** 🎨

---

## 🚀 CÓMO ACTIVARLO (3 PASOS)

### PASO 1️⃣: Obtener Credenciales de Meta

1. Ir a → **https://developers.facebook.com/**
2. Click en "Mis apps" → "Crear app"
3. Seleccionar tipo: "Comercio"
4. En la app, buscar "WhatsApp" y agregar el producto
5. Ir a "Configuración" → "Credenciales"
6. Copiar:
   - **Access Token** (el grande)
   - **Phone Number ID** (de tu número de WhatsApp)
   - **Business Account ID**

### PASO 2️⃣: Actualizar Configuración

Abrir archivo: `selenashop/settings.py`

Al final del archivo, encontrar esta sección (ya existe):

```python
# ==================== CONFIGURACIÓN WHATSAPP BUSINESS API (META) ====================

WHATSAPP_ACCESS_TOKEN = ''  # ← PEGAR AQUI
WHATSAPP_PHONE_NUMBER_ID = ''  # ← PEGAR AQUI
WHATSAPP_BUSINESS_ACCOUNT_ID = ''  # ← PEGAR AQUI
WHATSAPP_ADMIN_NUMBER = '593979607739'  # ← DEJA IGUAL
```

**Ejemplo completo:**
```python
WHATSAPP_ACCESS_TOKEN = 'EAABsbCS1iHgBAOZCZBu2kP7...'
WHATSAPP_PHONE_NUMBER_ID = '120242117...'
WHATSAPP_BUSINESS_ACCOUNT_ID = '1234567890...'
WHATSAPP_ADMIN_NUMBER = '593979607739'
```

### PASO 3️⃣: Guardar y Listo ✅

- Guardar el archivo
- No necesitas reiniciar Django
- ¡Sistema listo! Cuando se haga un pedido, automáticamente se envía el mensaje

---

## 🧪 PROBAR QUE TODO FUNCIONA

Ejecuta en terminal:

```bash
python test_whatsapp_integration.py
```

Deberías ver:
- ✅ Credenciales configuradas (si completaste PASO 2)
- 📱 Un ejemplo del mensaje que se enviará

---

## 📱 EJEMPLO DE MENSAJE

Cuando se realiza un pedido, el admin recibe algo así:

```
✨ *Pedido ORD-20240108-ABCD - Vórtice Ecuador* ✨
--------------------------------------
📋 *Datos del Cliente:*
👤 Nombre: Luis Alberto Vasquez Gomez
📧 Correo: xkrules.2005@gmail.com
📱 Teléfono: 0979607739
🏙️ Ciudad: Quito
🏠 Dirección: Kleber Franco
--------------------------------------
📦 *Detalles del pedido:*

🔹 *Camiseta V-N002*
   🔸 Talla: U
   🔸 Color: Rojo
   🔸 Cantidad: 1
   🔸 Precio unitario: $35.00
   🔸 Subtotal: $35.00

--------------------------------------
💰 *Resumen del pedido:*
🛍️ Subtotal: $35.00
🚚 Costo de envío: $5.00
✅ *Total a pagar: $40.00*
--------------------------------------

¡Gracias! 😊

🛍️ *Vórtice Ecuador - Moda con estilo*
```

---

## ⚠️ IMPORTANTE

### Seguridad de Credenciales

**NUNCA hacer commit de credenciales en Git.** Opciones:

#### Opción A: Usar archivo .env (RECOMENDADO)

1. Crear archivo `.env` en la raíz:
   ```
   WHATSAPP_ACCESS_TOKEN=tu_token_aqui
   WHATSAPP_PHONE_NUMBER_ID=tu_phone_id_aqui
   WHATSAPP_BUSINESS_ACCOUNT_ID=tu_business_id_aqui
   ```

2. Agregar `.env` a `.gitignore`

3. En `settings.py`:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
   WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
   WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
   ```

4. Instalar: `pip install python-dotenv`

---

## 🔧 ARCHIVOS MODIFICADOS/CREADOS

### Nuevos Archivos:
- ✅ `core/whatsapp.py` - Módulo de integración WhatsApp
- ✅ `WHATSAPP_SETUP_GUIDE.md` - Guía técnica detallada
- ✅ `test_whatsapp_integration.py` - Script de prueba

### Archivos Modificados:
- ✅ `core/views.py` - Integración en checkout_process()
- ✅ `selenashop/settings.py` - Configuración de credenciales
- ✅ `requirements.txt` - Agregado: requests==2.31.0

---

## 🐛 SOLUCIONAR PROBLEMAS

### El mensaje no llega

**Problema**: No aparece el mensaje en WhatsApp

**Causas posibles:**
1. Credenciales no configuradas
2. Credenciales incorrectas
3. Número de teléfono no validado en Meta

**Soluciones:**
- Ejecutar: `python test_whatsapp_integration.py`
- Revisar que WHATSAPP_ACCESS_TOKEN no esté vacío
- Validar número de teléfono en https://developers.facebook.com/

### Error "401 Unauthorized"

**Causa**: Token inválido o expiró

**Solución**: 
- Generar nuevo token en Meta
- Actualizar en settings.py

### Error "Invalid recipient"

**Causa**: El número no está registrado como WhatsApp Business

**Solución**:
- En Meta, validar el número
- Esperar confirmación de WhatsApp

---

## 📚 REFERENCIAS

- **Meta Developers**: https://developers.facebook.com/
- **Documentación WhatsApp API**: https://developers.facebook.com/docs/whatsapp/cloud-api

---

## ✅ CHECKLIST FINAL

- [ ] Credenciales obtenidas de Meta
- [ ] settings.py actualizado
- [ ] Script de prueba ejecutado exitosamente
- [ ] Primer pedido de prueba realizado
- [ ] Mensaje recibido en WhatsApp del admin
- [ ] Emojis se ven correctamente

---

**¡Sistema listo para notificar pedidos por WhatsApp! 🎉**
