from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('collections/', views.shop_collection_sub, name='shop-collection-sub'),
    path('product/<int:producto_id>/', views.product_detail, name='product_detail'),
    path('product/', views.product_detail, name='product_detail_demo'),  # Sin ID para ver demo
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('admin-panel/', views.admin_index, name='admin_index'),
    
    # Cart URLs
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/detail/', views.cart_detail, name='cart_detail'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('cart/save-note/', views.cart_save_note, name='cart_save_note'),
    path('cart/add-gift-wrap/', views.cart_add_gift_wrap, name='cart_add_gift_wrap'),
    path('cart/remove-gift-wrap/', views.cart_remove_gift_wrap, name='cart_remove_gift_wrap'),
    path('cart/recommendations/', views.cart_recommendations, name='cart_recommendations'),
    # Endpoint AJAX para cargar más productos nuevos
    path('api/productos-nuevos/', views.api_productos_nuevos, name='api_productos_nuevos'),
]
