# 📱 Configuración WhatsApp Business API de Meta

Este documento te guía paso a paso para configurar la integración de WhatsApp Business API en tu tienda.

## 🎯 Objetivo

Cuando un cliente realiza un pedido en el checkout, se envía automáticamente una notificación a WhatsApp del administrador con:
- Datos del cliente (nombre, email, teléfono, dirección)
- Detalles del pedido (productos, cantidades, precios)
- Total a pagar
- Método de pago

## 📋 Requisitos Previos

1. **Cuenta de Meta Business** (Facebook/Instagram)
2. **Número de teléfono verificado** para WhatsApp Business
3. Acceso a [Meta Business Console](https://business.facebook.com)

## 🔑 Paso 1: Obtener las Credenciales

### 1.1 Obtener el Phone Number ID

1. Ve a [Meta Business Console](https://business.facebook.com)
2. Navega a **Herramientas** → **WhatsApp Manager**
3. Selecciona tu número de teléfono
4. En la esquina superior derecha, verás un ícono de información ⓘ
5. Copia el **Phone Number ID** (ejemplo: `120212345678901234`)

### 1.2 Obtener el Business Account ID

1. En [Meta Business Console](https://business.facebook.com)
2. Ve a **Configuración** → **Información de la cuenta**
3. Copia el **Business Account ID** (ejemplo: `1234567890`)

### 1.3 Obtener el Access Token

1. Ve a [Meta Developers](https://developers.facebook.com)
2. Inicia sesión con tu cuenta de Meta
3. Selecciona tu **Aplicación** en el lado izquierdo
4. Navega a **Herramientas** → **Explorador de API Graph**
5. En el dropdown de tokens (arriba a la derecha), selecciona **Generar Token de Acceso**
6. Asegúrate de que tenga los permisos:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
7. Copia el token (ejemplo: `EAABBbBBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

> ⚠️ **IMPORTANTE**: Este token es sensible. Nunca lo compartas ni lo subas a GitHub.

### 1.4 Número del Admin

El número debe estar en formato internacional con el código de país:
- **Ecuador**: `+593979607739`
- **Colombia**: `+573001234567`
- **Argentina**: `+541123456789`

## ⚙️ Paso 2: Configurar Django

1. Abre `selenashop/settings.py`

2. Busca la sección `# ==================== CONFIGURACIÓN META WHATSAPP BUSINESS API ====================`

3. Reemplaza los valores:

```python
# ==================== CONFIGURACIÓN META WHATSAPP BUSINESS API ====================
WHATSAPP_PHONE_NUMBER_ID = '120212345678901234'  # Tu Phone Number ID
WHATSAPP_BUSINESS_ACCOUNT_ID = '1234567890'  # Tu Business Account ID
WHATSAPP_ACCESS_TOKEN = 'EAABBbBBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'  # Tu Access Token
WHATSAPP_ADMIN_NUMBER = '+593979607739'  # Número del admin (formato internacional)
WHATSAPP_API_URL = 'https://graph.instagram.com/v18.0'  # No cambiar
```

## 🔒 Seguridad: Usar Variables de Entorno (Recomendado)

Para desarrollo en producción, es **MEJOR** usar variables de entorno en lugar de hardcodear los tokens:

### Opción A: Archivo `.env` (Desarrollo Local)

1. Crea un archivo `.env` en la raíz del proyecto:

```bash
WHATSAPP_PHONE_NUMBER_ID=120212345678901234
WHATSAPP_BUSINESS_ACCOUNT_ID=1234567890
WHATSAPP_ACCESS_TOKEN=EAABBbBBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_ADMIN_NUMBER=+593979607739
```

2. Instala `python-decouple`:

```bash
pip install python-decouple
```

3. En `settings.py`, reemplaza el código:

```python
from decouple import config

WHATSAPP_PHONE_NUMBER_ID = config('WHATSAPP_PHONE_NUMBER_ID', default='')
WHATSAPP_BUSINESS_ACCOUNT_ID = config('WHATSAPP_BUSINESS_ACCOUNT_ID', default='')
WHATSAPP_ACCESS_TOKEN = config('WHATSAPP_ACCESS_TOKEN', default='')
WHATSAPP_ADMIN_NUMBER = config('WHATSAPP_ADMIN_NUMBER', default='+593979607739')
WHATSAPP_API_URL = 'https://graph.instagram.com/v18.0'
```

### Opción B: Variables de Entorno del Sistema

En Windows (PowerShell):
```powershell
$env:WHATSAPP_PHONE_NUMBER_ID = "120212345678901234"
$env:WHATSAPP_ACCESS_TOKEN = "EAABBbBBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

En Linux/Mac:
```bash
export WHATSAPP_PHONE_NUMBER_ID="120212345678901234"
export WHATSAPP_ACCESS_TOKEN="EAABBbBBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## ✅ Paso 3: Verificar que la Configuración Funciona

1. Abre Django Shell:

```bash
python manage.py shell
```

2. Verifica las credenciales:

```python
from django.conf import settings

print(f"Phone ID: {settings.WHATSAPP_PHONE_NUMBER_ID}")
print(f"Token: {settings.WHATSAPP_ACCESS_TOKEN[:20]}...")
print(f"Admin Number: {settings.WHATSAPP_ADMIN_NUMBER}")
```

3. Prueba el envío de un mensaje:

```python
from core.whatsapp_utils import enviar_mensaje_whatsapp

resultado = enviar_mensaje_whatsapp(
    '+593979607739',
    'Hola, este es un mensaje de prueba desde Django ✨'
)

print(resultado)
```

Si ves `'success': True`, ¡está configurado correctamente! ✅

## 🧪 Paso 4: Probar el Flujo Completo

1. Inicia el servidor: `python manage.py runserver`
2. Ve a http://127.0.0.1:8000/
3. Agrega un producto al carrito
4. Ve al checkout
5. Llena los datos y presiona "Realizar Pedido"
6. Deberías recibir un mensaje en WhatsApp del admin

## 🔧 Solución de Problemas

### ❌ "Credenciales de WhatsApp no configuradas"

- Verifica que los valores en `settings.py` no sean vacíos
- Asegúrate de haber reemplazado los valores de ejemplo

### ❌ "Error 401 - Unauthorized"

- El Access Token está expirado o es inválido
- Genera uno nuevo en [Meta Developers](https://developers.facebook.com)

### ❌ "Error 400 - Bad Request"

- El número de teléfono no está en formato internacional (`+` al inicio)
- Verifica que `WHATSAPP_ADMIN_NUMBER` tenga el formato correcto

### ❌ El mensaje no llega

- Asegúrate de haber iniciado una conversación previa con el admin desde WhatsApp
- La API de Meta requiere que el admin haya abierto una conversación
- Espera 24 horas después de registrar el número

### ✅ Ver logs del servidor

En la consola de Django, verás mensajes como:

```
✅ WhatsApp: Mensaje enviado exitosamente. ID: wamid.xxxx
```

o

```
❌ WhatsApp: Error 401. Token inválido
```

## 📚 Referencias Útiles

- [Documentación Oficial de WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api/)
- [Guía de Autenticación](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/)
- [Referencia de API](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/)

## 🚀 Próximos Pasos

Después de configurar WhatsApp, puedes:

1. **Personalizar el mensaje** en `core/whatsapp_utils.py` función `formatear_mensaje_pedido()`
2. **Agregar confirmación de lectura** en el admin
3. **Enviar múltiples mensajes** a diferentes administradores
4. **Agregar actualizaciones de estado** del pedido por WhatsApp

---

**¿Preguntas o problemas?** Revisa los logs de Django con:

```bash
tail -f logs/django.log
```
