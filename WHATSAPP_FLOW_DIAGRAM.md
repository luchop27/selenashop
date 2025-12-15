# 📊 DIAGRAMA DEL FLUJO - INTEGRACIÓN WHATSAPP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USUARIO EN EL NAVEGADOR                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    (1) Cliente llena CHECKOUT
                     Nombre, Dirección, Ciudad
                          Carrito con productos
                                    ↓
                    (2) Presiona "REALIZAR PEDIDO"
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BACKEND - DJANGO (views.py)                          │
│                                                                              │
│  checkout_process() {                                                       │
│    ✅ Valida formulario                                                     │
│    ✅ Obtiene datos: first_name, last_name, city, email, phone, etc        │
│    ✅ Calcula totales: subtotal + envío - descuento                         │
│    ✅ Crea el Pedido en BD                                                  │
│    ✅ Crea DetallePedido para cada producto                                 │
│    ✅ Limpia carrito                                                        │
│                                                                              │
│    🆕 ───────────────────────────────────────────────────────────────────  │
│    📱 ENVÍA NOTIFICACIÓN A WHATSAPP (NUEVO)                                │
│    🆕 ───────────────────────────────────────────────────────────────────  │
│                                                                              │
│    from core.whatsapp_utils import enviar_notificacion_pedido               │
│    resultado = enviar_notificacion_pedido(pedido)                           │
│                                                                              │
│    if resultado['success']:                                                 │
│      → Envió correctamente a WhatsApp del Admin                            │
│    else:                                                                    │
│      → No pudo enviar (token inválido, etc)                                │
│                                                                              │
│    ✅ Muestra mensaje de éxito                                              │
│    ✅ Redirige a order-confirmation.html                                    │
│  }                                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                   WHATSAPP_UTILS.PY (Archivo Nuevo)                         │
│                                                                              │
│  enviar_notificacion_pedido(pedido) {                                       │
│    ① Verifica credenciales configuradas                                     │
│    ② Llama a formatear_mensaje_pedido()                                     │
│    ③ Llama a enviar_mensaje_whatsapp()                                      │
│    ④ Retorna resultado {'success': True/False}                              │
│  }                                                                           │
│                                                                              │
│  formatear_mensaje_pedido(pedido) {                                         │
│    Crea un mensaje con:                                                     │
│    ✨ Número de pedido                                                      │
│    👤 Datos del cliente (nombre, email, teléfono, dirección)               │
│    📦 Detalles del pedido (productos, cantidades, precios)                 │
│    💰 Resumen (subtotal, envío, descuento, total)                          │
│    💳 Método de pago                                                        │
│  }                                                                           │
│                                                                              │
│  enviar_mensaje_whatsapp(numero, mensaje) {                                 │
│    ① Construye URL del endpoint Meta API                                    │
│    ② Prepara headers con Access Token                                       │
│    ③ Construye payload JSON con el mensaje                                  │
│    ④ Hace POST request a Meta API                                           │
│    ⑤ Retorna resultado o error                                              │
│  }                                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    META WHATSAPP BUSINESS API                               │
│                                                                              │
│  POST /v18.0/{PHONE_NUMBER_ID}/messages                                     │
│  {                                                                           │
│    "messaging_product": "whatsapp",                                         │
│    "recipient_type": "individual",                                          │
│    "to": "+593979607739",                                                   │
│    "type": "text",                                                          │
│    "text": {                                                                │
│      "body": "✨ *NUEVO PEDIDO #ORD-20250214-ABCD* ✨..."                   │
│    }                                                                         │
│  }                                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ADMINISTRADOR EN WHATSAPP MOBILE                          │
│                                                                              │
│  ┌─────────────────────────────────────────┐                               │
│  │ ✨ *NUEVO PEDIDO #ORD-20250214-ABCD* ✨ │                               │
│  │ ────────────────────────────────────────│                               │
│  │ 👤 Nombre: Luis Alberto Vasquez Gomez  │                               │
│  │ 📧 Correo: xkrules@gmail.com            │                               │
│  │ 📱 Teléfono: 0979607739                 │                               │
│  │ 🏠 Dirección: Calle Principal 123       │                               │
│  │                                         │                               │
│  │ 📦 DETALLES:                            │                               │
│  │ 🔹 Camiseta V-N002                      │                               │
│  │    • Cantidad: 1                        │                               │
│  │    • Precio: $35.00                     │                               │
│  │                                         │                               │
│  │ 💰 RESUMEN:                             │                               │
│  │ 🛍️ Subtotal: $35.00                    │                               │
│  │ 🚚 Envío: $5.00                        │                               │
│  │ ✅ TOTAL: $40.00                       │                               │
│  │                                         │                               │
│  │ 💳 Pago: Transferencia Bancaria         │                               │
│  └─────────────────────────────────────────┘                               │
│                                                                              │
│  El admin puede responder directamente desde WhatsApp                       │
│  (confirmación, aclaraciones, etc.)                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 SECUENCIA DE EVENTOS

