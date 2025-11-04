from django.contrib import admin
from .models import (
	Categoria,
	Estilo,
	Producto,
	Talla,
	Variante,
	Imagen,
)


# =========================
#  CATEGORÍAS
# =========================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
	list_display = (
		'nombre',
		'slug',
		'padre',
		'tipo',
		'estado',
		'posicion',
		'created_at',
	)
	list_filter = ('estado', 'tipo', 'created_at')
	search_fields = ('nombre', 'slug')
	prepopulated_fields = {'slug': ('nombre',)}
	list_editable = ('estado', 'posicion')
	autocomplete_fields = ('padre',)
	ordering = ('posicion', 'nombre')


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
	fields = ('url', 'variante')
	autocomplete_fields = ('variante',)


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
		'estilo',
		'precio_base',
		'stock_total',
		'num_variantes',
		'promedio_resenas',
		'tiene_tallas',
		'activo',
		'created_at',
	)
	list_filter = (
		'activo',
		'tiene_tallas',
		'categoria',
		'estilo',
		'created_at',
	)
	search_fields = ('nombre', 'slug', 'descripcion_corta', 'descripcion_larga')
	prepopulated_fields = {'slug': ('nombre',)}
	list_editable = ('activo', 'precio_base', 'tiene_tallas')
	inlines = [ImagenInline, VarianteInline]
	ordering = ('-created_at',)
	autocomplete_fields = ('categoria', 'estilo')
	actions = ['activar_productos', 'desactivar_productos', 'duplicar_producto']
	list_per_page = 20
	date_hierarchy = 'created_at'

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
				'estilo',
				'marca',
				'material',
			)
		}),
		('Venta', {
			'fields': (
				'precio_base',
				'tiene_tallas',
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
