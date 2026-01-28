from django.contrib import admin
from .models import (
	Coleccion,
	Categoria,
	Estilo,
	Producto,
	Talla,
	Variante,
	Imagen,
	Atributo,
	ValorAtributo,
	VarianteAtributo,
	GlobalProductContent,
	ShippingInfo,
	ReturnPolicy,
	CarritoItem,
)


# =========================
#  COLECCIONES
# =========================
class CategoriaInline(admin.TabularInline):
	"""Inline para ver/agregar categorías dentro de una colección"""
	model = Categoria
	extra = 0
	fields = ('nombre', 'slug', 'padre', 'tipo', 'estado', 'posicion')
	prepopulated_fields = {'slug': ('nombre',)}
	show_change_link = True


@admin.register(Coleccion)
class ColeccionAdmin(admin.ModelAdmin):
	list_display = (
		'nombre',
		'slug',
		'activo',
		'destacada',
		'num_categorias',
		'created_at',
	)
	list_filter = ('activo', 'destacada', 'created_at')
	search_fields = ('nombre', 'slug', 'descripcion')
	prepopulated_fields = {'slug': ('nombre',)}
	list_editable = ('activo', 'destacada')
	ordering = ('nombre',)
	
	# Agregar inline de categorías
	inlines = [CategoriaInline]
	
	# Organizar campos en el formulario
	fieldsets = (
		('Información Básica', {
			'fields': ('nombre', 'slug', 'descripcion')
		}),
		('Imagen', {
			'fields': ('imagen',)
		}),
		('Configuración', {
			'fields': ('activo', 'destacada', 'posicion')
		}),
	)
	
	def num_categorias(self, obj):
		"""Mostrar número de categorías en la colección"""
		count = obj.categorias.count()
		return f"{count} categorías"
	num_categorias.short_description = 'Categorías'


# =========================
#  CATEGORÍAS
# =========================
class SubcategoriaInline(admin.TabularInline):
	"""Inline para ver/agregar subcategorías dentro de una categoría"""
	model = Categoria
	fk_name = 'padre'
	extra = 0
	fields = ('nombre', 'slug', 'estado', 'posicion')
	prepopulated_fields = {'slug': ('nombre',)}
	show_change_link = True
	verbose_name = "Subcategoría"
	verbose_name_plural = "Subcategorías"
	
	def get_formset(self, request, obj=None, **kwargs):
		"""Heredar la colección del padre automáticamente"""
		formset = super().get_formset(request, obj, **kwargs)
		
		# Si hay un objeto padre (categoría principal), guardar la colección
		if obj and hasattr(obj, 'coleccion'):
			formset.parent_coleccion = obj.coleccion
		
		return formset


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
	list_display = (
		'nombre',
		'slug',
		'coleccion',
		'padre',
		'num_subcategorias',
		'num_productos',
		'estado',
	)
	list_filter = ('estado', 'coleccion', 'padre', 'created_at')
	search_fields = ('nombre', 'slug', 'descripcion')
	prepopulated_fields = {'slug': ('nombre',)}
	list_editable = ('estado',)
	autocomplete_fields = ('padre', 'coleccion')
	ordering = ('coleccion', 'nombre')
	
	# Agregar inline de subcategorías
	inlines = [SubcategoriaInline]
	
	# Organizar campos en el formulario
	fieldsets = (
		('Información Básica', {
			'fields': ('nombre', 'slug', 'descripcion')
		}),
		('Jerarquía', {
			'fields': ('coleccion', 'padre'),
			'description': '<strong>GUÍA:</strong><br>'
			              '• <strong>Categoría Principal:</strong> Selecciona solo COLECCIÓN (ej: Ropa)<br>'
			              '• <strong>Subcategoría:</strong> Selecciona PADRE (ej: Pantalones con padre=Ropa)<br>'
		}),
		('Configuración', {
			'fields': ('estado',)
		}),
	)
	
	def save_model(self, request, obj, form, change):
		"""Heredar colección del padre si es subcategoría"""
		if obj.padre and obj.padre.coleccion:
			# Si tiene padre, heredar su colección automáticamente
			obj.coleccion = obj.padre.coleccion
		super().save_model(request, obj, form, change)
	
	def save_formset(self, request, form, formset, change):
		"""Guardar subcategorías con la colección heredada del padre"""
		instances = formset.save(commit=False)
		
		for instance in instances:
			# Heredar colección del padre
			if hasattr(formset, 'parent_coleccion'):
				instance.coleccion = formset.parent_coleccion
			instance.save()
		
		# Eliminar instancias marcadas para borrar
		for obj in formset.deleted_objects:
			obj.delete()
		
		formset.save_m2m()
	
	def delete_model(self, request, obj):
		"""Eliminar categoría correctamente"""
		# Verificar si tiene subcategorías
		if obj.subcategorias.exists():
			from django.contrib import messages
			messages.warning(
				request, 
				f'La categoría "{obj.nombre}" tiene {obj.subcategorias.count()} subcategorías. '
				'Elimina primero las subcategorías o estas quedarán huérfanas.'
			)
		obj.delete()
	
	def delete_queryset(self, request, queryset):
		"""Eliminar múltiples categorías correctamente"""
		for obj in queryset:
			if obj.subcategorias.exists():
				from django.contrib import messages
				messages.warning(
					request,
					f'La categoría "{obj.nombre}" tiene subcategorías que quedarán huérfanas.'
				)
		queryset.delete()
	
	def has_delete_permission(self, request, obj=None):
		"""Permitir eliminación de categorías"""
		return True
	
	def num_subcategorias(self, obj):
		"""Mostrar número de subcategorías"""
		count = obj.subcategorias.count()
		if count > 0:
			return f"✓ {count}"
		return "-"
	num_subcategorias.short_description = 'Subcategorías'
	
	def num_productos(self, obj):
		"""Mostrar número de productos en la categoría"""
		from .models import Producto
		count = Producto.objects.filter(categoria=obj).count()
		return count
	num_productos.short_description = 'Productos'


