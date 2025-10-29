from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Producto, Categoria, Marca, ImagenProducto, VarianteProducto


# ============================================
# VISTAS DE PRODUCTOS
# ============================================

def producto_lista(request):
    """Vista para listar todos los productos"""
    productos = Producto.objects.select_related('categoria', 'marca').prefetch_related('imagenes').all()
    
    # Filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria', '')
    estado = request.GET.get('estado', '')
    
    if search:
        productos = productos.filter(
            Q(nombre__icontains=search) |
            Q(sku__icontains=search) |
            Q(descripcion__icontains=search)
        )
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if estado:
        productos = productos.filter(estado=estado)
    
    # Contexto
    categorias = Categoria.objects.filter(activo=True)
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'search': search,
        'categoria_id': categoria_id,
        'estado': estado,
    }
    
    return render(request, 'admin/productos/producto_lista.html', context)


def producto_agregar(request):
    """Vista para agregar un nuevo producto"""
    if request.method == 'POST':
        # Datos básicos del producto
        nombre = request.POST.get('nombre')
        sku = request.POST.get('sku')
        descripcion = request.POST.get('descripcion', '')
        descripcion_corta = request.POST.get('descripcion_corta', '')
        categoria_id = request.POST.get('categoria')
        marca_id = request.POST.get('marca', None)
        precio = request.POST.get('precio')
        precio_comparacion = request.POST.get('precio_comparacion', None)
        precio_costo = request.POST.get('precio_costo', None)
        stock = request.POST.get('stock', 0)
        stock_minimo = request.POST.get('stock_minimo', 5)
        destacado = request.POST.get('destacado') == 'on'
        nuevo = request.POST.get('nuevo') == 'on'
        en_oferta = request.POST.get('en_oferta') == 'on'
        
        # Crear producto
        producto = Producto(
            nombre=nombre,
            sku=sku,
            descripcion=descripcion,
            descripcion_corta=descripcion_corta,
            categoria_id=categoria_id,
            precio=precio,
            stock=int(stock),
            stock_minimo=int(stock_minimo),
            destacado=destacado,
            nuevo=nuevo,
            en_oferta=en_oferta
        )
        
        if marca_id:
            producto.marca_id = marca_id
        
        if precio_comparacion:
            producto.precio_comparacion = precio_comparacion
        
        if precio_costo:
            producto.precio_costo = precio_costo
        
        producto.save()
        
        messages.success(request, f'Producto "{producto.nombre}" creado exitosamente.')
        return redirect('productos:producto_lista')
    
    categorias = Categoria.objects.filter(activo=True)
    marcas = Marca.objects.filter(activo=True)
    
    context = {
        'categorias': categorias,
        'marcas': marcas,
    }
    
    return render(request, 'admin/productos/producto_agregar.html', context)


def producto_editar(request, pk):
    """Vista para editar un producto existente"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.sku = request.POST.get('sku')
        producto.descripcion = request.POST.get('descripcion', '')
        producto.descripcion_corta = request.POST.get('descripcion_corta', '')
        producto.categoria_id = request.POST.get('categoria')
        marca_id = request.POST.get('marca', None)
        producto.precio = request.POST.get('precio')
        precio_comparacion = request.POST.get('precio_comparacion', None)
        precio_costo = request.POST.get('precio_costo', None)
        producto.stock = int(request.POST.get('stock', 0))
        producto.stock_minimo = int(request.POST.get('stock_minimo', 5))
        producto.destacado = request.POST.get('destacado') == 'on'
        producto.nuevo = request.POST.get('nuevo') == 'on'
        producto.en_oferta = request.POST.get('en_oferta') == 'on'
        
        if marca_id:
            producto.marca_id = marca_id
        else:
            producto.marca = None
        
        if precio_comparacion:
            producto.precio_comparacion = precio_comparacion
        
        if precio_costo:
            producto.precio_costo = precio_costo
        
        producto.save()
        
        messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente.')
        return redirect('productos:producto_lista')
    
    categorias = Categoria.objects.filter(activo=True)
    marcas = Marca.objects.filter(activo=True)
    
    context = {
        'producto': producto,
        'categorias': categorias,
        'marcas': marcas,
        'editar': True,
    }
    
    return render(request, 'admin/productos/producto_agregar.html', context)


def producto_eliminar(request, pk):
    """Vista para eliminar un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado exitosamente.')
        return redirect('productos:producto_lista')
    
    return render(request, 'admin/productos/producto_eliminar.html', {'producto': producto})


