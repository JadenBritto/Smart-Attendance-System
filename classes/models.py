from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class ClassSection(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='classes')
    year = models.PositiveIntegerField()
    section = models.CharField(max_length=5)

    class Meta:
        ordering = ['department', 'year', 'section']
        unique_together = ['department', 'year', 'section']

    def __str__(self):
        return f"{self.department.code} Year {self.year} - Section {self.section}"