# =========================
#  ESTILOS
# =========================
@admin.register(Estilo)
class EstiloAdmin(admin.ModelAdmin):
	list_display = (
		'nombre',
		'slug',
		'activo',
		'posicion',
	)
	list_filter = ('activo',)
	search_fields = ('nombre', 'slug')
	prepopulated_fields = {'slug': ('nombre',)}
	list_editable = ('activo', 'posicion')
	ordering = ('posicion', 'nombre')


# =========================
#  INLINES (para Producto)
# =========================
class ImagenInline(admin.TabularInline):
	model = Imagen
	extra = 1
	fields = ('tipo_medio', 'imagen', 'video', 'url', 'variante', 'posicion')
	autocomplete_fields = ('variante',)
	
	def get_readonly_fields(self, request, obj=None):
		"""No hacer ningún campo readonly para permitir subir archivos"""
		return []
	
	# COMENTADO TEMPORALMENTE PARA PROBAR SIN INTERFERENCIAS DE JS
	# class Media:
	# 	css = {
	# 		'all': ('admin/css/imagen_inline.css',)
	# 	}
	# 	js = ('admin/js/imagen_inline.js',)


class VarianteInline(admin.TabularInline):
	model = Variante
	extra = 1
	fields = ('talla', 'color', 'sku', 'precio', 'stock')
	autocomplete_fields = ('talla',)


