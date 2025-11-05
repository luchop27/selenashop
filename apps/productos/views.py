from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView
from .models import Categoria, Estilo, Producto
from django.db.models import Sum, Min
from decimal import Decimal
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProductoForm, VarianteFormSet, ImagenFormSet


def panel_dashboard(request):
	"""Vista principal del dashboard"""
	total_productos = Producto.objects.count()
	total_categorias = Categoria.objects.filter(estado=True).count()
    
	return render(request, "index.html", {
		"total_productos": total_productos,
		"total_categorias": total_categorias,
	})

# =========================
#  VISTAS PÚBLICAS
# =========================


class ProductoListView(ListView):
	"""
	Lista general de productos.
	/productos/?categoria=slug&estilo=slug&q=texto
	"""
	model = Producto
	template_name = "catalogo/producto_list.html"  # usa siempre el mismo nombre
	context_object_name = "productos"
	paginate_by = 12

	def get_queryset(self):
		qs = (
			Producto.objects
			.filter(activo=True)
			.select_related("categoria", "estilo")
			.prefetch_related("imagenes", "variantes")
			.order_by("-created_at")
		)

		# ?categoria=vestidos
		categoria_slug = self.request.GET.get("categoria")
		if categoria_slug:
			qs = qs.filter(categoria__slug=categoria_slug, categoria__estado=True)

		# ?estilo=gala
		estilo_slug = self.request.GET.get("estilo")
		if estilo_slug:
			qs = qs.filter(estilo__slug=estilo_slug, estilo__activo=True)

		# ?q=blusa
		q = self.request.GET.get("q")
		if q:
			qs = qs.filter(nombre__icontains=q)

		return qs

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx["categorias"] = Categoria.objects.filter(estado=True).order_by("posicion", "nombre")
		ctx["estilos"] = Estilo.objects.filter(activo=True).order_by("posicion", "nombre")
		return ctx



class ProductoDetailView(DetailView):
	"""
	Detalle de un producto.
	/producto/<slug>/
	"""
	model = Producto
	template_name = "catalogo/producto_detail.html"
	context_object_name = "producto"
	slug_field = "slug"
	slug_url_kwarg = "slug"

	def get_queryset(self):
		return (
			Producto.objects
			.filter(activo=True)
			.select_related("categoria", "estilo")
			.prefetch_related("imagenes", "variantes")
		)

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		producto = self.object
		relacionados = (
			Producto.objects
			.filter(activo=True, categoria=producto.categoria)
			.exclude(pk=producto.pk)[:8]
		)
		ctx["relacionados"] = relacionados
		return ctx


class CategoriaProductoListView(ListView):
	"""
	/categoria/<slug>/
	"""
	model = Producto
	template_name = "catalogo/producto-list.html"
	context_object_name = "productos"
	paginate_by = 12

	def get_queryset(self):
		self.categoria = get_object_or_404(
			Categoria,
			slug=self.kwargs["slug"],
			estado=True
		)
		return (
			Producto.objects
			.filter(activo=True, categoria=self.categoria)
			.select_related("categoria", "estilo")
			.prefetch_related("imagenes", "variantes")
			.order_by("-created_at")
		)

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx["categoria_actual"] = self.categoria
		ctx["categorias"] = Categoria.objects.filter(estado=True)
		return ctx


class EstiloProductoListView(ListView):
	"""
	/estilo/<slug>/
	"""
	model = Producto
	template_name = "catalogo/producto-list.html"
	context_object_name = "productos"
	paginate_by = 12

	def get_queryset(self):
		self.estilo = get_object_or_404(
			Estilo,
			slug=self.kwargs["slug"],
			activo=True
		)
		return (
			Producto.objects
			.filter(activo=True, estilo=self.estilo)
			.select_related("categoria", "estilo")
			.prefetch_related("imagenes", "variantes")
			.order_by("-created_at")
		)

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx["estilo_actual"] = self.estilo
		ctx["estilos"] = Estilo.objects.filter(activo=True)
		return ctx


# =========================
#  VISTAS DEL PANEL (admin-ecomus)
# =========================
def panel_productos_list(request):
	"""
	Renderiza tu HTML del panel: admin-ecomus/product-list.html
	"""
	productos = (
		Producto.objects
		.select_related("categoria", "estilo")
		.prefetch_related("variantes", "imagenes")
		# agregamos datos calculados:
		.annotate(
			total_stock=Sum("variantes__stock"),          # suma de stock de todas las variantes
			precio_variante=Min("variantes__precio"),     # el precio más barato de las variantes
		)
		.order_by("-created_at")
	)

	# Calcular porcentaje de descuento (sale) para mostrar en la tabla
	for p in productos:
		pv = getattr(p, 'precio_variante', None)
		pb = getattr(p, 'precio_base', None)
		try:
			if pv is not None and pb is not None and pb > 0 and pv < pb:
				# pv and pb are Decimals; calcular porcentaje entero
				percent = int(((pb - pv) / pb) * Decimal(100))
				p.sale_percent = percent
			else:
				p.sale_percent = None
		except Exception:
			p.sale_percent = None
	return render(request, "product-list.html", {
		"productos": productos
	})

