# 🔑 GUÍA PASO A PASO: OBTENER CREDENCIALES DE META WHATSAPP

## 📱 Lo que necesitas:

- [ ] **Phone Number ID** (ejemplo: `120212345678901234`)
- [ ] **Business Account ID** (ejemplo: `1234567890`)
- [ ] **Access Token** (ejemplo: `EAABBbBBxxxxxxxx...`)
- [ ] **Número Admin** en formato internacional (ejemplo: `+593979607739`)

---

## 🟦 PARTE 1: OBTENER PHONE NUMBER ID

### Paso 1.1: Acceder a Meta Business Console

1. Abre [https://business.facebook.com](https://business.facebook.com)
2. Inicia sesión con tu cuenta de Meta/Facebook
3. En la barra lateral izquierda, busca **"WhatsApp Manager"** o **"WhatsApp"**
4. Haz clic para entrar al administrador de WhatsApp

> **Nota**: Si no ves WhatsApp Manager, primero debes:
> - Ir a Configuración → Aplicaciones
> - Conectar tu WhatsApp Business Account

### Paso 1.2: Encontrar el Phone Number ID

1. En WhatsApp Manager, ve a **"Números de teléfono"** o **"Phone Numbers"**
2. Selecciona el número de teléfono que registraste
3. Verás detalles como:
   - ✅ Número: +593979607739
   - ✅ **ID de número**: `120212345678901234` ← **ESTE ES EL QUE NECESITAS**
   - ✅ Estado: Verificado

4. **Copia este ID** (120212345678901234)

> 💡 **Consejo**: Si no aparece el ID directamente, busca el ícono ⓘ (información) en la esquina superior derecha de la pantalla.

---

## 🟦 PARTE 2: OBTENER BUSINESS ACCOUNT ID

### Paso 2.1: Ir a Configuración de la Cuenta

1. En Meta Business Console (arriba a la izquierda)
2. Haz clic en tu nombre o foto de perfil
3. Selecciona **"Configuración de la cuenta"** o **"Account Settings"**

### Paso 2.2: Buscar el Business Account ID

En la sección de Configuración, busca:

```
Información de la cuenta
├── ID de cuenta de negocio: 1234567890 ← ESTE
├── ID de dominio: ...
└── ...
```

**Copia este ID** (1234567890)

> 💡 **Alternativa**: Ve a https://business.facebook.com/settings/info y busca "Business ID"

---

## 🟦 PARTE 3: OBTENER ACCESS TOKEN

### Paso 3.1: Ir a Meta Developers

1. Abre [https://developers.facebook.com](https://developers.facebook.com)
2. Inicia sesión con tu cuenta (la misma de Meta Business)
3. En la barra superior, haz clic en tu perfil
4. Selecciona **"Mis aplicaciones"** o **"My Apps"**

### Paso 3.2: Seleccionar tu Aplicación

1. Si tienes una aplicación de WhatsApp, selecciónala
2. Si no, crea una:
   - Botón **"Crear aplicación"** o **"Create App"**
   - Nombre: "Vortice Ecuador Shop" (o similar)
   - Propósito: "Para negocios"
   - Continuar

### Paso 3.3: Generar Token de Acceso

1. En tu aplicación, ve a **"Herramientas"** → **"Explorador de API Graph"** (Graph API Explorer)

   O directamente: Haz clic en **"Configuración"** → **"Tokens de acceso"**

2. En el dropdown de **"Selecciona tu app"**, asegúrate de que tu app esté seleccionada

3. En el campo **"Token de acceso de usuario"**, haz clic en **"Generar token"**

4. **Selecciona los permisos necesarios**:
   - ✅ `whatsapp_business_messaging`
   - ✅ `whatsapp_business_management`
   - ✅ `business_management` (opcional pero recomendado)

5. Haz clic en **"Generar"**

6. Verás un token largo como:
   ```
   EAABBbBBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Paso 3.4: Copiar y Guardar el Token

**⚠️ IMPORTANTE**: 
- Este token es **SECRETO** - no lo compartas nunca
- Cópialo y guárdalo en un lugar seguro
- Tendrá una fecha de expiración
- Puedes generar nuevos tokens en cualquier momento

---

## 🟦 PARTE 4: NÚMERO DEL ADMINISTRADOR

El número debe estar en **formato internacional**.

### Ejemplos:

| País | Número Local | Número Internacional |
|------|--------------|----------------------|
| Ecuador | 0979607739 | **+593979607739** |
| Colombia | 3101234567 | **+573101234567** |
| Argentina | 1123456789 | **+541123456789** |
| México | 5551234567 | **+525551234567** |

**Formato correcto**:
- Comenzar con `+`
- Seguido del código de país
- Seguido del número sin el `0` inicial (si lo tiene)

---

## ✅ VERIFICAR TUS CREDENCIALES

Antes de configurar Django, verifica que tienes:

```
☐ Phone Number ID:        120212345678901234
☐ Business Account ID:    1234567890
☐ Access Token:           EAABBbBBxxxxxxxx...
☐ Admin Number:           +593979607739
```

---

## 🚨 PROBLEMAS COMUNES

### ❌ "No puedo encontrar Phone Number ID"

**Solución**:
1. Asegúrate de estar en **WhatsApp Manager** (no Facebook Manager)
2. Haz clic en el número de teléfono que registraste
3. Busca el ícono ⓘ en la esquina superior derecha
4. El ID estará en el panel que aparezca

### ❌ "El token generado no funciona"

**Solución**:
1. El token puede estar expirado (expiran después de cierto tiempo)
2. Genera uno nuevo en Developers
3. Asegúrate de incluir los permisos de `whatsapp_*`

### ❌ "No veo la opción de WhatsApp"

**Solución**:
1. Tienes que conectar tu WhatsApp Business Account primero
2. Ve a Meta Business Console → Configuración → Aplicaciones
3. Busca "WhatsApp Business" y haz clic en "Conectar"
4. Sigue los pasos para conectar tu número

### ❌ "El número está en formato incorrecto"

**Solución**:
1. Debe empezar con `+` 
2. Debe incluir el código de país (593 para Ecuador, 57 para Colombia, etc.)
3. **NO** incluir el 0 inicial si es que existe
4. Ejemplo correcto: `+593979607739`
5. Ejemplo incorrecto: `0979607739` o `979607739`

---

## 📝 PRÓXIMO PASO

Una vez que tengas los 4 datos, abre `selenashop/settings.py` y reemplaza:

```python
WHATSAPP_PHONE_NUMBER_ID = 'TU_PHONE_NUMBER_ID_AQUI'      # Paso 1
WHATSAPP_BUSINESS_ACCOUNT_ID = 'TU_BUSINESS_ACCOUNT_ID'   # Paso 2
WHATSAPP_ACCESS_TOKEN = 'TU_ACCESS_TOKEN_AQUI'            # Paso 3
WHATSAPP_ADMIN_NUMBER = '+593979607739'                    # Paso 4
```

Luego ejecuta:
```bash
python test_whatsapp.py
```

---

## 🎯 RESUMEN VISUAL

```
┌─────────────────────────────────────────────────────────────┐
│                   META BUSINESS CONSOLE                      │
│ https://business.facebook.com                               │
│                                                              │
│ WhatsApp Manager                                            │
│   └─ Números de teléfono                                    │
│      └─ Tu número: +593979607739                            │
│         └─ ID: 120212345678901234 ← COPIA ESTO             │
│                                                              │
│ Configuración                                               │
│   └─ Información de la cuenta                               │
│      └─ Business Account ID: 1234567890 ← COPIA ESTO        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   META DEVELOPERS                            │
│ https://developers.facebook.com                              │
│                                                              │
│ Mis Aplicaciones                                             │
│   └─ Tu App: "Vortice Ecuador Shop"                         │
│      └─ Herramientas → Explorador de API                   │
│         └─ Generar Token                                    │
│            └─ Token: EAABBbBB... ← COPIA ESTO               │
└─────────────────────────────────────────────────────────────┘

        ↓↓↓ PEGA TODO ESTO ↓↓↓

┌──────────────────────────────────────────────────────────────┐
│            ARCHIVO: selenashop/settings.py                   │
│                                                               │
│ WHATSAPP_PHONE_NUMBER_ID = '120212345678901234'              │
│ WHATSAPP_BUSINESS_ACCOUNT_ID = '1234567890'                  │
│ WHATSAPP_ACCESS_TOKEN = 'EAABBbBB...'                        │
│ WHATSAPP_ADMIN_NUMBER = '+593979607739'                      │
└──────────────────────────────────────────────────────────────┘
```

---

**¿Listo?** 🚀 Ahora ejecuta `python test_whatsapp.py` para verificar que todo funciona.
