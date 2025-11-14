from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Min, Sum

# Import Producto model to build the shop listing
from apps.productos.models import Producto


def inicio(request):
    """Renderiza la plantilla home-05.html (nuevo index)"""
    from apps.productos.models import Coleccion, Categoria, Producto
    from django.db.models import Count, Min
    
    # Obtener colecciones activas para el slider superior (excluyendo "básica")
    from django.db.models import Q
    colecciones = (
        Coleccion.objects
        .filter(activo=True)
        .exclude(Q(nombre__iexact='basica') | Q(nombre__iexact='básica'))  # Excluir colección básica (con o sin tilde)
        .annotate(num_productos=Count('productos'))
        .order_by('-destacada', '-created_at')[:5]  # Máximo 5 para el slider
    )
    
    # Obtener subcategorías de "Ropa" para la sección Featured Collections
    try:
        categoria_ropa = Categoria.objects.get(nombre__iexact='Ropa', estado=True)
        categorias_principales = (
            Categoria.objects
            .filter(estado=True, padre=categoria_ropa)
            .annotate(num_productos=Count('productos'))
            .order_by('nombre')[:10]
        )
    except Categoria.DoesNotExist:
        # Si no existe la categoría Ropa, mostrar categorías principales
        categorias_principales = (
            Categoria.objects
            .filter(estado=True, padre__isnull=True)
            .annotate(num_productos=Count('productos'))
            .order_by('nombre')[:10]
        )
    
    # Obtener productos destacados para Editor's Picks
    productos_destacados = (
        Producto.objects
        .filter(activo=True)
        .select_related('categoria', 'coleccion')
        .prefetch_related(
            'imagenes',
            'variantes',
            'variantes__talla',
            'variantes__atributos__valor_atributo__atributo',  # Sistema de atributos
        )
        .annotate(precio_minimo=Min('variantes__precio'))
        .order_by('-created_at')[:12]  # Últimos 12 productos
    )
    
    # Preparar datos auxiliares para cada producto (igual que en shop_collection_sub)
    for producto in productos_destacados:
        # Precio a mostrar
        if producto.precio_minimo:
            producto.display_price = f"{producto.precio_minimo:.2f}"
        else:
            producto.display_price = f"{producto.precio_base:.2f}"
        
        # Imagen principal
        imagenes = list(producto.imagenes.all()[:2])
        if imagenes:
            producto.main_image_src = imagenes[0].imagen.url
            producto.hover_image_src = imagenes[1].imagen.url if len(imagenes) > 1 else None
        else:
            producto.main_image_src = None
            producto.hover_image_src = None
        
        # Colores disponibles
        colores_list = list(producto.variantes.values_list('color', flat=True).distinct())
        producto.colors = [{'valor': c} for c in colores_list if c]
        
        # Tallas disponibles - USAR LA MISMA LÓGICA QUE shop_collection_sub
        size_values = []
        for v in producto.variantes.all():
            # 1. Primero intentar desde FK talla directa
            if getattr(v, 'talla', None) and getattr(v.talla, 'codigo', None):
                code = v.talla.codigo
                if code and code not in size_values:
                    size_values.append(code)
                continue
            
            # 2. Fallback: buscar en sistema de atributos (VarianteAtributo)
            for va in getattr(v, 'atributos', []).all() if hasattr(getattr(v, 'atributos', None), 'all') else []:
                val = getattr(va, 'valor_atributo', None)
                if not val:
                    continue
                atributo = getattr(val, 'atributo', None)
                nombre_at = (getattr(atributo, 'slug', '') or getattr(atributo, 'nombre', '')).lower()
                if 'talla' in nombre_at or 'size' in nombre_at:
                    valor = getattr(val, 'valor', None)
                    if valor and valor not in size_values:
                        size_values.append(valor)
        
        producto.sizes = size_values
        print(f"DEBUG - Producto: {producto.nombre}, Tallas: {producto.sizes}")  # DEBUG
        
        # Disponibilidad
        total_stock = sum(v.stock for v in producto.variantes.all())
        producto.availability = 'in-stock' if total_stock > 0 else 'out-of-stock'
    
    # Obtener categorías con subcategorías para el menú de navegación
    categorias_menu = (
        Categoria.objects
        .filter(estado=True, padre__isnull=True)
        .prefetch_related('subcategorias')
        .order_by('nombre')
    )
    
    context = {
        'colecciones': colecciones,
        'categorias_principales': categorias_principales,
        'productos_destacados': productos_destacados,
        # Productos nuevos: los últimos añadidos (8 iniciales)
        'productos_nuevos': None,
        'categorias_menu': categorias_menu,
    }
    # Preparar 'productos_nuevos' (últimos 8 productos activos)
    from django.db.models import Min
    productos_nuevos_qs = (
        Producto.objects
        .filter(activo=True)
        .select_related('categoria', 'coleccion')
        .prefetch_related('imagenes', 'variantes', 'variantes__talla', 'variantes__atributos__valor_atributo__atributo')
        .annotate(precio_minimo=Min('variantes__precio'))
        .order_by('-created_at')[:8]
    )

    productos_nuevos = list(productos_nuevos_qs)
    # Preparar campos auxiliares para la plantilla (mismo esquema que productos_destacados)
    for producto in productos_nuevos:
        if getattr(producto, 'precio_minimo', None):
            producto.display_price = f"{producto.precio_minimo:.2f}"
        else:
            producto.display_price = f"{producto.precio_base:.2f}"

        imagenes = list(producto.imagenes.all()[:2])
        if imagenes:
            producto.main_image_src = imagenes[0].imagen.url
            producto.hover_image_src = imagenes[1].imagen.url if len(imagenes) > 1 else producto.main_image_src
        else:
            producto.main_image_src = ''
            producto.hover_image_src = ''

        colores_list = list(producto.variantes.values_list('color', flat=True).distinct())
        producto.colors = [{'valor': c} for c in colores_list if c]

        # tallas
        size_values = []
        for v in producto.variantes.all():
            if getattr(v, 'talla', None) and getattr(v.talla, 'codigo', None):
                code = v.talla.codigo
                if code and code not in size_values:
                    size_values.append(code)
                continue
            for va in getattr(v, 'atributos', []).all() if hasattr(getattr(v, 'atributos', None), 'all') else []:
                val = getattr(va, 'valor_atributo', None)
                if not val:
                    continue
                atributo = getattr(val, 'atributo', None)
                nombre_at = (getattr(atributo, 'slug', '') or getattr(atributo, 'nombre', '')).lower()
                if 'talla' in nombre_at or 'size' in nombre_at:
                    valor = getattr(val, 'valor', None)
                    if valor and valor not in size_values:
                        size_values.append(valor)
        producto.sizes = size_values

    context['productos_nuevos'] = productos_nuevos
    return render(request, 'home-05.html', context)


