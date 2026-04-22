import json
import numpy as np
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count, Q
import pandas as pd

from accounts.decorators import teacher_required
from classes.models import ClassSection
from students.models import Student, FaceEncoding
from .models import AttendanceSession, AttendanceRecord
from .forms import AttendanceSessionForm
from recognition.utils import base64_to_image, image_to_rgb, resize_image
from recognition.detector import detect_faces
from recognition.encoder import encode_faces
from recognition.matcher import match_faces

# In-memory cache for class encodings during active sessions
_encoding_cache = {}


@login_required
def dashboard(request):
    today = date.today()
    classes = ClassSection.objects.select_related('department').all()

    if request.user.is_class_teacher and request.user.assigned_class:
        classes = classes.filter(pk=request.user.assigned_class_id)
    elif request.user.is_teacher_role:
        classes = classes.all()

    class_stats = []
    for cls in classes:
        total = cls.students.count()
        session = AttendanceSession.objects.filter(class_section=cls, date=today).first()
        present = 0
        absent = total
        if session:
            present = session.records.filter(status='present').count()
            absent = total - present
        class_stats.append({
            'class': cls,
            'total': total,
            'present': present,
            'absent': absent,
            'percentage': round(present / total * 100) if total > 0 else 0,
            'session': session,
        })

    return render(request, 'attendance/dashboard.html', {
        'class_stats': class_stats,
        'today': today,
    })


@login_required
@teacher_required
def select_class(request):
    """Show form to set up a new attendance session with date, subject, and time slot."""
    if request.method == 'POST':
        form = AttendanceSessionForm(request.POST, user=request.user)
        if form.is_valid():
            session = form.save(commit=False)
            session.taken_by = request.user
            session.save()
            # Create absent records for all students in the class
            students = Student.objects.filter(class_section=session.class_section)
            records = [
                AttendanceRecord(session=session, student=s, status='absent')
                for s in students
            ]
            AttendanceRecord.objects.bulk_create(records)
            return redirect('attendance:take_attendance', session_id=session.id)
    else:
        form = AttendanceSessionForm(user=request.user)
    return render(request, 'attendance/select_class.html', {'form': form})


@login_required
@teacher_required
def take_attendance(request, session_id):
    session = get_object_or_404(AttendanceSession, pk=session_id)
    cls = session.class_section

    # Cache encodings for this class
    cache_key = f'class_{cls.id}'
    if cache_key not in _encoding_cache:
        _load_class_encodings(cls.id, cache_key)

    records = session.records.select_related('student').all()
    students_data = []
    for record in records:
        students_data.append({
            'id': record.student.id,
            'roll_number': record.student.roll_number,
            'name': record.student.full_name,
            'status': record.status,
            'photo_url': record.student.photo.url if record.student.photo else '',
        })

    return render(request, 'attendance/take_attendance.html', {
        'session': session,
        'cls': cls,
        'students_json': json.dumps(students_data),
    })


def _load_class_encodings(class_id, cache_key):
    encodings = FaceEncoding.objects.filter(
        student__class_section_id=class_id,
        is_active=True,
    ).select_related('student')

    known_encs = []
    known_ids = []
    for fe in encodings:
        known_encs.append(fe.get_encoding())
        known_ids.append(fe.student_id)

    _encoding_cache[cache_key] = {
        'encodings': known_encs,
        'ids': known_ids,
    }


