import json
import numpy as np
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile
import base64

from accounts.decorators import class_teacher_required
from .models import Student, FaceEncoding
from .forms import StudentForm
from recognition.utils import base64_to_image, image_to_rgb, resize_image
from recognition.detector import detect_faces
from recognition.encoder import encode_faces


@login_required
@class_teacher_required
def student_list(request):
    students = Student.objects.select_related('class_section__department').all()
    if request.user.is_class_teacher and request.user.assigned_class:
        students = students.filter(class_section=request.user.assigned_class)
    return render(request, 'students/student_list.html', {'students': students})


@login_required
@class_teacher_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            # Handle webcam photo (base64)
            photo_data = request.POST.get('photo_data')
            if photo_data:
                fmt, imgstr = photo_data.split(';base64,')
                ext = fmt.split('/')[-1]
                photo_file = ContentFile(base64.b64decode(imgstr), name=f'{student.roll_number}.{ext}')
                student.photo = photo_file
                student.save()
            # Handle uploaded file (fallback if no webcam capture)
            elif request.FILES.get('photo_upload'):
                student.photo = request.FILES['photo_upload']
                student.save()

            # Handle face encoding
            encoding_data = request.POST.get('encoding_data')
            if encoding_data:
                encoding = json.loads(encoding_data)
                fe = FaceEncoding(student=student)
                fe.encoding_data = json.dumps(encoding)
                fe.save()

            messages.success(request, f'Student {student.full_name} registered successfully.')
            return redirect('students:student_list')
    else:
        form = StudentForm()
        if request.user.is_class_teacher and request.user.assigned_class:
            form.fields['class_section'].initial = request.user.assigned_class
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Register Student'})


@login_required
@class_teacher_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            student = form.save()
            photo_data = request.POST.get('photo_data')
            if photo_data:
                fmt, imgstr = photo_data.split(';base64,')
                ext = fmt.split('/')[-1]
                photo_file = ContentFile(base64.b64decode(imgstr), name=f'{student.roll_number}.{ext}')
                student.photo = photo_file
                student.save()
            elif request.FILES.get('photo_upload'):
                student.photo = request.FILES['photo_upload']
                student.save()

            encoding_data = request.POST.get('encoding_data')
            if encoding_data:
                student.face_encodings.update(is_active=False)
                encoding = json.loads(encoding_data)
                fe = FaceEncoding(student=student)
                fe.encoding_data = json.dumps(encoding)
                fe.save()

            messages.success(request, f'Student {student.full_name} updated successfully.')
            return redirect('students:student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form.html', {
        'form': form,
        'title': 'Edit Student',
        'student': student,
    })


@login_required
@class_teacher_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully.')
        return redirect('students:student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})


@login_required
@require_POST
def api_detect_face(request):
    """API endpoint: receives base64 image, returns face encoding if detected."""
    try:
        data = json.loads(request.body)
        image_data = data.get('image')
        if not image_data:
            return JsonResponse({'error': 'No image data'}, status=400)

        bgr_image = base64_to_image(image_data)
        if bgr_image is None:
            return JsonResponse({'error': 'Invalid image'}, status=400)

        bgr_image = resize_image(bgr_image)
        rgb_image = image_to_rgb(bgr_image)
        locations = detect_faces(rgb_image)

        if not locations:
            return JsonResponse({'detected': False, 'message': 'No face detected'})

        if len(locations) > 1:
            return JsonResponse({'detected': False, 'message': 'Multiple faces detected. Please ensure only one face is visible.'})

        encodings = encode_faces(rgb_image, locations)
        if not encodings:
            return JsonResponse({'detected': False, 'message': 'Could not encode face'})

        encoding_list = encodings[0].tolist()
        top, right, bottom, left = locations[0]
        return JsonResponse({
            'detected': True,
            'encoding': encoding_list,
            'location': {'top': top, 'right': right, 'bottom': bottom, 'left': left},
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
