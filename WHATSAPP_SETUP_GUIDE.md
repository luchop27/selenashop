# 📱 CONFIGURACIÓN DE WHATSAPP BUSINESS API

## 🎯 Objetivo
Enviar notificaciones automáticas al WhatsApp del admin cuando se realiza un pedido, incluyendo todos los detalles del cliente y los productos solicitados.

---

## 📋 Requisitos Previos

### 1. **Cuenta de Meta/Facebook**
   - Necesitas tener una cuenta de Meta (facebook.com)
   - Si no la tienes, crea una en https://www.facebook.com

### 2. **WhatsApp Business Account**
   - Accede a https://developers.facebook.com/
   - Crea una App o usa una existente
   - Activa la funcionalidad "WhatsApp" en tu app

---

## 🔧 PASOS PARA CONFIGURAR

### PASO 1: Crear/Acceder a la App en Meta

1. Ir a https://developers.facebook.com/apps
2. Click en "Crear App" o seleccionar app existente
3. Seleccionar como tipo: "Comercio" o "Utilidad"
4. Click en "Siguiente"

### PASO 2: Agregar WhatsApp a tu App

1. En el dashboard de la app, buscar "WhatsApp"
2. Click en "Configurar" o "Agregar producto"
3. Seleccionar "WhatsApp"

### PASO 3: Obtener Credenciales

#### **A. Access Token**
1. En el panel de WhatsApp, ir a "Tokens y IDs de campaña"
2. Click en "Generar Token"
3. Seleccionar los permisos necesarios:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
4. Copiar el token y guardarlo en un lugar seguro

#### **B. Phone Number ID**
1. En "Números de teléfono", buscar tu número de WhatsApp Business
2. Copiar el "ID del número de teléfono" (Phone Number ID)

#### **C. Business Account ID**
1. En "Configuración", buscar "ID de cuenta de empresa" (Business Account ID)
2. Copiar este ID

### PASO 4: Validar Números de Teléfono

1. En la sección "Números de teléfono", agregar el número del admin:
   - Ejemplo: +593979607739 (formato internacional)
2. WhatsApp enviará un código de verificación
3. Confirmar el código en la app de WhatsApp del teléfono

---

## 🔑 VARIABLES DE CONFIGURACIÓN

Actualizar el archivo `selenashop/settings.py`:

```python
# ==================== CONFIGURACIÓN WHATSAPP BUSINESS API (META) ====================

WHATSAPP_ACCESS_TOKEN = 'TU_ACCESS_TOKEN_AQUI'
WHATSAPP_PHONE_NUMBER_ID = 'TU_PHONE_NUMBER_ID_AQUI'
WHATSAPP_BUSINESS_ACCOUNT_ID = 'TU_BUSINESS_ACCOUNT_ID_AQUI'
WHATSAPP_ADMIN_NUMBER = '593979607739'  # Número en formato internacional, sin +
```

### ⚠️ OPCIONES DE SEGURIDAD

#### **Opción 1: Variables de Entorno (RECOMENDADO)**

1. Crear archivo `.env` en la raíz del proyecto:
   ```
   WHATSAPP_ACCESS_TOKEN=tu_token_aqui
   WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id_aqui
   WHATSAPP_BUSINESS_ACCOUNT_ID=tu_business_account_id_aqui
   WHATSAPP_ADMIN_NUMBER=593979607739
   ```

2. Instalar `python-dotenv`:
   ```bash
   pip install python-dotenv
   ```

3. En `settings.py`, importar al inicio:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   # Luego usar:
   WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
   WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
   WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
   WHATSAPP_ADMIN_NUMBER = os.getenv('WHATSAPP_ADMIN_NUMBER', '593979607739')
   ```

#### **Opción 2: Directamente en settings.py**

```python
WHATSAPP_ACCESS_TOKEN = 'TU_ACCESS_TOKEN_AQUI'
WHATSAPP_PHONE_NUMBER_ID = 'TU_PHONE_NUMBER_ID_AQUI'
WHATSAPP_BUSINESS_ACCOUNT_ID = 'TU_BUSINESS_ACCOUNT_ID_AQUI'
WHATSAPP_ADMIN_NUMBER = '593979607739'
```

⚠️ **NO HACER COMMIT** de credenciales reales en Git. Usar `.env` o archivo `.gitignore`.

---

## 📁 ARCHIVOS INVOLUCRADOS

### 1. **core/whatsapp.py** (NUEVO)
   - Clase `WhatsAppAPI`: Maneja comunicación con API de Meta
   - Función `enviar_notificacion_pedido()`: Envía notificación cuando se crea un pedido
   - Método `_formatear_mensaje_pedido()`: Formatea el mensaje con emojis

### 2. **core/views.py** (MODIFICADO)
   - Función `checkout_process()`: Integra envío de WhatsApp al crear pedido
   - Prepara datos del pedido para el mensaje

### 3. **selenashop/settings.py** (MODIFICADO)
   - Variables de configuración de WhatsApp

### 4. **requirements.txt** (MODIFICADO)
   - Agregado: `requests==2.31.0` (para hacer peticiones HTTP a la API)

---

## 🧪 PRUEBAS

### Test 1: Verificar Credenciales

```python
from core.whatsapp import WhatsAppAPI
from django.conf import settings

