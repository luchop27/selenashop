from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView
from .models import Categoria, Estilo, Producto, Atributo, ValorAtributo, Coleccion
from django.db.models import Sum, Min, Q, Max
from decimal import Decimal
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from .forms import ProductoForm, VarianteFormSet, ImagenFormSet
from django.views.decorators.http import require_POST

# Importar decoradores de seguridad
from core.decorators import admin_required, superuser_required


def _get_marcas_existentes():
	"""Devuelve marcas existentes limpias para sugerencias en formularios de producto."""
	marcas_qs = (
		Producto.objects
		.exclude(marca__isnull=True)
		.values_list('marca', flat=True)
	)
	marcas = []
	seen = set()
	for marca in marcas_qs:
		valor = ' '.join((marca or '').split())
		if not valor:
			continue
		key = valor.lower()
		if key in seen:
			continue
		seen.add(key)
		marcas.append(valor)
	marcas.sort(key=lambda m: m.lower())
	return marcas


@admin_required
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
	template_name = "shop-collection-sub.html"
	context_object_name = "productos"
	paginate_by = 12

	def get_queryset(self):
		from django.db.models import Min, Sum, Q
		
		qs = (
			Producto.objects
			.filter(activo=True)
			.select_related("categoria", "coleccion")
			.prefetch_related(
				"imagenes",
				"variantes",
				"variantes__talla",
				"variantes__atributos__valor_atributo__atributo",
			)
			.annotate(precio_variante=Min('variantes__precio'), total_stock=Sum('variantes__stock'))
			.order_by("-created_at")
		)

		# ?categoria=vestidos
		categoria_slug = self.request.GET.get("categoria")
		if categoria_slug:
			# Buscar la categoría por slug
			try:
				categoria = Categoria.objects.get(slug=categoria_slug, estado=True)
				# Si es una categoría principal (tiene subcategorías), incluir productos de todas sus subcategorías
				if categoria.subcategorias.exists():
					# Obtener IDs de la categoría y todas sus subcategorías
					categoria_ids = [categoria.id]
					categoria_ids.extend(categoria.subcategorias.filter(estado=True).values_list('id', flat=True))
					qs = qs.filter(categoria_id__in=categoria_ids)
				else:
					# Si es una subcategoría o categoría sin hijos, filtrar solo por ella
					qs = qs.filter(categoria=categoria)
			except Categoria.DoesNotExist:
				# Si no existe la categoría, no filtrar
				pass

		# Filtrado por stock/disponibilidad
		stock_filter = self.request.GET.get("stock")
		if stock_filter == "en-stock":
			qs = qs.filter(total_stock__gt=0)
		elif stock_filter == "agotado":
			qs = qs.filter(Q(total_stock=0) | Q(total_stock__isnull=True))

		# Filtrado por precio
		precio_min = self.request.GET.get("precio_min")
		precio_max = self.request.GET.get("precio_max")
		if precio_min:
			try:
				qs = qs.filter(precio_variante__gte=float(precio_min))
			except (ValueError, TypeError):
				pass
		if precio_max:
			try:
				qs = qs.filter(precio_variante__lte=float(precio_max))
			except (ValueError, TypeError):
				pass

		# ?q=blusa
		q = self.request.GET.get("q")
		if q:
			qs = qs.filter(nombre__icontains=q)

		return qs
		if q:
			qs = qs.filter(nombre__icontains=q)

		return qs

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		
		# Obtener categoría actual si existe
		categoria_slug = self.request.GET.get("categoria")
		categoria_actual = None
		categorias_a_mostrar = []
		
		if categoria_slug:
			try:
				categoria_actual = Categoria.objects.get(slug=categoria_slug, estado=True)
			except Categoria.DoesNotExist:
				pass
		
		# Determinar qué categorías mostrar en el slider
		if categoria_actual:
			print(f"DEBUG ProductoListView: Categoría actual: {categoria_actual.nombre} (ID: {categoria_actual.id})")
			print(f"DEBUG ProductoListView: Tiene padre: {categoria_actual.padre}")
			
			# Si la categoría tiene subcategorías, mostrarlas
			subcategorias = Categoria.objects.filter(
				padre=categoria_actual,
				estado=True
			).order_by('nombre')
			
			print(f"DEBUG ProductoListView: Subcategorías encontradas: {subcategorias.count()}")
			
			if subcategorias.exists():
				# Tiene subcategorías, mostrarlas
				categorias_a_mostrar = list(subcategorias)
				print(f"DEBUG ProductoListView: Mostrando subcategorías de {categoria_actual.nombre}")
			elif categoria_actual.padre:
				# Es una subcategoría, mostrar sus hermanas (otras subcategorías del mismo padre)
				categorias_a_mostrar = list(
					Categoria.objects.filter(
						padre=categoria_actual.padre,
						estado=True
					).order_by('nombre')
				)
				print(f"DEBUG ProductoListView: Es subcategoría, mostrando hermanas: {len(categorias_a_mostrar)}")
			else:
				# Es categoría principal sin subcategorías, mostrar todas las categorías principales
				categorias_a_mostrar = list(
					Categoria.objects.filter(
						padre__isnull=True,
						estado=True
					).order_by('nombre')
				)
				print(f"DEBUG ProductoListView: Es categoría principal sin hijos, mostrando principales: {len(categorias_a_mostrar)}")
		else:
			# Si no hay categoría seleccionada, mostrar categorías principales
			categorias_a_mostrar = list(
				Categoria.objects.filter(
					padre__isnull=True,
					estado=True
				).order_by('nombre')
			)
			print(f"DEBUG ProductoListView: Sin categoría, mostrando principales: {len(categorias_a_mostrar)}")
		
		print(f"DEBUG ProductoListView: Total categorías a mostrar: {len(categorias_a_mostrar)}")
		for cat in categorias_a_mostrar:
			print(f"  - {cat.nombre} (slug: {cat.slug}, imagen: {bool(cat.imagen)})")
		
		# Preparar cada producto con los campos que necesita el template
		productos = ctx.get('productos', [])
		for p in productos:
			# Precio a mostrar: variante (mín) o precio_base
			p.display_price = getattr(p, 'precio_variante', None) or p.precio_base

			# Imágenes
			imgs = list(p.imagenes.all().order_by('posicion', 'created_at'))
			p.main_image_src = imgs[0].imagen.url if imgs and imgs[0].imagen else ''
			p.hover_image_src = imgs[1].imagen.url if len(imgs) > 1 and imgs[1].imagen else p.main_image_src

			# Colores únicos desde variantes
			color_values = []
			for v in p.variantes.all():
				if v.color and v.color not in color_values:
					color_values.append(v.color)
			p.colors = [{'valor': c} for c in color_values]

			# Tallas únicas desde variantes (sistema dual: FK talla + VarianteAtributo)
			size_values = []
			for v in p.variantes.all():
				# 1. Prioridad: FK directo a talla.codigo
				if getattr(v, 'talla', None) and getattr(v.talla, 'codigo', None):
					code = v.talla.codigo
					if code and code not in size_values:
						size_values.append(code)
					continue

				# 2. Fallback: buscar en atributos de variante (ValorAtributo)
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

			# Disponibilidad
			total_stock = getattr(p, 'total_stock', 0) or 0
			p.availability = 'In stock' if total_stock > 0 else 'Out of stock'

		ctx["categoria_actual"] = categoria_actual
		ctx["categorias_a_mostrar"] = categorias_a_mostrar
		ctx["categorias"] = Categoria.objects.filter(estado=True).order_by("nombre")
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
@admin_required
def panel_productos_list(request):
	"""
	Renderiza tu HTML del panel: admin-ecomus/product-list.html
	"""
	from django.core.paginator import Paginator
	from django.db.models import Q
	
	# Búsqueda general
	search = request.GET.get('q', '').strip()
	
	# Filtro de colección
	coleccion_filtro = request.GET.get('coleccion', '')
	
	# Base queryset para todos los productos
	productos = (
		Producto.objects
		.select_related("categoria", "coleccion")
		.prefetch_related("variantes", "imagenes")
		.annotate(
			total_stock=Sum("variantes__stock"),
			precio_variante=Min("variantes__precio"),
		)
		.order_by("-created_at")
	)
	
	# Aplicar búsqueda si existe
	if search:
		productos = productos.filter(
			Q(nombre__icontains=search) |
			Q(descripcion_corta__icontains=search) |
			Q(marca__icontains=search)
		)
	
	# Aplicar filtro de colección si existe
	if coleccion_filtro:
		try:
			coleccion_seleccionada = Coleccion.objects.get(slug=coleccion_filtro)
			productos = productos.filter(coleccion=coleccion_seleccionada)
		except Coleccion.DoesNotExist:
			pass
	
	# Paginación
	paginator = Paginator(productos, 20)
	page = request.GET.get('page', 1)
	productos_page = paginator.get_page(page)
	
	# Calcular porcentaje de descuento (sale)
	for p in productos_page:
		pv = getattr(p, 'precio_variante', None)
		pb = getattr(p, 'precio_base', None)
		try:
			if pv is not None and pb is not None and pb > 0 and pv < pb:
				percent = int(((pb - pv) / pb) * Decimal(100))
				p.sale_percent = percent
			else:
				p.sale_percent = None
		except Exception:
			p.sale_percent = None
	
	# Obtener todas las colecciones para el filtro
	colecciones_disponibles = Coleccion.objects.filter(activo=True).order_by('nombre')
	
	return render(request, "product-list.html", {
		"productos": productos_page,
		"total_productos": productos.count(),
		"colecciones_disponibles": colecciones_disponibles,
		"coleccion_filtro": coleccion_filtro,
		"search": search,
	})

