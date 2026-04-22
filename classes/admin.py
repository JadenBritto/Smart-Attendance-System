from django.contrib import admin
from .models import Department, ClassSection


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'year', 'section']
    list_filter = ['department', 'year']
