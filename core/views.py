from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Min, Sum, Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

# Import Producto model to build the shop listing
from apps.productos.models import Producto

# Importar decoradores de seguridad
from .decorators import admin_required, superuser_required


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
        
        # Imagen principal (solo imágenes, no videos)
        imagenes = list(producto.imagenes.filter(tipo_medio='imagen')[:2])
        if imagenes:
            producto.main_image_src = imagenes[0].src
            producto.hover_image_src = imagenes[1].src if len(imagenes) > 1 else producto.main_image_src
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

        imagenes = list(producto.imagenes.filter(tipo_medio='imagen')[:2])
        if imagenes:
            producto.main_image_src = imagenes[0].src
            producto.hover_image_src = imagenes[1].src if len(imagenes) > 1 else producto.main_image_src
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
        imagenes = list(p.imagenes.filter(tipo_medio='imagen')[:2])
        if imagenes:
            # usar la propiedad .src si está disponible, fallback a .imagen.url
            p.main_image_src = getattr(imagenes[0], 'src', None) or (imagenes[0].src)
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
                from django.urls import reverse
                try:
                    product_url = reverse('productos:producto_detail', kwargs={'slug': getattr(producto, 'slug')})
                except Exception:
                    product_url = f'/producto/{getattr(producto, "slug", getattr(producto, "id", ""))}/'
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

def about_us(request):
    from apps.productos.models import Categoria
    from .models import AboutUs
    
    about_us_config = AboutUs.objects.filter(activo=True).first()
    
    if not about_us_config:
        about_us_config = AboutUs.objects.create(
            mision_titulo='Our mission',
            mision_texto='...',
            activo=True
        )
    
    # Ahora esto funcionará correctamente
    imagenes_slider = about_us_config.imagenes_slider.filter(activo=True).order_by('posicion')
    
    categorias_menu = (
        Categoria.objects
        .filter(estado=True, padre__isnull=True)
        .prefetch_related('subcategorias')
        .order_by('nombre')
    )
    
    context = {
        'categorias_menu': categorias_menu,
        'about_us': about_us_config,
        'imagenes_slider': imagenes_slider,
    }
    return render(request, 'about-us.html', context)


def contacto(request):
    """Vista para la página de Contacto"""
    from apps.productos.models import Categoria
    
    # Obtener categorías con subcategorías para el menú de navegación
    categorias_menu = (
        Categoria.objects
        .filter(estado=True, padre__isnull=True)
        .prefetch_related('subcategorias')
        .order_by('nombre')
    )
    
    context = {
        'categorias_menu': categorias_menu,
    }
    return render(request, 'contact-2.html', context)


