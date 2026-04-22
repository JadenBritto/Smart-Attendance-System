from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        CLASS_TEACHER = 'class_teacher', 'Class Teacher'
        TEACHER = 'teacher', 'Teacher'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.TEACHER)
    assigned_class = models.ForeignKey(
        'classes.ClassSection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_teacher',
    )

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_class_teacher(self):
        return self.role == self.Role.CLASS_TEACHER

    @property
    def is_teacher_role(self):
        return self.role == self.Role.TEACHER

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