def home_05(request):
    """Alias para la función inicio"""
    return inicio(request)

def shop_collection_sub(request):
    """Lista de productos para la plantilla `shop-collection-sub.html`.

    - Filtra por categoría si se pasa `?categoria=<id_or_slug>`
    - Ordena por id (asc)
    - Anota precio mínimo de variantes y stock total
    - Prepara campos auxiliares que la plantilla espera: display_price, main_image_src,
      hover_image_src, colors, availability
    - Envía categorías o subcategorías según el contexto
    """
    from apps.productos.models import Categoria
    
    categoria_param = request.GET.get('categoria')
    categoria_actual = None
    categorias_a_mostrar = []

    qs = (
        Producto.objects
        .filter(activo=True)
        .select_related('categoria')
        # prefetch imagenes, variantes, tallas y atributos de variantes (fallbacks)
        .prefetch_related(
            'imagenes',
            'variantes',
            'variantes__talla',
            'variantes__atributos__valor_atributo__atributo',
        )
        .annotate(precio_variante=Min('variantes__precio'), total_stock=Sum('variantes__stock'))
        .order_by('id')
    )

    if categoria_param:
        # aceptar id numérico o slug
        try:
            cid = int(categoria_param)
            categoria_actual = Categoria.objects.filter(id=cid, estado=True).first()
            qs = qs.filter(categoria_id=cid)
        except Exception:
            categoria_actual = Categoria.objects.filter(slug=categoria_param, estado=True).first()
            qs = qs.filter(categoria__slug=categoria_param)
    
    # Determinar qué categorías mostrar en el slider
    if categoria_actual:
        print(f"DEBUG: Categoría actual: {categoria_actual.nombre} (ID: {categoria_actual.id})")
        print(f"DEBUG: Tiene padre: {categoria_actual.padre}")
        
        # Si la categoría tiene subcategorías, mostrarlas
        subcategorias = Categoria.objects.filter(
            padre=categoria_actual,
            estado=True
        ).order_by('nombre')
        
        print(f"DEBUG: Subcategorías encontradas: {subcategorias.count()}")
        
        if subcategorias.exists():
            # Tiene subcategorías, mostrarlas
            categorias_a_mostrar = list(subcategorias)
            print(f"DEBUG: Mostrando subcategorías de {categoria_actual.nombre}")
        elif categoria_actual.padre:
            # Es una subcategoría, mostrar sus hermanas (otras subcategorías del mismo padre)
            categorias_a_mostrar = list(
                Categoria.objects.filter(
                    padre=categoria_actual.padre,
                    estado=True
                ).order_by('nombre')
            )
            print(f"DEBUG: Es subcategoría, mostrando hermanas: {len(categorias_a_mostrar)}")
        else:
            # Es categoría principal sin subcategorías, mostrar todas las categorías principales
            categorias_a_mostrar = list(
                Categoria.objects.filter(
                    padre__isnull=True,
                    estado=True
                ).order_by('nombre')
            )
            print(f"DEBUG: Es categoría principal sin hijos, mostrando principales: {len(categorias_a_mostrar)}")
    else:
        # Si no hay categoría seleccionada, mostrar categorías principales
        categorias_a_mostrar = list(
            Categoria.objects.filter(
                padre__isnull=True,
                estado=True
            ).order_by('nombre')
        )
        print(f"DEBUG: Sin categoría, mostrando principales: {len(categorias_a_mostrar)}")
    
    print(f"DEBUG: Total categorías a mostrar: {len(categorias_a_mostrar)}")
    for cat in categorias_a_mostrar:
        print(f"  - {cat.nombre} (slug: {cat.slug}, imagen: {bool(cat.imagen)})")

    productos = list(qs)

    # Preparar campos que la plantilla reutiliza (imagen principal, hover, precio, colores)
    for p in productos:
        # precio a mostrar: variante (mín) o precio_base
        p.display_price = getattr(p, 'precio_variante', None) or p.precio_base

        imgs = list(p.imagenes.all().order_by('posicion', 'created_at'))
        p.main_image_src = imgs[0].src if imgs else ''
        p.hover_image_src = imgs[1].src if len(imgs) > 1 else p.main_image_src

        # colores únicos desde variantes (puede omitirse si no hay)
        color_values = []
        for v in p.variantes.all():
            if v.color and v.color not in color_values:
                color_values.append(v.color)
        p.colors = [{'valor': c} for c in color_values]

        # tallas únicas desde variantes
        size_values = []
        for v in p.variantes.all():
            # prefer direct foreign-key talla.codigo
            if getattr(v, 'talla', None) and getattr(v.talla, 'codigo', None):
                code = v.talla.codigo
                if code and code not in size_values:
                    size_values.append(code)
                continue

            # fallback: buscar en atributos de variante (ValorAtributo) si existe
            for va in getattr(v, 'atributos', []).all() if hasattr(getattr(v, 'atributos', None), 'all') else []:
                val = getattr(va, 'valor_atributo', None)
                if not val:
                    continue
                atributo = getattr(val, 'atributo', None)
                nombre_at = (getattr(atributo, 'slug', '') or getattr(atributo, 'nombre', '')).lower()
                if 'talla' in nombre_at or 'size' in nombre_at:
                    valor = getattr(val, 'valor', None)
                    if valor and valor not in size_values:
                        size_values.append(valor)

        p.sizes = size_values

        # descripción corta para mostrar en el modal
        p.short_description = p.descripcion_corta or (p.descripcion_larga[:180] if p.descripcion_larga else '')

        # disponibilidad calculada a partir del stock total
        total_stock = getattr(p, 'total_stock', None)
        try:
            p.availability = 'In stock' if (total_stock is not None and total_stock > 0) else 'Out of stock'
        except Exception:
            p.availability = 'In stock'

    return render(request, 'shop-collection-sub.html', {
        'productos': productos,
        'categoria_actual': categoria_actual,
        'categorias_a_mostrar': categorias_a_mostrar,
    })


