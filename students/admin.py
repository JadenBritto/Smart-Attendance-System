from django.contrib import admin
from .models import Student, FaceEncoding


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'first_name', 'last_name', 'class_section']
    list_filter = ['class_section']
    search_fields = ['roll_number', 'first_name', 'last_name']


@admin.register(FaceEncoding)
class FaceEncodingAdmin(admin.ModelAdmin):
    list_display = ['student', 'is_active', 'created_at']
    list_filter = ['is_active']
