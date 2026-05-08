from django.urls import path

from . import views


urlpatterns = [
    path(
        "student-dashboard/",
        views.student_dashboard,
        name="student_dashboard"
    ),
    path(
        "my-attendance/",
        views.my_attendance,
        name="my_attendance"
    ),
    path(
        "performance/",
        views.performance,
        name="performance"
    ),
    path(
        "my-profile/",
        views.my_profile,
        name="my_profile"
    ),
]
