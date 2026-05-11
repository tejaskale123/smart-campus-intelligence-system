from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from collections import Counter
import json


from .face_utils import recognize_faces
import threading


from bson import ObjectId
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render

from django.conf import settings
import csv
import os
import cv2
from django.http import HttpResponse

from database.mongo import db
from apps.authentication.models import UserProfile
from .decorators import (
    admin_only,
    get_user_role,
    role_guard,
    student_only,
    teacher_only,
    teacher_or_admin,
)
from .services import create_student, get_all_students, get_student

from django.shortcuts import render
from pymongo import MongoClient
from database.mongo import db


client = MongoClient("mongodb://localhost:27017/")

db = client["smart_campus_db"]

students_collection = db["students"]

attendance_collection = db["attendance"]

STUDENTS_COLLECTION = db["students"]
ATTENDANCE_COLLECTION = db["attendance_logs"]
VALID_ATTENDANCE_STATUS = ["Present", "Absent"]


# ==============================
# DATA HELPERS
# ==============================

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


def get_all_attendance_records(limit=None):
    cursor = ATTENDANCE_COLLECTION.find().sort("attendance_date", -1)
    if limit:
        cursor = cursor.limit(limit)
    return serialize_attendance(cursor)


def get_attendance_summary(records):
    total = len(records)
    present = len([
        record for record in records
        if record.get("status") == "Present"
    ])
    absent = total - present
    percentage = round((present / total) * 100, 2) if total else 0

    return {
        "total_attendance": total,
        "present_count": present,
        "absent_count": absent,
        "present_students": present,
        "absent_students": absent,
        "attendance_percentage": percentage,
    }


def get_weekly_attendance_data(records):
    labels = []
    values = []
    today = datetime.today().date()

    for day_offset in range(6, -1, -1):
        current_day = today - timedelta(days=day_offset)
        current_date = current_day.strftime("%Y-%m-%d")
        labels.append(current_day.strftime("%a"))
        values.append(len([
            record for record in records
            if record.get("attendance_date") == current_date
            and record.get("status") == "Present"
        ]))

    return labels, values


def get_student_weekly_attendance_data(records):
    labels = []
    values = []
    today = datetime.today().date()

    for day_offset in range(6, -1, -1):
        current_day = today - timedelta(days=day_offset)
        current_date = current_day.strftime("%Y-%m-%d")
        labels.append(current_day.strftime("%a"))
        values.append(1 if any(
            record.get("attendance_date") == current_date
            and record.get("status") == "Present"
            for record in records
        ) else 0)

    return labels, values


def get_monthly_attendance_data(records):
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    monthly_counts = {month: 0 for month in months}

    for record in records:
        attendance_date = record.get("attendance_date")
        if not attendance_date:
            continue

        try:
            month_index = int(str(attendance_date).split("-")[1]) - 1
            monthly_counts[months[month_index]] += 1
        except (ValueError, IndexError):
            continue

    return list(monthly_counts.keys()), list(monthly_counts.values())


def get_total_teachers():
    try:
        return User.objects.filter(userprofile__role="teacher").count()
    except Exception:
        return 0


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
        filters.append({"student_name": student.get("name", "")})
    if student.get("username"):
        filters.append({"student_username": student.get("username", "")})
    if student.get("email"):
        filters.append({"student_email": student.get("email", "")})

    return {"$or": filters}


def get_student_attendance_records(student):
    return serialize_attendance(
        ATTENDANCE_COLLECTION.find(
            get_student_attendance_filter(student)
        ).sort("attendance_date", -1)
    )