# Alias para las vistas de usuarios (para mantener compatibilidad)
def login_usuario(request):
    """Alias a la vista de login en usuarios"""
    from apps.usuarios.views import login_usuario as login_view
    return login_view(request)


def logout_usuario(request):
    """Alias a la vista de logout en usuarios"""
    from apps.usuarios.views import logout_usuario as logout_view
    return logout_view(request)


@login_required(login_url='/login/')
def dashboard_redirect(request):
    """Redirección al dashboard si el usuario es admin"""
    if request.user.rol == 'admin_tienda' or request.user.is_staff:
        return redirect('core:admin_index')
    else:
        messages.error(request, 'No tienes permiso para acceder al panel de administración.')
        return redirect('core:inicio')


def admin_index(request):
    """Renderiza el índice del panel administrativo"""
    if not request.user.is_authenticated or (request.user.rol != 'admin_tienda' and not request.user.is_staff):
        return redirect('core:inicio')
    # Render the original admin HTML (pindex.html) which is located in the
    # project folder `admin-ecomus/` and is included in TEMPLATES['DIRS'].
    return render(request, 'pindex.html')


def product_detail(request, producto_id=None):
    """Vista para mostrar los detalles de un producto"""
    from django.shortcuts import get_object_or_404
    from apps.productos.models import Producto
    
    if producto_id:
        # Obtener el producto con todas sus relaciones
        producto = get_object_or_404(
            Producto.objects
            .select_related('categoria', 'coleccion')
            .prefetch_related(
                'imagenes',
                'variantes',
                'variantes__talla',
                'variantes__atributos__valor_atributo__atributo',
            ),
            id=producto_id,
            activo=True
        )
        
        # Obtener todas las imágenes del producto
        imagenes = list(producto.imagenes.all())
        
        # Obtener todas las variantes
        variantes = list(producto.variantes.all())
        print(f"DEBUG - Producto ID: {producto.id}, Nombre: {producto.nombre}")
        print(f"DEBUG - Total variantes encontradas: {len(variantes)}")
        for v in variantes:
            print(f"DEBUG - Variante ID: {v.id}, Talla: {v.talla}, Color: {v.color}, Stock: {v.stock}")
        
        # Extraer colores únicos
        colores_disponibles = []
        colores_vistos = set()
        for variante in variantes:
            if variante.color and variante.color not in colores_vistos:
                colores_disponibles.append({
                    'nombre': variante.color,
                    'valor': variante.color
                })
                colores_vistos.add(variante.color)
        
        # Extraer tallas únicas
        tallas_disponibles = []
        tallas_vistas = set()
        for variante in variantes:
            # Primero intentar desde FK talla directa
            if hasattr(variante, 'talla') and variante.talla and hasattr(variante.talla, 'codigo'):
                codigo = variante.talla.codigo
                if codigo and codigo not in tallas_vistas:
                    tallas_disponibles.append({
                        'codigo': codigo,
                        'nombre': getattr(variante.talla, 'nombre', codigo)
                    })
                    tallas_vistas.add(codigo)
            else:
                # Fallback: buscar en sistema de atributos
                for va in variante.atributos.all():
                    val = va.valor_atributo
                    if val and val.atributo:
                        nombre_attr = (val.atributo.slug or val.atributo.nombre).lower()
                        if 'talla' in nombre_attr or 'size' in nombre_attr:
                            valor = val.valor
                            if valor and valor not in tallas_vistas:
                                tallas_disponibles.append({
                                    'codigo': valor,
                                    'nombre': valor
                                })
                                tallas_vistas.add(valor)
        
        # Calcular precio mínimo y máximo
        precios = [v.precio for v in variantes if v.precio]
        precio_min = min(precios) if precios else producto.precio_base
        precio_max = max(precios) if precios else producto.precio_base
        
        # Verificar si hay descuento (comparando con precio base del producto)
        tiene_descuento = precio_min < producto.precio_base if precio_min and producto.precio_base else False
        
        # Productos relacionados (misma categoría/subcategoría)
        productos_relacionados = (
            Producto.objects
            .filter(activo=True, categoria=producto.categoria)
            .exclude(id=producto.id)
            .select_related('categoria', 'coleccion')
            .prefetch_related('imagenes', 'variantes')
            .annotate(precio_minimo=Min('variantes__precio'))
            .order_by('-created_at')  # Más recientes primero
            [:8]
        )
        
        # Preparar productos relacionados para el template
        for prod in productos_relacionados:
            imagenes_rel = list(prod.imagenes.all()[:2])
            if imagenes_rel:
                prod.main_image = imagenes_rel[0]
                prod.main_image_src = imagenes_rel[0].imagen.url if imagenes_rel[0].imagen else None
                prod.hover_image = imagenes_rel[1] if len(imagenes_rel) > 1 else None
                prod.hover_image_src = imagenes_rel[1].imagen.url if len(imagenes_rel) > 1 and imagenes_rel[1].imagen else None
            else:
                prod.main_image_src = None
                prod.hover_image_src = None
            
            prod.display_price = prod.precio_minimo if prod.precio_minimo else prod.precio_base
            
            # Obtener colores y tallas del producto relacionado
            prod_variantes = list(prod.variantes.all())
            
            # Colores
            colores_prod = []
            colores_vistos_prod = set()
            for var in prod_variantes:
                if var.color and var.color not in colores_vistos_prod:
                    colores_prod.append({'valor': var.color, 'nombre': var.color})
                    colores_vistos_prod.add(var.color)
            prod.colors = colores_prod
            
            # Tallas
            tallas_prod = []
            tallas_vistas_prod = set()
            for var in prod_variantes:
                if hasattr(var, 'talla') and var.talla and hasattr(var.talla, 'codigo'):
                    codigo = var.talla.codigo
                    if codigo and codigo not in tallas_vistas_prod:
                        tallas_prod.append(codigo)
                        tallas_vistas_prod.add(codigo)
            prod.sizes = tallas_prod
        
        # Productos recientes de cualquier subcategoría de ropa
        from apps.productos.models import Categoria
        
        # Buscar la categoría "Ropa" o cualquier categoría principal
        try:
            categoria_ropa = Categoria.objects.get(nombre__icontains='Ropa', padre__isnull=True)
            # Obtener todas las subcategorías de Ropa
            subcategorias_ropa = categoria_ropa.subcategorias.filter(estado=True)
            subcategorias_ids = list(subcategorias_ropa.values_list('id', flat=True))
            
            # Agregar la categoría principal también
            subcategorias_ids.append(categoria_ropa.id)
            
            # Obtener productos de todas estas categorías
            productos_recientes = Producto.objects.filter(
                activo=True,
                categoria_id__in=subcategorias_ids
            ).exclude(
                id=producto.id
            ).select_related(
                'categoria', 'coleccion'
            ).prefetch_related(
                'imagenes', 'variantes', 'variantes__talla'
            ).annotate(
                precio_minimo=Min('variantes__precio')
            ).order_by('-created_at')[:6]
            
        except Categoria.DoesNotExist:
            # Si no existe la categoría "Ropa", mostrar productos de cualquier categoría
            productos_recientes = Producto.objects.filter(
                activo=True
            ).exclude(
                id=producto.id
            ).select_related(
                'categoria', 'coleccion'
            ).prefetch_related(
                'imagenes', 'variantes', 'variantes__talla'
            ).annotate(
                precio_minimo=Min('variantes__precio')
            ).order_by('-created_at')[:6]
        
        # Preparar datos de productos recientes
        for prod in productos_recientes:
            imagenes_rec = list(prod.imagenes.all()[:2])
            if imagenes_rec:
                prod.main_image_src = imagenes_rec[0].imagen.url if imagenes_rec[0].imagen else None
                prod.hover_image_src = imagenes_rec[1].imagen.url if len(imagenes_rec) > 1 and imagenes_rec[1].imagen else None
            else:
                prod.main_image_src = None
                prod.hover_image_src = None
            
            prod.display_price = prod.precio_minimo if prod.precio_minimo else prod.precio_base
            
            # Colores
            prod_variantes_rec = list(prod.variantes.all())
            colores_rec = []
            colores_vistos_rec = set()
            for var in prod_variantes_rec:
                if hasattr(var, 'color') and var.color:
                    color = var.color
                    if color not in colores_vistos_rec:
                        colores_rec.append({'valor': color, 'nombre': color})
                        colores_vistos_rec.add(color)
            prod.colors = colores_rec
            
            # Tallas
            tallas_rec = []
            tallas_vistas_rec = set()
            for var in prod_variantes_rec:
                if hasattr(var, 'talla') and var.talla and hasattr(var.talla, 'codigo'):
                    codigo = var.talla.codigo
                    if codigo and codigo not in tallas_vistas_rec:
                        tallas_rec.append(codigo)
                        tallas_vistas_rec.add(codigo)
            prod.sizes = tallas_rec
        
        # Obtener información adicional del producto
        from apps.productos.models import ShippingInfo, ReturnPolicy, GlobalProductContent
        
        # Global product content (Features, Materials, Care instructions)
        global_content = GlobalProductContent.objects.filter(activo=True).first()
        
        # Shipping info (obtener la primera activa)
        shipping_info = ShippingInfo.objects.filter(activo=True).first()
        
        # Return policies (obtener todas las activas)
        return_policies = ReturnPolicy.objects.filter(activo=True).order_by('orden')
        
        # Preparar datos de variantes con stock para JavaScript
        import json
        variantes_stock = {}
        for variante in variantes:
            if variante.talla:
                key = f"{variante.talla.codigo}"
                # Solo agregar color a la clave si realmente existe y no está vacío
                if variante.color and variante.color.strip():
                    key += f"_{variante.color}"
                variantes_stock[key] = {
                    'id': variante.id,
                    'stock': variante.stock,
                    'talla': variante.talla.codigo if variante.talla else None,
                    'color': variante.color if variante.color else '',
                    'precio': str(variante.precio) if variante.precio else str(producto.precio_base)
                }
                # Debug: imprimir información de la variante
                print(f"DEBUG Backend - Clave: '{key}' - Stock: {variante.stock} - Precio: {variante.precio} - Color: '{variante.color}'")
        variantes_json = json.dumps(variantes_stock)
        print(f"DEBUG Backend - Variantes JSON completo: {variantes_json}")
        
        context = {
            'producto': producto,
            'imagenes': imagenes,
            'variantes': variantes,
            'variantes_json': variantes_json,
            'colores_disponibles': colores_disponibles,
            'tallas_disponibles': tallas_disponibles,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'tiene_descuento': tiene_descuento,
            'productos_relacionados': productos_relacionados,
            'productos_recientes': productos_recientes,
            'global_content': global_content,
            'shipping_info': shipping_info,
            'return_policies': return_policies,
        }
    else:
        # Sin ID, mostrar template demo
        context = {}
    
    return render(request, 'product-detail.html', context)


