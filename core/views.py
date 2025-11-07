from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Min, Sum

# Import Producto model to build the shop listing
from apps.productos.models import Producto


def inicio(request):
    """Renderiza la plantilla home-05.html (nuevo index)"""
    return render(request, 'home-05.html')


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