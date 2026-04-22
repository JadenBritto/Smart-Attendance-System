from django.db import models
from django.conf import settings


class AttendanceSession(models.Model):
    class_section = models.ForeignKey(
        'classes.ClassSection',
        on_delete=models.CASCADE,
        related_name='attendance_sessions',
    )
    taken_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_sessions',
    )
    date = models.DateField()
    subject = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.class_section} - {self.subject} ({self.date})"


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        LATE = 'late', 'Late'

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='records',
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ABSENT)
    recognized_at = models.DateTimeField(null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ['session', 'student']

    def __str__(self):
        return f"{self.student} - {self.get_status_display()}"