@admin_required
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


@login_required(login_url='/admin/login/')
def panel_categorias_list(request):
	"""Lista categorías con jerarquía (principales y subcategorías)"""
	if request.user.rol != 'admin_tienda' and not request.user.is_staff:
		messages.error(request, 'No tienes permiso para acceder.')
		return redirect('core:inicio')
	
	# Obtener el ID de la categoría padre si se está navegando por subcategorías
	padre_id = request.GET.get('padre')
	
	if padre_id:
		# Mostrar subcategorías de una categoría específica
		try:
			categoria_padre = Categoria.objects.get(id=padre_id)
			categorias = Categoria.objects.filter(padre_id=padre_id).order_by('nombre')
		except Categoria.DoesNotExist:
			categoria_padre = None
			categorias = Categoria.objects.filter(padre__isnull=True).order_by('nombre')
	else:
		# Mostrar solo categorías principales (sin padre)
		categoria_padre = None
		categorias = Categoria.objects.filter(padre__isnull=True).order_by('nombre')
	
	# Búsqueda
	search = request.GET.get('q', '')
	if search:
		categorias = categorias.filter(nombre__icontains=search)
	
	# Anotar cada categoría con el conteo de subcategorías
	from django.db.models import Count
	categorias = categorias.annotate(
		num_subcategorias=Count('subcategorias'),
		num_productos=Count('productos')
	)
	
	return render(request, "category-list.html", {
		"categorias": categorias,
		"categoria_padre": categoria_padre,
		"search": search,
	})


@login_required(login_url='/admin/login/')
def panel_categoria_crear(request):
	"""Crear nueva categoría"""
	if request.user.rol != 'admin_tienda' and not request.user.is_staff:
		messages.error(request, 'No tienes permiso para acceder.')
		return redirect('core:inicio')
	
	if request.method == 'POST':
		from .forms import CategoriaForm
		form = CategoriaForm(request.POST, request.FILES)
		
		if form.is_valid():
			try:
				print(f"DEBUG FILES: {request.FILES}")
				categoria = form.save(commit=False)
				print(f"DEBUG imagen antes de save: {categoria.imagen}")
				categoria.save()
				print(f"DEBUG imagen despues de save: {categoria.imagen}")
				messages.success(request, f'Categoría "{categoria.nombre}" creada correctamente.')
				return redirect('productos:panel_categorias')
			except Exception as e:
				messages.error(request, f'Error al crear la categoría: {str(e)}')
				import traceback
				print(traceback.format_exc())  # Para debug en consola
		else:
			# Mostrar errores específicos del formulario
			for field, errors in form.errors.items():
				for error in errors:
					messages.error(request, f'{field}: {error}')
			messages.error(request, 'Por favor corrige los errores en el formulario.')
	else:
		from .forms import CategoriaForm
		form = CategoriaForm()
	
	# Obtener colecciones y categorías para los selects
	from .models import Coleccion
	colecciones = Coleccion.objects.filter(activo=True).order_by('nombre')
	categorias = Categoria.objects.filter(estado=True, padre__isnull=True).order_by('nombre')
	
	return render(request, "new-category.html", {
		'form': form,
		'colecciones': colecciones,
		'categorias': categorias,
	})


@login_required(login_url='/admin/login/')
def panel_categoria_edit(request, pk):
	"""
	Editar una categoría con soporte para imágenes
	"""
	categoria = get_object_or_404(Categoria, pk=pk)
	
	if request.method == 'POST':
		from .forms import CategoriaForm
		
		# Manejar eliminación de imagen actual
		if request.POST.get('remove_imagen'):
			if categoria.imagen:
				categoria.imagen.delete()
				categoria.save()
		
		form = CategoriaForm(request.POST, request.FILES, instance=categoria)
		
		if form.is_valid():
			try:
				categoria = form.save()
				messages.success(request, f'Categoría "{categoria.nombre}" actualizada correctamente.')
				return redirect('productos:panel_categorias')
			except Exception as e:
				messages.error(request, f'Error al actualizar la categoría: {str(e)}')
		else:
			messages.error(request, 'Por favor corrige los errores en el formulario.')
	else:
		from .forms import CategoriaForm
		form = CategoriaForm(instance=categoria)
	
	# Obtener colecciones y categorías para los selects
	from .models import Coleccion
	colecciones = Coleccion.objects.filter(activo=True).order_by('nombre')
	categorias = Categoria.objects.filter(estado=True, padre__isnull=True).exclude(pk=pk).order_by('nombre')
	
	return render(request, "edit-category.html", {
		'form': form,
		'categoria': categoria,
		'colecciones': colecciones,
		'categorias': categorias,
	})


@login_required(login_url='/admin/login/')
@require_POST
def panel_categoria_delete(request, pk):
	"""
	Eliminar una categoría
	"""
	if request.user.rol != 'admin_tienda' and not request.user.is_staff:
		messages.error(request, 'No tienes permiso para eliminar categorías.')
		return redirect('core:inicio')

	try:
		categoria = Categoria.objects.get(pk=pk)
	except Categoria.DoesNotExist:
		messages.error(request, 'La categoría no existe o ya fue eliminada.')
		return redirect('productos:panel_categorias')

	nombre_categoria = categoria.nombre
	padre_id = categoria.padre_id

	if categoria.subcategorias.exists():
		messages.warning(
			request,
			f'La categoría "{nombre_categoria}" tiene {categoria.subcategorias.count()} subcategorías. '
			'Las subcategorías quedarán sin categoría padre.'
		)

	try:
		categoria.delete()
	except Exception as e:
		messages.error(request, f'No se pudo eliminar la categoría: {str(e)}')
		if padre_id:
			return redirect(f'/admin-panel/categorias/?padre={padre_id}')
		return redirect('productos:panel_categorias')

	messages.success(request, f'Categoría "{nombre_categoria}" eliminada exitosamente.')
	if padre_id:
		return redirect(f'/admin-panel/categorias/?padre={padre_id}')
	return redirect('productos:panel_categorias')



# =========================
#  ADMIN PANEL ECOMUS - PRODUCTOS
# =========================

