from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView
from .models import Categoria, Estilo, Producto
from django.db.models import Sum, Min, Q, Max
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
				categoria = form.save(commit=False)
				# Asegurar que posicion tenga un valor por defecto
				if not hasattr(categoria, 'posicion') or categoria.posicion is None:
					categoria.posicion = 0
				categoria.save()
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


def panel_categoria_delete(request, pk):
	"""
	Eliminar una categoría
	"""
	try:
		categoria = Categoria.objects.get(pk=pk)
	except Categoria.DoesNotExist:
		messages.error(request, 'La categoría no existe.')
		return redirect('productos:panel_categorias')
	
	if request.method == 'POST':
		nombre_categoria = categoria.nombre
		# Verificar si tiene subcategorías
		if categoria.subcategorias.exists():
			messages.warning(
				request, 
				f'La categoría "{nombre_categoria}" tiene {categoria.subcategorias.count()} subcategorías. '
				'Las subcategorías quedarán sin categoría padre.'
			)
		
		# Obtener el ID del padre antes de eliminar (si es subcategoría)
		padre_id = categoria.padre.id if categoria.padre else None
		
		# Eliminar la categoría
		categoria.delete()
		messages.success(request, f'Categoría "{nombre_categoria}" eliminada exitosamente.')
		
		# Redirigir a la lista correcta
		if padre_id:
			return redirect(f'/admin-panel/categorias/?padre={padre_id}')
		else:
			return redirect('productos:panel_categorias')
	
	# Si no es POST, redirigir a la lista
	messages.error(request, 'Método no permitido.')
	return redirect('productos:panel_categorias')


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
		
		if form.is_valid():
			producto = form.save()
			
			# Procesar imágenes múltiples
			imagenes = request.FILES.getlist('imagenes')
			for index, imagen_file in enumerate(imagenes):
				from .models import Imagen
				Imagen.objects.create(
					producto=producto,
					imagen=imagen_file,
					posicion=index
				)
			
			# Procesar variantes dinámicas desde el formulario
			import json
			variante_index = 0
			while True:
				sku_key = f'variante_{variante_index}_sku'
				if sku_key not in request.POST:
					break
				
				sku = request.POST.get(sku_key, '').strip()
				stock = request.POST.get(f'variante_{variante_index}_stock', '0')
				atributos_json = request.POST.get(f'variante_{variante_index}_atributos', '[]')
				
				# Crear la variante usando el precio_base del producto
				from .models import Variante, VarianteAtributo, ValorAtributo, Talla
				
				# Primero, verificar si hay un atributo de talla para asignarlo al campo talla
				talla_obj = None
				color_valor = None
				
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
						
						# Si es color, guardarlo
						elif 'color' in atributo_nombre and valor_nombre:
							color_valor = valor_nombre
				except Exception as e:
					print(f"Error extrayendo talla/color de atributos: {e}")
				
				# Generar SKU automático: slug-TALLA (o slug-COLOR si no hay talla)
				if not sku:
					if talla_obj:
						sku = f"{producto.slug}-{talla_obj.codigo}"
					elif color_valor:
						sku = f"{producto.slug}-{color_valor.upper()}"
					else:
						sku = f"{producto.slug}-{variante_index + 1}"
				
				# Crear la variante con la talla asignada
				variante = Variante.objects.create(
					producto=producto,
					talla=talla_obj,  # Asignar la talla al campo ForeignKey
					color=color_valor,  # Asignar el color al campo CharField
					sku=sku,
					precio=producto.precio_base,
					stock=int(stock) if stock else 0
				)
				print(f"DEBUG - Variante creada: ID={variante.id}, SKU={variante.sku}, Talla={variante.talla}, Color={variante.color}, Stock={variante.stock}")
				
				# Asociar atributos a la variante (para mantener compatibilidad con sistema de atributos)
				try:
					atributos_data = json.loads(atributos_json)
					for attr in atributos_data:
						valor_id = attr.get('valorId')
						if valor_id:
							valor_atributo = ValorAtributo.objects.get(id=valor_id)
							VarianteAtributo.objects.create(
								variante=variante,
								valor_atributo=valor_atributo
							)
				except Exception as e:
					print(f"Error procesando atributos de variante: {e}")
				
				variante_index += 1
			
			total_imagenes = len(imagenes)
			messages.success(request, f'Producto "{producto.nombre}" creado exitosamente con {variante_index} variante(s) y {total_imagenes} imagen(es).')
			return redirect('productos:admin_productos_list')
	else:
		form = ProductoForm()
	
	return render(request, 'add-product.html', {
		'form': form,
	})


@login_required
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


