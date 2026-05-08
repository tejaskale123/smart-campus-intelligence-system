from django.db import models
from django.contrib.auth.models import User


class Attendance(models.Model):

    STATUS_CHOICES = (

        ('Present', 'Present'),

        ('Absent', 'Absent'),

    )

    student = models.ForeignKey(

        User,

        on_delete=models.CASCADE
    )

    date = models.DateField(auto_now_add=True)

    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES
    )

    def __str__(self):

        return f"{self.student.username} - {self.status}"
