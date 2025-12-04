from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Ciudad, Provincia


@admin.register(Provincia)
class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'provincia', 'codigo_postal', 'activa')
    list_filter = ('activa', 'provincia')
    search_fields = ('nombre', 'provincia__nombre')
    ordering = ('provincia', 'nombre')


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('email', 'nombre', 'apellido', 'telefono', 'provincia', 'ciudad', 'rol', 'is_active', 'fecha_registro')
    list_filter = ('rol', 'is_active', 'provincia', 'ciudad')
    ordering = ('-fecha_registro',)
    search_fields = ('email', 'nombre', 'apellido', 'telefono')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('nombre', 'apellido', 'telefono', 'provincia', 'ciudad')}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('fecha_registro', 'fecha_edicion')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'rol', 'is_staff', 'is_superuser'),
        }),
    )