@admin_required
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
	productos = Producto.objects.select_related('categoria', 'coleccion').prefetch_related('variantes', 'imagenes').order_by('-created_at')
	
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
	
	# Filtro por colección
	coleccion_filtro = request.GET.get('coleccion', '')
	if coleccion_filtro:
		try:
			coleccion_seleccionada = Coleccion.objects.get(slug=coleccion_filtro)
			productos = productos.filter(coleccion=coleccion_seleccionada)
		except Coleccion.DoesNotExist:
			pass
	
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
	colecciones_disponibles = Coleccion.objects.filter(activo=True).order_by('nombre')
	
	return render(request, 'product-list.html', {
		'productos': productos_page,
		'categorias': categorias,
		'colecciones_disponibles': colecciones_disponibles,
		'coleccion_filtro': coleccion_filtro,
		'search': search,
		'total_productos': productos.count(),
	})


@admin_required
def admin_producto_add(request):
	"""
	Agregar nuevo producto con el diseño de ecomus
	"""
	if request.user.rol != 'admin_tienda' and not request.user.is_staff:
		messages.error(request, 'No tienes permiso para acceder.')
		return redirect('core:inicio')
	
	if request.method == 'POST':
		form = ProductoForm(request.POST, request.FILES)
		
		if form.is_valid():
			producto = form.save()
			
			# Obtener imágenes cargadas (NO guardarlas aún)
			imagenes = request.FILES.getlist('imagenes')
			print(f"\n{'='*50}")
			print(f"DEBUG - Total archivos recibidos: {len(imagenes)}")
			print(f"DEBUG - request.FILES keys: {list(request.FILES.keys())}")
			print(f"DEBUG - request.POST keys: {list(request.POST.keys())}")
			for idx, archivo in enumerate(imagenes):
				print(f"  Archivo {idx}:")
				print(f"    Nombre: {archivo.name}")
				print(f"    Tamaño: {archivo.size} bytes")
				print(f"    Tipo: {archivo.content_type}")
				extension = archivo.name.lower().split('.')[-1]
				print(f"    Extensión: .{extension}")
				es_video = extension in ['mp4', 'webm', 'mov', 'avi', 'mkv']
				print(f"    Es video: {es_video}")
			print(f"{'='*50}\n")
			
			# Procesar variantes dinámicas desde el formulario
			import json
			variante_index = 0
			
			# Verificar si la categoría del producto es "Ropa" o tiene variantes con atributos
			es_categoria_ropa = producto.categoria and 'ropa' in producto.categoria.nombre.lower()
			
			while True:
				sku_key = f'variante_{variante_index}_sku'
				if sku_key not in request.POST:
					break
				
				sku = request.POST.get(sku_key, '').strip()
				stock = request.POST.get(f'variante_{variante_index}_stock', '0')
				atributos_json = request.POST.get(f'variante_{variante_index}_atributos', '[]')
				
				print(f"\n=== DEBUG VARIANTE {variante_index} ===")
				print(f"SKU recibido: '{sku}'")
				print(f"Stock recibido: '{stock}' (tipo: {type(stock)})")
				print(f"Atributos JSON: {atributos_json[:100]}")
				
				# Crear la variante usando el precio_base del producto
				from .models import Variante, VarianteAtributo, ValorAtributo, Talla
				
				# Primero, verificar si hay un atributo de talla para asignarlo al campo talla
				talla_obj = None
				
				try:
					atributos_data = json.loads(atributos_json)
					for attr in atributos_data:
						atributo_nombre = attr.get('atributoNombre', '').lower()
						valor_nombre = attr.get('valorNombre', '')
						
						# Si es una talla, buscar o crear el objeto Talla
						if 'talla' in atributo_nombre and valor_nombre:
							talla_obj, created = Talla.objects.get_or_create(
								codigo=valor_nombre.upper(),
								defaults={'nombre': valor_nombre}
							)
							print(f"DEBUG - Talla {'creada' if created else 'encontrada'}: {talla_obj.codigo}")
				except Exception as e:
					print(f"Error extrayendo talla de atributos: {e}")
				
				# Generar SKU automático: slug-TALLA
				if not sku:
					if talla_obj:
						sku = f"{producto.slug}-{talla_obj.codigo}"
				
				# Crear la variante con la talla asignada
				variante = Variante.objects.create(
					producto=producto,
					talla=talla_obj,
					sku=sku,
					precio=producto.precio_base,
					stock=int(stock) if stock else 0
				)
				print(f"DEBUG - Variante creada: ID={variante.id}, SKU={variante.sku}, Talla={variante.talla}, Stock={variante.stock}")
				
				# Asociar atributos a la variante (para mantener compatibilidad con sistema de atributos)
				try:
					atributos_data = json.loads(atributos_json)
					for attr in atributos_data:
						atributo_nombre = (attr.get('atributoNombre') or '').strip().lower()
						if atributo_nombre == 'marca':
							continue

						valor_id = attr.get('valorId')
						if valor_id:
							valor_atributo = ValorAtributo.objects.get(id=valor_id)
							if valor_atributo.atributo.nombre.strip().lower() == 'marca':
								continue

							VarianteAtributo.objects.create(
								variante=variante,
								valor_atributo=valor_atributo
							)
				except Exception as e:
					print(f"Error procesando atributos de variante: {e}")
				
				variante_index += 1
			
			# Si no se crearon variantes (productos sin atributos como accesorios), crear una variante por defecto
			if variante_index == 0 and not es_categoria_ropa:
				from .models import Variante
				Variante.objects.create(
					producto=producto,
					sku=f"{producto.slug}-DEFAULT",
					precio=producto.precio_base,
					stock=int(request.POST.get('stock_default', '0'))
				)
				variante_index = 1
				print(f"DEBUG - Variante por defecto creada para producto sin atributos")
			
			# GUARDAR TODAS LAS IMÁGENES Y VIDEOS DEL PRODUCTO
			from .models import Imagen
			imagenes_guardadas = 0
			videos_guardados = 0
			
			for archivo in imagenes:
				# Determinar si es imagen o video por extensión
				extension = archivo.name.lower().split('.')[-1]
				es_video = extension in ['mp4', 'webm', 'mov', 'avi', 'mkv']
				
				print(f"\nProcesando archivo: {archivo.name}")
				print(f"  Extensión: .{extension}")
				print(f"  Es video: {es_video}")
				
				try:
					if es_video:
						imagen_obj = Imagen.objects.create(
							producto=producto,
							tipo_medio='video',
							video=archivo,
							variante=None
						)
						videos_guardados += 1
						print(f"  ✓ Video guardado con ID: {imagen_obj.id}")
					else:
						imagen_obj = Imagen.objects.create(
							producto=producto,
							tipo_medio='imagen',
							imagen=archivo,
							variante=None
						)
						imagenes_guardadas += 1
						print(f"  ✓ Imagen guardada con ID: {imagen_obj.id}")
				except Exception as e:
					print(f"  ✗ ERROR al guardar: {e}")
					import traceback
					traceback.print_exc()
			
			total_archivos = imagenes_guardadas + videos_guardados
			messages.success(request, f'Producto "{producto.nombre}" creado exitosamente con {variante_index} variante(s), {imagenes_guardadas} imagen(es) y {videos_guardados} video(s).')
			return redirect('productos:admin_productos_list')
	else:
		form = ProductoForm()
	
	return render(request, 'add-product.html', {
		'form': form,
		'marcas_existentes': _get_marcas_existentes(),
	})


@admin_required
def admin_producto_view(request, pk):
	"""
	Ver detalles completos de un producto incluyendo imágenes y variantes
	"""
	if request.user.rol != 'admin_tienda' and not request.user.is_staff:
		messages.error(request, 'No tienes permiso para acceder.')
		return redirect('core:inicio')
	
	try:
		producto = Producto.objects.prefetch_related(
			'imagenes',
			'variantes__atributos__valor_atributo__atributo'
		).select_related('categoria', 'coleccion').get(pk=pk)
	except Producto.DoesNotExist:
		messages.error(request, 'El producto no existe.')
		return redirect('productos:admin_productos_list')
	
	return render(request, 'product-view.html', {
		'producto': producto,
	})