@login_required
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
			producto = form.save()
			print(f"Producto guardado: {producto.nombre}")
			
			# Procesar eliminación de imágenes
			imagenes_eliminar = request.POST.get('imagenes_eliminar', '')
			if imagenes_eliminar:
				ids_eliminar = [int(id) for id in imagenes_eliminar.split(',') if id.strip()]
				Imagen.objects.filter(id__in=ids_eliminar, producto=producto).delete()
			
			# Procesar nuevas imágenes
			imagenes = request.FILES.getlist('imagenes')
			if imagenes:
				# Obtener la máxima posición actual
				max_posicion = producto.imagenes.aggregate(Max('posicion'))['posicion__max'] or 0
				for index, imagen_file in enumerate(imagenes):
					Imagen.objects.create(
						producto=producto,
						imagen=imagen_file,
						posicion=max_posicion + index + 1
					)
			
		# Eliminar variantes antiguas
		producto.variantes.all().delete()
		print("DEBUG - Variantes antiguas eliminadas")
		
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
			
			print(f"\nDEBUG - Procesando variante {variante_index}:")
			print(f"  SKU: {sku}")
			print(f"  Stock: {stock}")
			print(f"  Atributos: {atributos_json[:100]}...")
			
			# Primero, verificar si hay un atributo de talla para asignarlo al campo talla
			talla_obj = None
			color_valor = None
			
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
					
					# Si es color, guardarlo
					elif 'color' in atributo_nombre and valor_nombre:
						color_valor = valor_nombre
						print(f"  Color encontrado: {color_valor}")
			except Exception as e:
				print(f"  ❌ Error extrayendo talla/color de atributos: {e}")
			
			# Generar SKU automático: slug-TALLA (o slug-COLOR si no hay talla)
			if not sku:
				if talla_obj:
					sku = f"{producto.slug}-{talla_obj.codigo}"
				elif color_valor:
					sku = f"{producto.slug}-{color_valor.upper()}"
				else:
					sku = f"{producto.slug}-{variante_index + 1}"
			
			# Crear la variante con la talla asignada
			variante = Variante.objects.create(
				producto=producto,
				talla=talla_obj,
				color=color_valor,
				sku=sku,
				precio=producto.precio_base,
				stock=int(stock) if stock else 0
			)
			print(f"  ✅ Variante creada: ID={variante.id}, SKU={variante.sku}, Talla={variante.talla}, Color={variante.color}, Stock={variante.stock}")
			
			# Asociar atributos a la variante (para mantener compatibilidad con sistema de atributos)
			try:
				atributos_data = json.loads(atributos_json)
				for attr in atributos_data:
					valor_id = attr.get('valorId')
					if valor_id:
						valor_atributo = ValorAtributo.objects.get(id=valor_id)
						VarianteAtributo.objects.create(
							variante=variante,
							valor_atributo=valor_atributo
						)
			except Exception as e:
				print(f"  ❌ Error procesando atributos de variante: {e}")
			
			variante_index += 1
		
		print(f"\nDEBUG - Total variantes procesadas: {variante_index}")
		total_imagenes = len(imagenes) if imagenes else 0
		messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente con {variante_index} variante(s) y {total_imagenes} nueva(s) imagen(es).')
		return redirect('productos:admin_productos_list')
	else:
		form = ProductoForm(instance=producto)
	
	# Preparar datos de variantes existentes para el JavaScript
	variantes_data = []
	
	# Buscar atributos de talla y color una sola vez
	atributo_talla = Atributo.objects.filter(nombre__icontains='talla').first()
	atributo_color = Atributo.objects.filter(nombre__icontains='color').first()
	
	for variante in producto.variantes.all():
		atributos = []
		
		# Primero intentar extraer desde campos directos (talla FK y color CharField)
		if variante.talla and atributo_talla:
			# Buscar el ValorAtributo correspondiente a la talla
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
			'atributos': atributos
		})
	
	print(f"\nDEBUG GET - Total variantes preparadas: {len(variantes_data)}")
	print(f"JSON enviado al template: {json.dumps(variantes_data, indent=2)}\n")
	
	return render(request, 'edit-product.html', {
		'form': form,
		'producto': producto,
		'variantes_json': json.dumps(variantes_data),
	})


@login_required
def admin_producto_delete(request, pk):
	"""
	Eliminar un producto existente
	"""
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

@login_required
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


@login_required
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


@login_required
def admin_coleccion_edit(request, pk):
	"""Editar colección existente"""
	coleccion = get_object_or_404(Coleccion, pk=pk)
	
	if request.method == 'POST':
		from .forms import ColeccionForm
		form = ColeccionForm(request.POST, request.FILES, instance=coleccion)
		
		# Verificar si se solicitó eliminar la imagen actual
		if request.POST.get('remove_imagen') == 'true':
			if coleccion.imagen:
				coleccion.imagen.delete(save=False)
		
		if form.is_valid():
			form.save()
			messages.success(request, f'Colección "{coleccion.nombre}" actualizada.')
			return redirect('productos:admin_colecciones_list')
		else:
			messages.error(request, 'Por favor corrige los errores en el formulario.')
	else:
		from .forms import ColeccionForm
		form = ColeccionForm(instance=coleccion)
	
	return render(request, 'collection-edit.html', {
		'coleccion': coleccion,
		'form': form,
	})


@login_required
def admin_coleccion_delete(request, pk):
	"""Eliminar colección"""
	coleccion = get_object_or_404(Coleccion, pk=pk)
	nombre = coleccion.nombre
	coleccion.delete()
	messages.success(request, f'Colección "{nombre}" eliminada.')
	return redirect('productos:admin_colecciones_list')



