from datetime import datetime
from bson import ObjectId
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.authentication.decorators import (
    teacher_or_admin,
    get_user_role,
)
from .helper_views import *
from database.mongo import db

STUDENTS_COLLECTION = db["students"]
ATTENDANCE_COLLECTION = db["attendance_logs"]


def clean_value(value, fallback="-"):
    value = "" if value is None else str(value).strip()
    return value or fallback


def student_display_name(student):
    return clean_value(
        student.get("name")
        or student.get("student_name")
        or student.get("full_name"),
        "Unnamed Student"
    )


def prepare_student_option(student):
    student["id"] = str(student["_id"])
    student["display_name"] = student_display_name(student)
    student["display_course"] = clean_value(
        student.get("course")
        or student.get("department")
        or student.get("student_course")
    )
    student["display_email"] = clean_value(
        student.get("email")
        or student.get("student_email")
    )
    return student


@login_required
@teacher_or_admin
def attendance_list(request):
    role = get_user_role(request.user)
    search_query = request.GET.get("search")

    if role == "student":
        student = find_student_for_user(request.user)
        attendance_filter = get_student_attendance_filter(student)
    elif search_query:
        attendance_filter = {
            "student_name": {
                "$regex": search_query,
                "$options": "i"
            }
        }
    else:
        attendance_filter = {}

    attendance_records = serialize_attendance(
        ATTENDANCE_COLLECTION.find(attendance_filter).sort("attendance_date", -1)
    )
    for record in attendance_records:
        record["display_type"] = record.get("type") or record.get("status", "-")
        record["student_course"] = record.get("student_course") or record.get("course") or "-"
        record["student_email"] = record.get("student_email") or record.get("email") or "-"

    summary = get_attendance_summary(attendance_records)

    return render(
        request,
        "attendance/attendance_list.html",
        {
            "attendance_records": attendance_records,
            "present_count": summary["present_count"],
            "absent_count": summary["absent_count"],
            "present_students": summary["present_students"],
            "absent_students": summary["absent_students"],
            "total_attendance": summary["total_attendance"],
            "attendance_percentage": summary["attendance_percentage"],
        }
    )

@login_required
@teacher_or_admin
def add_attendance(request):

    students = [
        prepare_student_option(student)
        for student in STUDENTS_COLLECTION.find()
    ]

    students.sort(key=lambda item: item["display_name"].lower())

    if request.method == "POST":

        student_id = request.POST.get("student_id")

        attendance_date = request.POST.get("attendance_date")

        status = request.POST.get("status")

        if not student_id:

            messages.error(
                request,
                "Please select student."
            )

            return redirect("add_attendance")

        if not attendance_date:

            messages.error(
                request,
                "Please select attendance date."
            )

            return redirect("add_attendance")

        if status not in VALID_ATTENDANCE_STATUS:

            messages.error(
                request,
                "Invalid attendance status."
            )

            return redirect("add_attendance")

        student = STUDENTS_COLLECTION.find_one({

            "_id": ObjectId(student_id)

        })

        if not student:

            messages.error(
                request,
                "Student not found."
            )

            return redirect("add_attendance")

        ATTENDANCE_COLLECTION.insert_one({

            "student_id": str(student["_id"]),

            "student_name": student_display_name(student),

            "student_email": clean_value(
                student.get("email")
                or student.get("student_email")
            ),

            "student_course": clean_value(
                student.get("course")
                or student.get("department")
                or student.get("student_course")
            ),

            "attendance_date": attendance_date,

            "time": datetime.now().strftime("%H:%M:%S"),

            "status": status,

            "method": "Manual",

            "created_at": datetime.now()

        })

        messages.success(
            request,
            "Attendance added successfully."
        )

        return redirect("attendance_list")

    return render(

        request,

        "attendance/add_attendance.html",

        {

            "students": students,

            "current": "add_attendance"

        }

    )

@login_required
def attendance_history(request):
    attendance_data = ATTENDANCE_COLLECTION.find().sort("attendance_date", -1)
    return render(
        request,
        "authentication/attendance_history.html",
        {"attendance_data": attendance_data}
    )
