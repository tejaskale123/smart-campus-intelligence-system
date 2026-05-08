from django.urls import path

from .views import (
    add_attendance,
    add_student,
    add_teacher,
    admin_dashboard,
    admin_teachers,
    analytics,
    attendance_list,
    add_attendance,
    dashboard,
    delete_student,
    delete_teacher,
    login_page,
    logout_page,
    register_page,
    reports,
    settings_page,
    student_detail,
    students_list,
    teacher_dashboard,
    update_student,
    update_teacher,
    
)


urlpatterns = [
    # AUTH
    path("", login_page, name="login"),
    path("login/", login_page, name="login"),
    path("logout/", logout_page, name="logout"),
    path("register/", register_page, name="register"),

    # GENERAL ROLE REDIRECT HANDLER
    path("dashboard/", dashboard, name="dashboard"),

    # ADMIN
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("add-student/", add_student, name="add_student"),
    path("teachers/", admin_teachers, name="admin_teachers"),
    path("add-teacher/", add_teacher, name="add_teacher"),
    path("update-teacher/<int:teacher_id>/", update_teacher, name="update_teacher"),
    path("delete-teacher/<int:teacher_id>/", delete_teacher, name="delete_teacher"),
    path("analytics/", analytics, name="analytics"),
    path("reports/", reports, name="reports"),
    path("settings/", settings_page, name="settings"),
    path("update-student/<str:student_id>/", update_student, name="update_student"),
    path("delete-student/<str:student_id>/", delete_student, name="delete_student"),

    # TEACHER
    path("teacher-dashboard/", teacher_dashboard, name="teacher_dashboard"),
    path("add-attendance/", add_attendance, name="add_attendance"),
    path("attendance-list/", attendance_list, name="attendance_list"),
    path("students/", students_list, name="students_list"),
    path("students/", students_list, name="students_page"),
    path("students-list/", students_list, name="students_list_legacy"),

    # GENERAL DETAIL
    path("student/<str:student_id>/", student_detail, name="student_detail"),

    path(
    "attendance-list/",
    attendance_list,
    name="attendance_list"
),

path(
    "add-attendance/",
    add_attendance,
    name="add_attendance"
),
]