def panel_producto_crear(request):
	"""
	Renderiza el HTML de crear producto del panel.
	Luego lo cambiamos a un ModelForm.
	"""
	if request.method == 'POST':
		form = ProductoForm(request.POST)
		if form.is_valid():
			producto = form.save()
			variante_formset = VarianteFormSet(request.POST, instance=producto)
			imagen_formset = ImagenFormSet(request.POST, instance=producto)
			if variante_formset.is_valid() and imagen_formset.is_valid():
				variante_formset.save()
				imagen_formset.save()
				messages.success(request, 'Producto creado correctamente.')
				return redirect(reverse('productos:panel_productos'))
			else:
				# si los formsets fallan, mostramos errores en la plantilla
				pass
		else:
			variante_formset = VarianteFormSet(request.POST)
			imagen_formset = ImagenFormSet(request.POST, request.FILES)
	else:
		form = ProductoForm()
		variante_formset = VarianteFormSet()
		imagen_formset = ImagenFormSet()

	return render(request, "add-product.html", {
		'form': form,
		'variante_formset': variante_formset,
		'imagen_formset': imagen_formset,
	})


def panel_categorias_list(request):
	categorias = Categoria.objects.filter(estado=True).order_by("posicion", "nombre")
	return render(request, "category-list.html", {
		"categorias": categorias
	})


def panel_categoria_crear(request):
	return render(request, "new-category.html")


# =========================
#  ADMIN PANEL ECOMUS - PRODUCTOS
# =========================

@login_required(login_url='/admin/login/')
def admin_productos_list(request):
	"""
	Lista de productos para el admin panel de ecomus
	Con búsqueda, filtros y paginación
	"""
	from django.core.paginator import Paginator
	from django.db.models import Q, Sum
	
	if request.user.rol != 'admin_tienda' and not request.user.is_staff:
		messages.error(request, 'No tienes permiso para acceder.')
		return redirect('core:inicio')
	
	# Obtener productos con sus relaciones
	productos = Producto.objects.select_related('categoria', 'estilo').prefetch_related('variantes', 'imagenes').order_by('-created_at')
	
	# Búsqueda
	search = request.GET.get('q', '')
	if search:
		productos = productos.filter(
			Q(nombre__icontains=search) | 
			Q(descripcion_corta__icontains=search) |
			Q(marca__icontains=search)
		)
	
	# Filtro por categoría
	categoria_id = request.GET.get('categoria')
	if categoria_id:
		productos = productos.filter(categoria_id=categoria_id)
	
	# Filtro por estado
	estado = request.GET.get('estado')
	if estado:
		productos = productos.filter(activo=(estado == 'active'))
	
	# Paginación
	paginator = Paginator(productos, 20)
	page = request.GET.get('page', 1)
	productos_page = paginator.get_page(page)
	
	# Para los filtros
	categorias = Categoria.objects.filter(estado=True).order_by('nombre')
	
	return render(request, 'product-list.html', {
		'productos': productos_page,
		'categorias': categorias,
		'search': search,
		'total_productos': productos.count(),
	})


@login_required(login_url='/admin/login/')
def admin_producto_add(request):
	"""
	Agregar nuevo producto con el diseño de ecomus
	"""
	if request.user.rol != 'admin_tienda' and not request.user.is_staff:
		messages.error(request, 'No tienes permiso para acceder.')
		return redirect('core:inicio')
	
	if request.method == 'POST':
		form = ProductoForm(request.POST, request.FILES)
		variante_formset = VarianteFormSet(request.POST, request.FILES)
		imagen_formset = ImagenFormSet(request.POST, request.FILES)
		
		if form.is_valid():
			producto = form.save()
			
			# Guardar variantes
			variante_formset = VarianteFormSet(request.POST, request.FILES, instance=producto)
			if variante_formset.is_valid():
				variante_formset.save()
			
			# Guardar imágenes
			imagen_formset = ImagenFormSet(request.POST, request.FILES, instance=producto)
			if imagen_formset.is_valid():
				imagen_formset.save()
			
			messages.success(request, f'Producto "{producto.nombre}" creado exitosamente.')
			return redirect('productos:admin_productos_list')
	else:
		form = ProductoForm()
		variante_formset = VarianteFormSet()
		imagen_formset = ImagenFormSet()
	
	# Para los selects
	categorias = Categoria.objects.filter(estado=True).order_by('nombre')
	estilos = Estilo.objects.filter(activo=True).order_by('nombre')
	
	from .models import Talla
	tallas = Talla.objects.all().order_by('codigo')
	
	return render(request, 'add-product.html', {
		'form': form,
		'variante_formset': variante_formset,
		'imagen_formset': imagen_formset,
		'categorias': categorias,
		'estilos': estilos,
		'tallas': tallas,
	})


