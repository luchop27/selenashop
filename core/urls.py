from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('home-02/', views.home_02, name='home_02'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('admin-panel/', views.admin_index, name='admin_index'),
]
