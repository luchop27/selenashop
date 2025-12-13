# 📸 GUÍA VISUAL: DÓNDE ENCONTRAR LAS CREDENCIALES

## Pantalla 1: Acceso a Meta Developers

```
PASO 1: Abre https://developers.facebook.com/

┌─────────────────────────────────────────────────┐
│  facebook.com/developers                        │
│                                                 │
│  [Mis apps ▼]  [Documentos]  [Comunidad] ▶     │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │  📱 Mi Tienda App (Ejemplo)             │   │
│  │  ─────────────────────────────────────  │   │
│  │  ID: 1234567890                        │   │
│  │                                        │   │
│  │  [Ir a la app] [Editar]                │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘

Haz click en tu app (o "Crear app" si es la primera)
```

---

## Pantalla 2: Dashboard de Tu App

```
PASO 2: Dentro de tu app, ve a Productos

┌─────────────────────────────────────────────────┐
│  Mi Tienda App  [Configuración ▼]              │
│  ─────────────────────────────────────────────  │
│                                                 │
│  PRODUCTOS:                                     │
│  ├─ Facebook SDK        [Configurar]            │
│  ├─ WhatsApp ✨         [Configurar]            │ ← CLICK AQUI
│  ├─ Instagram Graph     [Configurar]            │
│  └─ Otros...                                    │
│                                                 │
└─────────────────────────────────────────────────┘

Busca "WhatsApp" y haz click en "Configurar"
```

---

## Pantalla 3: Panel de WhatsApp

```
PASO 3: Dentro de WhatsApp, verás varias opciones

┌─────────────────────────────────────────────────┐
│  WhatsApp - Vórtice Ecuador                     │
│  ─────────────────────────────────────────────  │
│                                                 │
│  📋 MENÚ IZQUIERDO:                             │
│  ├─ Inicio                                      │
│  ├─ Números de teléfono      ← AQUI (Paso 5)   │
│  ├─ Configuración             ← AQUI (Paso 4)  │
│  ├─ Plantillas                                  │
│  ├─ Análitica                                   │
│  └─ Todos los productos                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Pantalla 4: OBTENER ACCESS TOKEN (PASO 4)

```
PASO 4.1: Ve a Configuración → Credenciales

┌─────────────────────────────────────────────────┐
│  Configuración                                  │
│  ─────────────────────────────────────────────  │
│                                                 │
│  IZQUIERDA:                                     │
│  ├─ Información general                         │
│  ├─ Credenciales    ✨ ← CLICK AQUI             │
│  ├─ Permisos                                    │
│  └─ Logs                                        │
│                                                 │
└─────────────────────────────────────────────────┘

PASO 4.2: En Credenciales, busca la sección de Tokens

┌─────────────────────────────────────────────────┐
│  Credenciales                                   │
│  ─────────────────────────────────────────────  │
│                                                 │
│  📌 TOKENS DE ACCESO:                           │
│  ├─ Token de usuario       [Generar]            │
│  └─ Token de sistema       [Generar]            │
│                                                 │
│  🔐 CLAVES DE ACCESO:                           │
│  ├─ App ID:      1234567890                     │
│  ├─ App Secret:  XXXXX...                       │
│                                                 │
│  [Generar token] ← HABLAMOS AQUI                │
│                                                 │
└─────────────────────────────────────────────────┘

PASO 4.3: Haz click en "Generar token"

Se abrirá un cuadro. Asegúrate de que ESTE seleccionado:
  ✅ whatsapp_business_messaging
  ✅ whatsapp_business_management

Haz click en "Generar"

RESULTADO:
┌─────────────────────────────────────────────────┐
│  Tu Token (cópialo completo):                   │
│                                                 │
│  EAABsbCS1iHgBAOZCZBu2kP7PNZBz...              │
│  EAAAASfBzcABAOZCZBu2kP7PNZBAAAB...            │
│  ...muchos caracteres más...                    │
│                                                 │
│  [Copiar]  ← HABLAMOS AQUI                      │
│                                                 │
└─────────────────────────────────────────────────┘

⭐ ESTE ES TU ACCESS TOKEN
Guárdalo en un lugar seguro
```

---

## Pantalla 5: OBTENER PHONE NUMBER ID (PASO 5)

```
PASO 5.1: Ve a "Números de teléfono"