# =========================
#  VISTAS ATRIBUTOS
# =========================
from django.core.paginator import Paginator
from .models import Atributo, ValorAtributo


@login_required
def admin_atributos_list(request):
	"""Lista todos los atributos con paginación y búsqueda"""
	atributos_list = Atributo.objects.all().order_by('posicion', 'nombre')
	
	# Búsqueda
	search = request.GET.get('search', '')
	if search:
		atributos_list = atributos_list.filter(nombre__icontains=search)
	
	# Paginación
	paginator = Paginator(atributos_list, 10)
	page = request.GET.get('page', 1)
	atributos = paginator.get_page(page)
	
	# Agregar valores a cada atributo
	for atributo in atributos:
		atributo.valores_str = ', '.join([v.valor for v in atributo.valores.filter(activo=True)[:10]])
		if atributo.valores.filter(activo=True).count() > 10:
			atributo.valores_str += '...'
	
	return render(request, 'attributes.html', {
		'atributos': atributos,
		'search': search,
	})


@login_required
def admin_atributo_add(request):
	"""Agregar nuevo atributo"""
	if request.method == 'POST':
		# Procesar formulario
		nombre = request.POST.get('nombre')
		tipo = request.POST.get('tipo', 'texto')
		descripcion = request.POST.get('descripcion', '')
		
		from django.utils.text import slugify
		slug = slugify(nombre)
		
		# Crear atributo
		atributo = Atributo.objects.create(
			nombre=nombre,
			slug=slug,
			tipo=tipo,
			descripcion=descripcion,
			activo=True
		)
		
		# Procesar valores
		valores = request.POST.get('valores', '').split(',')
		for i, valor in enumerate(valores, 1):
			valor = valor.strip()
			if valor:
				ValorAtributo.objects.create(
					atributo=atributo,
					valor=valor,
					posicion=i,
					activo=True
				)
		
		messages.success(request, f'Atributo "{nombre}" creado exitosamente.')
		return redirect('productos:admin_atributos_list')
	
	return render(request, 'add-attributes.html', {})


@login_required  
def admin_atributo_edit(request, pk):
	"""Editar atributo existente"""
	atributo = get_object_or_404(Atributo, pk=pk)
	
	if request.method == 'POST':
		atributo.nombre = request.POST.get('nombre')
		atributo.tipo = request.POST.get('tipo', 'texto')
		atributo.descripcion = request.POST.get('descripcion', '')
		
		from django.utils.text import slugify
		atributo.slug = slugify(atributo.nombre)
		atributo.save()
		
		# Actualizar valores
		atributo.valores.all().delete()
		valores = request.POST.get('valores', '').split(',')
		for i, valor in enumerate(valores, 1):
			valor = valor.strip()
			if valor:
				ValorAtributo.objects.create(
					atributo=atributo,
					valor=valor,
					posicion=i,
					activo=True
				)
		
		messages.success(request, f'Atributo "{atributo.nombre}" actualizado.')
		return redirect('productos:admin_atributos_list')
	
	# Juntar valores en string
	valores_str = ', '.join([v.valor for v in atributo.valores.all()])
	
	return render(request, 'add-attributes.html', {
		'atributo': atributo,
		'valores_str': valores_str,
	})


@login_required
def admin_atributo_delete(request, pk):
	"""Eliminar atributo"""
	atributo = get_object_or_404(Atributo, pk=pk)
	nombre = atributo.nombre
	atributo.delete()
	messages.success(request, f'Atributo "{nombre}" eliminado.')
	return redirect('productos:admin_atributos_list')


from django.http import JsonResponse

@login_required
def api_atributos_list(request):
	"""API para obtener atributos activos con sus valores"""
	atributos = Atributo.objects.filter(activo=True).prefetch_related('valores').order_by('posicion', 'nombre')
	
	data = []
	for atributo in atributos:
		valores = []
		for valor in atributo.valores.filter(activo=True).order_by('posicion'):
			valores.append({
				'id': valor.id,
				'valor': valor.valor,
				'codigo_color': valor.codigo_color or '',
			})
		
		data.append({
			'id': atributo.id,
			'nombre': atributo.nombre,
			'tipo': atributo.tipo,
			'valores': valores,
		})
	
	return JsonResponse(data, safe=False)
