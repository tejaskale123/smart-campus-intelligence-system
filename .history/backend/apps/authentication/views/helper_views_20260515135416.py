from datetime import datetime, timedelta
from django.contrib.auth.models import User
from database.mongo import db

STUDENTS_COLLECTION = db["students"]
ATTENDANCE_COLLECTION = db["attendance_logs"]

VALID_ATTENDANCE_STATUS = ["Present", "Absent"]


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

    cursor = ATTENDANCE_COLLECTION.find().sort(
        "attendance_date",
        -1
    )

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

    percentage = round(
        (present / total) * 100,
        2
    ) if total else 0

    return {
        "total_attendance": total,
        "present_count": present,
        "absent_count": absent,
        "attendance_percentage": percentage,
    }


def get_total_teachers():

    try:
        return User.objects.filter(
            userprofile__role="teacher"
        ).count()

    except Exception:
        return 0