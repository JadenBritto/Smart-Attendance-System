import json

from django.db import models


class Student(models.Model):
    roll_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    class_section = models.ForeignKey(
        'classes.ClassSection',
        on_delete=models.CASCADE,
        related_name='students',
    )
    photo = models.ImageField(upload_to='student_photos/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['roll_number']

    def __str__(self):
        return f"{self.roll_number} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class FaceEncoding(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='face_encodings')
    encoding_data = models.TextField(help_text='JSON array of 128 floats')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_encoding(self, encoding_array):
        self.encoding_data = json.dumps(encoding_array.tolist())

    def get_encoding(self):
        return json.loads(self.encoding_data)

    def __str__(self):
        return f"Encoding for {self.student}"
