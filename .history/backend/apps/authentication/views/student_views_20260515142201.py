from bson import ObjectId
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.authentication.decorators import (
    admin_only,
    teacher_or_admin,
    get_user_role,
)
from apps.authentication.services import (
    create_student,
    get_student,
)
from .helper_views import *
from database.mongo import db

STUDENTS_COLLECTION = db["students"]


@login_required
@admin_only
def add_student(request):
    if request.method == "POST":
        profile_image = request.FILES.get("profile_image")
        student_data = {
            "name": request.POST.get("name"),
            "course": request.POST.get("course"),
            "age": request.POST.get("age"),
            "email": request.POST.get("email"),
            "profile_image": profile_image.name if profile_image else "",
        }

        create_student(student_data)

        if profile_image:
            with open(f"media/{profile_image.name}", "wb+") as destination:
                for chunk in profile_image.chunks():
                    destination.write(chunk)

        return redirect("students_list")

    return render(request, "students/add_student.html")


@login_required
@teacher_or_admin
def students_list(request):
    search_query = (request.GET.get("search") or "").strip()
    student_filter = (
        {"name": {"$regex": search_query, "$options": "i"}}
        if search_query else {}
    )
    projection = {
        "name": 1,
        "course": 1,
        "age": 1,
        "email": 1,
        "profile_image": 1,
    }

    students = [
        serialize_student(student)
        for student in STUDENTS_COLLECTION.find(
            student_filter,
            projection
        ).sort("name", 1)
    ]

    student_ids = [student["id"] for student in students]
    student_names = [
        student.get("name", "")
        for student in students
        if student.get("name")
    ]
    attendance_match = []
    if student_ids:
        attendance_match.append({"student_id": {"$in": student_ids}})
    if student_names:
        attendance_match.append({"student_name": {"$in": student_names}})

    stats_by_student_id = {}
    stats_by_student_name = {}

    if attendance_match:
        pipeline = [
            {"$match": {"$or": attendance_match}},
            {
                "$group": {
                    "_id": {
                        "student_id": "$student_id",
                        "student_name": "$student_name",
                        "status": "$status",
                    },
                    "count": {"$sum": 1},
                }
            },
        ]

        for row in ATTENDANCE_COLLECTION.aggregate(pipeline):
            group_key = row.get("_id", {})
            status = group_key.get("status")
            count = row.get("count", 0)
            student_id = group_key.get("student_id")
            student_name = group_key.get("student_name")

            for stats_map, key in (
                (stats_by_student_id, student_id),
                (stats_by_student_name, student_name),
            ):
                if not key:
                    continue
                stats = stats_map.setdefault(key, {"total": 0, "present": 0})
                stats["total"] += count
                if status == "Present":
                    stats["present"] += count

    for student in students:
        stats = (
            stats_by_student_id.get(student["id"])
            or stats_by_student_name.get(student.get("name", ""))
            or {"total": 0, "present": 0}
        )
        total = stats["total"]
        present = stats["present"]
        percentage = round((present / total) * 100, 2) if total else 0

        student["attendance_percentage"] = percentage
        student["attendance_alert"] = (
            "Low Attendance" if percentage < 75 else "Good"
        )

    return render(
        request,
        "students/students_list.html",
        {"students": students}
    )


@login_required
@admin_only
def update_student(request, student_id):
    student = get_student(student_id)

    if request.method == "POST":
        updated_data = {
            "name": request.POST.get("name"),
            "course": request.POST.get("course"),
            "age": request.POST.get("age"),
            "email": request.POST.get("email"),
        }
        STUDENTS_COLLECTION.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": updated_data}
        )
        return redirect("students_list")

    return render(
        request,
        "students/update_student.html",
        {"student": student}
    )


@login_required
@admin_only
def delete_student(request, student_id):
    STUDENTS_COLLECTION.delete_one({"_id": ObjectId(student_id)})
    return redirect("students_list")


@login_required
def student_detail(request, student_id):
    student = serialize_student(get_student(student_id))
    if not student:
        messages.error(request, "Student not found.")
        return redirect("dashboard")

    if get_user_role(request.user) == "student":
        current_student = find_student_for_user(request.user)
        if not current_student or str(current_student["_id"]) != student["id"]:
            messages.error(request, "You can only access your own student data.")
            return redirect("student_dashboard")

    attendance_records = get_student_attendance_records(student)
    summary = get_attendance_summary(attendance_records)

    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
            "attendance_records": attendance_records,
            "attendance_percentage": summary["attendance_percentage"],
        }
    )
