import json
from collections import Counter, defaultdict
from django.shortcuts import render
from database.mongo import db


STUDENTS_COLLECTION = db["students"]
ATTENDANCE_COLLECTION = db["attendance_logs"]


def clean_value(value, fallback="-"):
    value = "" if value is None else str(value).strip()
    return value or fallback


def student_name(student):
    return clean_value(
        student.get("name")
        or student.get("student_name")
        or student.get("full_name"),
        "Unnamed Student"
    )


def analytics_view(request):
    students = []
    for student in STUDENTS_COLLECTION.find():
        students.append({
            "id": str(student.get("_id")),
            "name": student_name(student),
            "course": clean_value(student.get("course")),
            "email": clean_value(student.get("email")),
            "attendance_percentage": 0,
        })

    attendance_records = list(ATTENDANCE_COLLECTION.find())
    total_students = len(students)
    total_attendance = len(attendance_records)
    present_students = len([
        record for record in attendance_records
        if record.get("status") == "Present"
    ])
    absent_students = len([
        record for record in attendance_records
        if record.get("status") == "Absent"
    ])
    attendance_percentage = round(
        (present_students / total_attendance) * 100,
        2
    ) if total_attendance else 0

    stats_by_name = defaultdict(lambda: {"total": 0, "present": 0})
    for record in attendance_records:
        name = clean_value(record.get("student_name"), "")
        if not name:
            continue
        stats_by_name[name.lower()]["total"] += 1
        if record.get("status") == "Present":
            stats_by_name[name.lower()]["present"] += 1

    for student in students:
        stats = stats_by_name.get(student["name"].lower(), {"total": 0, "present": 0})
        student["attendance_percentage"] = round(
            (stats["present"] / stats["total"]) * 100,
            2
        ) if stats["total"] else 0

    course_counts = Counter(student["course"] for student in students)
    course_labels = json.dumps(list(course_counts.keys()))
    course_values = json.dumps(list(course_counts.values()))

    low_attendance_students = [
        student for student in students
        if student["attendance_percentage"] and student["attendance_percentage"] < 75
    ]

    ai_insights = [
        f"{total_students} students are currently registered.",
        f"{total_attendance} attendance records are available for analysis.",
        f"{len(low_attendance_students)} students are below 75% attendance.",
        f"Overall attendance rate is {attendance_percentage}%.",
    ]

    recent_activities = []
    for record in ATTENDANCE_COLLECTION.find().sort("attendance_date", -1).limit(5):
        recent_activities.append(
            f"{clean_value(record.get('student_name'), 'Student')} - "
            f"{clean_value(record.get('type'), record.get('status') or 'Attendance')} "
            f"on {clean_value(record.get('attendance_date'))}"
        )

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

    return render(request, "analytics/analytics.html", context)
