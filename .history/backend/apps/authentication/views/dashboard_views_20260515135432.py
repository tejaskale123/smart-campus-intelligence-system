from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.contrib.auth import logout

from apps.authentication.decorators import (
    admin_only,
    teacher_only,
    student_only,
    get_user_role
)

from .helper_views import (
    get_all_attendance_records,
    get_attendance_summary,
    get_total_teachers
)

from database.mongo import db

STUDENTS_COLLECTION = db["students"]


@login_required
def dashboard(request):

    role = get_user_role(request.user)

    if role == "admin":
        return redirect("admin_dashboard")

    if role == "teacher":
        return redirect("teacher_dashboard")

    if role == "student":
        return redirect("student_dashboard")

    messages.error(
        request,
        "Invalid role assigned."
    )

    logout(request)

    return redirect("login")


@login_required
@admin_only
def admin_dashboard(request):

    attendance_records = get_all_attendance_records()

    summary = get_attendance_summary(
        attendance_records
    )

    context = {

        "total_students":
        STUDENTS_COLLECTION.count_documents({}),

        "total_teachers":
        get_total_teachers(),

        "attendance_records":
        attendance_records[:10],

        "present_count":
        summary["present_count"],

        "absent_count":
        summary["absent_count"],
    }

    return render(
        request,
        "dashboard/admin_dashboard.html",
        context
    )


@login_required
@teacher_only
def teacher_dashboard(request):

    attendance_records = get_all_attendance_records()

    context = {

        "attendance_records":
        attendance_records[:10]
    }

    return render(
        request,
        "dashboard/teacher_dashboard.html",
        context
    )


@login_required
@student_only
def student_dashboard(request):

    return render(
        request,
        "dashboard/student_dashboard.html"
    )