api = WhatsAppAPI()
print(f"Token configurado: {bool(api.access_token)}")
print(f"Phone Number ID: {bool(api.phone_number_id)}")
print(f"Business Account ID: {bool(api.business_account_id)}")
```

### Test 2: Enviar Mensaje de Prueba

```python
from core.whatsapp import WhatsAppAPI

api = WhatsAppAPI()
resultado = api._enviar_mensaje_texto(
    '593979607739',  # Número del admin
    'Prueba de WhatsApp desde Vórtice Ecuador'
)
print(resultado)
```

### Test 3: Realizar Pedido de Prueba

1. Acceder a http://localhost:8000/checkout/
2. Completar formulario con datos de prueba
3. Click en "Realizar Pedido"
4. Verificar que el mensaje llegue al WhatsApp del admin

---

## 📊 FORMATO DEL MENSAJE

```
✨ *Pedido ORD-20240103-ABCD - Vórtice Ecuador* ✨
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
   🔸 Cantidad: 1
   🔸 Precio unitario: $35.00
   🔸 Subtotal: $35.00

--------------------------------------
💰 *Resumen del pedido:*
🛍️ Subtotal: $35.00
🎁 Envoltura de regalo: $5.00
🚚 Costo de envío: $5.00
✅ *Total a pagar: $45.00*
--------------------------------------

¡Gracias! 😊

🛍️ *Vórtice Ecuador - Moda con estilo*
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Crear cuenta Meta/Facebook
- [ ] Crear App en Meta
- [ ] Activar WhatsApp en la app
- [ ] Obtener Access Token
- [ ] Obtener Phone Number ID
- [ ] Obtener Business Account ID
- [ ] Validar número de teléfono del admin
- [ ] Actualizar `settings.py` con credenciales
- [ ] Instalar `requests` (pip install requests)
- [ ] Realizar pedido de prueba
- [ ] Verificar que el mensaje llega por WhatsApp
- [ ] Revisar logs en Django si hay errores

---

## 🐛 TROUBLESHOOTING

### Error: "WhatsApp API credentials no configuradas"
**Causa**: Las credenciales no están configuradas en settings.py
**Solución**: Revisar que `WHATSAPP_ACCESS_TOKEN` no esté vacío

### Error: "401 Unauthorized"
**Causa**: El Access Token es inválido o expiró
**Solución**: Generar un nuevo token en Meta

### Error: "Invalid recipient"
**Causa**: El número de teléfono no está registrado en WhatsApp Business
**Solución**: Validar el número en la consola de Meta

### El mensaje no llega
**Causa**: Posibles razones:
1. Número no validado en WhatsApp Business
2. Credenciales incorrectas
3. Error de red/conectividad
**Solución**: 
- Revisar logs en Django: `python manage.py runserver`
- Validar número en Meta
- Verificar conexión a internet

---

## 🔗 REFERENCIAS

- **Meta Developers**: https://developers.facebook.com/
- **WhatsApp Business API Docs**: https://developers.facebook.com/docs/whatsapp/cloud-api/reference
- **Guía de Setup**: https://developers.facebook.com/docs/whatsapp/cloud-api/get-started

---

## 📝 NOTAS

- Los mensajes se envían **de forma asíncrona** (no bloquean el proceso de pedido)
- Si falla el envío, el pedido se crea igual y se registra el error en logs
- Se puede configurar un número diferente para producción vs desarrollo
- El API tiene límite de mensajes, consultar plan de Meta

---

**Última actualización**: 8 de Diciembre 2024
**Versión**: 1.0