def shop_collection_sub(request):
    """Lista de productos para la plantilla `shop-collection-sub.html`.

    - Filtra por categoría si se pasa `?categoria=<id_or_slug>`
    - Filtra por colección si se pasa `?coleccion=<slug>`
    - Ordena por id (asc)
    - Anota precio mínimo de variantes y stock total
    - Prepara campos auxiliares que la plantilla espera: display_price, main_image_src,
      hover_image_src, colors, availability
    - Envía categorías o subcategorías según el contexto
    """
    from apps.productos.models import Categoria, Coleccion
    
    categoria_param = request.GET.get('categoria')
    coleccion_param = request.GET.get('coleccion')
    categoria_actual = None
    coleccion_actual = None
    categorias_a_mostrar = []

    qs = (
        Producto.objects
        .filter(activo=True)
        .select_related('categoria', 'coleccion')
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

    # Filtrar por colección si se especifica
    if coleccion_param:
        coleccion_actual = Coleccion.objects.filter(slug=coleccion_param).first()
        if coleccion_actual:
            qs = qs.filter(coleccion=coleccion_actual)
            print(f"DEBUG: Filtrando por colección: {coleccion_actual.nombre}")

    # Filtrar por categoría si se especifica
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
    elif coleccion_actual:
        # Si se filtra por colección, mostrar las subcategorías de Ropa
        try:
            categoria_ropa = Categoria.objects.get(slug='ropa', estado=True)
            categorias_a_mostrar = list(
                Categoria.objects.filter(
                    padre=categoria_ropa,
                    estado=True
                ).order_by('nombre')
            )
            print(f"DEBUG: Filtrando por colección, mostrando subcategorías de Ropa: {len(categorias_a_mostrar)}")
        except Categoria.DoesNotExist:
            # Si no existe la categoría Ropa, mostrar categorías principales
            categorias_a_mostrar = list(
                Categoria.objects.filter(
                    padre__isnull=True,
                    estado=True
                ).order_by('nombre')
            )
            print(f"DEBUG: Categoría Ropa no encontrada, mostrando principales: {len(categorias_a_mostrar)}")
    else:
        # Si no hay categoría ni colección seleccionada, mostrar subcategorías de Ropa por defecto
        try:
            categoria_ropa = Categoria.objects.get(slug='ropa', estado=True)
            categorias_a_mostrar = list(
                Categoria.objects.filter(
                    padre=categoria_ropa,
                    estado=True
                ).order_by('nombre')
            )
            print(f"DEBUG: Sin filtros, mostrando subcategorías de Ropa: {len(categorias_a_mostrar)}")
        except Categoria.DoesNotExist:
            # Si no existe la categoría Ropa, mostrar categorías principales
            categorias_a_mostrar = list(
                Categoria.objects.filter(
                    padre__isnull=True,
                    estado=True
                ).order_by('nombre')
            )
            print(f"DEBUG: Sin filtros y Ropa no encontrada, mostrando principales: {len(categorias_a_mostrar)}")
    
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
            p.availability = 'En stock' if (total_stock is not None and total_stock > 0) else 'Agotado'
        except Exception:
            p.availability = 'En stock'

    return render(request, 'shop-collection-sub.html', {
        'productos': productos,
        'categoria_actual': categoria_actual,
        'coleccion_actual': coleccion_actual,
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


@admin_required
def dashboard_redirect(request):
    """Redirección al dashboard si el usuario es admin"""
    return redirect('core:admin_index')


@admin_required
def admin_index(request):
    """Renderiza el índice del panel administrativo con métricas consolidadas."""
    from .services.admin_dashboard_service import get_admin_dashboard_context

    context = get_admin_dashboard_context()
    return render(request, 'pindex.html', context)


def product_detail(request, slug=None):
    """Vista para mostrar los detalles de un producto"""
    from django.shortcuts import get_object_or_404
    from apps.productos.models import Producto
    
    if slug:
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
            slug=slug,
            activo=True
        )
        
        # Obtener todas las imágenes del producto
        imagenes = list(producto.imagenes.all())
        
        print(f"DEBUG - Total imágenes del producto: {len(imagenes)}")
        
        # Obtener todas las variantes
        variantes = list(producto.variantes.all())
        print(f"DEBUG - Producto ID: {producto.id}, Nombre: {producto.nombre}")
        print(f"DEBUG - Total variantes encontradas: {len(variantes)}")
        for v in variantes:
            print(f"DEBUG - Variante ID: {v.id}, Talla: {v.talla}, Color: {v.color}, Stock: {v.stock}")
        
        # Extraer tallas únicas (solo variantes con stock > 0)
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
            imagenes_rel = list(prod.imagenes.filter(tipo_medio='imagen')[:2])
            if imagenes_rel:
                prod.main_image = imagenes_rel[0]
                prod.main_image_src = imagenes_rel[0].imagen.url if imagenes_rel[0].imagen else None
                prod.hover_image = imagenes_rel[1] if len(imagenes_rel) > 1 else None
                prod.hover_image_src = imagenes_rel[1].imagen.url if len(imagenes_rel) > 1 and imagenes_rel[1].imagen else None
            else:
                prod.main_image_src = None
                prod.hover_image_src = None
            
            prod.display_price = prod.precio_minimo if prod.precio_minimo else prod.precio_base
            
            # Obtener tallas del producto relacionado
            prod_variantes = list(prod.variantes.all())
            
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
            imagenes_rec = list(prod.imagenes.filter(tipo_medio='imagen')[:2])
            if imagenes_rec:
                prod.main_image_src = imagenes_rec[0].imagen.url if imagenes_rec[0].imagen else None
                prod.hover_image_src = imagenes_rec[1].imagen.url if len(imagenes_rec) > 1 and imagenes_rec[1].imagen else None
            else:
                prod.main_image_src = None
                prod.hover_image_src = None
            
            prod.display_price = prod.precio_minimo if prod.precio_minimo else prod.precio_base
            
            # Tallas
            prod_variantes_rec = list(prod.variantes.all())
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
        variantes_map = {}  # Mapa COLOR-TALLA -> datos variante
        variante_default_id = None  # Para productos sin atributos
        
        for variante in variantes:
            if variante.talla:
                key = f"{variante.talla.codigo}"
                
                variantes_stock[key] = {
                    'id': variante.id,
                    'stock': variante.stock,
                    'talla': variante.talla.codigo if variante.talla else None,
                    'precio': str(variante.precio) if variante.precio else str(producto.precio_base)
                }
                
                # Obtener imagen asociada a esta variante
                imagen_url = None
                imagenes_variante = producto.imagenes.filter(variante=variante)
                if imagenes_variante.exists():
                    imagen_url = imagenes_variante.first().imagen.url
                elif imagenes:  # Fallback a primera imagen
                    imagen_url = imagenes[0].src
                
                variantes_map[key] = {
                    'stock': variante.stock,
                    'precio': str(variante.precio) if variante.precio else str(producto.precio_base),
                    'imagen': imagen_url,
                    'id': variante.id,
                    'talla': variante.talla.codigo if variante.talla else None
                }
                
                # Debug: imprimir información de la variante
                print(f"DEBUG Backend - Talla '{key}' - Stock: {variante.stock} - Precio: {variante.precio} - Imagen: {imagen_url}")
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
        variantes_map_json = json.dumps(variantes_map)
        print(f"DEBUG Backend - Variantes JSON completo: {variantes_json}")
        print(f"DEBUG Backend - Variantes MAP JSON: {variantes_map_json}")
        
        # Verificar si el producto está en el wishlist del usuario
        in_wishlist = False
        wishlist_item_id = None
        if request.user.is_authenticated:
            from apps.usuarios.models import Wishlist
            wishlist_item = Wishlist.objects.filter(
                usuario=request.user,
                producto=producto
            ).first()
            if wishlist_item:
                in_wishlist = True
                wishlist_item_id = wishlist_item.id
        
        context = {
            'producto': producto,
            'imagenes': imagenes,
            'variantes': variantes,
            'variantes_map_json': variantes_map_json,  # Mapa completo de variantes para JS
            'tallas_disponibles': tallas_disponibles,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'tiene_descuento': tiene_descuento,
            'productos_relacionados': productos_relacionados,
            'productos_recientes': productos_recientes,
            'global_content': global_content,
            'shipping_info': shipping_info,
            'return_policies': return_policies,
            'in_wishlist': in_wishlist,
            'wishlist_item_id': wishlist_item_id,
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
            'producto_slug': item.get('producto_slug', ''),  # Agregar el slug del producto
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

        imagenes = list(producto.imagenes.filter(tipo_medio='imagen')[:2])
        if imagenes:
            producto.main_image_src = imagenes[0].src
            producto.hover_image_src = imagenes[1].src if len(imagenes) > 1 else producto.main_image_src
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
    from apps.usuarios.models import Ciudad, Provincia
    
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
    
    # Obtener todas las provincias y ciudades de la BD
    provincias = Provincia.objects.all().order_by('nombre')
    ciudades = Ciudad.objects.select_related('provincia').all().order_by('provincia__nombre', 'nombre')
    
    # Obtener datos del usuario registrado si existe
    user_provincia = None
    user_ciudad = None
    user_nombre = None
    user_apellido = None
    user_email = None
    user_telefono = None
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'provincia') and request.user.provincia:
            user_provincia = request.user.provincia.id
        if hasattr(request.user, 'ciudad') and request.user.ciudad:
            user_ciudad = request.user.ciudad.nombre
        if hasattr(request.user, 'nombre') and request.user.nombre:
            user_nombre = request.user.nombre
        if hasattr(request.user, 'apellido') and request.user.apellido:
            user_apellido = request.user.apellido
        if hasattr(request.user, 'email') and request.user.email:
            user_email = request.user.email
        if hasattr(request.user, 'telefono') and request.user.telefono:
            user_telefono = request.user.telefono
    
    # Verificar si el usuario tiene cupón de carnaval disponible
    carnival_discount = 0
    carnival_coupon_available = False
    from datetime import datetime
    now = datetime.now()
    
    # TEMPORAL: Permitir en enero (mes 1) y febrero (mes 2) para pruebas
    if request.user.is_authenticated and now.year == 2026 and now.month in [1, 2]:
        if hasattr(request.user, 'has_carnival_coupon_available'):
            carnival_coupon_available = request.user.has_carnival_coupon_available()
            if carnival_coupon_available:
                # Calcular 10% de descuento sobre el subtotal
                from decimal import Decimal
                subtotal = cart.get_total_price()
                carnival_discount = subtotal * Decimal('0.10')
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
        'provincias': provincias,
        'ciudades': ciudades,
        'user_provincia_id': user_provincia,
        'user_ciudad_name': user_ciudad,
        'user_nombre': user_nombre,
        'user_apellido': user_apellido,
        'user_email': user_email,
        'user_telefono': user_telefono,
        'note': cart.get_note(),
        'has_gift_wrap': cart.has_gift_wrap(),
        'carnival_coupon_available': carnival_coupon_available,
        'carnival_discount': carnival_discount,
    }
    
    return render(request, 'checkout.html', context)


def calculate_shipping(request):
    """
    Vista AJAX para calcular el costo de envío según la ciudad seleccionada y el total del carrito.
    
    Lógica:
    - Machala + total > $50 = Envío gratis
    - Machala + total <= $50 = Envío $3
    - Otra ciudad + total >= $90 = Envío gratis
    - Otra ciudad + total < $90 = Envío $7
    """
    from decimal import Decimal
    import logging
    
    logger = logging.getLogger(__name__)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        city = request.POST.get('city', '').strip()
        cart_total_str = request.POST.get('cart_total', '0')
        cart_total = Decimal(cart_total_str)
        
        logger.info(f'📦 ENVÍO: city={city}, cart_total_str={cart_total_str}, cart_total={cart_total}')
        
        if not city:
            return JsonResponse({'error': 'Ciudad no especificada'}, status=400)
        
        shipping_cost = Decimal('0')
        free_shipping = False
        
        if city.lower() == 'machala':
            # Machala: gratis si > $50, sino $3
            if cart_total > Decimal('50'):
                shipping_cost = Decimal('0')
                free_shipping = True
                logger.info(f'✅ Machala: {cart_total} > $50 → Gratis')
            else:
                shipping_cost = Decimal('3')
                logger.info(f'✅ Machala: {cart_total} <= $50 → $3')
        else:
            # Otras ciudades: gratis si >= $90, sino $7
            if cart_total >= Decimal('90'):
                shipping_cost = Decimal('0')
                free_shipping = True
                logger.info(f'✅ {city}: {cart_total} >= $90 → Gratis')
            else:
                shipping_cost = Decimal('7')
                logger.info(f'✅ {city}: {cart_total} < $90 → $7')
        
        total_with_shipping = cart_total + shipping_cost
        
        return JsonResponse({
            'success': True,
            'shipping_cost': float(shipping_cost),
            'free_shipping': free_shipping,
            'total_with_shipping': float(total_with_shipping),
            'message': 'Envío gratis' if free_shipping else f'Envío: ${shipping_cost}'
        })
    
    except Exception as e:
        logger.error(f'❌ Error al calcular envío: {str(e)}', exc_info=True)
        return JsonResponse({
            'error': f'Error al calcular envío: {str(e)}'
        }, status=400)



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
        
        # Obtener costo de envío (puede venir del formulario)
        shipping_cost = Decimal(request.POST.get('shipping_cost', '0'))
        
        # Aplicar código de descuento si existe
        discount_code = request.POST.get('discount_code_applied', '').strip()
        discount_amount = Decimal(request.POST.get('discount_amount', '0'))
        
        # 🎭 CUPÓN DE CARNAVAL AUTOMÁTICO - FEBRERO 2026
        carnival_discount_applied = False
        from datetime import datetime
        now = datetime.now()
        
        # TEMPORAL: Permitir en enero (mes 1) y febrero (mes 2) para pruebas
        if request.user.is_authenticated and now.year == 2026 and now.month in [1, 2]:
            if hasattr(request.user, 'has_carnival_coupon_available') and request.user.has_carnival_coupon_available():
                # Aplicar 10% de descuento automáticamente
                carnival_discount = subtotal * Decimal('0.10')
                discount_amount += carnival_discount
                discount_code = 'CARNAVAL2026' if not discount_code else f'{discount_code}+CARNAVAL2026'
                carnival_discount_applied = True
                print(f'🎭 Cupón de carnaval aplicado: ${carnival_discount}')
        
        # Validar código de descuento manual si se proporcionó (además del carnival)
        if discount_code and 'CARNAVAL2026' not in discount_code:
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
        
        # Total = subtotal + envío + regalo - descuento
        total = subtotal + shipping_cost + gift_wrap_cost - discount_amount
        
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
            shipping_cost=shipping_cost,
            gift_wrap=gift_wrap,
            gift_wrap_cost=gift_wrap_cost,
            discount_code=discount_code if discount_code else None,
            discount_amount=discount_amount,
            total=total,
            estado='pendiente'
        )
        
        # Crear los detalles del pedido
        for item in cart:
            # Obtener la variante para guardar la referencia correcta
            variante_obj = None
            if item['variante_id']:
                try:
                    variante_obj = Variante.objects.get(id=item['variante_id'])
                except Variante.DoesNotExist:
                    pass
            
            DetallePedido.objects.create(
                pedido=pedido,
                producto=item['producto'],
                variante=variante_obj,  # Usar el objeto variante en lugar de variante_id
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
        
        # 🎭 Marcar cupón de carnaval como usado
        if carnival_discount_applied and request.user.is_authenticated:
            request.user.carnival_coupon_used_2026 = True
            request.user.carnival_coupon_used_date = now
            request.user.save()
            print(f'✅ Cupón de carnaval marcado como usado para {request.user.email}')
        
        # Asegurar que la sesión se guarde completamente
        request.session.modified = True
        request.session.save()
        
        # 📱 Enviar notificación a WhatsApp del administrador
        from .whatsapp_utils import enviar_notificacion_pedido
        resultado_whatsapp = enviar_notificacion_pedido(pedido)
        
        if resultado_whatsapp.get('success'):
            messages.success(
                request,
                f'✅ ¡Pedido realizado! #{pedido.numero_pedido} | Notificación enviada al admin'
            )
        else:
            messages.success(
                request,
                f'✅ ¡Pedido realizado! #{pedido.numero_pedido}'
            )
        
        # Redirigir a página de confirmación
        return redirect('core:order_confirmation', numero_pedido=pedido.numero_pedido)
        
    except Exception as e:
        import traceback
        print(f'❌ ERROR EN CHECKOUT_PROCESS: {str(e)}')
        print(f'Traceback: {traceback.format_exc()}')
        messages.error(request, f'Error al procesar el pedido: {str(e)}')
        return redirect('core:checkout')


def order_confirmation(request, numero_pedido):
    """
    Vista para mostrar la confirmación del pedido
    """
    from django.shortcuts import get_object_or_404
    from .models import Pedido
    
    pedido = get_object_or_404(Pedido, numero_pedido=numero_pedido)
    
    # Verificar que el pedido pertenece al usuario (si está autenticado)
    if request.user.is_authenticated and pedido.usuario and pedido.usuario != request.user:
        messages.error(request, 'No tienes permiso para ver este pedido.')
        return redirect('core:inicio')
    
    context = {
        'pedido': pedido,
    }
    
    return render(request, 'order-confirmation.html', context)


def get_order_status(request, numero_pedido):
    """
    Endpoint AJAX para obtener el estado actual de un pedido sin recargar la página
    
    Retorna JSON con:
    - estado: estado actual del pedido
    - pagado: boolean si está pagado
    - estado_display: nombre legible del estado
    - fecha_pago: fecha del pago si existe
    """
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    from .models import Pedido
    
    try:
        pedido = get_object_or_404(Pedido, numero_pedido=numero_pedido)
        
        # Verificar permisos
        if request.user.is_authenticated and pedido.usuario and pedido.usuario != request.user:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permiso para ver este pedido.'
            }, status=403)
        
        # Retornar estado actual del pedido
        return JsonResponse({
            'success': True,
            'estado': pedido.estado,
            'estado_display': pedido.get_estado_display(),
            'pagado': pedido.pagado,
            'fecha_pago': pedido.fecha_pago.isoformat() if pedido.fecha_pago else None,
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


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

# ==================== ADMIN ORDER VIEWS ====================
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Pedido

@admin_required
def admin_order_list(request):
    """
    Vista para listar todos los pedidos en el panel de administración con filtros.
    """
    if not request.user.is_staff and not (hasattr(request.user, 'rol') and request.user.rol == 'admin_tienda'):
        return redirect('core:inicio')

    pedidos = Pedido.objects.all().select_related('usuario').prefetch_related('items').order_by('-created_at')
    
    # Filtro por nombre/cliente
    search_query = request.GET.get('q', '')
    if search_query:
        pedidos = pedidos.filter(
            Q(numero_pedido__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filtro por estado
    estado_filter = request.GET.get('estado', '')
    if estado_filter:
        pedidos = pedidos.filter(estado=estado_filter)
    
    # Filtro por pago
    pago_filter = request.GET.get('pago', '')
    if pago_filter == 'pagado':
        pedidos = pedidos.filter(pagado=True)
    elif pago_filter == 'no_pagado':
        pedidos = pedidos.filter(pagado=False)
    
    return render(request, 'oder-list.html', {
        'pedidos': pedidos,
        'search_query': search_query,
        'estado_filter': estado_filter,
        'pago_filter': pago_filter,
    })

@admin_required
def admin_order_detail_select(request):
    """
    Vista para seleccionar un pedido y ver su detalle.
    """
    if not request.user.is_staff and not (hasattr(request.user, 'rol') and request.user.rol == 'admin_tienda'):
        return redirect('core:inicio')
    
    # Si se envía un pedido_id por POST, redirigir al detalle
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        if pedido_id:
            return redirect('core:admin_order_detail', pedido_id=pedido_id)
    
    # Buscar pedidos si hay búsqueda
    search_query = request.GET.get('q', '')
    pedidos = Pedido.objects.all().select_related('usuario').order_by('-created_at')
    
    if search_query:
        pedidos = pedidos.filter(
            Q(numero_pedido__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    return render(request, 'oder-detail-select.html', {
        'pedidos': pedidos[:50],  # Limitar a 50 resultados
        'search_query': search_query
    })

@admin_required
def admin_order_detail(request, pedido_id):
    """
    Vista para ver los detalles de un pedido específico en el panel de administración.
    """
    if not request.user.is_staff and not (hasattr(request.user, 'rol') and request.user.rol == 'admin_tienda'):
        return redirect('core:inicio')

    pedido = get_object_or_404(Pedido.objects.select_related('usuario').prefetch_related('items'), id=pedido_id)
    return render(request, 'oder-detail.html', {'pedido': pedido})

@admin_required
def admin_order_tracking_select(request):
    """
    Vista para seleccionar un pedido y ver su seguimiento.
    """
    if not request.user.is_staff and not (hasattr(request.user, 'rol') and request.user.rol == 'admin_tienda'):
        return redirect('core:inicio')
    
    # Si se envía un pedido_id por POST, redirigir al seguimiento
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        if pedido_id:
            return redirect('core:admin_order_tracking', pedido_id=pedido_id)
    
    # Buscar pedidos si hay búsqueda
    search_query = request.GET.get('q', '')
    pedidos = Pedido.objects.all().select_related('usuario').order_by('-created_at')
    
    if search_query:
        pedidos = pedidos.filter(
            Q(numero_pedido__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    return render(request, 'oder-tracking-select.html', {
        'pedidos': pedidos[:50],  # Limitar a 50 resultados
        'search_query': search_query
    })

@admin_required
def admin_order_tracking(request, pedido_id):
    """
    Vista para el seguimiento de un pedido específico.
    """
    pedido = get_object_or_404(Pedido.objects.select_related('usuario').prefetch_related('items'), id=pedido_id)
    return render(request, 'oder-tracking.html', {'pedido': pedido})

@admin_required
@require_POST
def admin_order_mark_paid(request, pedido_id):
    """
    Vista para marcar un pedido como pagado.
    Se puede marcar cualquier pedido como pagado, independientemente de su estado.
    """
    if not request.user.is_staff and not (hasattr(request.user, 'rol') and request.user.rol == 'admin_tienda'):
        return JsonResponse({'success': False, 'message': 'No tienes permiso'}, status=403)
    
    from django.utils import timezone
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar si ya está pagado
    if pedido.pagado:
        return JsonResponse({
            'success': False, 
            'message': 'Este pedido ya está marcado como pagado'
        }, status=400)
    
    # Marcar como pagado
    pedido.pagado = True
    pedido.fecha_pago = timezone.now()
    pedido.save()
    
    messages.success(request, f'Pedido {pedido.numero_pedido} marcado como pagado.')
    
    return JsonResponse({
        'success': True,
        'message': 'Pedido marcado como pagado exitosamente'
    })

@admin_required
@csrf_protect
@require_POST
def admin_order_update_status(request, pedido_id):
    """
    Vista para actualizar el estado del pedido (procesando, enviado, entregado).
    Solo accessible para staff/admin.
    """
    
    import json
    from django.utils import timezone
    
    try:
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        
        # Validar estado
        estados_validos = ['procesando', 'enviado', 'entregado']
        if nuevo_estado not in estados_validos:
            return JsonResponse({
                'success': False,
                'message': 'Estado inválido. Debe ser: procesando, enviado o entregado'
            }, status=400)
        
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        # Validar transición de estados
        transiciones = {
            'pendiente': ['procesando', 'cancelado'],
            'procesando': ['enviado', 'cancelado'],
            'enviado': ['entregado'],
            'entregado': [],
            'cancelado': []
        }
        
        if nuevo_estado not in transiciones.get(pedido.estado, []):
            return JsonResponse({
                'success': False,
                'message': f'No se puede cambiar de {pedido.get_estado_display()} a {dict(Pedido.ESTADO_CHOICES).get(nuevo_estado, nuevo_estado)}'
            }, status=400)
        
        # Cambiar estado
        pedido.estado = nuevo_estado
        pedido.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Estado actualizado a {pedido.get_estado_display()}',
            'nuevo_estado': nuevo_estado,
            'nuevo_estado_display': pedido.get_estado_display()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)

@admin_required
@require_POST
def admin_order_cancel(request, pedido_id):
    """
    Vista para cancelar un pedido y devolver el stock.
    """
    
    from apps.productos.models import Variante
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar si ya está cancelado
    if pedido.estado == 'cancelado':
        return JsonResponse({
            'success': False, 
            'message': 'Este pedido ya está cancelado'
        }, status=400)
    
    # Verificar si ya está pagado
    if pedido.pagado:
        return JsonResponse({
            'success': False, 
            'message': 'No se puede cancelar un pedido que ya está pagado'
        }, status=400)
    
    stock_returned = []
    
    try:
        # Devolver stock de cada item del pedido
        for item in pedido.items.all():
            if item.variante:
                try:
                    # Usar la referencia directa a la variante
                    variante = item.variante
                    variante.stock += item.cantidad
                    variante.save()
                    
                    stock_returned.append(f"• {item.nombre_producto} ({item.talla or 'Sin talla'}, {item.color or 'Sin color'}): +{item.cantidad} unidades")
                except Exception as e:
                    # Si hay algún error, registrar pero continuar
                    stock_returned.append(f"• {item.nombre_producto}: Error al devolver stock - {str(e)}")
            elif hasattr(item, 'variante_id') and item.variante_id:
                # Fallback: usar variante_id si existe (compatibilidad con pedidos antiguos)
                try:
                    variante = Variante.objects.get(id=item.variante_id)
                    variante.stock += item.cantidad
                    variante.save()
                    
                    stock_returned.append(f"• {item.nombre_producto} ({item.talla or 'Sin talla'}, {item.color or 'Sin color'}): +{item.cantidad} unidades")
                except Variante.DoesNotExist:
                    stock_returned.append(f"• {item.nombre_producto}: Variante no encontrada (no se pudo devolver stock)")
            else:
                stock_returned.append(f"• {item.nombre_producto}: Sin variante asociada (no se pudo devolver stock)")
        
        # Marcar pedido como cancelado
        pedido.estado = 'cancelado'
        pedido.save()
        
        messages.success(request, f'Pedido {pedido.numero_pedido} cancelado y stock devuelto.')
        
        return JsonResponse({
            'success': True,
            'message': 'Pedido cancelado exitosamente',
            'stock_returned': '\n'.join(stock_returned) if stock_returned else 'No se encontraron productos para devolver stock'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al cancelar el pedido: {str(e)}'
        }, status=500)


# ==================== GESTIÓN DE USUARIOS ====================

@admin_required
def admin_user_list(request):
    """Lista todos los usuarios del sistema"""
    from apps.usuarios.models import Usuario
    
    # Verificar permisos de administrador
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('core:inicio')
    
    # Obtener parámetros de búsqueda y filtros
    search_query = request.GET.get('q', '')
    rol_filtro = request.GET.get('rol', '')
    estado_filtro = request.GET.get('estado', '')
    
    # Construir queryset base
    usuarios = Usuario.objects.all().order_by('-fecha_registro')
    
    # Aplicar filtros de búsqueda
    if search_query:
        usuarios = usuarios.filter(
            Q(email__icontains=search_query) |
            Q(nombre__icontains=search_query) |
            Q(apellido__icontains=search_query) |
            Q(telefono__icontains=search_query) |
            Q(ciudad__icontains=search_query)
        )
    
    # Aplicar filtro por rol
    if rol_filtro:
        usuarios = usuarios.filter(rol=rol_filtro)
    
    # Aplicar filtro por estado
    if estado_filtro == 'activo':
        usuarios = usuarios.filter(is_active=True)
    elif estado_filtro == 'inactivo':
        usuarios = usuarios.filter(is_active=False)
    
    # Paginación
    paginator = Paginator(usuarios, 20)  # 20 usuarios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener choices para los filtros
    rol_choices = Usuario.ROLES
    
    context = {
        'usuarios': page_obj,
        'search_query': search_query,
        'rol_filtro': rol_filtro,
        'estado_filtro': estado_filtro,
        'rol_choices': rol_choices,
        'total_usuarios': usuarios.count(),
    }
    
    return render(request, 'all-user.html', context)


@admin_required
def admin_user_detail(request, user_id):
    """Vista detallada de un usuario específico"""
    from apps.usuarios.models import Usuario
    from django.shortcuts import get_object_or_404
    
    usuario = get_object_or_404(Usuario, id=user_id)
    
    # Obtener pedidos del usuario
    pedidos_usuario = Pedido.objects.filter(
        Q(email=usuario.email) | 
        Q(first_name=usuario.nombre, last_name=usuario.apellido)
    ).order_by('-fecha_pedido')[:10]  # Últimos 10 pedidos
    
    context = {
        'usuario': usuario,
        'pedidos_usuario': pedidos_usuario,
        'total_pedidos': pedidos_usuario.count(),
    }
    
    return render(request, 'user-detail.html', context)


@admin_required
def admin_user_edit(request, user_id):
    """Vista para editar un usuario del sistema"""
    from apps.usuarios.models import Usuario, Ciudad, Provincia
    from django.shortcuts import get_object_or_404
    
    usuario = get_object_or_404(Usuario, id=user_id)
    
    if request.method == 'POST':
        # Actualizar información personal
        usuario.nombre = request.POST.get('nombre', usuario.nombre)
        usuario.apellido = request.POST.get('apellido', usuario.apellido)
        usuario.telefono = request.POST.get('telefono', usuario.telefono)
        usuario.rol = request.POST.get('rol', usuario.rol)
        usuario.is_active = request.POST.get('is_active') == 'on'
        usuario.is_staff = request.POST.get('is_staff') == 'on'
        
        # Actualizar provincia y ciudad
        provincia_id = request.POST.get('provincia')
        ciudad_id = request.POST.get('ciudad')
        
        if provincia_id:
            try:
                usuario.provincia = Provincia.objects.get(id=provincia_id)
            except Provincia.DoesNotExist:
                pass
        
        if ciudad_id:
            try:
                usuario.ciudad = Ciudad.objects.get(id=ciudad_id)
            except Ciudad.DoesNotExist:
                pass
        
        # Actualizar contraseña si se proporciona
        nueva_password = request.POST.get('nueva_password')
        if nueva_password:
            usuario.set_password(nueva_password)
        
        try:
            usuario.save()
            messages.success(request, f'Usuario {usuario.email} actualizado exitosamente.')
            return redirect('core:admin_user_detail', user_id=usuario.id)
        except Exception as e:
            messages.error(request, f'Error al actualizar el usuario: {str(e)}')
    
    # Obtener todas las provincias y ciudades para los selectores
    provincias = Provincia.objects.filter(activa=True).order_by('nombre')
    ciudades = Ciudad.objects.filter(activa=True).order_by('nombre')
    
    context = {
        'usuario': usuario,
        'provincias': provincias,
        'ciudades': ciudades,
        'roles': Usuario.ROLES,
    }
    
    return render(request, 'edit-user.html', context)


@admin_required
@require_POST
def admin_user_delete(request, user_id):
    """Elimina un usuario del sistema"""
    from apps.usuarios.models import Usuario
    from django.shortcuts import get_object_or_404
    from django.contrib.auth import authenticate, login, logout
    from django.http import JsonResponse
    
    try:
        usuario = get_object_or_404(Usuario, id=user_id)
        
        # No permitir eliminar al propio usuario
        if usuario.id == request.user.id:
            return JsonResponse({'success': False, 'message': 'No puedes eliminar tu propia cuenta.'}, status=400)
        
        # No permitir eliminar otros administradores
        if usuario.is_staff and usuario.rol == 'admin_tienda':
            return JsonResponse({'success': False, 'message': 'No se puede eliminar a otros administradores.'}, status=400)
        
        email_usuario = usuario.email
        usuario.delete()
        
        messages.success(request, f'Usuario {email_usuario} eliminado exitosamente.')
        
        return JsonResponse({
            'success': True,
            'message': 'Usuario eliminado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar el usuario: {str(e)}'
        }, status=500)


# ==================== WISHLIST VIEWS ====================

def wishlist(request):
    """
    Vista para mostrar la página del wishlist con los productos favoritos del usuario
    """
    from apps.usuarios.models import Wishlist
    from django.db.models import Min
    
    if not request.user.is_authenticated:
        # Si no está autenticado, mostrar template con modal
        context = {
            'productos': [],
            'total_items': 0,
            'show_login_modal': True,
        }
        return render(request, 'wishlist_page.html', context)
    
    # Obtener todos los items del wishlist del usuario
    wishlist_items = Wishlist.objects.filter(usuario=request.user).select_related('producto').prefetch_related(
        'producto__imagenes',
        'producto__variantes',
        'producto__categoria'
    ).order_by('-agregado')
    
    # Preparar datos de productos para el template
    productos_wishlist = []
    for item in wishlist_items:
        producto = item.producto
        
        # Precio
        producto.display_price = producto.precio_base
        
        # Imágenes
        imagenes = list(producto.imagenes.filter(tipo_medio='imagen')[:2])
        if imagenes:
            producto.main_image_src = imagenes[0].src
            producto.hover_image_src = imagenes[1].imagen.url if len(imagenes) > 1 and imagenes[1].imagen else None
        else:
            producto.main_image_src = None
            producto.hover_image_src = None
        
        # Colores
        colores_list = []
        for variante in producto.variantes.all():
            if variante.color and variante.color not in colores_list:
                colores_list.append(variante.color)
        producto.colors = [{'valor': c} for c in colores_list]
        
        # Tallas
        tallas_list = []
        for variante in producto.variantes.all():
            if variante.talla and variante.talla.codigo and variante.talla.codigo not in tallas_list:
                tallas_list.append(variante.talla.codigo)
        producto.sizes = tallas_list
        
        # Disponibilidad
        total_stock = sum(v.stock for v in producto.variantes.all())
        producto.availability = 'En stock' if total_stock > 0 else 'Agotado'
        
        # Agregar el item al wishlist
        producto.wishlist_item_id = item.id
        producto.in_wishlist = True
        
        productos_wishlist.append(producto)
    
    context = {
        'productos': productos_wishlist,
        'total_items': len(productos_wishlist),
    }
    
    return render(request, 'wishlist_page.html', context)


@require_POST
def wishlist_add(request):
    """
    Endpoint AJAX para agregar un producto al wishlist
    """
    from apps.usuarios.models import Wishlist
    from django.http import JsonResponse
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'require_login': True,
            'message': 'Debes iniciar sesión para usar la lista de deseos'
        }, status=401)
    
    product_id = request.POST.get('product_id')
    
    if not product_id:
        return JsonResponse({
            'success': False,
            'message': 'ID de producto no especificado'
        }, status=400)
    
    try:
        producto = Producto.objects.get(id=product_id, activo=True)
        
        # Crear o obtener el item del wishlist
        wishlist_item, created = Wishlist.objects.get_or_create(
            usuario=request.user,
            producto=producto
        )
        
        if created:
            return JsonResponse({
                'success': True,
                'message': 'Producto agregado a favoritos',
                'wishlist_id': wishlist_item.id,
                'in_wishlist': True
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'El producto ya está en favoritos',
                'wishlist_id': wishlist_item.id,
                'in_wishlist': True
            })
            
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Producto no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)


@require_POST
def wishlist_remove(request):
    """
    Endpoint AJAX para remover un producto del wishlist
    """
    from apps.usuarios.models import Wishlist
    from django.http import JsonResponse
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Debes iniciar sesión para usar el wishlist'
        }, status=401)
    
    wishlist_id = request.POST.get('wishlist_id')
    
    if not wishlist_id:
        return JsonResponse({
            'success': False,
            'message': 'ID de wishlist no especificado'
        }, status=400)
    
    try:
        from apps.usuarios.models import Wishlist
        wishlist_item = Wishlist.objects.get(id=wishlist_id, usuario=request.user)
        wishlist_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Producto removido de favoritos',
            'in_wishlist': False
        })
        
    except Wishlist.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Item de wishlist no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)


