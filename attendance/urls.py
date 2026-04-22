from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('select-class/', views.select_class, name='select_class'),
    path('take/<int:session_id>/', views.take_attendance, name='take_attendance'),
    path('api/recognize/', views.api_recognize_faces, name='api_recognize_faces'),
    path('session/<int:session_id>/close/', views.close_session, name='close_session'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('session/<int:session_id>/export/', views.export_session, name='export_session'),
    path('session/<int:session_id>/toggle/<int:student_id>/', views.manual_toggle, name='manual_toggle'),
    path('reports/', views.reports, name='reports'),
]
