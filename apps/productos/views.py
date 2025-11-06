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
				from .models import Variante, VarianteAtributo, ValorAtributo
				variante = Variante.objects.create(
					producto=producto,
					sku=sku if sku else f'VAR-{producto.id}-{variante_index}',
					precio=producto.precio_base,  # Usar el precio_base del producto
					stock=int(stock) if stock else 0
				)
				
				# Asociar atributos a la variante
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
	if request.user.rol != 'admin_tienda' and not request.user.is_staff:
		messages.error(request, 'No tienes permiso para acceder.')
		return redirect('core:inicio')
	
	try:
		producto = Producto.objects.prefetch_related('variantes__atributos__valor_atributo').get(pk=pk)
	except Producto.DoesNotExist:
		messages.error(request, 'El producto no existe.')
		return redirect('productos:admin_productos_list')
	
	if request.method == 'POST':
		form = ProductoForm(request.POST, request.FILES, instance=producto)
		
		if form.is_valid():
			producto = form.save()
			
			# Procesar eliminación de imágenes
			imagenes_eliminar = request.POST.get('imagenes_eliminar', '')
			if imagenes_eliminar:
				from .models import Imagen
				ids_eliminar = [int(id) for id in imagenes_eliminar.split(',') if id.strip()]
				Imagen.objects.filter(id__in=ids_eliminar, producto=producto).delete()
			
			# Procesar nuevas imágenes
			imagenes = request.FILES.getlist('imagenes')
			if imagenes:
				from .models import Imagen
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
			
			# Procesar nuevas variantes dinámicas desde el formulario
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
				from .models import Variante, VarianteAtributo, ValorAtributo
				variante = Variante.objects.create(
					producto=producto,
					sku=sku if sku else f'VAR-{producto.id}-{variante_index}',
					precio=producto.precio_base,  # Usar el precio_base del producto
					stock=int(stock) if stock else 0
				)
				
				# Asociar atributos a la variante
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
			
			total_imagenes = len(imagenes) if imagenes else 0
			messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente con {variante_index} variante(s) y {total_imagenes} nueva(s) imagen(es).')
			return redirect('productos:admin_productos_list')
	else:
		form = ProductoForm(instance=producto)
	
	# Preparar datos de variantes existentes para el JavaScript
	variantes_data = []
	for variante in producto.variantes.all():
		atributos = []
		for va in variante.atributos.all():
			atributos.append({
				'atributoId': va.valor_atributo.atributo.id,
				'atributoNombre': va.valor_atributo.atributo.nombre,
				'valorId': va.valor_atributo.id,
				'valorNombre': va.valor_atributo.valor,
			})
		variantes_data.append({
			'sku': variante.sku,
			'precio': str(variante.precio),
			'stock': variante.stock,
			'atributos': atributos
		})
	
	import json
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
	categorias = Categoria.objects.filter(estado=True).order_by('posicion', 'nombre')
	
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
def api_colecciones_list(request):
	"""API para obtener todas las colecciones activas"""
	from django.http import JsonResponse
	from .models import Coleccion
	colecciones = Coleccion.objects.filter(activo=True).order_by('posicion', 'nombre')
	
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
	
	colecciones = Coleccion.objects.all().order_by('posicion', 'nombre')
	
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
		nombre = request.POST.get('nombre')
		descripcion = request.POST.get('descripcion', '')
		slug = request.POST.get('slug')
		activo = request.POST.get('activo') == 'on'
		destacada = request.POST.get('destacada') == 'on'
		posicion = int(request.POST.get('posicion', 0))
		imagen = request.FILES.get('imagen')
		
		# Crear colección
		coleccion = Coleccion.objects.create(
			nombre=nombre,
			slug=slug,
			descripcion=descripcion,
			activo=activo,
			destacada=destacada,
			posicion=posicion,
			imagen=imagen
		)
		
		messages.success(request, f'Colección "{nombre}" creada exitosamente.')
		return redirect('productos:admin_colecciones_list')
	
	return render(request, 'collection-add.html')


@login_required
def admin_coleccion_edit(request, pk):
	"""Editar colección existente"""
	coleccion = get_object_or_404(Coleccion, pk=pk)
	
	if request.method == 'POST':
		coleccion.nombre = request.POST.get('nombre')
		coleccion.descripcion = request.POST.get('descripcion', '')
		coleccion.slug = request.POST.get('slug')
		coleccion.activo = request.POST.get('activo') == 'on'
		coleccion.destacada = request.POST.get('destacada') == 'on'
		coleccion.posicion = int(request.POST.get('posicion', 0))
		
		if request.FILES.get('imagen'):
			coleccion.imagen = request.FILES.get('imagen')
		
		coleccion.save()
		
		messages.success(request, f'Colección "{coleccion.nombre}" actualizada.')
		return redirect('productos:admin_colecciones_list')
	
	return render(request, 'collection-edit.html', {
		'coleccion': coleccion,
	})


@login_required
def admin_coleccion_delete(request, pk):
	"""Eliminar colección"""
	coleccion = get_object_or_404(Coleccion, pk=pk)
	nombre = coleccion.nombre
	coleccion.delete()
	messages.success(request, f'Colección "{nombre}" eliminada.')
	return redirect('productos:admin_colecciones_list')