# ==================== CART VIEWS ====================

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .cart import Cart
from apps.productos.models import Variante

@require_POST
def cart_add(request):
    """
    Vista para agregar productos al carrito via AJAX
    """
    cart = Cart(request)
    producto_id = request.POST.get('producto_id')
    variante_id = request.POST.get('variante_id')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        producto = Producto.objects.get(id=producto_id, activo=True)
        cart.add(producto=producto, variante_id=variante_id, quantity=quantity)
        
        return JsonResponse({
            'success': True,
            'message': 'Producto agregado al carrito',
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price())
        })
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Producto no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_POST
def cart_remove(request):
    """
    Vista para eliminar productos del carrito via AJAX
    """
    cart = Cart(request)
    product_id = request.POST.get('product_id')
    
    cart.remove(product_id)
    
    return JsonResponse({
        'success': True,
        'message': 'Producto eliminado del carrito',
        'cart_count': len(cart),
        'cart_total': str(cart.get_total_price())
    })


@require_POST
def cart_update(request):
    """
    Vista para actualizar la cantidad de productos en el carrito via AJAX
    """
    cart = Cart(request)
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    cart.update_quantity(product_id, quantity)
    
    # Calcular el total del item
    item_total = None
    for item in cart:
        if f"{item['producto_id']}_{item['variante_id']}" == product_id or str(item['producto_id']) == product_id:
            item_total = str(item['total_precio'])
            break
    
    return JsonResponse({
        'success': True,
        'message': 'Carrito actualizado',
        'cart_count': len(cart),
        'cart_total': str(cart.get_total_price()),
        'item_total': item_total
    })


