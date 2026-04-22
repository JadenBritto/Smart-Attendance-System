from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'role', 'assigned_class']
    list_filter = ['role']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role', 'assigned_class')}),
    )
