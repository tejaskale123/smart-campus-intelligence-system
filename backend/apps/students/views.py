from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.authentication.decorators import student_only
from apps.authentication.models import UserProfile
from database.mongo import db


STUDENTS_COLLECTION = db["students"]
ATTENDANCE_COLLECTION = db["attendance_logs"]


def serialize_student(student):
    if not student:
        return None
    student["id"] = str(student["_id"])
    return student


def serialize_attendance(cursor):
    records = []
    for record in cursor:
        record["id"] = str(record["_id"])
        records.append(record)
    return records


def find_student_for_user(user):
    filters = [
        {"username": user.username},
        {"name": user.username},
        {"user_id": str(user.id)},
    ]
    if user.email:
        filters.extend([
            {"email": user.email},
            {"student_username": user.username},
        ])
    return STUDENTS_COLLECTION.find_one({"$or": filters})


def get_student_attendance_filter(student):
    if not student:
        return {"_id": None}

    filters = [{"student_id": str(student["_id"])}]
    if student.get("name"):
        filters.append({"student_name": student.get("name")})
    if student.get("username"):
        filters.append({"student_username": student.get("username")})
    if student.get("email"):
        filters.append({"student_email": student.get("email")})

    return {"$or": filters}


def get_student_context(user):
    profile = UserProfile.objects.get(user=user, role="student")
    student = serialize_student(find_student_for_user(user)) or {
        "id": "",
        "name": user.username,
        "username": user.username,
        "email": user.email,
        "course": "",
        "age": "",
        "profile_image": "",
    }

    attendance_records = serialize_attendance(
        ATTENDANCE_COLLECTION.find(
            get_student_attendance_filter(student)
        ).sort("attendance_date", -1)
    )

    total_classes = len(attendance_records)
    total_present = len([
        record for record in attendance_records
        if record.get("status") == "Present"
    ])
    total_absent = total_classes - total_present
    attendance_percentage = (
        round((total_present / total_classes) * 100, 2)
        if total_classes else 0
    )

    weekly_labels = []
    weekly_values = []
    today = datetime.today().date()
    for day_offset in range(6, -1, -1):
        current_day = today - timedelta(days=day_offset)
        current_date = current_day.strftime("%Y-%m-%d")
        weekly_labels.append(current_day.strftime("%a"))
        weekly_values.append(1 if any(
            record.get("attendance_date") == current_date
            and record.get("status") == "Present"
            for record in attendance_records
        ) else 0)

    return {
        "profile": profile,
        "student": student,
        "attendance_records": attendance_records,
        "attendance_percentage": attendance_percentage,
        "total_present": total_present,
        "total_absent": total_absent,
        "total_classes": total_classes,
        "weekly_labels": weekly_labels,
        "weekly_values": weekly_values,
    }


@login_required
@student_only
def student_dashboard(request):
    return render(
        request,
        "students/student_dashboard.html",
        get_student_context(request.user)
    )


@login_required
@student_only
def my_attendance(request):
    return render(
        request,
        "students/my_attendance.html",
        get_student_context(request.user)
    )


@login_required
@student_only
def performance(request):
    context = get_student_context(request.user)
    percentage = context["attendance_percentage"]
    context.update({
        "python_marks": min(100, round(percentage + 7)),
        "django_marks": min(100, round(percentage + 2)),
        "mongodb_marks": min(100, round(percentage + 5)),
    })
    return render(request, "students/performance.html", context)


@login_required
@student_only
def my_profile(request):
    return render(
        request,
        "students/my_profile.html",
        get_student_context(request.user)
    )