@admin_required
def admin_producto_edit(request, pk):
	"""
	Editar producto existente con el diseño de ecomus
	"""
	# Imports necesarios para toda la función
	from .models import Atributo, ValorAtributo, Variante, VarianteAtributo, Talla, Imagen
	import json
	
	if request.user.rol != 'admin_tienda' and not request.user.is_staff:
		messages.error(request, 'No tienes permiso para acceder.')
		return redirect('core:inicio')
	
	try:
		producto = Producto.objects.prefetch_related('variantes__atributos__valor_atributo').get(pk=pk)
	except Producto.DoesNotExist:
		messages.error(request, 'El producto no existe.')
		return redirect('productos:admin_productos_list')
	
	if request.method == 'POST':
		print("\n" + "="*50)
		print("DEBUG - EDICIÓN DE PRODUCTO")
		print("="*50)
		print("POST data recibido:")
		for key, value in request.POST.items():
			if key.startswith('variante_'):
				print(f"  {key}: {value[:100] if len(str(value)) > 100 else value}")
		print("="*50 + "\n")
		
		form = ProductoForm(request.POST, request.FILES, instance=producto)
		
		if form.is_valid():
			try:
				with transaction.atomic():
					producto = form.save(commit=False)
					bajo_pedido_solicitado = request.POST.get('bajo_pedido') == 'on'
					
					# Protección temporal: evita que signals eliminen el producto
					# mientras el reemplazo de variantes deja stock en 0 momentáneamente.
					producto.bajo_pedido = True
					
					# Guardar producto padre y verificar consistencia de PK
					producto.save()
					print(f"Producto guardado: {producto.nombre}")
					print(f"DEBUG - Producto ID: {producto.pk}")
					
					# Procesar eliminación de imágenes
					imagenes_eliminar = request.POST.get('imagenes_eliminar', '')
					if imagenes_eliminar:
						ids_eliminar = [int(id) for id in imagenes_eliminar.split(',') if id.strip()]
						Imagen.objects.filter(id__in=ids_eliminar, producto=producto).delete()
					
					# Procesar nuevas imágenes (guardarlas temporalmente)
					imagenes_nuevas = request.FILES.getlist('imagenes')
					print(f"\n{'='*50}")
					print(f"DEBUG EDIT - Total imágenes nuevas recibidas: {len(imagenes_nuevas)}")
					print(f"DEBUG EDIT - request.FILES keys: {list(request.FILES.keys())}")
					for idx, img in enumerate(imagenes_nuevas):
						print(f"  Imagen {idx}: {img.name} ({img.size} bytes)")
					print(f"{'='*50}\n")
					
					# Obtener imágenes existentes del producto
					imagenes_existentes = list(producto.imagenes.filter(variante__isnull=True))
					print(f"DEBUG - Imágenes existentes: {len(imagenes_existentes)}")
					
					# Combinar imágenes existentes + nuevas para el selector
					todas_imagenes = imagenes_existentes + imagenes_nuevas
					
					# Eliminar variantes antiguas (dentro de transacción)
					producto.variantes.all().delete()
					print("DEBUG - Variantes antiguas eliminadas")
					
					# Eliminar imágenes asociadas a variantes (se recrearán)
					producto.imagenes.filter(variante__isnull=False).delete()
					
					# Procesar nuevas variantes dinámicas desde el formulario
					variante_index = 0
					
					while True:
						sku_key = f'variante_{variante_index}_sku'
						if sku_key not in request.POST:
							print(f"DEBUG - No se encontró {sku_key}, finalizando bucle")
							break
						
						sku = request.POST.get(sku_key, '').strip()
						stock = request.POST.get(f'variante_{variante_index}_stock', '0')
						atributos_json = request.POST.get(f'variante_{variante_index}_atributos', '[]')
						
						print(f"\n=== DEBUG EDIT VARIANTE {variante_index} ===")
						print(f"SKU recibido: '{sku}'")
						print(f"Stock recibido: '{stock}' (tipo: {type(stock)})")
						print(f"Atributos JSON: {atributos_json[:100]}")
						
						print(f"\nDEBUG - Procesando variante {variante_index}:")
						print(f"  SKU: {sku}")
						print(f"  Stock: {stock}")
						print(f"  Atributos: {atributos_json[:100]}...")
						
						# Primero, verificar si hay un atributo de talla para asignarlo al campo talla
						talla_obj = None
						
						try:
							atributos_data = json.loads(atributos_json)
							for attr in atributos_data:
								atributo_nombre = attr.get('atributoNombre', '').lower()
								valor_nombre = attr.get('valorNombre', '')
								
								# Si es una talla, buscar o crear el objeto Talla
								if 'talla' in atributo_nombre and valor_nombre:
									talla_obj, created = Talla.objects.get_or_create(
										codigo=valor_nombre.upper(),
										defaults={'nombre': valor_nombre}
									)
									print(f"  Talla {'creada' if created else 'encontrada'}: {talla_obj.codigo}")
						except Exception as e:
							print(f"  ❌ Error extrayendo talla de atributos: {e}")
						
						# Generar SKU automático: slug-TALLA
						if not sku:
							if talla_obj:
								sku = f"{producto.slug}-{talla_obj.codigo}"
						
						# Crear la variante con la talla asignada
						variante = Variante.objects.create(
							producto=producto,
							talla=talla_obj,
							sku=sku,
							precio=producto.precio_base,
							stock=int(stock) if stock else 0
						)
						print(f"  ✅ Variante creada: ID={variante.id}, SKU={variante.sku}, Talla={variante.talla}, Stock={variante.stock}")
						
						# Procesar atributos adicionales de la variante
						try:
							atributos_data = json.loads(atributos_json)
							for attr in atributos_data:
								atributo_nombre = (attr.get('atributoNombre') or '').strip().lower()
								if atributo_nombre == 'marca':
									continue

								valor_id = attr.get('valorId')
								if valor_id:
									valor_atributo = ValorAtributo.objects.get(id=valor_id)
									if valor_atributo.atributo.nombre.strip().lower() == 'marca':
										continue

									VarianteAtributo.objects.create(
										variante=variante,
										valor_atributo=valor_atributo
									)
						except Exception as e:
							print(f"  ❌ Error procesando atributos de variante: {e}")
						
						variante_index += 1
					
					print(f"\nDEBUG - Total variantes procesadas: {variante_index}")
					
					# GUARDAR TODAS LAS IMÁGENES NUEVAS DEL PRODUCTO
					imagenes_guardadas = 0
					for imagen_file in imagenes_nuevas:
						Imagen.objects.create(
							producto=producto,
							imagen=imagen_file,
							variante=None  # Todas las imágenes son del producto
						)
						imagenes_guardadas += 1
						print(f"DEBUG - Imagen guardada: {imagen_file.name}")

					# Restaurar valor real solicitado por el formulario.
					if producto.bajo_pedido != bajo_pedido_solicitado:
						producto.bajo_pedido = bajo_pedido_solicitado
						producto.save(update_fields=['bajo_pedido'])
				
				messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente con {variante_index} variante(s) y {imagenes_guardadas} imagen(es) nueva(s).')
				return redirect('productos:admin_productos_list')
			except IntegrityError as e:
				print(f"ERROR INTEGRITY - admin_producto_edit: {e}")
				messages.error(request, 'Error de integridad al guardar el producto. No se aplicaron cambios parciales.')
				return redirect('productos:admin_productos_list')
			except Exception as e:
				print(f"ERROR GENERAL - admin_producto_edit: {e}")
				messages.error(request, f'Error al actualizar el producto: {str(e)}')
				return redirect('productos:admin_productos_list')
	else:
		form = ProductoForm(instance=producto)
		
		# Preparar datos de variantes existentes para el JavaScript
		variantes_data = []
		atributo_talla = Atributo.objects.filter(nombre__iexact='talla').first()
		atributo_color = Atributo.objects.filter(nombre__iexact='color').first()
		
		for variante in producto.variantes.all():
			print(f"\nDEBUG GET - Procesando variante: {variante.sku}")
			atributos = []
			
			# Verificar si tiene talla como campo directo
			if variante.talla and atributo_talla:
				# Buscar el ValorAtributo correspondiente a esta talla
				valor_talla = ValorAtributo.objects.filter(
					atributo=atributo_talla,
					valor=variante.talla.codigo
				).first()
				if valor_talla:
					atributos.append({
						'atributoId': atributo_talla.id,
						'atributoNombre': atributo_talla.nombre,
						'valorId': valor_talla.id,
						'valorNombre': valor_talla.valor,
					})
					print(f"DEBUG GET - Variante {variante.sku}: Talla {variante.talla.codigo} convertida a atributo")
			
			if variante.color and atributo_color:
				# Buscar el ValorAtributo correspondiente al color
				valor_color = ValorAtributo.objects.filter(
					atributo=atributo_color,
					valor=variante.color
				).first()
				if valor_color:
					atributos.append({
						'atributoId': atributo_color.id,
						'atributoNombre': atributo_color.nombre,
						'valorId': valor_color.id,
						'valorNombre': valor_color.valor,
					})
					print(f"DEBUG GET - Variante {variante.sku}: Color {variante.color} convertido a atributo")
			
			# Si no se encontraron atributos desde campos directos, buscar en sistema de atributos
			if not atributos:
				for va in variante.atributos.all():
					if va.valor_atributo.atributo.nombre.strip().lower() == 'marca':
						continue

					atributos.append({
						'atributoId': va.valor_atributo.atributo.id,
						'atributoNombre': va.valor_atributo.atributo.nombre,
						'valorId': va.valor_atributo.id,
						'valorNombre': va.valor_atributo.valor,
					})
				print(f"DEBUG GET - Variante {variante.sku}: Usando atributos del sistema")
			
			variantes_data.append({
				'sku': variante.sku,
				'precio': str(variante.precio),
				'stock': variante.stock,
				'atributos': atributos,
				'imagen_index': None  # Se llenará abajo
			})
		
		# Obtener imágenes del producto y mapear cuál está usando cada variante
		imagenes_producto = list(producto.imagenes.all().order_by('posicion'))
		imagenes_data = []
		
		for idx, img in enumerate(imagenes_producto):
			imagen_info = {
				'id': img.id,
				'url': img.imagen.url,
				'posicion': idx,
				'variante_sku': img.variante.sku if img.variante else None
			}
			
			# Si esta imagen está asociada a una variante, actualizar variantes_data
			if img.variante:
				# Actualizar variantes_data para indicar qué imagen usa
				for vdata in variantes_data:
					if vdata['sku'] == img.variante.sku:
						vdata['imagen_index'] = idx
						break
			
			imagenes_data.append(imagen_info)
	
	print(f"\nDEBUG GET - Total variantes preparadas: {len(variantes_data)}")
	print(f"DEBUG GET - Total imágenes: {len(imagenes_data)}")
	print(f"DEBUG GET - Imágenes: {imagenes_data}")
	
	# Convertir datos a JSON para el template
	import json
	variantes_json = json.dumps(variantes_data)
	imagenes_json = json.dumps(imagenes_data)
	
	return render(request, 'edit-product.html', {
		'form': form,
		'producto': producto,
		'categorias': Categoria.objects.filter(estado=True),
		'colecciones': Coleccion.objects.filter(activo=True),
		'atributos': Atributo.objects.filter(activo=True).exclude(nombre__iexact='color').exclude(nombre__iexact='marca'),
		'variantes_json': variantes_json,
		'imagenes_producto': imagenes_json,
		'marcas_existentes': _get_marcas_existentes(),
	})


