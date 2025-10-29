from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    # URLs de Productos
    path('', views.producto_lista, name='producto_lista'),
    path('agregar/', views.producto_agregar, name='producto_agregar'),
    path('editar/<int:pk>/', views.producto_editar, name='producto_editar'),
    path('eliminar/<int:pk>/', views.producto_eliminar, name='producto_eliminar'),
    
    # URLs de Categorías
    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/agregar/', views.categoria_agregar, name='categoria_agregar'),
    path('categorias/editar/<int:pk>/', views.categoria_editar, name='categoria_editar'),
    path('categorias/eliminar/<int:pk>/', views.categoria_eliminar, name='categoria_eliminar'),
    
    # URLs de Marcas
    path('marcas/', views.marca_lista, name='marca_lista'),
    path('marcas/agregar/', views.marca_agregar, name='marca_agregar'),
    path('marcas/editar/<int:pk>/', views.marca_editar, name='marca_editar'),
    path('marcas/eliminar/<int:pk>/', views.marca_eliminar, name='marca_eliminar'),
]