def build_dashboard_context(records=None):
    attendance_records = records if records is not None else get_all_attendance_records()
    summary = get_attendance_summary(attendance_records)
    weekly_labels, weekly_values = get_weekly_attendance_data(attendance_records)
    monthly_labels, monthly_values = get_monthly_attendance_data(attendance_records)

    return {
        "total_students": STUDENTS_COLLECTION.count_documents({}),
        "total_teachers": get_total_teachers(),
        "total_attendance": summary["total_attendance"],
        "present_count": summary["present_count"],
        "absent_count": summary["absent_count"],
        "present_students": summary["present_students"],
        "absent_students": summary["absent_students"],
        "attendance_percentage": summary["attendance_percentage"],
        "weekly_labels": weekly_labels,
        "weekly_values": weekly_values,
        "monthly_labels": monthly_labels,
        "monthly_values": monthly_values,
        "attendance_records": attendance_records[:10],
        "recent_attendance": attendance_records[:8],
    }


def build_student_dashboard_context(user):
    student = serialize_student(find_student_for_user(user))
    attendance_records = get_student_attendance_records(student)
    context = build_dashboard_context(attendance_records)
    context.update({
        "student": student,
        "attendance_records": attendance_records,
    })
    return context


def get_students_for_dropdown():
    students = list(STUDENTS_COLLECTION.find().sort("name", 1))
    for student in students:
        student["id"] = str(student["_id"])
    return students


# ==============================
# AUTH VIEWS
# ==============================

def home(request):
    return render(request, "base/base.html")