@admin_required
def admin_producto_delete(request, pk):
	"""Elimina un producto (vista de confirmación o procesamiento directo)"""
	if request.user.rol != 'admin_tienda' and not request.user.is_staff:
		messages.error(request, 'No tienes permiso para acceder.')
		return redirect('core:inicio')
	
	try:
		producto = Producto.objects.get(pk=pk)
	except Producto.DoesNotExist:
		messages.error(request, 'El producto no existe.')
		return redirect('productos:admin_productos_list')
	
	if request.method == 'POST':
		nombre_producto = producto.nombre
		# Django eliminará automáticamente las variantes relacionadas (CASCADE)
		# También eliminará VarianteAtributo relacionadas con esas variantes
		producto.delete()
		messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente.')
		return redirect('productos:admin_productos_list')
	
	# Si no es POST, mostrar confirmación (opcional, por ahora redirigir)
	messages.warning(request, 'Método no permitido.')
	return redirect('productos:admin_productos_list')


@admin_required
def admin_atributos_list(request):
	"""Lista todos los atributos con búsqueda y paginación"""
	if request.user.rol != 'admin_tienda' and not request.user.is_staff:
		messages.error(request, 'No tienes permiso para acceder.')
		return redirect('core:inicio')
	
	search = request.GET.get('search', '').strip()
	atributos_list = Atributo.objects.prefetch_related('valores').order_by('posicion', 'nombre')
	
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


def _parse_valores_atributo(raw_valores):
	"""Normaliza valores de atributo separados por coma sin duplicados."""
	valores_limpios = []
	for valor in (raw_valores or '').split(','):
		valor = valor.strip()
		if valor and valor not in valores_limpios:
			valores_limpios.append(valor)
	return valores_limpios


@admin_required
def admin_atributo_add(request):
	"""Agregar nuevo atributo"""
	if request.method == 'POST':
		# Procesar formulario
		nombre = (request.POST.get('nombre') or '').strip()
		tipo = (request.POST.get('tipo') or 'texto').strip()
		descripcion = (request.POST.get('descripcion') or '').strip()
		valores_raw = request.POST.get('valores', '')

		if not nombre:
			messages.error(request, 'El nombre del atributo es obligatorio.')
			return render(request, 'add-attributes.html', {
				'valores_str': valores_raw,
			})

		tipos_validos = {choice[0] for choice in Atributo.TIPO_CHOICES}
		if tipo not in tipos_validos:
			tipo = 'texto'
		
		from django.utils.text import slugify
		slug_base = slugify(nombre) or 'atributo'
		slug = slug_base
		slug_suffix = 2
		while Atributo.objects.filter(slug=slug).exists():
			slug = f'{slug_base}-{slug_suffix}'
			slug_suffix += 1

		if Atributo.objects.filter(nombre__iexact=nombre).exists():
			messages.error(request, f'Ya existe un atributo con el nombre "{nombre}".')
			return render(request, 'add-attributes.html', {
				'valores_str': valores_raw,
			})
		
		# Crear atributo
		atributo = Atributo.objects.create(
			nombre=nombre,
			slug=slug,
			tipo=tipo,
			descripcion=descripcion,
			activo=True
		)
		
		# Procesar valores
		for i, valor in enumerate(_parse_valores_atributo(valores_raw), 1):
				ValorAtributo.objects.create(
					atributo=atributo,
					valor=valor,
					posicion=i,
					activo=True
				)
		
		messages.success(request, f'Atributo "{nombre}" creado exitosamente.')
		return redirect('productos:admin_atributos_list')
	
	return render(request, 'add-attributes.html', {})


@admin_required  
def admin_atributo_edit(request, pk):
	"""Editar atributo existente"""
	atributo = get_object_or_404(Atributo, pk=pk)
	
	if request.method == 'POST':
		nombre = (request.POST.get('nombre') or '').strip()
		tipo = (request.POST.get('tipo') or 'texto').strip()
		descripcion = (request.POST.get('descripcion') or '').strip()
		valores_raw = request.POST.get('valores', '')

		if not nombre:
			messages.error(request, 'El nombre del atributo es obligatorio.')
			return render(request, 'add-attributes.html', {
				'atributo': atributo,
				'valores_str': valores_raw,
			})

		tipos_validos = {choice[0] for choice in Atributo.TIPO_CHOICES}
		if tipo not in tipos_validos:
			tipo = 'texto'

		if Atributo.objects.filter(nombre__iexact=nombre).exclude(pk=atributo.pk).exists():
			messages.error(request, f'Ya existe un atributo con el nombre "{nombre}".')
			return render(request, 'add-attributes.html', {
				'atributo': atributo,
				'valores_str': valores_raw,
			})

		atributo.nombre = nombre
		atributo.tipo = tipo
		atributo.descripcion = descripcion
		
		from django.utils.text import slugify
		slug_base = slugify(atributo.nombre) or 'atributo'
		slug = slug_base
		slug_suffix = 2
		while Atributo.objects.filter(slug=slug).exclude(pk=atributo.pk).exists():
			slug = f'{slug_base}-{slug_suffix}'
			slug_suffix += 1
		atributo.slug = slug
		atributo.save()
		
		# Actualizar valores
		atributo.valores.all().delete()
		for i, valor in enumerate(_parse_valores_atributo(valores_raw), 1):
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