def cart_detail(request):
    """
    Vista para obtener los detalles completos del carrito via AJAX
    """
    cart = Cart(request)
    
    items = []
    for item in cart:
        items.append({
            'product_id': f"{item['producto_id']}_{item['variante_id']}" if item['variante_id'] else str(item['producto_id']),
            'producto_id': item['producto_id'],
            'variante_id': item['variante_id'],
            'nombre': item['nombre'],
            'precio': str(item['precio_decimal']),
            'quantity': item['quantity'],
            'total': str(item['total_precio']),
            'imagen': item['imagen'],
            'color': item.get('color'),
            'talla': item.get('talla'),
        })
    
    return JsonResponse({
        'success': True,
        'items': items,
        'cart_count': len(cart),
        'cart_total': str(cart.get_total_price())
    })


def cart_clear(request):
    """
    Vista para limpiar todo el carrito
    """
    cart = Cart(request)
    cart.clear()
    
    return JsonResponse({
        'success': True,
        'message': 'Carrito vaciado',
        'cart_count': 0,
        'cart_total': '0.00'
    })


def api_productos_nuevos(request):
    """Endpoint AJAX: devuelve el HTML de los siguientes productos nuevos.

    Parámetros GET:
    - offset: desde qué índice (int)
    - limit: cuántos devolver (int)
    """
    from django.template.loader import render_to_string
    from django.db.models import Min

    try:
        offset = int(request.GET.get('offset', 0))
    except Exception:
        offset = 0

    try:
        limit = int(request.GET.get('limit', 4))
    except Exception:
        limit = 4

    qs = (
        Producto.objects
        .filter(activo=True)
        .select_related('categoria', 'coleccion')
        .prefetch_related('imagenes', 'variantes', 'variantes__talla', 'variantes__atributos__valor_atributo__atributo')
        .annotate(precio_minimo=Min('variantes__precio'))
        .order_by('-created_at')
    )

    productos_slice = list(qs[offset:offset + limit])

    # Preparar campos auxiliares (misma lógica que en inicio)
    for producto in productos_slice:
        if getattr(producto, 'precio_minimo', None):
            producto.display_price = f"{producto.precio_minimo:.2f}"
        else:
            producto.display_price = f"{producto.precio_base:.2f}"

        imagenes = list(producto.imagenes.all()[:2])
        if imagenes:
            producto.main_image_src = imagenes[0].imagen.url
            producto.hover_image_src = imagenes[1].imagen.url if len(imagenes) > 1 else producto.main_image_src
        else:
            producto.main_image_src = ''
            producto.hover_image_src = ''

        colores_list = list(producto.variantes.values_list('color', flat=True).distinct())
        producto.colors = [{'valor': c} for c in colores_list if c]

        size_values = []
        for v in producto.variantes.all():
            if getattr(v, 'talla', None) and getattr(v.talla, 'codigo', None):
                code = v.talla.codigo
                if code and code not in size_values:
                    size_values.append(code)
                continue
            for va in getattr(v, 'atributos', []).all() if hasattr(getattr(v, 'atributos', None), 'all') else []:
                val = getattr(va, 'valor_atributo', None)
                if not val:
                    continue
                atributo = getattr(val, 'atributo', None)
                nombre_at = (getattr(atributo, 'slug', '') or getattr(atributo, 'nombre', '')).lower()
                if 'talla' in nombre_at or 'size' in nombre_at:
                    valor = getattr(val, 'valor', None)
                    if valor and valor not in size_values:
                        size_values.append(valor)
        producto.sizes = size_values

    # Renderizar fragmento HTML con los productos (plantilla parcial)
    html = render_to_string('includes/product_cards.html', {'productos': productos_slice}, request=request)

    return JsonResponse({
        'html': html,
        'count': len(productos_slice),
    })