# ============================================
# VISTAS DE CATEGORÍAS
# ============================================

def categoria_lista(request):
    """Vista para listar todas las categorías"""
    categorias = Categoria.objects.select_related('padre').all()
    
    context = {
        'categorias': categorias,
    }
    
    return render(request, 'admin/productos/categoria_lista.html', context)


def categoria_agregar(request):
    """Vista para agregar una nueva categoría"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        padre_id = request.POST.get('padre', '')
        orden = request.POST.get('orden', 0)
        activo = request.POST.get('activo') == 'on'
        
        categoria = Categoria(
            nombre=nombre,
            descripcion=descripcion,
            orden=int(orden),
            activo=activo
        )
        
        if padre_id:
            categoria.padre_id = int(padre_id)
        
        categoria.save()
        messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente.')
        return redirect('productos:categoria_lista')
    
    categorias_padre = Categoria.objects.filter(padre__isnull=True, activo=True)
    
    context = {
        'categorias_padre': categorias_padre,
    }
    
    return render(request, 'admin/productos/categoria_agregar.html', context)


def categoria_editar(request, pk):
    """Vista para editar una categoría existente"""
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        categoria.nombre = request.POST.get('nombre')
        categoria.descripcion = request.POST.get('descripcion', '')
        padre_id = request.POST.get('padre', '')
        categoria.orden = int(request.POST.get('orden', 0))
        categoria.activo = request.POST.get('activo') == 'on'
        
        if padre_id:
            categoria.padre_id = int(padre_id)
        else:
            categoria.padre = None
        
        categoria.save()
        messages.success(request, f'Categoría "{categoria.nombre}" actualizada exitosamente.')
        return redirect('productos:categoria_lista')
    
    categorias_padre = Categoria.objects.filter(padre__isnull=True, activo=True).exclude(pk=pk)
    
    context = {
        'categoria': categoria,
        'categorias_padre': categorias_padre,
        'editar': True,
    }
    
    return render(request, 'admin/productos/categoria_agregar.html', context)


def categoria_eliminar(request, pk):
    """Vista para eliminar una categoría"""
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría "{nombre}" eliminada exitosamente.')
        return redirect('productos:categoria_lista')
    
    return render(request, 'admin/productos/categoria_eliminar.html', {'categoria': categoria})


# ============================================
# VISTAS DE MARCAS
# ============================================

def marca_lista(request):
    """Vista para listar todas las marcas"""
    marcas = Marca.objects.all()
    
    context = {
        'marcas': marcas,
    }
    
    return render(request, 'admin/productos/marca_lista.html', context)


def marca_agregar(request):
    """Vista para agregar una nueva marca"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        activo = request.POST.get('activo') == 'on'
        
        marca = Marca(
            nombre=nombre,
            descripcion=descripcion,
            activo=activo
        )
        
        marca.save()
        messages.success(request, f'Marca "{marca.nombre}" creada exitosamente.')
        return redirect('productos:marca_lista')
    
    return render(request, 'admin/productos/marca_agregar.html')


def marca_editar(request, pk):
    """Vista para editar una marca existente"""
    marca = get_object_or_404(Marca, pk=pk)
    
    if request.method == 'POST':
        marca.nombre = request.POST.get('nombre')
        marca.descripcion = request.POST.get('descripcion', '')
        marca.activo = request.POST.get('activo') == 'on'
        marca.save()
        
        messages.success(request, f'Marca "{marca.nombre}" actualizada exitosamente.')
        return redirect('productos:marca_lista')
    
    context = {
        'marca': marca,
        'editar': True,
    }
    
    return render(request, 'admin/productos/marca_agregar.html', context)


def marca_eliminar(request, pk):
    """Vista para eliminar una marca"""
    marca = get_object_or_404(Marca, pk=pk)
    
    if request.method == 'POST':
        nombre = marca.nombre
        marca.delete()
        messages.success(request, f'Marca "{nombre}" eliminada exitosamente.')
        return redirect('productos:marca_lista')
    
    return render(request, 'admin/productos/marca_eliminar.html', {'marca': marca})