┌─────────────────────────────────────────────────┐
│  Números de teléfono                            │
│  ─────────────────────────────────────────────  │
│                                                 │
│  Tus números de WhatsApp Business:              │
│                                                 │
│  ┌──────────────────────────────┐               │
│  │ 📱 +593 979607739           │               │
│  │ ──────────────────────────  │               │
│  │ ID: 102345678901234         │               │
│  │ Estado: Verificado ✅       │               │
│  │                             │               │
│  │ [Ver detalles]              │               │
│  └──────────────────────────────┘               │
│                                                 │
│  [Agregar número]                              │
│                                                 │
└─────────────────────────────────────────────────┘

Haz click en tu número o en "Ver detalles"

PASO 5.2: Detalles del número

┌─────────────────────────────────────────────────┐
│  Detalles - +593 979607739                      │
│  ─────────────────────────────────────────────  │
│                                                 │
│  Información:                                   │
│  ├─ ID del número: 102345678901234 ← AQUI      │
│  ├─ Teléfono: +593 979607739                   │
│  ├─ Estado: Verificado                         │
│  ├─ Calidad: Desconocida                       │
│  ├─ Nombre: Mi Tienda                          │
│  ├─ Categoría: Negocios                        │
│  └─ Zona horaria: America/Guayaquil             │
│                                                 │
└─────────────────────────────────────────────────┘

⭐ ESTE ES TU PHONE NUMBER ID: 102345678901234
```

---

## Pantalla 6: OBTENER BUSINESS ACCOUNT ID (PASO 6)

```
PASO 6.1: Ve a "Configuración" → "Información"

┌─────────────────────────────────────────────────┐
│  Configuración                                  │
│  ─────────────────────────────────────────────  │
│                                                 │
│  MENÚ IZQUIERDO:                                │
│  ├─ Información general    ✨ ← CLICK AQUI      │
│  ├─ Credenciales                               │
│  └─ Permisos                                    │
│                                                 │
└─────────────────────────────────────────────────┘

PASO 6.2: En Información general

┌─────────────────────────────────────────────────┐
│  Información General                            │
│  ─────────────────────────────────────────────  │
│                                                 │
│  DATOS DE LA CUENTA:                            │
│  ├─ Nombre: Vórtice Ecuador                     │
│  ├─ Email: admin@vortice.com                    │
│  ├─ Teléfono: +593 979607739                    │
│  ├─ País: Ecuador                               │
│  └─ ID de cuenta: 123456789012345 ← AQUI       │
│                                                 │
│  DATOS DEL NEGOCIO:                             │
│  ├─ Categoría: Moda y Accesorios                │
│  ├─ Sitio web: vortice.ec                       │
│  └─ Dirección: Quito, Ecuador                   │
│                                                 │
└─────────────────────────────────────────────────┘

⭐ ESTE ES TU BUSINESS ACCOUNT ID: 123456789012345
```

---

## RESUMEN: Los 3 Que Necesitas

```
┌─────────────────────────────────────┐
│ CREDENCIALES OBTENIDAS ✅           │
├─────────────────────────────────────┤
│                                     │
│ 1️⃣  ACCESS TOKEN:                   │
│    EAABsbCS1iHgBAOZCZBu2...        │
│                                     │
│ 2️⃣  PHONE NUMBER ID:                │
│    102345678901234                  │
│                                     │
│ 3️⃣  BUSINESS ACCOUNT ID:            │
│    123456789012345                  │
│                                     │
└─────────────────────────────────────┘

SIGUIENTE PASO:
→ Abre: selenashop/settings.py
→ Ve al final
→ Pega en WHATSAPP_* = '...'
→ Guarda (Ctrl+S)
→ Ejecuta: python test_whatsapp_complete.py
```

---

## 🎯 Checklist

- [ ] Accedí a Meta Developers
- [ ] Seleccioné mi app
- [ ] Agregué WhatsApp
- [ ] Copié Access Token
- [ ] Copié Phone Number ID
- [ ] Copié Business Account ID
- [ ] Pegué en settings.py
- [ ] Guardé el archivo
- [ ] Ejecuté test

---

## 🆘 Si No Encuentras Algo

**"No veo el botón Generar token"**
→ Recarga la página
→ Verifica estar en la sección correcta
→ Prueba con otro navegador

**"Mi número no está en la lista"**
→ Ve a "Números de teléfono"
→ Click "Agregar número"
→ WhatsApp te enviará un código
→ Confirma el código

**"No encuentro Business Account ID"**
→ Ve a Configuración (en WhatsApp)
→ Selecciona "Información general"
→ Busca "ID de cuenta"

**"Los IDs son números muy largos"**
→ Sí, son así correctamente
→ Cópialos completos sin espacios

---

**¡Listo! Ya tienes todo lo que necesitas.** ✅
