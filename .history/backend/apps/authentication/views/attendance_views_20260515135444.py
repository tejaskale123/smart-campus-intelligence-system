from datetime import datetime

from bson import ObjectId

from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib import messages

from django.contrib.auth.decorators import login_required

from apps.authentication.decorators import (
    teacher_or_admin
)

from database.mongo import db

from .helper_views import (
    serialize_attendance,
    get_attendance_summary,
    VALID_ATTENDANCE_STATUS
)

STUDENTS_COLLECTION = db["students"]
ATTENDANCE_COLLECTION = db["attendance_logs"]


@login_required
@teacher_or_admin
def attendance_list(request):

    attendance_records = serialize_attendance(

        ATTENDANCE_COLLECTION.find().sort(
            "attendance_date",
            -1
        )
    )

    summary = get_attendance_summary(
        attendance_records
    )

    return render(
        request,
        "attendance/attendance_list.html",
        {
            "attendance_records": attendance_records,
            "present_count": summary["present_count"],
            "absent_count": summary["absent_count"],
        }
    )


@login_required
@teacher_or_admin
def add_attendance(request):

    students = list(
        STUDENTS_COLLECTION.find().sort("name", 1)
    )

    for student in students:
        student["id"] = str(student["_id"])

    if request.method == "POST":

        student_id = request.POST.get(
            "student_id"
        )

        attendance_date = request.POST.get(
            "attendance_date"
        )

        status = request.POST.get(
            "status"
        )

        if status not in VALID_ATTENDANCE_STATUS:

            messages.error(
                request,
                "Invalid status"
            )

            return redirect("add_attendance")

        student = STUDENTS_COLLECTION.find_one({
            "_id": ObjectId(student_id)
        })

        ATTENDANCE_COLLECTION.insert_one({

            "student_id":
            str(student["_id"]),

            "student_name":
            student.get("name"),

            "attendance_date":
            attendance_date,

            "status":
            status,

            "created_at":
            datetime.now()
        })

        messages.success(
            request,
            "Attendance Added"
        )

        return redirect("attendance_list")

    return render(
        request,
        "attendance/add_attendance.html",
        {
            "students": students
        }
    )