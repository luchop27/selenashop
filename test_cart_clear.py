"""
Script para verificar que el carrito se limpia correctamente después de un checkout.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selenashop.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.sessions.models import Session
from apps.usuarios.models import Usuario
from apps.productos.models import Producto, Variante, CarritoItem
from core.cart import Cart
from core.models import Pedido
from decimal import Decimal
import json

def test_cart_cleanup_after_checkout():
    """
    Simular un checkout completo y verificar que:
    1. El carrito se limpia de la BD
    2. El carrito se limpia de la sesión
    3. El pedido se crea correctamente
    """
    print("\n" + "="*80)
    print("🧪 PRUEBA: Limpieza de carrito después del checkout")
    print("="*80 + "\n")
    
    # Crear cliente de prueba
    client = Client()
    session = client.session
    
    # Crear un usuario de prueba
    try:
        usuario = Usuario.objects.create_user(
            email='prueba@test.com',
            password='test123456',
            nombre='Prueba',
            apellido='Usuario'
        )
        print(f"✅ Usuario creado: {usuario.email}")
    except Exception as e:
        usuario = Usuario.objects.get(email='prueba@test.com')
        print(f"⚠️ Usuario ya existe: {usuario.email}")
    
    # Crear un producto de prueba
    try:
        from apps.productos.models import Categoria
        categoria = Categoria.objects.first()
        if not categoria:
            categoria = Categoria.objects.create(
                nombre='Test',
                descripcion='Test',
                estado=True
            )
        
        producto = Producto.objects.create(
            nombre='Producto de Prueba',
            descripcion_corta='Descripción',
            precio_base=Decimal('50.00'),
            activo=True,
            categoria=categoria
        )
        print(f"✅ Producto creado: {producto.nombre}")
    except Exception as e:
        producto = Producto.objects.filter(nombre='Producto de Prueba').first()
        if producto:
            print(f"⚠️ Producto ya existe: {producto.nombre}")
        else:
            print(f"❌ No se pudo crear el producto: {str(e)}")
            return
    
    # Crear una variante
    try:
        from apps.productos.models import Talla
        talla = Talla.objects.first()
        if not talla:
            talla = Talla.objects.create(codigo='M', nombre='Mediano')
        
        variante = Variante.objects.create(
            producto=producto,
            precio=Decimal('50.00'),
            stock=10,
            color='Rojo',
            talla=talla
        )
        print(f"✅ Variante creada: {variante.id} (stock: {variante.stock})")
    except Exception as e:
        variante = Variante.objects.filter(producto=producto).first()
        if variante:
            print(f"⚠️ Variante ya existe: {variante.id}")
        else:
            print(f"❌ No se pudo crear la variante: {str(e)}")
            return
    
    # 1️⃣ LOGIN DEL USUARIO
    print("\n--- PASO 1: Login del usuario ---")
    client.login(email='prueba@test.com', password='test123456')
    print("✅ Usuario autenticado")
    
    # 2️⃣ AGREGAR PRODUCTO AL CARRITO
    print("\n--- PASO 2: Agregar producto al carrito ---")
    session = client.session
    from django.test import RequestFactory
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.auth.middleware import AuthenticationMiddleware
    
    # Crear una fake request para usar con Cart
    factory = RequestFactory()
    request = factory.get('/')
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.user = usuario
    request.session.save()
    
    # Agregar al carrito
    cart = Cart(request)
    cart.add(producto, variante_id=variante.id, quantity=2)
    cart.save()
    print(f"✅ Producto agregado: {len(cart)} items en carrito")
    
    # Verificar en BD
    carrito_items_antes = CarritoItem.objects.filter(usuario=usuario).count()
    print(f"✅ Items en BD: {carrito_items_antes}")
    
    # 3️⃣ REALIZAR CHECKOUT
    print("\n--- PASO 3: Realizar checkout ---")
    checkout_data = {
        'first_name': 'Juan',
        'last_name': 'Pérez',
        'email': 'juan@test.com',
        'phone': '0987654321',
        'province': '1',
        'city': 'Guayaquil',
        'address': 'Calle principal 123',
        'country': 'Ecuador',
        'payment_method': 'bank_transfer',
        'terms_accepted': True,
        'discount_code_applied': '',
        'discount_amount': '0',
        'shipping_cost': '5.00'
    }
    
    response = client.post('/checkout/process/', checkout_data, follow=True)
    print(f"✅ Checkout realizado: {response.status_code}")
    
    # 4️⃣ VERIFICAR QUE EL CARRITO SE LIMPIÓ
    print("\n--- PASO 4: Verificar que el carrito se limpió ---")
    
    # Recargar usuario
    usuario.refresh_from_db()
    
    # Crear nueva instancia de Cart para recargar desde BD
    request2 = factory.get('/')
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request2)
    request2.user = usuario
    request2.session.save()
    
    cart2 = Cart(request2)
    
    # Verificar carrito vacío
    carrito_items_despues = CarritoItem.objects.filter(usuario=usuario).count()
    items_en_sesion = len(cart2)
    
    print(f"📊 Items en BD después del checkout: {carrito_items_despues}")
    print(f"📊 Items en sesión después del checkout: {items_en_sesion}")
    
    # 5️⃣ VERIFICAR QUE EL PEDIDO SE CREÓ
    print("\n--- PASO 5: Verificar que el pedido se creó ---")
    pedidos = Pedido.objects.filter(email='juan@test.com').order_by('-created_at')
    
    if pedidos.exists():
        pedido = pedidos.first()
        print(f"✅ Pedido creado: {pedido.numero_pedido}")
        print(f"   - Estado: {pedido.estado}")
        print(f"   - Total: ${pedido.total}")
        print(f"   - Items: {pedido.items.count()}")
    else:
        print("❌ No se creó el pedido")
        return
    
    # 6️⃣ RESULTADOS FINALES
    print("\n" + "="*80)
    print("📋 RESULTADOS:")
    print("="*80)
    
    success = True
    
    if carrito_items_antes == 0:
        print("❌ El carrito no se agregó correctamente antes del checkout")
        success = False
    else:
        print(f"✅ Carrito tenía {carrito_items_antes} items ANTES del checkout")
    
    if carrito_items_despues == 0:
        print(f"✅ Carrito se limpió correctamente en BD (0 items después)")
    else:
        print(f"❌ PROBLEMA: Carrito tiene {carrito_items_despues} items DESPUÉS del checkout")
        success = False
    
    if items_en_sesion == 0:
        print(f"✅ Carrito se limpió correctamente en sesión (0 items después)")
    else:
        print(f"❌ PROBLEMA: Sesión tiene {items_en_sesion} items DESPUÉS del checkout")
        success = False
    
    if pedidos.exists():
        print(f"✅ Pedido creado correctamente: {pedido.numero_pedido}")
    else:
        print("❌ Pedido no se creó")
        success = False
    
    print("="*80)
    if success:
        print("✅ PRUEBA EXITOSA: Todo funcionó correctamente")
    else:
        print("❌ PRUEBA FALLIDA: Hay problemas que revisar")
    print("="*80 + "\n")
    
    return success

if __name__ == '__main__':
    test_cart_cleanup_after_checkout()