def wishlist_count(request):
    """
    Endpoint AJAX para obtener el contador de items en el wishlist
    """
    from apps.usuarios.models import Wishlist
    from django.http import JsonResponse
    
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(usuario=request.user).count()
    else:
        count = 0
    
    return JsonResponse({
        'success': True,
        'count': count
    })


# Vistas para páginas estáticas
def terms_conditions(request):
    """Renderiza la página de términos y condiciones desde el admin Django"""
    from apps.ayudas.models import PaginaAyuda
    pagina = None
    try:
        pagina = PaginaAyuda.objects.get(tipo='terminos', activo=True)
    except PaginaAyuda.DoesNotExist:
        # Si no existe, mostrar una página por defecto
        pass
    
    if pagina:
        return render(request, 'terms-conditions.html', {'pagina': pagina})
    else:
        # Renderizar template vacío si no hay contenido
        return render(request, 'terms-conditions.html', {'pagina': None})


def privacy_policy(request):
    """Renderiza la página de política de privacidad desde el admin Django"""
    from apps.ayudas.models import PaginaAyuda
    pagina = None
    try:
        pagina = PaginaAyuda.objects.get(tipo='privacidad', activo=True)
    except PaginaAyuda.DoesNotExist:
        pass
    
    if pagina:
        return render(request, 'terms-conditions.html', {'pagina': pagina})
    else:
        return render(request, 'terms-conditions.html', {'pagina': None})


def delivery_return(request):
    """Renderiza la página de devoluciones y cambios desde el admin Django"""
    from apps.ayudas.models import PaginaAyuda
    pagina = None
    try:
        pagina = PaginaAyuda.objects.get(tipo='devoluciones', activo=True)
    except PaginaAyuda.DoesNotExist:
        pass
    
    if pagina:
        return render(request, 'terms-conditions.html', {'pagina': pagina})
    else:
        return render(request, 'terms-conditions.html', {'pagina': None})


def shipping_delivery(request):
    """Renderiza la página de envíos desde el admin Django"""
    from apps.ayudas.models import PaginaAyuda
    pagina = None
    try:
        pagina = PaginaAyuda.objects.get(tipo='envios', activo=True)
    except PaginaAyuda.DoesNotExist:
        pass
    
    if pagina:
        return render(request, 'terms-conditions.html', {'pagina': pagina})
    else:
        return render(request, 'terms-conditions.html', {'pagina': None})


def faq(request):
    """Renderiza la página de FAQ (redirige a la vista dinámicamente cargada desde ayudas)"""
    from apps.ayudas.views import faq_list
    return faq_list(request)


def compare(request):
    """Renderiza la página de comparación"""
    return render(request, 'compare.html')