@admin_required
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
	atributos = Atributo.objects.filter(activo=True).exclude(nombre__iexact='marca').prefetch_related('valores').order_by('posicion', 'nombre')
	
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


@login_required
def api_categorias_list(request):
	"""API para obtener todas las categorías con su jerarquía"""
	from django.http import JsonResponse
	categorias = Categoria.objects.filter(estado=True).order_by('nombre')
	
	data = []
	for categoria in categorias:
		data.append({
			'id': categoria.id,
			'nombre': categoria.nombre,
			'slug': categoria.slug,
			'padre': categoria.padre.id if categoria.padre else None,
			'coleccion': categoria.coleccion.id if categoria.coleccion else None,
		})
	
	return JsonResponse(data, safe=False)


@login_required
@login_required
def api_colecciones_list(request):
	"""API para obtener todas las colecciones activas"""
	from django.http import JsonResponse
	from .models import Coleccion
	colecciones = Coleccion.objects.filter(activo=True).order_by('nombre')
	
	data = []
	for coleccion in colecciones:
		data.append({
			'id': coleccion.id,
			'nombre': coleccion.nombre,
			'slug': coleccion.slug,
		})
	
	return JsonResponse(data, safe=False)


# =========================
#  COLECCIONES - ADMIN ECOMUS
# =========================
from .models import Coleccion

@admin_required
def admin_colecciones_list(request):
	"""Lista de colecciones con paginación y búsqueda"""
	search = request.GET.get('search', '')
	
	colecciones = Coleccion.objects.all().order_by('nombre')
	
	if search:
		colecciones = colecciones.filter(
			Q(nombre__icontains=search) |
			Q(descripcion__icontains=search)
		)
	
	# Paginación
	from django.core.paginator import Paginator
	paginator = Paginator(colecciones, 10)
	page = request.GET.get('page')
	colecciones = paginator.get_page(page)
	
	return render(request, 'collections-list.html', {
		'colecciones': colecciones,
		'search': search,
	})


@admin_required
def admin_coleccion_add(request):
	"""Agregar nueva colección"""
	if request.method == 'POST':
		from .forms import ColeccionForm
		form = ColeccionForm(request.POST, request.FILES)
		
		if form.is_valid():
			coleccion = form.save()
			messages.success(request, f'Colección "{coleccion.nombre}" creada exitosamente.')
			return redirect('productos:admin_colecciones_list')
		else:
			messages.error(request, 'Por favor corrige los errores en el formulario.')
	else:
		from .forms import ColeccionForm
		form = ColeccionForm()
	
	return render(request, 'collection-add.html', {
		'form': form,
	})


@admin_required
def admin_coleccion_edit(request, pk):
	"""Editar colección existente"""
	coleccion = get_object_or_404(Coleccion, pk=pk)
	imagen_anterior_nombre = coleccion.imagen.name if coleccion.imagen else None
	imagen_anterior_storage = coleccion.imagen.storage if coleccion.imagen else None
	
	if request.method == 'POST':
		from .forms import ColeccionForm
		form = ColeccionForm(request.POST, request.FILES, instance=coleccion)
		remove_imagen = request.POST.get('remove_imagen') == 'true'
		nueva_imagen = request.FILES.get('imagen')

		if form.is_valid():
			coleccion_actualizada = form.save(commit=False)
			imagen_actualizada = False
			imagen_eliminada = False

			# Evitar borrar usando el field de la misma instancia antes del save,
			# porque puede cerrar el archivo recién subido (InMemoryUploadedFile).
			if nueva_imagen:
				# ModelForm ya asigna el nuevo archivo en commit=False.
				imagen_actualizada = True
			elif remove_imagen:
				coleccion_actualizada.imagen = None
				imagen_eliminada = bool(imagen_anterior_nombre)

			coleccion_actualizada.save()

			# Limpiar archivo anterior solo después de guardar exitosamente.
			imagen_nueva_nombre = coleccion_actualizada.imagen.name if coleccion_actualizada.imagen else None
			if imagen_actualizada and imagen_anterior_nombre and imagen_anterior_storage:
				if imagen_anterior_nombre != imagen_nueva_nombre:
					imagen_anterior_storage.delete(imagen_anterior_nombre)
			elif imagen_eliminada and imagen_anterior_nombre and imagen_anterior_storage:
				imagen_anterior_storage.delete(imagen_anterior_nombre)

			if imagen_actualizada:
				messages.success(request, f'Colección "{coleccion_actualizada.nombre}" actualizada con nueva imagen.')
			elif imagen_eliminada:
				messages.success(request, f'Colección "{coleccion_actualizada.nombre}" actualizada y la imagen fue eliminada.')
			else:
				messages.success(request, f'Colección "{coleccion_actualizada.nombre}" actualizada.')

			return redirect('productos:admin_colecciones_list')
		else:
			if 'imagen' in form.errors:
				messages.error(request, f'La imagen fue rechazada: {form.errors["imagen"][0]}')
			else:
				messages.error(request, 'Por favor corrige los errores en el formulario.')
	else:
		from .forms import ColeccionForm
		form = ColeccionForm(instance=coleccion)
	
	return render(request, 'collection-edit.html', {
		'coleccion': coleccion,
		'form': form,
	})


@admin_required
def admin_coleccion_delete(request, pk):
	"""Eliminar colección"""
	coleccion = get_object_or_404(Coleccion, pk=pk)
	nombre = coleccion.nombre
	coleccion.delete()
	messages.success(request, f'Colección "{nombre}" eliminada.')
	return redirect('productos:admin_colecciones_list')



