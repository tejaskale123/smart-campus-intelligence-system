from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("teacher", "Teacher"),
        ("student", "Student"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="userprofile"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            role="admin" if instance.is_superuser else "student"
        )
    elif hasattr(instance, "userprofile"):
        instance.userprofile.save()
