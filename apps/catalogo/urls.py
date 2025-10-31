# apps/catalogo/urls.py
from django.urls import path
from . import views

app_name = "catalogo"

urlpatterns = [
    # públicas
    path('productos/', views.ProductoListView.as_view(), name='producto_list'),
    path('producto/<slug:slug>/', views.ProductoDetailView.as_view(), name='producto_detail'),
    path('categoria/<slug:slug>/', views.CategoriaProductoListView.as_view(), name='producto_por_categoria'),
    path('estilo/<slug:slug>/', views.EstiloProductoListView.as_view(), name='producto_por_estilo'),

    # ----- PANEL CUSTOM -----
    path('admin-panel/productos/', views.panel_productos_list, name='panel_productos'),
    path('admin-panel/productos/agregar/', views.panel_producto_crear, name='panel_producto_crear'),
    path('admin-panel/categorias/', views.panel_categorias_list, name='panel_categorias'),
    path('admin-panel/categorias/nueva/', views.panel_categoria_crear, name='panel_categoria_crear'),
]