def login_page(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            logout(request)
            return render(
                request,
                "authentication/login.html",
                {"error": "Profile not found. Please contact admin."}
            )

        if profile.role == "admin":
            return redirect("admin_dashboard")
        if profile.role == "teacher":
            return redirect("teacher_dashboard")
        if profile.role == "student":
            return redirect("student_dashboard")

        logout(request)
        return render(
            request,
            "authentication/login.html",
            {"error": "Invalid role assigned. Please contact admin."}
        )

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                logout(request)
                return render(
                    request,
                    "authentication/login.html",
                    {"error": "Profile not found. Please contact admin."}
                )

            if profile.role == "admin":
                return redirect("admin_dashboard")
            if profile.role == "teacher":
                return redirect("teacher_dashboard")
            if profile.role == "student":
                return redirect("student_dashboard")

            logout(request)
            return render(
                request,
                "authentication/login.html",
                {"error": "Invalid role assigned. Please contact admin."}
            )

        return render(
            request,
            "authentication/login.html",
            {"error": "Invalid username or password"}
        )

    return render(request, "authentication/login.html")


def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        User.objects.create_user(username=username, password=password)
        return redirect("login")

    return render(request, "authentication/register.html")


def logout_page(request):
    logout(request)
    return redirect("login")


# ==============================
# DASHBOARD VIEWS
# ==============================

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
@admin_only
def admin_teachers(request):
    teachers = (
        UserProfile.objects
        .select_related("user")
        .filter(role="teacher")
        .order_by("user__username")
    )

    return render(
        request,
        "teachers/teachers_list.html",
        {"teachers": teachers}
    )


@login_required
@admin_only
def add_teacher(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        department = (request.POST.get("department") or "").strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("add_teacher")

        teacher_user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        profile = teacher_user.userprofile
        profile.role = "teacher"
        profile.department = department
        profile.save()

        messages.success(request, "Teacher created successfully.")
        return redirect("admin_teachers")

    return render(request, "teachers/add_teacher.html")


@login_required
@admin_only
def update_teacher(request, teacher_id):
    profile = get_object_or_404(
        UserProfile.objects.select_related("user"),
        id=teacher_id,
        role="teacher"
    )

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        department = (request.POST.get("department") or "").strip()

        if (
            User.objects
            .filter(username=username)
            .exclude(id=profile.user.id)
            .exists()
        ):
            messages.error(request, "Username already exists.")
            return redirect("update_teacher", teacher_id=profile.id)

        profile.user.username = username
        profile.user.email = email
        if password:
            profile.user.set_password(password)
        profile.user.save()

        profile.department = department
        profile.save()

        messages.success(request, "Teacher updated successfully.")
        return redirect("admin_teachers")

    return render(
        request,
        "teachers/add_teacher.html",
        {"teacher": profile, "is_update": True}
    )


@login_required
@admin_only
def delete_teacher(request, teacher_id):
    profile = get_object_or_404(UserProfile, id=teacher_id, role="teacher")
    profile.user.delete()
    messages.success(request, "Teacher deleted successfully.")
    return redirect("admin_teachers")

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
        attendance_percentage = round(
            (present_students / total_students) * 100,
            2
        )

    context = {
        "students": students,
        "total_students": total_students,
        "present_students": present_students,
        "absent_students": absent_students,
        "attendance_percentage": attendance_percentage,
    }

    return render(
        request,
        "analytics/analytics.html",
        context
    )

@login_required
@admin_only
def reports(request):
    return render(request, "dashboard/reports.html")


@login_required
@admin_only
def settings_page(request):
    if request.method == "POST":
        email = (request.POST.get("admin_email") or "").strip()
        password = request.POST.get("password") or ""

        if email:
            request.user.email = email

        if password:
            request.user.set_password(password)
            messages.info(request, "Password updated. Please login again.")
            request.user.save()
            logout(request)
            return redirect("login")

        request.user.save()
        messages.success(request, "Settings saved successfully.")
        return redirect("settings")

    return render(request, "dashboard/settings.html")


# ==============================
# STUDENT MANAGEMENT
# ==============================

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
                stats = stats_map.setdefault(
                    key,
                    {"total": 0, "present": 0}
                )
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
            "Low Attendance"
            if percentage < 75
            else "Good"
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


# ==============================
# ATTENDANCE
# ==============================

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

        ATTENDANCE_COLLECTION.find(

            attendance_filter

        ).sort(

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

            "present_students": summary["present_students"],

            "absent_students": summary["absent_students"],

            "total_attendance": summary["total_attendance"],

            "attendance_percentage": summary["attendance_percentage"],

        }

    )

#============================
# ATTENDANCE
#===========================
@login_required
@teacher_or_admin
def add_attendance(request):

    students = list(

        STUDENTS_COLLECTION.find().sort("name", 1)

    )

    for student in students:

        student["id"] = str(student["_id"])

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

        existing_record = ATTENDANCE_COLLECTION.find_one({

            "student_id": str(student["_id"]),

            "attendance_date": attendance_date

        })

        if existing_record:

            messages.warning(

                request,

                "Attendance already marked for this date."

            )

            return redirect("attendance_list")

        ATTENDANCE_COLLECTION.insert_one({

            "student_id": str(student["_id"]),

            "student_name": student.get("name"),

            "student_email": student.get("email"),

            "student_course": student.get("course"),

            "attendance_date": attendance_date,

            "status": status,

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

            "students": students

        }

    )


# ==============================
# REPORTS
# ==============================

@login_required
@admin_only
def reports_page(request):

    attendance_records = list(

        ATTENDANCE_COLLECTION.find().sort(

            "attendance_date",

            -1

        )

    )

    total_attendance = len(attendance_records)

    present_count = len([

        record for record in attendance_records

        if record.get("status") == "Present"

    ])

    absent_count = len([

        record for record in attendance_records

        if record.get("status") == "Absent"

    ])

    attendance_percentage = 0

    if total_attendance > 0:

        attendance_percentage = round(

            (present_count / total_attendance) * 100,

            1

        )

    context = {

        "attendance_records": attendance_records,

        "total_attendance": total_attendance,

        "present_count": present_count,

        "absent_count": absent_count,

        "attendance_percentage": attendance_percentage,

    }

    return render(

        request,

        "dashboard/reports.html",

        context

    )

    # =====================================
# PDF REPORT
# =====================================

@login_required
@admin_only
def download_pdf_report(request):

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="attendance_report.pdf"'

    response.write(
        b"SMART CAMPUS PDF REPORT"
    )

    return response


# =====================================
# CSV EXPORT
# =====================================

@login_required
@admin_only
def export_csv_report(request):

    response = HttpResponse(
        content_type='text/csv'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="attendance_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Student',
        'Email',
        'Course',
        'Status',
        'Date'
    ])

    attendance_records = ATTENDANCE_COLLECTION.find()

    for attendance in attendance_records:

        writer.writerow([

            attendance.get(
                'student_name'
            ),

            attendance.get(
                'student_email'
            ),

            attendance.get(
                'student_course'
            ),

            attendance.get(
                'status'
            ),

            attendance.get(
                'attendance_date'
            )

        ])

    return response


