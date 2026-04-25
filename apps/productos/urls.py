# apps/productos/urls.py

from django.urls import path
from . import views

app_name = "productos"

urlpatterns = [
    # públicas
    path('productos/', views.ProductoListView.as_view(), name='producto_list'),
    # API Quick View
    path('productos/api/<int:producto_id>/quick-view/', 
     views.producto_quick_view, 
     name='producto_quick_view'),
    path('producto/<slug:slug>/', views.ProductoDetailView.as_view(), name='producto_detail'),
    path('categoria/<slug:slug>/', views.CategoriaProductoListView.as_view(), name='producto_por_categoria'),
    path('estilo/<slug:slug>/', views.EstiloProductoListView.as_view(), name='producto_por_estilo'),

    # ----- ADMIN PANEL ECOMUS -----
    path('admin-panel/', views.panel_dashboard, name='panel_dashboard'),
    path('admin-panel/products/', views.admin_productos_list, name='admin_productos_list'),
    path('admin-panel/products/add/', views.admin_producto_add, name='admin_producto_add'),
    path('admin-panel/products/view/<int:pk>/', views.admin_producto_view, name='admin_producto_view'),
    path('admin-panel/products/edit/<int:pk>/', views.admin_producto_edit, name='admin_producto_edit'),
    path('admin-panel/products/delete/<int:pk>/', views.admin_producto_delete, name='admin_producto_delete'),
    
    # Atributos
    path('admin-panel/attributes/', views.admin_atributos_list, name='admin_atributos_list'),
    path('admin-panel/attributes/add/', views.admin_atributo_add, name='admin_atributo_add'),
    path('admin-panel/attributes/edit/<int:pk>/', views.admin_atributo_edit, name='admin_atributo_edit'),
    path('admin-panel/attributes/delete/<int:pk>/', views.admin_atributo_delete, name='admin_atributo_delete'),
    
    # Colecciones
    path('admin-panel/collections/', views.admin_colecciones_list, name='admin_colecciones_list'),
    path('admin-panel/collections/add/', views.admin_coleccion_add, name='admin_coleccion_add'),
    path('admin-panel/collections/edit/<int:pk>/', views.admin_coleccion_edit, name='admin_coleccion_edit'),
    path('admin-panel/collections/delete/<int:pk>/', views.admin_coleccion_delete, name='admin_coleccion_delete'),
    
    # API Atributos
    path('admin-panel/api/atributos/', views.api_atributos_list, name='api_atributos_list'),
    path('admin-panel/api/categorias/', views.api_categorias_list, name='api_categorias_list'),
    path('admin-panel/api/colecciones/', views.api_colecciones_list, name='api_colecciones_list'),
    
    # Panel custom legacy
    path('admin-panel/productos/', views.panel_productos_list, name='panel_productos'),
    path('admin-panel/productos/agregar/', views.panel_producto_crear, name='panel_producto_crear'),
    path('admin-panel/categorias/', views.panel_categorias_list, name='panel_categorias'),
    path('admin-panel/categorias/nueva/', views.panel_categoria_crear, name='panel_categoria_crear'),
    path('admin-panel/categorias/editar/<int:pk>/', views.panel_categoria_edit, name='panel_categoria_edit'),
    path('admin-panel/categorias/eliminar/<int:pk>/', views.panel_categoria_delete, name='panel_categoria_delete'),

    # ── Quick Edit: API de edición rápida (solo administradores is_staff) ──
    path('productos/api/quick-edit/<int:producto_id>/',
         views.get_product_data_quick_edit,
         name='get_product_data_quick_edit'),
    path('productos/api/quick-edit/<int:producto_id>/guardar/',
         views.update_product_quick,
         name='update_product_quick'),
]