@login_required
@require_POST
def api_recognize_faces(request):
    """API endpoint: receive base64 frame, recognize faces, update attendance."""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        image_data = data.get('image')

        if not session_id or not image_data:
            return JsonResponse({'error': 'Missing data'}, status=400)

        session = get_object_or_404(AttendanceSession, pk=session_id, is_active=True)
        cache_key = f'class_{session.class_section_id}'

        if cache_key not in _encoding_cache:
            _load_class_encodings(session.class_section_id, cache_key)

        cached = _encoding_cache[cache_key]
        known_encodings = [np.array(e) for e in cached['encodings']]
        known_ids = cached['ids']

        bgr_image = base64_to_image(image_data)
        if bgr_image is None:
            return JsonResponse({'error': 'Invalid image'}, status=400)

        bgr_image = resize_image(bgr_image)
        rgb_image = image_to_rgb(bgr_image)
        locations = detect_faces(rgb_image)

        if not locations:
            return JsonResponse({'recognized': [], 'face_count': 0})

        unknown_encodings = encode_faces(rgb_image, locations)
        matches = match_faces(unknown_encodings, known_encodings, known_ids)

        recognized = []
        now = timezone.now()
        for i, match in enumerate(matches):
            top, right, bottom, left = locations[i]
            face_info = {
                'location': {'top': top, 'right': right, 'bottom': bottom, 'left': left},
            }
            if match:
                student = Student.objects.get(pk=match['student_id'])
                AttendanceRecord.objects.filter(
                    session=session,
                    student=student,
                    status='absent',
                ).update(
                    status='present',
                    recognized_at=now,
                    confidence=match['confidence'],
                )
                face_info['student_id'] = student.id
                face_info['name'] = student.full_name
                face_info['roll_number'] = student.roll_number
                face_info['confidence'] = match['confidence']
            else:
                face_info['name'] = 'Unknown'

            recognized.append(face_info)

        records = session.records.select_related('student').all()
        students_status = [
            {
                'id': r.student.id,
                'roll_number': r.student.roll_number,
                'name': r.student.full_name,
                'status': r.status,
            }
            for r in records
        ]

        return JsonResponse({
            'recognized': recognized,
            'face_count': len(locations),
            'students': students_status,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@teacher_required
def close_session(request, session_id):
    session = get_object_or_404(AttendanceSession, pk=session_id)
    if request.method == 'POST':
        session.is_active = False
        session.save()
        cache_key = f'class_{session.class_section_id}'
        _encoding_cache.pop(cache_key, None)
        messages.success(request, 'Attendance session closed.')
        return redirect('attendance:session_detail', session_id=session.id)
    return redirect('attendance:take_attendance', session_id=session.id)


@login_required
@teacher_required
def session_detail(request, session_id):
    session = get_object_or_404(
        AttendanceSession.objects.select_related('class_section__department', 'taken_by'),
        pk=session_id,
    )
    records = session.records.select_related('student').order_by('student__roll_number')
    present = records.filter(status='present')
    absent = records.filter(status='absent')

    return render(request, 'attendance/session_detail.html', {
        'session': session,
        'present': present,
        'absent': absent,
        'total': records.count(),
    })


@login_required
@teacher_required
def reports(request):
    classes = ClassSection.objects.select_related('department').all()
    selected_class = request.GET.get('class_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    sessions = AttendanceSession.objects.select_related('class_section__department', 'taken_by')

    if selected_class:
        sessions = sessions.filter(class_section_id=selected_class)
    if date_from:
        sessions = sessions.filter(date__gte=date_from)
    if date_to:
        sessions = sessions.filter(date__lte=date_to)

    sessions = sessions.annotate(
        present_count=Count('records', filter=Q(records__status='present')),
        absent_count=Count('records', filter=Q(records__status='absent')),
        total_count=Count('records'),
    )

    return render(request, 'attendance/reports.html', {
        'classes': classes,
        'sessions': sessions,
        'selected_class': selected_class,
        'date_from': date_from or '',
        'date_to': date_to or '',
    })


@login_required
@teacher_required
def export_session(request, session_id):
    session = get_object_or_404(
        AttendanceSession.objects.select_related('class_section'),
        pk=session_id,
    )
    records = session.records.select_related('student').order_by('student__roll_number')

    fmt = request.GET.get('format', 'csv')

    data = []
    for r in records:
        data.append({
            'Roll Number': r.student.roll_number,
            'Name': r.student.full_name,
            'Status': r.get_status_display(),
            'Time': r.recognized_at.strftime('%H:%M:%S') if r.recognized_at else '-',
            'Confidence': f'{r.confidence:.2%}' if r.confidence else '-',
        })

    df = pd.DataFrame(data)
    filename = f"attendance_{session.class_section}_{session.date}"

    if fmt == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        df.to_excel(response, index=False, engine='openpyxl')
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        df.to_csv(response, index=False)

    return response


@login_required
@teacher_required
def manual_toggle(request, session_id, student_id):
    """Toggle a student's attendance status manually."""
    if request.method == 'POST':
        record = get_object_or_404(
            AttendanceRecord,
            session_id=session_id,
            student_id=student_id,
        )
        if record.status == 'present':
            record.status = 'absent'
            record.recognized_at = None
            record.confidence = None
        else:
            record.status = 'present'
            record.recognized_at = timezone.now()
        record.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': record.status})

        return redirect('attendance:session_detail', session_id=session_id)
    return JsonResponse({'error': 'POST required'}, status=405)
