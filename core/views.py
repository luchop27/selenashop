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
    # Preparar 'productos_nuevos' (últimos 8 productos activos) pero solo de la categoría "Ropa"
    from django.db.models import Min
    # Intentar localizar la categoría principal de ropa y sus subcategorías
    try:
        categoria_ropa = Categoria.objects.get(nombre__iexact='Ropa', estado=True)
    except Categoria.DoesNotExist:
        # Fallback: buscar por nombre que contenga 'ropa' (insensible a mayúsculas)
        categoria_ropa = Categoria.objects.filter(nombre__icontains='ropa', padre__isnull=True, estado=True).first()

    if categoria_ropa:
        sub_ids = list(categoria_ropa.subcategorias.filter(estado=True).values_list('id', flat=True))
        categorias_ids = sub_ids + [categoria_ropa.id]
        productos_nuevos_qs = (
            Producto.objects
            .filter(activo=True, categoria_id__in=categorias_ids)
            .select_related('categoria', 'coleccion')
            .prefetch_related('imagenes', 'variantes', 'variantes__talla', 'variantes__atributos__valor_atributo__atributo')
            .annotate(precio_minimo=Min('variantes__precio'))
            .order_by('-created_at')[:8]
        )
    else:
        # Si no existe la categoría ropa, conservar el comportamiento anterior
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
    # --- Shop Gram: productos aleatorios de la categoría 'Ropa' ---
    try:
        categoria_ropa_main = Categoria.objects.filter(nombre__icontains='ropa', padre__isnull=True, estado=True).first()
    except Exception:
        categoria_ropa_main = None

    if categoria_ropa_main:
        sub_ids = list(categoria_ropa_main.subcategorias.filter(estado=True).values_list('id', flat=True))
        categorias_ids = sub_ids + [categoria_ropa_main.id]
        shop_qs = (
            Producto.objects
            .filter(activo=True, categoria_id__in=categorias_ids)
            .select_related('categoria', 'coleccion')
            .prefetch_related('imagenes', 'variantes')
            .annotate(precio_minimo=Min('variantes__precio'))
            .order_by('?')[:5]
        )
    else:
        shop_qs = (
            Producto.objects
            .filter(activo=True)
            .select_related('categoria', 'coleccion')
            .prefetch_related('imagenes', 'variantes')
            .annotate(precio_minimo=Min('variantes__precio'))
            .order_by('?')[:5]
        )

    shop_gram_products = list(shop_qs)
    for p in shop_gram_products:
        # precio a mostrar
        if getattr(p, 'precio_minimo', None):
            p.display_price = f"{p.precio_minimo:.2f}"
        else:
            p.display_price = f"{p.precio_base:.2f}"

        # imágenes
        imagenes = list(p.imagenes.all()[:2])
        if imagenes:
            # usar la propiedad .src si está disponible, fallback a .imagen.url
            p.main_image_src = getattr(imagenes[0], 'src', None) or (imagenes[0].imagen.url if imagenes[0].imagen else '')
            p.hover_image_src = (
                getattr(imagenes[1], 'src', None)
                if len(imagenes) > 1 else p.main_image_src
            ) or (imagenes[1].imagen.url if len(imagenes) > 1 and imagenes[1].imagen else p.main_image_src)
        else:
            p.main_image_src = ''
            p.hover_image_src = ''

        # descripción corta para el modal
        p.short_description = p.descripcion_corta or (p.descripcion_larga[:150] if p.descripcion_larga else '')

    context['shop_gram_products'] = shop_gram_products
    # --- Testimonial / Reseñas: traer reseñas verificadas recientes ---
    try:
        from apps.resenas.models import Resena

        # Intentar reseñas verificadas; si no hay, traer cualquier reseña reciente
        qs_resenas = list(
            Resena.objects
            .filter(verificado=True)
            .select_related('usuario', 'producto')
            .order_by('-creado_en')[:5]
        )

        if not qs_resenas:
            qs_resenas = list(
                Resena.objects
                .all()
                .select_related('usuario', 'producto')
                .order_by('-creado_en')[:5]
            )

        testimonials = []
        for r in qs_resenas:
            usuario = getattr(r, 'usuario', None)
            if usuario:
                nombre = ''
                try:
                    nombre = usuario.get_full_name() if callable(getattr(usuario, 'get_full_name', None)) else ''
                except Exception:
                    nombre = ''
                if not nombre:
                    nombre = getattr(usuario, 'nombre', '') or getattr(usuario, 'username', '') or getattr(usuario, 'email', '') or 'Cliente'
            else:
                nombre = 'Cliente'

            producto = getattr(r, 'producto', None)
            product_image = ''
            product_title = ''
            product_url = '#'
            product_price = ''
            if producto:
                product_title = getattr(producto, 'nombre', '')
                product_url = f'/product/{getattr(producto, "id", "")}/'
                first_img = producto.imagenes.first() if hasattr(producto, 'imagenes') else None
                if first_img and getattr(first_img, 'imagen', None):
                    try:
                        product_image = first_img.imagen.url
                    except Exception:
                        product_image = ''
                try:
                    precio_min = getattr(producto, 'precio_minimo', None)
                    if precio_min:
                        product_price = f"{precio_min:.2f}"
                    else:
                        product_price = str(getattr(producto, 'precio_base', ''))
                except Exception:
                    product_price = str(getattr(producto, 'precio_base', ''))

            time_ago = r.get_tiempo_transcurrido() if hasattr(r, 'get_tiempo_transcurrido') else getattr(r, 'creado_en', '')

            testimonials.append({
                'rating': getattr(r, 'calificacion', 5) or 5,
                'heading': getattr(r, 'titulo', '') or '',
                'text': getattr(r, 'comentario', '') or '',
                'author_name': nombre,
                'metas': getattr(r, 'metas', '') or time_ago,
                'product_image': product_image,
                'product_title': product_title,
                'product_url': product_url,
                'product_price': product_price,
            })

    except Exception:
        testimonials = []

    # Si no hay reseñas en la BD, usar un fallback de ejemplo para evitar el mensaje "No reviews yet".
    if not testimonials:
        testimonials = [
            {
                'rating': 5,
                'heading': 'Excelente servicio',
                'text': 'Me encantó la calidad del producto y la rapidez en el envío.',
                'author_name': 'María López',
                'metas': 'Cliente de España',
                'product_image': '/static/images/shop/products/img-p2.png',
                'product_title': 'Jersey thong body',
                'product_url': '#',
                'product_price': '105.95',
            },
            {
                'rating': 5,
                'heading': 'Muy buena calidad',
                'text': 'La tela es suave y el tallaje es perfecto. Volveré a comprar.',
                'author_name': 'Carlos Ruiz',
                'metas': 'Cliente de México',
                'product_image': '/static/images/shop/products/img-p3.png',
                'product_title': 'Cotton jersey top',
                'product_url': '#',
                'product_price': '7.95',
            },
            {
                'rating': 5,
                'heading': 'Recomiendo 100%',
                'text': 'Muy buena atención al cliente y producto tal como se describe.',
                'author_name': 'Ana Gómez',
                'metas': 'Cliente de USA',
                'product_image': '/static/images/shop/products/img-p4.png',
                'product_title': 'Ribbed modal T-shirt',
                'product_url': '#',
                'product_price': '18.95',
            },
        ]

    context['testimonials'] = testimonials
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
        variante_default_id = None  # Para productos sin atributos
        
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
            else:
                # Variante default (sin talla) para productos sin atributos
                variante_default_id = variante.id
                variantes_stock['default'] = {
                    'id': variante.id,
                    'stock': variante.stock,
                    'talla': None,
                    'color': '',
                    'precio': str(variante.precio) if variante.precio else str(producto.precio_base)
                }
                print(f"DEBUG Backend - Variante DEFAULT: ID={variante.id} - Stock: {variante.stock} - Precio: {variante.precio}")
        
        variantes_json = json.dumps(variantes_stock)
        print(f"DEBUG Backend - Variantes JSON completo: {variantes_json}")
        
        context = {
            'producto': producto,
            'imagenes': imagenes,
            'variantes': variantes,
            'variantes_json': variantes_json,
            'variante_default_id': variante_default_id,  # Para productos sin atributos
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
        # Obtener stock de la variante
        stock = 0
        if item['variante_id']:
            try:
                from apps.productos.models import Variante
                variante = Variante.objects.get(id=item['variante_id'])
                stock = variante.stock
            except:
                stock = 0
        
        items.append({
            'product_id': f"{item['producto_id']}_{item['variante_id']}" if item['variante_id'] else str(item['producto_id']),
            'producto_id': item['producto_id'],
            'variante_id': item['variante_id'],
            'nombre': item['nombre'],
            'precio': str(item['precio_decimal']),
            'quantity': item['quantity'],
            'total': str(item['total_precio']),
            'imagen': item['imagen'],
            'talla': item.get('talla'),
            'stock': stock,
        })
    
    return JsonResponse({
        'success': True,
        'items': items,
        'cart_count': len(cart),
        'cart_total': str(cart.get_total_price()),
        'note': cart.get_note(),
        'has_gift_wrap': cart.has_gift_wrap()
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


def cart_save_note(request):
    """
    Vista para guardar una nota en el pedido
    """
    if request.method == 'POST':
        cart = Cart(request)
        note = request.POST.get('note', '')
        cart.set_note(note)
        
        return JsonResponse({
            'success': True,
            'message': 'Nota guardada correctamente',
            'note': note
        })
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


def cart_add_gift_wrap(request):
    """
    Vista para agregar gift wrap al carrito
    """
    if request.method == 'POST':
        cart = Cart(request)
        cart.set_gift_wrap(True)
        
        return JsonResponse({
            'success': True,
            'message': 'Gift wrap agregado',
            'cart_total': str(cart.get_total_price()),
            'gift_wrap_cost': '5.00'
        })
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


def cart_remove_gift_wrap(request):
    """
    Vista para remover gift wrap del carrito
    """
    if request.method == 'POST':
        cart = Cart(request)
        cart.set_gift_wrap(False)
        
        return JsonResponse({
            'success': True,
            'message': 'Gift wrap removido',
            'cart_total': str(cart.get_total_price())
        })
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


def view_cart(request):
    """
    Vista para mostrar la página completa del carrito (view-cart.html)
    """
    from apps.productos.models import Variante, Producto
    
    cart = Cart(request)
    cart_items = []
    
    for item in cart:
        # Obtener stock de la variante
        stock = 0
        if item['variante_id']:
            try:
                variante = Variante.objects.get(id=item['variante_id'])
                stock = variante.stock
            except:
                stock = 0
        else:
            # Si no hay variante_id, buscar la variante default del producto
            try:
                producto_obj = Producto.objects.get(id=item['producto_id'])
                variante_default = producto_obj.variantes.first()  # Primera variante (default)
                if variante_default:
                    stock = variante_default.stock
            except:
                stock = 0
        
        cart_items.append({
            'product_id': f"{item['producto_id']}_{item['variante_id']}" if item['variante_id'] else str(item['producto_id']),
            'producto': item['producto'],
            'producto_id': item['producto_id'],
            'variante_id': item['variante_id'],
            'nombre': item['nombre'],
            'precio': item['precio_decimal'],
            'quantity': item['quantity'],
            'total': item['total_precio'],
            'imagen': item['imagen'],
            'talla': item.get('talla'),
            'color': item.get('color'),
            'stock': stock,
        })
    
    # Obtener productos recomendados (productos aleatorios activos)
    productos_recomendados = Producto.objects.filter(
        activo=True
    ).prefetch_related('imagenes', 'variantes').order_by('?')[:8]
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
        'note': cart.get_note(),
        'has_gift_wrap': cart.has_gift_wrap(),
        'productos_recomendados': productos_recomendados,
    }
    
    return render(request, 'view-cart.html', context)


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

    # Intentar restringir a categoría 'Ropa' y sus subcategorías, si existe
    from apps.productos.models import Categoria
    try:
        categoria_ropa_ajax = Categoria.objects.filter(nombre__icontains='ropa', padre__isnull=True, estado=True).first()
    except Exception:
        categoria_ropa_ajax = None

    if categoria_ropa_ajax:
        sub_ids_ajax = list(categoria_ropa_ajax.subcategorias.filter(estado=True).values_list('id', flat=True))
        categorias_ajax_ids = sub_ids_ajax + [categoria_ropa_ajax.id]
        qs = (
            Producto.objects
            .filter(activo=True, categoria_id__in=categorias_ajax_ids)
            .select_related('categoria', 'coleccion')
            .prefetch_related('imagenes', 'variantes', 'variantes__talla', 'variantes__atributos__valor_atributo__atributo')
            .annotate(precio_minimo=Min('variantes__precio'))
            .order_by('-created_at')
        )
    else:
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


# ==================== CHECKOUT VIEWS ====================

def checkout(request):
    """
    Vista para mostrar la página de checkout
    """
    from apps.productos.models import Variante, Producto
    
    cart = Cart(request)
    
    # Verificar si el carrito está vacío
    if len(cart) == 0:
        messages.warning(request, 'Tu carrito está vacío. Agrega productos antes de continuar.')
        return redirect('core:view_cart')
    
    # Preparar items del carrito para el template
    cart_items = []
    for item in cart:
        cart_items.append({
            'product_id': f"{item['producto_id']}_{item['variante_id']}" if item['variante_id'] else str(item['producto_id']),
            'producto': item['producto'],
            'producto_id': item['producto_id'],
            'variante_id': item['variante_id'],
            'nombre': item['nombre'],
            'precio': item['precio_decimal'],
            'quantity': item['quantity'],
            'total': item['total_precio'],
            'imagen': item['imagen'],
            'talla': item.get('talla'),
            'color': item.get('color'),
        })
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
        'note': cart.get_note(),
        'has_gift_wrap': cart.has_gift_wrap(),
    }
    
    return render(request, 'checkout.html', context)


def checkout_process(request):
    """
    Vista para procesar el pedido del checkout
    """
    if request.method != 'POST':
        return redirect('core:checkout')
    
    from apps.productos.models import Variante, Producto
    from .models import Pedido, DetallePedido
    from decimal import Decimal
    
    cart = Cart(request)
    
    # Verificar si el carrito está vacío
    if len(cart) == 0:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('core:view_cart')
    
    try:
        # Obtener datos del formulario
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        country = request.POST.get('country', 'Ecuador').strip()  # Siempre Ecuador
        city = request.POST.get('city', '').strip()
        other_city = request.POST.get('other_city', '').strip()
        address = request.POST.get('address', '').strip()
        order_note = request.POST.get('order_note', '').strip()
        payment_method = request.POST.get('payment_method', 'bank_transfer')
        
        # Si seleccionó "Otra ciudad", usar el campo other_city
        if city == 'Otra' and other_city:
            city = other_city
        
        # Validar campos requeridos
        if not all([first_name, last_name, email, phone, city, address]):
            messages.error(request, 'Por favor, completa todos los campos requeridos.')
            return redirect('core:checkout')
        
        # Calcular totales
        subtotal = cart.get_total_price()
        gift_wrap = cart.has_gift_wrap()
        gift_wrap_cost = Decimal('5.00') if gift_wrap else Decimal('0.00')
        
        # Aplicar código de descuento si existe
        discount_code = request.POST.get('discount_code_applied', '').strip()
        discount_amount = Decimal(request.POST.get('discount_amount', '0'))
        
        # Validar código de descuento si se proporcionó
        if discount_code:
            from .models import CodigoDescuento
            try:
                codigo = CodigoDescuento.objects.get(codigo=discount_code)
                es_valido, mensaje = codigo.es_valido(subtotal)
                if not es_valido:
                    messages.warning(request, f'El código de descuento ya no es válido: {mensaje}')
                    discount_amount = Decimal('0')
                    discount_code = ''
                else:
                    # Incrementar uso del código
                    codigo.usos_actuales += 1
                    codigo.save()
            except CodigoDescuento.DoesNotExist:
                messages.warning(request, 'El código de descuento no es válido')
                discount_amount = Decimal('0')
                discount_code = ''
        
        total = subtotal + gift_wrap_cost - discount_amount
        
        # Crear el pedido
        pedido = Pedido.objects.create(
            usuario=request.user if request.user.is_authenticated else None,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            country=country,
            city=city,
            address=address,
            order_note=order_note,
            metodo_pago=payment_method,
            subtotal=subtotal,
            gift_wrap=gift_wrap,
            gift_wrap_cost=gift_wrap_cost,
            discount_code=discount_code if discount_code else None,
            discount_amount=discount_amount,
            total=total,
            estado='pendiente'
        )
        
        # Crear los detalles del pedido
        for item in cart:
            DetallePedido.objects.create(
                pedido=pedido,
                producto=item['producto'],
                variante_id=item['variante_id'],
                nombre_producto=item['nombre'],
                talla=item.get('talla'),
                color=item.get('color'),
                precio_unitario=item['precio_decimal'],
                cantidad=item['quantity'],
                subtotal=item['total_precio'],
                imagen_url=item['imagen']
            )
            
            # Actualizar stock de la variante
            if item['variante_id']:
                try:
                    variante = Variante.objects.get(id=item['variante_id'])
                    if variante.stock >= item['quantity']:
                        variante.stock -= item['quantity']
                        variante.save()
                except Variante.DoesNotExist:
                    pass
        
        # Limpiar el carrito
        cart.clear()
        
        # Mensaje de éxito
        messages.success(
            request,
            f'¡Pedido realizado con éxito! Tu número de pedido es: {pedido.numero_pedido}'
        )
        
        # Redirigir a página de confirmación
        return redirect('core:order_confirmation', pedido_id=pedido.id)
        
    except Exception as e:
        messages.error(request, f'Error al procesar el pedido: {str(e)}')
        return redirect('core:checkout')


def order_confirmation(request, pedido_id):
    """
    Vista para mostrar la confirmación del pedido
    """
    from django.shortcuts import get_object_or_404
    from .models import Pedido
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar que el pedido pertenece al usuario (si está autenticado)
    if request.user.is_authenticated and pedido.usuario and pedido.usuario != request.user:
        messages.error(request, 'No tienes permiso para ver este pedido.')
        return redirect('core:inicio')
    
    context = {
        'pedido': pedido,
    }
    
    return render(request, 'order-confirmation.html', context)


@require_POST
def validate_discount_code(request):
    """
    Vista AJAX para validar códigos de descuento
    """
    from .models import CodigoDescuento
    from decimal import Decimal
    
    discount_code = request.POST.get('discount_code', '').strip().upper()
    
    if not discount_code:
        return JsonResponse({
            'valid': False,
            'message': 'Por favor ingresa un código de descuento'
        })
    
    try:
        codigo = CodigoDescuento.objects.get(codigo=discount_code)
        
        # Obtener monto del carrito
        cart = Cart(request)
        cart_total = cart.get_total_price()
        
        # Validar el código
        es_valido, mensaje = codigo.es_valido(cart_total)
        
        if not es_valido:
            return JsonResponse({
                'valid': False,
                'message': mensaje
            })
        
        # Calcular descuento
        discount_amount = codigo.calcular_descuento(cart_total)
        
        return JsonResponse({
            'valid': True,
            'discount_amount': float(discount_amount),
            'discount_type': codigo.tipo,
            'discount_value': float(codigo.valor),
            'message': 'Código válido'
        })
        
    except CodigoDescuento.DoesNotExist:
        return JsonResponse({
            'valid': False,
            'message': 'El código de descuento no existe'
        })