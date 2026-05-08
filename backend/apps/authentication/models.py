from django.db import models

from django.contrib.auth.models import User


class UserProfile(models.Model):

    ROLE_ADMIN = 'admin'
    ROLE_TEACHER = 'teacher'
    ROLE_STUDENT = 'student'

    ROLE_CHOICES = (

        (ROLE_ADMIN, 'Admin'),

        (ROLE_TEACHER, 'Teacher'),

        (ROLE_STUDENT, 'Student'),

    )

    user = models.OneToOneField(

        User,

        on_delete=models.CASCADE

    )

    role = models.CharField(

        max_length=20,

        choices=ROLE_CHOICES,

        default=ROLE_STUDENT

    )

    def __str__(self):

        return self.user.username
