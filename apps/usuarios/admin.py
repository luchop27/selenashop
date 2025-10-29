from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('email', 'rol', 'is_active', 'fecha_registro')
    list_filter = ('rol', 'is_active')
    ordering = ('-fecha_registro',)
    search_fields = ('email', 'nombre', 'apellido')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('nombre', 'apellido', 'telefono', 'ciudad')}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('fecha_registro', 'fecha_edicion')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'rol', 'is_staff', 'is_superuser'),
        }),
    )