# =========================
#  API QUICK VIEW
# =========================
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def producto_quick_view(request, producto_id):
    """
    API endpoint para obtener datos del producto para Quick View
    Funciona con el sistema de Atributos y es compatible con tu estructura actual
    """
    try:
        # Usar el mismo patrón de prefetch que usas en ProductoListView
        producto = Producto.objects.select_related(
            "categoria", "coleccion"
        ).prefetch_related(
            "imagenes",
            "variantes",
            "variantes__talla",
            "variantes__atributos__valor_atributo__atributo"
        ).get(id=producto_id, activo=True)
        
        # Preparar imágenes (mismo formato que usas en panel_producto_crear)
        imagenes = []
        for img in producto.imagenes.all().order_by('posicion', 'created_at')[:5]:
            imagenes.append({
                'src': img.src,
                'url': img.src
            })
        
        # Obtener todos los atributos únicos del producto
        atributos_dict = {}
        
        for variante in producto.variantes.all():
            # Primero intentar extraer desde campos directos (talla FK y color CharField)
            # Esto es compatible con tu lógica en admin_producto_edit
            
            # Procesar Talla desde FK
            if variante.talla:
                atributo_talla = Atributo.objects.filter(
                    nombre__icontains='talla'
                ).first()
                
                if atributo_talla:
                    if atributo_talla.id not in atributos_dict:
                        atributos_dict[atributo_talla.id] = {
                            'id': atributo_talla.id,
                            'nombre': atributo_talla.nombre,
                            'slug': atributo_talla.slug,
                            'tipo': atributo_talla.tipo,
                            'valores': {}
                        }
                    
                    # Buscar el ValorAtributo correspondiente
                    valor_talla = ValorAtributo.objects.filter(
                        atributo=atributo_talla,
                        valor=variante.talla.codigo
                    ).first()
                    
                    if valor_talla and valor_talla.id not in atributos_dict[atributo_talla.id]['valores']:
                        atributos_dict[atributo_talla.id]['valores'][valor_talla.id] = {
                            'id': valor_talla.id,
                            'valor': valor_talla.valor,
                            'codigo_color': valor_talla.codigo_color or ''
                        }
            
            # Procesar Color desde CharField
            if variante.color:
                atributo_color = Atributo.objects.filter(
                    nombre__icontains='color'
                ).first()
                
                if atributo_color:
                    if atributo_color.id not in atributos_dict:
                        atributos_dict[atributo_color.id] = {
                            'id': atributo_color.id,
                            'nombre': atributo_color.nombre,
                            'slug': atributo_color.slug,
                            'tipo': atributo_color.tipo,
                            'valores': {}
                        }
                    
                    # Buscar el ValorAtributo correspondiente
                    valor_color = ValorAtributo.objects.filter(
                        atributo=atributo_color,
                        valor=variante.color
                    ).first()
                    
                    if valor_color and valor_color.id not in atributos_dict[atributo_color.id]['valores']:
                        atributos_dict[atributo_color.id]['valores'][valor_color.id] = {
                            'id': valor_color.id,
                            'valor': valor_color.valor,
                            'codigo_color': valor_color.codigo_color or ''
                        }
            
            # Procesar atributos del sistema de VarianteAtributo
            for variante_atributo in variante.atributos.all():
                valor_attr = variante_atributo.valor_atributo
                atributo = valor_attr.atributo
                
                if atributo.id not in atributos_dict:
                    atributos_dict[atributo.id] = {
                        'id': atributo.id,
                        'nombre': atributo.nombre,
                        'slug': atributo.slug,
                        'tipo': atributo.tipo,
                        'valores': {}
                    }
                
                if valor_attr.id not in atributos_dict[atributo.id]['valores']:
                    atributos_dict[atributo.id]['valores'][valor_attr.id] = {
                        'id': valor_attr.id,
                        'valor': valor_attr.valor,
                        'codigo_color': valor_attr.codigo_color or ''
                    }
        
        # Preparar variantes con sus atributos (mismo patrón que admin_producto_edit)
        variantes = []
        variantes_stock = {}  # Para JSON de control de stock en quick view
        variante_default_id = None  # Para productos sin atributos
        atributo_talla = Atributo.objects.filter(nombre__icontains='talla').first()
        atributo_color = Atributo.objects.filter(nombre__icontains='color').first()
        
        for variante in producto.variantes.all():
            atributos_variante = {}
            
            # Extraer desde campos directos (talla FK y color CharField)
            if variante.talla and atributo_talla:
                valor_talla = ValorAtributo.objects.filter(
                    atributo=atributo_talla,
                    valor=variante.talla.codigo
                ).first()
                if valor_talla:
                    atributos_variante[atributo_talla.slug] = {
                        'atributo_id': atributo_talla.id,
                        'atributo_nombre': atributo_talla.nombre,
                        'valor_id': valor_talla.id,
                        'valor': valor_talla.valor,
                        'codigo_color': valor_talla.codigo_color or ''
                    }
            
            if variante.color and atributo_color:
                valor_color = ValorAtributo.objects.filter(
                    atributo=atributo_color,
                    valor=variante.color
                ).first()
                if valor_color:
                    atributos_variante[atributo_color.slug] = {
                        'atributo_id': atributo_color.id,
                        'atributo_nombre': atributo_color.nombre,
                        'valor_id': valor_color.id,
                        'valor': valor_color.valor,
                        'codigo_color': valor_color.codigo_color or ''
                    }
            
            # Completar con atributos del sistema
            for va in variante.atributos.all():
                valor_attr = va.valor_atributo
                atributo = valor_attr.atributo
                
                if atributo.slug not in atributos_variante:
                    atributos_variante[atributo.slug] = {
                        'atributo_id': atributo.id,
                        'atributo_nombre': atributo.nombre,
                        'valor_id': valor_attr.id,
                        'valor': valor_attr.valor,
                        'codigo_color': valor_attr.codigo_color or ''
                    }
            
            variantes.append({
                'id': variante.id,
                'sku': variante.sku,
                'precio': str(variante.precio or producto.precio_base),
                'stock': variante.stock,
                'atributos': atributos_variante,
                # Mantener compatibilidad
                'talla': variante.talla.codigo if variante.talla else None,
                'color': variante.color or None
            })
            
            # Preparar JSON de stock para JavaScript (igual que en product_detail)
            if variante.talla:
                key = f"{variante.talla.codigo}"
                if variante.color and variante.color.strip():
                    key += f"_{variante.color}"
                variantes_stock[key] = {
                    'id': variante.id,
                    'stock': variante.stock,
                    'talla': variante.talla.codigo if variante.talla else None,
                    'color': variante.color if variante.color else '',
                    'precio': str(variante.precio) if variante.precio else str(producto.precio_base)
                }
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
        
        # Calcular stock total (mismo patrón que ProductoListView)
        from django.db.models import Sum
        total_stock = producto.variantes.aggregate(
            total=Sum('stock')
        )['total'] or 0

        # Estado del wishlist para el usuario actual (si está autenticado)
        in_wishlist = False
        wishlist_item_id = None
        if request.user.is_authenticated:
            from apps.usuarios.models import Wishlist
            wishlist_item = Wishlist.objects.filter(usuario=request.user, producto=producto).first()
            if wishlist_item:
                in_wishlist = True
                wishlist_item_id = wishlist_item.id
        
        data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'url': producto.get_absolute_url(),
            'precio': str(producto.precio_base),
            'descripcion_corta': producto.descripcion_corta or '',
            'descripcion_larga': producto.descripcion_larga or '',
            'marca': producto.marca or '',
            'stock': total_stock,
            'imagenes': imagenes,
            'variantes': variantes,
            'variantes_stock': variantes_stock,  # JSON para control de stock en JS
            'variante_default_id': variante_default_id,  # Para productos sin atributos
            'atributos': list(atributos_dict.values()),
            'tiene_tallas': producto.tiene_tallas,
            'in_wishlist': in_wishlist,
            'wishlist_item_id': wishlist_item_id,
        }
        
        return JsonResponse(data)
        
    except Producto.DoesNotExist:
        return JsonResponse({
            'error': 'Producto no encontrado'
        }, status=404)
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Para debug
        return JsonResponse({
            'error': str(e)
        }, status=500)


