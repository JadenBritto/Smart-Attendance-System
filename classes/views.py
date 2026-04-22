from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import admin_required
from .models import Department, ClassSection
from .forms import DepartmentForm, ClassSectionForm


@login_required
@admin_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'classes/department_list.html', {'departments': departments})


@login_required
@admin_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully.')
            return redirect('classes:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'classes/department_form.html', {'form': form, 'title': 'Add Department'})


@login_required
@admin_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully.')
            return redirect('classes:department_list')
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'classes/department_form.html', {'form': form, 'title': 'Edit Department'})


@login_required
@admin_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, 'Department deleted successfully.')
        return redirect('classes:department_list')
    return render(request, 'classes/confirm_delete.html', {'object': dept, 'type': 'Department'})


@login_required
@admin_required
def class_list(request):
    classes = ClassSection.objects.select_related('department').all()
    return render(request, 'classes/class_list.html', {'classes': classes})


@login_required
@admin_required
def class_create(request):
    if request.method == 'POST':
        form = ClassSectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class created successfully.')
            return redirect('classes:class_list')
    else:
        form = ClassSectionForm()
    return render(request, 'classes/class_form.html', {'form': form, 'title': 'Add Class'})


@login_required
@admin_required
def class_edit(request, pk):
    cls = get_object_or_404(ClassSection, pk=pk)
    if request.method == 'POST':
        form = ClassSectionForm(request.POST, instance=cls)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully.')
            return redirect('classes:class_list')
    else:
        form = ClassSectionForm(instance=cls)
    return render(request, 'classes/class_form.html', {'form': form, 'title': 'Edit Class'})


@login_required
@admin_required
def class_delete(request, pk):
    cls = get_object_or_404(ClassSection, pk=pk)
    if request.method == 'POST':
        cls.delete()
        messages.success(request, 'Class deleted successfully.')
        return redirect('classes:class_list')
    return render(request, 'classes/confirm_delete.html', {'object': cls, 'type': 'Class'})