# =========================
#  PRODUCTOS
# =========================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = (
		'nombre',
		'slug',
		'categoria',
		'coleccion',
		'precio_base',
		'stock_total',
		'num_variantes',
		'promedio_resenas',
		'tiene_tallas',
		'bajo_pedido',
		'activo',
		'created_at',
	)
	list_filter = (
		'activo',
		'bajo_pedido',
		'tiene_tallas',
		'categoria',
		'coleccion',
		'created_at',
	)
	search_fields = ('nombre', 'slug', 'descripcion_corta', 'descripcion_larga')
	prepopulated_fields = {'slug': ('nombre',)}
	list_editable = ('activo', 'precio_base', 'tiene_tallas', 'bajo_pedido')
	inlines = [ImagenInline, VarianteInline]
	ordering = ('-created_at',)
	autocomplete_fields = ('categoria', 'coleccion')
	actions = ['activar_productos', 'desactivar_productos', 'duplicar_producto']
	list_per_page = 20
	date_hierarchy = 'created_at'
	
	def save_model(self, request, obj, form, change):
		"""Asegurar que el modelo se guarde correctamente"""
		import logging
		logger = logging.getLogger(__name__)
		logger.info(f"=== GUARDANDO PRODUCTO: {obj.nombre} ===")
		super().save_model(request, obj, form, change)
	
	def save_formset(self, request, form, formset, change):
		"""Procesar y guardar los formsets de imágenes/videos y variantes"""
		import logging
		logger = logging.getLogger(__name__)
		
		if formset.model == Imagen:
			logger.info(f"=== GUARDANDO FORMSET DE IMAGENES ===")
			instances = formset.save(commit=False)
			
			for instance in instances:
				logger.info(f"Imagen/Video a guardar:")
				logger.info(f"  - Tipo: {instance.tipo_medio}")
				logger.info(f"  - Tiene imagen: {bool(instance.imagen)}")
				logger.info(f"  - Tiene video: {bool(instance.video)}")
				instance.save()
				logger.info(f"  ✓ Guardado exitoso")
			
			for obj in formset.deleted_objects:
				obj.delete()
			formset.save_m2m()
		else:
			formset.save()

	fieldsets = (
		('Datos básicos', {
			'fields': (
				'nombre',
				'slug',
				'tipo',
				'descripcion_corta',
				'descripcion_larga',
			)
		}),
		('Clasificación', {
			'fields': (
				'categoria',
				'coleccion',
				'marca',
			)
		}),
		('Venta', {
			'fields': (
				'precio_base',
				'tiene_tallas',
				'bajo_pedido',
				'activo',
			)
		}),
		('Tiempos', {
			'fields': (
				'created_at',
				'updated_at',
			),
			'classes': ('collapse',)
		}),
	)
	readonly_fields = ('created_at', 'updated_at')

	def stock_total(self, obj):
		"""Muestra el stock total sumando todas las variantes"""
		total = sum(v.stock for v in obj.variantes.all())
		if total == 0:
			return '❌ Sin stock'
		elif total < 10:
			return f'⚠️ {total}'
		return f'✅ {total}'
	stock_total.short_description = 'Stock Total'

	def num_variantes(self, obj):
		"""Número de variantes del producto"""
		count = obj.variantes.count()
		return f'{count} variante{"s" if count != 1 else ""}'
	num_variantes.short_description = 'Variantes'

	def promedio_resenas(self, obj):
		"""Calcula el promedio de las reseñas"""
		resenas = obj.resenas.all()
		if not resenas:
			return '—'
		promedio = sum(r.calificacion for r in resenas) / len(resenas)
		estrellas = '⭐' * round(promedio)
		return f'{estrellas} ({promedio:.1f})'
	promedio_resenas.short_description = 'Reseñas'

	def activar_productos(self, request, queryset):
		"""Acción para activar productos seleccionados"""
		updated = queryset.update(activo=True)
		self.message_user(request, f'{updated} producto(s) activado(s).')
	activar_productos.short_description = '✅ Activar productos seleccionados'

	def desactivar_productos(self, request, queryset):
		"""Acción para desactivar productos seleccionados"""
		updated = queryset.update(activo=False)
		self.message_user(request, f'{updated} producto(s) desactivado(s).')
	desactivar_productos.short_description = '❌ Desactivar productos seleccionados'

	def duplicar_producto(self, request, queryset):
		"""Acción para duplicar productos"""
		for producto in queryset:
			# Guardamos las variantes e imágenes originales
			variantes_originales = list(producto.variantes.all())
			imagenes_originales = list(producto.imagenes.all())
			
			# Duplicamos el producto
			producto.pk = None
			producto.nombre = f'{producto.nombre} (Copia)'
			producto.slug = f'{producto.slug}-copia'
			producto.save()
			
			# Duplicamos las variantes
			for variante in variantes_originales:
				variante.pk = None
				variante.producto = producto
				variante.sku = f'{variante.sku}-copia'
				variante.save()
			
			# Duplicamos las imágenes
			for imagen in imagenes_originales:
				imagen.pk = None
				imagen.producto = producto
				imagen.variante = None
				imagen.save()
		
		self.message_user(request, f'{queryset.count()} producto(s) duplicado(s).')
	duplicar_producto.short_description = '📋 Duplicar productos seleccionados'