```
TIEMPO    EVENTO                              UBICACIÓN
──────────────────────────────────────────────────────────────────
T=0:00    Cliente presiona "Realizar Pedido"  Navegador (Frontend)
T=0:01    Django recibe POST /checkout        Backend (Django)
T=0:02    Valida y crea Pedido BD             core/views.py
T=0:03    Llama enviar_notificacion_pedido()  core/whatsapp_utils.py
T=0:04    Construye URL de Meta API           core/whatsapp_utils.py
T=0:05    POST request a Meta WhatsApp API    Servidor → Meta (HTTPS)
T=0:10    Meta API responde ✅                Meta → Servidor
T=0:15    Mensaje llega a WhatsApp del Admin  Admin recibe mensaje
T=0:16    Redirige a order-confirmation       Backend → Frontend
T=0:17    Usuario ve "Pedido #ORD-xxx"       Navegador (Frontend)
```

## 📁 ARCHIVOS MODIFICADOS

### 1. selenashop/settings.py
```python
# Línea ~180: Agregadas estas variables
WHATSAPP_PHONE_NUMBER_ID = 'YOUR_PHONE_NUMBER_ID'
WHATSAPP_BUSINESS_ACCOUNT_ID = 'YOUR_BUSINESS_ACCOUNT_ID'
WHATSAPP_ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
WHATSAPP_ADMIN_NUMBER = '+593979607739'
WHATSAPP_API_URL = 'https://graph.instagram.com/v18.0'
```

### 2. core/views.py (checkout_process)
```python
# Antes: Solo creaba el pedido
# Ahora: También envía a WhatsApp

from .whatsapp_utils import enviar_notificacion_pedido
resultado = enviar_notificacion_pedido(pedido)
```

### 3. core/whatsapp_utils.py (NUEVO ARCHIVO)
```python
- enviar_notificacion_pedido(pedido)
- formatear_mensaje_pedido(pedido)
- enviar_mensaje_whatsapp(numero, mensaje)
- generar_link_whatsapp_web(numero, mensaje)
```

## ✅ FLUJO SIN CAMBIOS

El checkout, formulario y validación **NO CAMBIARON**.
Solo agregamos la notificación automática **DESPUÉS** de crear el pedido.

## 🧪 PRUEBAS

```bash
# Test 1: Verificar credenciales
python test_whatsapp.py

# Test 2: Hacer un pedido real
# 1. Ve a http://127.0.0.1:8000
# 2. Agrega un producto al carrito
# 3. Completa el checkout
# 4. Presiona "Realizar Pedido"
# 5. Verifica que recibes el mensaje en WhatsApp

# Test 3: Ver logs
# En la consola del servidor Django, verás:
# ✅ WhatsApp: Mensaje enviado exitosamente. ID: wamid.xxx
```
