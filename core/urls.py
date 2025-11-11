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
]