# =========================
#  TALLAS
# =========================
@admin.register(Talla)
class TallaAdmin(admin.ModelAdmin):
	list_display = ('codigo', 'nombre')
	search_fields = ('codigo', 'nombre')
	ordering = ('codigo',)


# =========================
#  VARIANTES
# (por si quieres editarlas fuera del producto)
# =========================
@admin.register(Variante)
class VarianteAdmin(admin.ModelAdmin):
	list_display = (
		'producto',
		'talla',
		'color',
		'sku',
		'precio',
		'stock',
		'created_at',
	)
	list_filter = ('talla', 'color', 'producto')
	search_fields = ('sku', 'producto__nombre')
	autocomplete_fields = ('producto', 'talla')
	ordering = ('producto', 'talla', 'color')


# =========================
#  IMÁGENES
# (también las registramos por separado)
# =========================
@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
	list_display = (
		'url',
		'producto',
		'variante',
	)
	list_filter = ('producto',)
	search_fields = ('url', 'producto__nombre')
	autocomplete_fields = ('producto', 'variante')
	ordering = ('producto', 'url')


# =========================
#  ATRIBUTOS (Nuevo)
# =========================
class ValorAtributoInline(admin.TabularInline):
	model = ValorAtributo
	extra = 3
	fields = ('valor', 'codigo_color', 'posicion', 'activo')


@admin.register(Atributo)
class AtributoAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'tipo', 'num_valores', 'activo', 'posicion', 'created_at')
	list_filter = ('tipo', 'activo', 'created_at')
	search_fields = ('nombre', 'slug', 'descripcion')
	prepopulated_fields = {'slug': ('nombre',)}
	list_editable = ('activo', 'posicion')
	inlines = [ValorAtributoInline]
	ordering = ('posicion', 'nombre')

	fieldsets = (
		('Información Básica', {
			'fields': ('nombre', 'slug', 'tipo', 'descripcion')
		}),
		('Configuración', {
			'fields': ('activo', 'posicion')
		}),
		('Fechas', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)
	readonly_fields = ('created_at', 'updated_at')

	def num_valores(self, obj):
		"""Muestra el número de valores del atributo"""
		count = obj.valores.filter(activo=True).count()
		total = obj.valores.count()
		return f'{count} activos de {total}'
	num_valores.short_description = 'Valores'


@admin.register(ValorAtributo)
class ValorAtributoAdmin(admin.ModelAdmin):
	list_display = ('atributo', 'valor', 'mostrar_color', 'posicion', 'activo', 'created_at')
	list_filter = ('atributo', 'activo', 'created_at')
	search_fields = ('valor', 'atributo__nombre')
	list_editable = ('posicion', 'activo')
	autocomplete_fields = ('atributo',)
	ordering = ('atributo', 'posicion', 'valor')

	def mostrar_color(self, obj):
		"""Muestra el color visualmente si existe"""
		if obj.codigo_color:
			return f'<span style="display:inline-block;width:20px;height:20px;background:{obj.codigo_color};border:1px solid #ccc;border-radius:3px;"></span> {obj.codigo_color}'
		return '—'
	mostrar_color.short_description = 'Color'
	mostrar_color.allow_tags = True


@admin.register(VarianteAtributo)
class VarianteAtributoAdmin(admin.ModelAdmin):
	list_display = ('variante', 'valor_atributo', 'producto_nombre')
	list_filter = ('valor_atributo__atributo',)
	search_fields = ('variante__producto__nombre', 'variante__sku', 'valor_atributo__valor')
	autocomplete_fields = ('variante', 'valor_atributo')
	ordering = ('variante', 'valor_atributo')

	def producto_nombre(self, obj):
		"""Muestra el nombre del producto"""
		return obj.variante.producto.nombre
	producto_nombre.short_description = 'Producto'


# =========================
#  GLOBAL PRODUCT CONTENT
# =========================
@admin.register(GlobalProductContent)
class GlobalProductContentAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'activo')
	
	fieldsets = (
		('Features Section', {
			'fields': ('features_content',),
			'description': 'Contenido HTML para la sección Features (usar <li> tags)'
		}),
		('Materials Care Section', {
			'fields': ('materials_content',),
			'description': 'Contenido HTML para Materials Care (usar <li> tags)'
		}),
		('Care Instructions Icons', {
			'fields': (
				('care_icon_1', 'care_text_1'),
				('care_icon_2', 'care_text_2'),
				('care_icon_3', 'care_text_3'),
				('care_icon_4', 'care_text_4'),
				('care_icon_5', 'care_text_5'),
			),
			'description': 'Íconos y texto para instrucciones de cuidado'
		}),
		('Bottom Text', {
			'fields': ('product_code_text',),
			'description': 'Texto que aparece debajo de los íconos SVG'
		}),
		('Estado', {
			'fields': ('activo',)
		}),
	)
	
	def has_add_permission(self, request):
		# Solo permitir una instancia
		return not GlobalProductContent.objects.exists()
	
	def has_delete_permission(self, request, obj=None):
		# No permitir eliminar la única instancia
		return False


