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
    path('admin-panel/orders/', views.admin_order_list, name='admin_order_list'),
    path('admin-panel/orders/detail/', views.admin_order_detail_select, name='admin_order_detail_select'),
    path('admin-panel/orders/detail/<int:pedido_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin-panel/orders/tracking/', views.admin_order_tracking_select, name='admin_order_tracking_select'),
    path('admin-panel/orders/tracking/<int:pedido_id>/', views.admin_order_tracking, name='admin_order_tracking'),
    path('admin-panel/orders/<int:pedido_id>/mark-paid/', views.admin_order_mark_paid, name='admin_order_mark_paid'),
    path('admin-panel/orders/<int:pedido_id>/update-status/', views.admin_order_update_status, name='admin_order_update_status'),
    path('admin-panel/orders/<int:pedido_id>/cancel/', views.admin_order_cancel, name='admin_order_cancel'),
    
    # User Management URLs
    path('admin-panel/users/', views.admin_user_list, name='admin_user_list'),
    path('admin-panel/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin-panel/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-panel/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    
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
    
    # Checkout URLs
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.checkout_process, name='checkout_process'),
    path('checkout/validate-discount/', views.validate_discount_code, name='validate_discount_code'),
    path('checkout/calculate-shipping/', views.calculate_shipping, name='calculate_shipping'),
    path('order/confirmation/<int:pedido_id>/', views.order_confirmation, name='order_confirmation'),
    path('api/order/<int:pedido_id>/status/', views.get_order_status, name='get_order_status'),  # AJAX: obtener estado del pedido
    
    # Endpoint AJAX para cargar más productos nuevos
    path('api/productos-nuevos/', views.api_productos_nuevos, name='api_productos_nuevos'),
    
    # Páginas estáticas
    path('about-us/', views.about_us, name='about_us'),
    path('nosotros/', views.about_us, name='nosotros'),
    path('contacto/', views.contacto, name='contacto'),
]
