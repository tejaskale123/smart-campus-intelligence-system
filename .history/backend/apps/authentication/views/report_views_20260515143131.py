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


@login_required
@admin_only
def reports(request):
    return render(request, "dashboard/reports.html")


@login_required
@admin_only
def reports_page(request):
    attendance_records = list(
        ATTENDANCE_COLLECTION.find().sort("attendance_date", -1)
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
        'Date'
    ])

    attendance_records = ATTENDANCE_COLLECTION.find()
    for attendance in attendance_records:
        writer.writerow([
            attendance.get('student_name'),
            attendance.get('student_email'),
            attendance.get('student_course'),
            attendance.get('status'),
            attendance.get('attendance_date')
        ])

    return response


@login_required
@admin_only
def download_pdf_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(180, 750, "SMART CAMPUS REPORT")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 720, f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}")

    pdf.setFont("Helvetica-Bold", 14)
    y = 670
    pdf.drawString(50, y, "Student")
    pdf.drawString(250, y, "Status")
    pdf.drawString(400, y, "Date")

    y -= 30
    attendance_records = ATTENDANCE_COLLECTION.find()
    pdf.setFont("Helvetica", 12)

    for attendance in attendance_records:
        student_name = attendance.get('student_name', 'Unknown')
        status = attendance.get('status', 'N/A')
        date = attendance.get('attendance_date', 'N/A')

        pdf.drawString(50, y, str(student_name))
        pdf.drawString(250, y, str(status))
        pdf.drawString(400, y, str(date))

        y -= 25
        if y < 60:
            pdf.showPage()
            y = 750

    pdf.save()
    return response


@login_required
@admin_only
def performance_report(request):
    students = list(STUDENTS_COLLECTION.find())
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
