import csv
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from apps.authentication.decorators import (
    admin_only,
)
from .helper_views import *
from database.mongo import db

ATTENDANCE_COLLECTION = db["attendance_logs"]
STUDENTS_COLLECTION = db["students"]


def clean_value(value, fallback="-"):
    value = "" if value is None else str(value).strip()
    return value or fallback


def display_student_name(record):
    return clean_value(
        record.get("student_name")
        or record.get("name")
        or record.get("full_name"),
        "Unknown Student"
    )


def serialize_report_record(record):
    return {
        "student_name": display_student_name(record),
        "student_email": clean_value(record.get("student_email") or record.get("email")),
        "student_course": clean_value(record.get("student_course") or record.get("course")),
        "status": clean_value(record.get("status")),
        "type": clean_value(record.get("type"), "Manual"),
        "time": clean_value(record.get("time")),
        "attendance_date": clean_value(record.get("attendance_date")),
        "method": clean_value(record.get("method"), "Manual"),
    }


@login_required
@admin_only
def reports(request):
    return render(request, "dashboard/reports.html")


@login_required
@admin_only
def reports_page(request):
    attendance_records = [
        serialize_report_record(record)
        for record in ATTENDANCE_COLLECTION.find().sort("attendance_date", -1)
    ]
    total_students = STUDENTS_COLLECTION.count_documents({})
    face_records = len(
        [record for record in attendance_records if record["method"] == "Face Recognition"]
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
        attendance_percentage = round((present_count / total_attendance) * 100, 1)

    context = {
        "attendance_records": attendance_records,
        "recent_records": attendance_records[:8],
        "total_students": total_students,
        "face_records": face_records,
        "total_attendance": total_attendance,
        "present_count": present_count,
        "absent_count": absent_count,
        "attendance_percentage": attendance_percentage,
    }

    return render(request, "dashboard/reports.html", context)


@login_required
@admin_only
def export_csv_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Student',
        'Email',
        'Course',
        'Status',
        'Type',
        'Time',
        'Date',
        'Method'
    ])

    attendance_records = ATTENDANCE_COLLECTION.find().sort("attendance_date", -1)
    for attendance in attendance_records:
        record = serialize_report_record(attendance)
        writer.writerow([
            record["student_name"],
            record["student_email"],
            record["student_course"],
            record["status"],
            record["type"],
            record["time"],
            record["attendance_date"],
            record["method"],
        ])

    return response


@login_required
@admin_only
def download_pdf_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(165, 750, "Smart Campus Attendance Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 720, f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}")

    attendance_records = [
        serialize_report_record(record)
        for record in ATTENDANCE_COLLECTION.find().sort("attendance_date", -1)
    ]
    total = len(attendance_records)
    present = len([record for record in attendance_records if record["status"] == "Present"])
    absent = len([record for record in attendance_records if record["status"] == "Absent"])

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, 695, f"Total Records: {total}")
    pdf.drawString(190, 695, f"Present: {present}")
    pdf.drawString(300, 695, f"Absent: {absent}")

    y = 670
    pdf.drawString(40, y, "Student")
    pdf.drawString(185, y, "Course")
    pdf.drawString(275, y, "Status")
    pdf.drawString(345, y, "Type")
    pdf.drawString(405, y, "Date")
    pdf.drawString(485, y, "Method")

    y -= 30
    pdf.setFont("Helvetica", 9)

    for attendance in attendance_records:
        pdf.drawString(40, y, attendance["student_name"][:24])
        pdf.drawString(185, y, attendance["student_course"][:13])
        pdf.drawString(275, y, attendance["status"][:10])
        pdf.drawString(345, y, attendance["type"][:8])
        pdf.drawString(405, y, attendance["attendance_date"][:12])
        pdf.drawString(485, y, attendance["method"][:16])

        y -= 25
        if y < 60:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = 750

    pdf.save()
    return response


@login_required
@admin_only
def performance_report(request):
    students = []
    for student in STUDENTS_COLLECTION.find():
        students.append({
            "name": clean_value(student.get("name") or student.get("student_name"), "Unnamed Student"),
            "course": clean_value(student.get("course")),
            "email": clean_value(student.get("email")),
        })

    attendance_records = list(ATTENDANCE_COLLECTION.find())

    total_students = len(students)
    total_attendance = len(attendance_records)
    present_count = len([
        a for a in attendance_records
        if a.get('status') == 'Present'
    ])
    absent_count = len([
        a for a in attendance_records
        if a.get('status') == 'Absent'
    ])

    attendance_percentage = round(
        (present_count / total_attendance) * 100,
        2
    ) if total_attendance else 0

    context = {
        "total_students": total_students,
        "total_attendance": total_attendance,
        "present_count": present_count,
        "absent_count": absent_count,
        "attendance_percentage": attendance_percentage,
        "students": students,
    }

    return render(request, "dashboard/performance_report.html", context)