def cart_recommendations(request):
    """
    Vista para obtener productos recomendados basados en el carrito
    Muestra productos de las mismas categorías que los productos en el carrito
    """
    cart = Cart(request)
    
    # Obtener IDs de productos en el carrito
    cart_product_ids = [int(item['producto_id']) for item in cart]
    
    if not cart_product_ids:
        # Si el carrito está vacío, mostrar productos destacados o recientes
        productos_recomendados = Producto.objects.filter(
            activo=True
        ).select_related(
            'categoria', 'coleccion'
        ).prefetch_related(
            'imagenes'
        ).annotate(
            precio_minimo=Min('variantes__precio')
        ).order_by('-created_at')[:6]
    else:
        # Obtener categorías de productos en el carrito
        from apps.productos.models import Categoria
        productos_en_carrito = Producto.objects.filter(id__in=cart_product_ids).select_related('categoria')
        categorias_ids = list(set([p.categoria_id for p in productos_en_carrito if p.categoria_id]))
        
        # Buscar productos de las mismas categorías que no están en el carrito
        productos_recomendados = Producto.objects.filter(
            activo=True,
            categoria_id__in=categorias_ids
        ).exclude(
            id__in=cart_product_ids
        ).select_related(
            'categoria', 'coleccion'
        ).prefetch_related(
            'imagenes'
        ).annotate(
            precio_minimo=Min('variantes__precio')
        ).order_by('-created_at')[:6]
    
    # Preparar datos de productos
    recommendations = []
    for producto in productos_recomendados:
        primera_imagen = producto.imagenes.first()
        imagen_url = primera_imagen.imagen.url if primera_imagen and primera_imagen.imagen else None
        
        precio = producto.precio_minimo if producto.precio_minimo else producto.precio_base
        
        recommendations.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(precio),
            'imagen': imagen_url,
            'url': f'/product/{producto.id}/'
        })
    
    return JsonResponse({
        'success': True,
        'recommendations': recommendations
    })