# =============================================================================
#  QUICK EDIT - Edición rápida de productos (solo administradores is_staff)
# =============================================================================

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@staff_member_required(login_url='/login/')
@require_GET
def get_product_data_quick_edit(request, producto_id):
    """
    Vista GET que devuelve los datos de un producto en JSON para rellenar
    el formulario del modal de edición rápida.

    URL: /productos/api/quick-edit/<producto_id>/
    Respuesta: JSON con datos básicos, imágenes y variantes del producto.
    """
    from .models import Producto, Imagen, Variante

    try:
        # Obtener el producto con sus relaciones
        producto = get_object_or_404(
            Producto.objects
            .prefetch_related('imagenes', 'variantes__talla'),
            pk=producto_id
        )

        # Serializar imágenes (solo imágenes, no videos)
        imagenes_data = []
        for img in producto.imagenes.filter(tipo_medio='imagen').order_by('posicion', 'created_at'):
            if img.imagen:
                imagenes_data.append({
                    'id': img.id,
                    'url': img.imagen.url,
                    'posicion': img.posicion,
                })
            elif img.url:
                imagenes_data.append({
                    'id': img.id,
                    'url': img.url,
                    'posicion': img.posicion,
                })

        # Serializar variantes con talla y stock (sin precio por variante)
        variantes_data = []
        for variante in producto.variantes.all().select_related('talla'):
            variantes_data.append({
                'id': variante.id,
                'sku': variante.sku,
                'talla_codigo': variante.talla.codigo if variante.talla else None,
                'color': variante.color,
                'stock': variante.stock,
            })

        # Todas las tallas del sistema (para el selector "Agregar Talla")
        from .models import ValorAtributo
        valores_talla = ValorAtributo.objects.filter(
            atributo__nombre__icontains='talla',
            activo=True
        ).order_by('posicion', 'valor')
        
        tallas_disponibles = []
        for v in valores_talla:
            tallas_disponibles.append({
                'id': v.id,
                'codigo': v.valor.upper(),
                'nombre': v.valor
            })

        # Construir respuesta JSON
        data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'marca': producto.marca or '',
            'precio_base': float(producto.precio_base),
            'descripcion_corta': producto.descripcion_corta or '',
            'imagenes': imagenes_data,
            'variantes': variantes_data,
            'tallas_disponibles': tallas_disponibles,
        }

        return JsonResponse(data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required(login_url='/login/')
def update_product_quick(request, producto_id):
    """
    Vista POST que recibe y guarda los cambios del formulario de edición rápida.

    Maneja:
    - Actualización de datos básicos (nombre, marca, precio, descripción).
    - Reemplazo de imágenes existentes (si se sube un archivo nuevo).
    - Eliminación de imágenes (si se marca el checkbox de eliminar).
    - Agregar nuevas imágenes adicionales.
    - Actualización de stock y precio de cada variante.

    URL: /productos/api/quick-edit/<producto_id>/guardar/
    Respuesta: JSON { ok: true, nombre: ..., precio_base: ..., main_image_url: ... }
    """
    import os
    from .models import Producto, Imagen, Variante

    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        producto = get_object_or_404(Producto, pk=producto_id)

        # ── 1. Actualizar datos básicos ────────────────────────────────────
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            producto.nombre = nombre

        marca = request.POST.get('marca', '').strip()
        if marca:
            producto.marca = marca

        precio_base_raw = request.POST.get('precio_base', '').strip()
        if precio_base_raw:
            try:
                from decimal import Decimal
                producto.precio_base = Decimal(precio_base_raw)
            except Exception:
                pass  # Ignorar si no es un número válido

        descripcion_corta = request.POST.get('descripcion_corta', '').strip()
        producto.descripcion_corta = descripcion_corta

        producto.save(update_fields=['nombre', 'marca', 'precio_base', 'descripcion_corta', 'updated_at'])

        # ── 2. Eliminar imágenes marcadas para borrar ──────────────────────
        ids_a_eliminar = request.POST.getlist('eliminar_imagenes[]')
        for imagen_id_str in ids_a_eliminar:
            try:
                imagen_id = int(imagen_id_str)
                img_obj = Imagen.objects.get(pk=imagen_id, producto=producto)
                # Borrar archivo físico del disco
                if img_obj.imagen and img_obj.imagen.name:
                    ruta_archivo = img_obj.imagen.path
                    if os.path.isfile(ruta_archivo):
                        os.remove(ruta_archivo)
                # Eliminar el registro de la BD
                img_obj.delete()
            except (Imagen.DoesNotExist, ValueError, OSError) as e:
                # No interrumpir el flujo por una imagen que ya no existe
                print(f'[QuickEdit] Advertencia al eliminar imagen {imagen_id_str}: {e}')

        # ── 3. Reemplazar imágenes existentes con archivos nuevos ──────────
        # Los campos de reemplazo se envían como imagen_nueva_<ID>
        for clave, archivo in request.FILES.items():
            if not clave.startswith('imagen_nueva_'):
                continue
            try:
                imagen_id = int(clave.replace('imagen_nueva_', ''))
                img_obj = Imagen.objects.get(pk=imagen_id, producto=producto)

                # Borrar archivo físico anterior
                if img_obj.imagen and img_obj.imagen.name:
                    ruta_antigua = img_obj.imagen.path
                    if os.path.isfile(ruta_antigua):
                        os.remove(ruta_antigua)

                # Guardar el nuevo archivo
                img_obj.imagen = archivo
                img_obj.save(update_fields=['imagen'])
            except (Imagen.DoesNotExist, ValueError, OSError) as e:
                print(f'[QuickEdit] Advertencia al reemplazar imagen {clave}: {e}')

        # ── 4. Agregar nuevas imágenes adicionales ─────────────────────────
        nuevas_imagenes = request.FILES.getlist('imagenes_nuevas')
        posicion_max = producto.imagenes.count()  # Posición inicial para las nuevas
        for idx, archivo_nuevo in enumerate(nuevas_imagenes):
            Imagen.objects.create(
                producto=producto,
                imagen=archivo_nuevo,
                tipo_medio='imagen',
                posicion=posicion_max + idx,
            )

        # ── 5. Actualizar stock de variantes EXISTENTES (precio único en producto) ──
        for clave, valor in request.POST.items():
            if clave.startswith('variante_stock_'):
                try:
                    variante_id = int(clave.replace('variante_stock_', ''))
                    variante = Variante.objects.get(pk=variante_id, producto=producto)
                    variante.stock = max(0, int(valor)) if valor.strip() else 0
                    variante.save(update_fields=['stock', 'updated_at'])
                except (Variante.DoesNotExist, ValueError) as e:
                    print(f'[QuickEdit] Advertencia al actualizar stock variante {clave}: {e}')

        # ── 6. Eliminar variantes (tallas) marcadas para quitar ────────────
        from django.db import IntegrityError
        ids_variantes_eliminar = request.POST.getlist('eliminar_variantes[]')
        for var_id_str in ids_variantes_eliminar:
            try:
                var_id = int(var_id_str)
                variante = Variante.objects.get(pk=var_id, producto=producto)
                variante.delete()
            except (Variante.DoesNotExist, ValueError) as e:
                print(f'[QuickEdit] Advertencia al eliminar variante {var_id_str}: {e}')

        # ── 7. Crear nuevas variantes (tallas agregadas en el modal) ───────
        import uuid
        from .models import Talla, ValorAtributo, VarianteAtributo
        idx = 0
        while True:
            talla_id_str = request.POST.get(f'nueva_variante_talla_{idx}')
            if talla_id_str is None:
                break
            try:
                talla_id  = int(talla_id_str) # Esto ahora es el ID de ValorAtributo
                stock_raw = request.POST.get(f'nueva_variante_stock_{idx}', '0').strip()
                stock     = max(0, int(stock_raw)) if stock_raw else 0

                # Obtener el ValorAtributo
                valor_attr = ValorAtributo.objects.get(pk=talla_id)
                
                # Sincronizar o crear la Talla correspondiente
                talla, _ = Talla.objects.get_or_create(
                    codigo=valor_attr.valor.upper(),
                    defaults={'nombre': valor_attr.valor}
                )

                # Verificar que la combinación producto + talla no exista ya
                if Variante.objects.filter(producto=producto, talla=talla).exists():
                    print(f'[QuickEdit] Talla {talla.codigo} ya existe para este producto.')
                else:
                    # Generar SKU único: slug-TALLA[-sufijo si colisiona]
                    sku_base = f"{producto.slug}-{talla.codigo}"
                    sku = sku_base
                    if Variante.objects.filter(sku=sku).exists():
                        sku = f"{sku_base}-{uuid.uuid4().hex[:4]}"

                    nueva_variante = Variante.objects.create(
                        producto=producto,
                        talla=talla,
                        sku=sku,
                        precio=producto.precio_base,  # hereda el precio base del producto
                        stock=stock,
                    )
                    
                    # Para mantener consistencia con el sistema de atributos
                    VarianteAtributo.objects.create(
                        variante=nueva_variante,
                        valor_atributo=valor_attr
                    )
                    
            except (ValorAtributo.DoesNotExist, Talla.DoesNotExist, ValueError, IntegrityError) as e:
                print(f'[QuickEdit] Advertencia al crear variante {idx}: {e}')
            idx += 1

        # ── 8. Preparar URL de imagen principal para actualizar el DOM ─────
        main_image_url = ''
        primera_imagen = producto.imagenes.filter(tipo_medio='imagen').order_by('posicion', 'created_at').first()
        if primera_imagen and primera_imagen.imagen:
            main_image_url = primera_imagen.imagen.url

        # ── 9. Respuesta de éxito ──────────────────────────────────────────
        return JsonResponse({
            'ok': True,
            'nombre': producto.nombre,
            'precio_base': float(producto.precio_base),
            'main_image_url': main_image_url,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)