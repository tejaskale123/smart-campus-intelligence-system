from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from apps.authentication.decorators import (
    admin_only,
    admin_required,
    teacher_only,
    student_only,
    get_user_role,
)
from .helper_views import *
from database.mongo import db

students_collection = db["students"]
attendance_collection = db["attendance_logs"]


@login_required
def dashboard(request):
    role = get_user_role(request.user)

    if role == "admin":
        return admin_dashboard(request)

    if role == "teacher":
        return teacher_dashboard(request)

    if role == "student":
        return student_dashboard(request)

    messages.error(request, "Invalid role assigned. Please contact admin.")
    logout(request)
    return redirect("login")


@login_required
@admin_only
def admin_dashboard(request):
    context = build_dashboard_context()
    return render(request, "dashboard/admin_dashboard.html", context)


@login_required
@teacher_only
def teacher_dashboard(request):
    context = build_dashboard_context()
    return render(request, "dashboard/teacher_dashboard.html", context)


@login_required
@student_only
def student_dashboard(request):
    student = serialize_student(find_student_for_user(request.user))

    if not student:
        student = {
            "id": "",
            "name": request.user.username,
            "username": request.user.username,
            "email": request.user.email,
            "course": "",
            "age": "",
            "profile_image": "",
        }
        return render(
            request,
            "dashboard/student_dashboard.html",
            {
                "student": student,
                "attendance_records": [],
                "attendance_percentage": 0,
                "total_present": 0,
                "total_absent": 0,
                "total_classes": 0,
                "weekly_labels": [],
                "weekly_values": [],
            }
        )

    attendance_records = get_student_attendance_records(student)
    total_classes = len(attendance_records)
    total_present = len([
        attendance for attendance in attendance_records
        if attendance.get("status") == "Present"
    ])
    total_absent = total_classes - total_present

    attendance_percentage = (
        round((total_present / total_classes) * 100, 2)
        if total_classes else 0
    )
    weekly_labels, weekly_values = get_student_weekly_attendance_data(attendance_records)

    context = {
        "student": student,
        "attendance_records": attendance_records,
        "attendance_percentage": attendance_percentage,
        "total_present": total_present,
        "total_absent": total_absent,
        "total_classes": total_classes,
        "weekly_labels": weekly_labels,
        "weekly_values": weekly_values,
    }

    return render(request, "dashboard/student_dashboard.html", context)


@login_required
@student_only
def student_profile(request):
    return student_dashboard(request)


@login_required
@admin_required
def analytics(request):
    students = list(students_collection.find())
    total_students = len(students)
    attendance_records = list(attendance_collection.find())

    present_students = len([
        a for a in attendance_records
        if a.get("status") == "Present"
    ])
    absent_students = len([
        a for a in attendance_records
        if a.get("status") == "Absent"
    ])

    attendance_percentage = 0
    if total_students > 0:
        attendance_percentage = round((present_students / total_students) * 100, 2)

    context = {
        "students": students,
        "total_students": total_students,
        "present_students": present_students,
        "absent_students": absent_students,
        "attendance_percentage": attendance_percentage,
    }

    return render(request, "analytics/analytics.html", context)
