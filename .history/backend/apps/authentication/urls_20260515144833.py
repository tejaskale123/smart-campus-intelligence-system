from django.urls import path

from .views import *

urlpatterns = [

    # =========================
    # AUTHENTICATION
    # =========================

    path(
        "",
        login_page,
        name="login"
    ),

    path(
        "login/",
        login_page,
        name="login"
    ),

    path(
        "logout/",
        logout_page,
        name="logout"
    ),

    path(
        "register/",
        register_page,
        name="register"
    ),

    # =========================
    # DASHBOARD
    # =========================

    path(
        "dashboard/",
        dashboard,
        name="dashboard"
    ),

    path(
        "admin-dashboard/",
        admin_dashboard,
        name="admin_dashboard"
    ),

    path(
        "teacher-dashboard/",
        teacher_dashboard,
        name="teacher_dashboard"
    ),

    # =========================
    # STUDENTS
    # =========================

    path(
        "students/",
        students_list,
        name="students_list"
    ),

    path(
        "add-student/",
        add_student,
        name="add_student"
    ),

    path(
        "update-student/<str:student_id>/",
        update_student,
        name="update_student"
    ),

    path(
        "delete-student/<str:student_id>/",
        delete_student,
        name="delete_student"
    ),

    path(
        "student/<str:student_id>/",
        student_detail,
        name="student_detail"
    ),

    # =========================
    # TEACHERS
    # =========================

    path(
        "teachers/",
        admin_teachers,
        name="admin_teachers"
    ),

    path(
        "add-teacher/",
        add_teacher,
        name="add_teacher"
    ),

    path(
        "update-teacher/<int:teacher_id>/",
        update_teacher,
        name="update_teacher"
    ),

    path(
        "delete-teacher/<int:teacher_id>/",
        delete_teacher,
        name="delete_teacher"
    ),

    # =========================
    # ATTENDANCE
    # =========================

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

    path(
        "attendance-history/",
        attendance_history,
        name="attendance_history"
    ),

    # =========================
    # REPORTS
    # =========================

    path(
        "reports/",
        reports_page,
        name="reports"
    ),

    path(
        "download-pdf-report/",
        download_pdf_report,
        name="download_pdf_report"
    ),

    path(
        "export-csv-report/",
        export_csv_report,
        name="export_csv_report"
    ),

    path(
        "performance-report/",
        performance_report,
        name="performance_report"
    ),

    # =========================
    # ANALYTICS
    # =========================

    path(
        "analytics/",
        analytics_view,
        name="analytics"
    ),

    # =========================
    # FACE ATTENDANCE
    # =========================

    path(
        "register-face/",
        register_face,
        name="register_face"
    ),

    path(
        "face-attendance/",
        face_attendance_page,
        name="face_attendance"
    ),

    path(
        "start-face-attendance/",
        start_face_attendance,
        name="start_face_attendance"
    ),

    # =========================
    # SETTINGS
    # =========================

    path(
        "settings/",
        settings_page,
        name="settings"
    ),

]