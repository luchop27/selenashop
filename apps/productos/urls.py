# apps/productos/urls.py

from django.urls import path
from . import views

app_name = "productos"

urlpatterns = [
    # públicas
    path('productos/', views.ProductoListView.as_view(), name='producto_list'),
    path('producto/<slug:slug>/', views.ProductoDetailView.as_view(), name='producto_detail'),
    path('categoria/<slug:slug>/', views.CategoriaProductoListView.as_view(), name='producto_por_categoria'),
    path('estilo/<slug:slug>/', views.EstiloProductoListView.as_view(), name='producto_por_estilo'),

    # ----- ADMIN PANEL ECOMUS -----
    path('admin-panel/', views.panel_dashboard, name='panel_dashboard'),
    path('admin-panel/products/', views.admin_productos_list, name='admin_productos_list'),
    path('admin-panel/products/add/', views.admin_producto_add, name='admin_producto_add'),
    
    # Atributos
    path('admin-panel/attributes/', views.admin_atributos_list, name='admin_atributos_list'),
    path('admin-panel/attributes/add/', views.admin_atributo_add, name='admin_atributo_add'),
    path('admin-panel/attributes/edit/<int:pk>/', views.admin_atributo_edit, name='admin_atributo_edit'),
    path('admin-panel/attributes/delete/<int:pk>/', views.admin_atributo_delete, name='admin_atributo_delete'),
    
    # API Atributos
    path('admin-panel/api/atributos/', views.api_atributos_list, name='api_atributos_list'),
    
    # Panel custom legacy
    path('admin-panel/productos/', views.panel_productos_list, name='panel_productos'),
    path('admin-panel/productos/agregar/', views.panel_producto_crear, name='panel_producto_crear'),
    path('admin-panel/categorias/', views.panel_categorias_list, name='panel_categorias'),
    path('admin-panel/categorias/nueva/', views.panel_categoria_crear, name='panel_categoria_crear'),
]