# =====================================
# DOWNLOAD PDF REPORT
# =====================================

@login_required
@admin_only
def download_pdf_report(request):

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = (
        'attachment; filename="attendance_report.pdf"'
    )

    # CREATE PDF

    pdf = canvas.Canvas(
        response,
        pagesize=letter
    )

    width, height = letter

    # TITLE

    pdf.setFont(
        "Helvetica-Bold",
        24
    )

    pdf.drawString(
        180,
        750,
        "SMART CAMPUS REPORT"
    )

    # DATE

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        50,
        720,
        f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    )

    # TABLE HEADERS

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    y = 670

    pdf.drawString(50, y, "Student")
    pdf.drawString(250, y, "Status")
    pdf.drawString(400, y, "Date")

    y -= 30

    # FETCH DATA

    attendance_records = ATTENDANCE_COLLECTION.find()

    pdf.setFont(
        "Helvetica",
        12
    )

    for attendance in attendance_records:

        student_name = attendance.get(
            'student_name',
            'Unknown'
        )

        status = attendance.get(
            'status',
            'N/A'
        )

        date = attendance.get(
            'attendance_date',
            'N/A'
        )

        pdf.drawString(
            50,
            y,
            str(student_name)
        )

        pdf.drawString(
            250,
            y,
            str(status)
        )

        pdf.drawString(
            400,
            y,
            str(date)
        )

        y -= 25

        # NEW PAGE

        if y < 60:

            pdf.showPage()

            y = 750

    # SAVE PDF

    pdf.save()

    return response

 # =====================================
# PERFORMANCE REPORT
# =====================================

@login_required
@admin_only
def performance_report(request):

    students = list(
        STUDENTS_COLLECTION.find()
    )

    attendance_records = list(
        ATTENDANCE_COLLECTION.find()
    )

    total_students = len(students)

    total_attendance = len(attendance_records)

    present_count = len([
        a for a in attendance_records
        if a.get("status") == "Present"
    ])

    absent_count = len([
        a for a in attendance_records
        if a.get("status") == "Absent"
    ])

    if total_attendance > 0:

        attendance_percentage = round(
            (present_count / total_attendance) * 100,
            2
        )

    else:

        attendance_percentage = 0

    context = {

        "total_students": total_students,

        "total_attendance": total_attendance,

        "present_count": present_count,

        "absent_count": absent_count,

        "attendance_percentage": attendance_percentage,

        "students": students,

    }

    return render(
        request,
        "dashboard/performance_report.html",
        context
    )