# =========================
#  SHIPPING INFO
# =========================
@admin.register(ShippingInfo)
class ShippingInfoAdmin(admin.ModelAdmin):
	list_display = ('titulo', 'tiempo_nacional', 'tiempo_internacional', 'costo_envio', 'activo')
	list_filter = ('activo',)
	list_editable = ('activo',)
	
	fieldsets = (
		('Información Básica', {
			'fields': ('titulo', 'descripcion')
		}),
		('Tiempos de Entrega', {
			'fields': ('tiempo_nacional', 'tiempo_internacional')
		}),
		('Costos', {
			'fields': ('costo_envio', 'envio_gratis_desde')
		}),
		('Estado', {
			'fields': ('activo',)
		}),
	)


# =========================
#  RETURN POLICIES
# =========================
@admin.register(ReturnPolicy)
class ReturnPolicyAdmin(admin.ModelAdmin):
	list_display = ('titulo', 'dias_devolucion', 'orden', 'activo')
	list_filter = ('activo',)
	list_editable = ('orden', 'activo')
	ordering = ('orden',)
	
	fieldsets = (
		('Información Básica', {
			'fields': ('titulo', 'descripcion', 'icono')
		}),
		('Configuración', {
			'fields': ('dias_devolucion', 'orden', 'activo')
		}),
	)

# =========================
#  CARRITO PERSISTENTE
# =========================
@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
	list_display = ('usuario', 'producto', 'variante', 'cantidad', 'precio', 'fecha_agregado')
	list_filter = ('usuario', 'fecha_agregado', 'fecha_actualizado')
	search_fields = ('usuario__email', 'producto__nombre')
	readonly_fields = ('fecha_agregado', 'fecha_actualizado', 'total_precio')
	
	fieldsets = (
		('Usuario y Producto', {
			'fields': ('usuario', 'producto', 'variante')
		}),
		('Cantidad y Precio', {
			'fields': ('cantidad', 'precio', 'total_precio')
		}),
		('Detalles de Variante', {
			'fields': ('color', 'talla_codigo', 'talla_nombre', 'imagen_url'),
			'classes': ('collapse',)
		}),
		('Fechas', {
			'fields': ('fecha_agregado', 'fecha_actualizado'),
			'classes': ('collapse',)
		}),
	)
	
	def total_precio(self, obj):
		return f"${obj.total_precio:.2f}"
	total_precio.short_description = "Total"