def analytics_view(request):

    # ====================================
    # STUDENTS DATA
    # ====================================

    students = [

        {
            "name": "Tejas Kale",
            "course": "BCA",
            "email": "tejas@gmail.com",
            "attendance_percentage": 82
        },

        {
            "name": "Rohit",
            "course": "MCA",
            "email": "rohit@gmail.com",
            "attendance_percentage": 65
        },

        {
            "name": "Soham",
            "course": "B.Tech",
            "email": "soham@gmail.com",
            "attendance_percentage": 90
        },

        {
            "name": "Vijay",
            "course": "B.Com",
            "email": "vijay@gmail.com",
            "attendance_percentage": 70
        }

    ]

    # ====================================
    # DASHBOARD COUNTS
    # ====================================

    total_students = len(students)

    present_students = 3

    absent_students = 1

    attendance_percentage = round(
        (present_students / total_students) * 100,
        2
    )

    # ====================================
    # COURSE DISTRIBUTION
    # ====================================

    course_counts = Counter(

        student["course"]

        for student in students

    )

    course_labels = json.dumps(
        list(course_counts.keys())
    )

    course_values = json.dumps(
        list(course_counts.values())
    )

    # ====================================
    # LOW ATTENDANCE
    # ====================================

    low_attendance_students = [

        student

        for student in students

        if student["attendance_percentage"] < 75

    ]

    # ====================================
    # AI INSIGHTS
    # ====================================

    ai_insights = [

        "Attendance increased this week",

        "BCA students performing well",

        "2 students need attendance warning",

        "Overall analytics are stable"

    ]

    # ====================================
    # RECENT ACTIVITY
    # ====================================

    recent_activities = [

        "Rohit marked present today",

        "Teacher uploaded attendance",

        "New student added to BCA"

    ]

    # ====================================
    # CONTEXT
    # ====================================

    context = {

        "students": students,

        "total_students": total_students,

        "present_students": present_students,

        "absent_students": absent_students,

        "attendance_percentage": attendance_percentage,

        "course_labels": course_labels,

        "course_values": course_values,

        "ai_insights": ai_insights,

        "low_attendance_students": low_attendance_students,

        "recent_activities": recent_activities,

    }

    return render(
        request,
        "analytics/analytics.html",
        context
    )

    def face_attendance_page(request):

     return render(
        request,
        "authentication/face_attendance.html"
    )



def start_face_attendance(request):

    threading.Thread(
        target=recognize_faces
    ).start()

    return render(
        request,
        "authentication/face_attendance.html"
    )

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)


FACES_DIR = os.path.join(
    BASE_DIR,
    "media",
    "faces"
)



BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

FACES_DIR = os.path.join(
    BASE_DIR,
    "media",
    "faces"
)

os.makedirs(FACES_DIR, exist_ok=True)


# ==========================================
# FACE ATTENDANCE SYSTEM
# ==========================================

import base64
from django.http import JsonResponse


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

FACES_DIR = os.path.join(
    BASE_DIR,
    "media",
    "faces"
)

os.makedirs(
    FACES_DIR,
    exist_ok=True
)


# ==========================================
# FACE ATTENDANCE PAGE
# ==========================================

def face_attendance_page(request):

    return render(
        request,
        "authentication/face_attendance.html"
    )


# ==========================================
# START FACE ATTENDANCE
# ==========================================

def start_face_attendance(request):

    threading.Thread(
        target=recognize_faces
    ).start()

    return render(
        request,
        "authentication/face_attendance.html"
    )


# ==========================================
# REGISTER FACE
# ==========================================

def register_face(request):

    if request.method == "POST":

        student_name = request.POST.get(
              "student_name"
)

roll_number = request.POST.get(
    "roll_number"
)

course = request.POST.get(
    "course"
)

        images = request.POST.getlist(
            "images[]"
        )

       

        # VALIDATION
        if not student_name:
          
            return JsonResponse({

                "status": "error",

                "message":
                "Student name required"

            })



        # CREATE FOLDER
        student_folder = os.path.join(

            FACES_DIR,

            student_name
            .lower()
            .replace(" ", "_")

        )

        os.makedirs(
            student_folder,
            exist_ok=True
        )



        # SAVE IMAGES
        for index, image_data in enumerate(images):

            try:

                format, imgstr = image_data.split(
                    ";base64,"
                )

                image_bytes = base64.b64decode(
                    imgstr
                )

                image_path = os.path.join(

                    student_folder,

                    f"{index+1}.jpg"

                )

                with open(
                    image_path,
                    "wb"
                ) as f:

                    f.write(image_bytes)

            except Exception as e:

                print(
                    "Image Save Error:",
                    e
                )


    print(
        f"{student_name} registered successfully"
    )

    # RELOAD FACE DATASET
    from importlib import reload
    from apps.authentication import face_utils

    reload(face_utils)

    return JsonResponse({

        "status": "success",

        "message":
        f"{student_name} registered"

    })


    return render(

        request,

        "authentication/register_face.html"

    )