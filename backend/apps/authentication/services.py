from bson import ObjectId

from database.mongo import db


STUDENTS_COLLECTION = db["students"]
ATTENDANCE_COLLECTION = db["attendance_logs"]


def to_object_id(value):
    try:
        return ObjectId(value)
    except Exception:
        return None


# ==============================
# STUDENTS
# ==============================

def create_student(data):
    return STUDENTS_COLLECTION.insert_one(data)


def get_all_students(query=None):
    return STUDENTS_COLLECTION.find(query or {}).sort("name", 1)


def get_student_by_id(student_id):
    object_id = to_object_id(student_id)
    if not object_id:
        return None

    return STUDENTS_COLLECTION.find_one({"_id": object_id})


# Backward-compatible name used by existing views.
def get_student(student_id):
    return get_student_by_id(student_id)


# ==============================
# ATTENDANCE
# ==============================

def save_attendance(student, attendance_date, status):
    if not student or status not in ["Present", "Absent"] or not attendance_date:
        return None

    attendance_data = {
        "student_id": str(student["_id"]),
        "student_name": student.get("name", ""),
        "attendance_date": attendance_date,
        "status": status,
    }

    return ATTENDANCE_COLLECTION.insert_one(attendance_data)


def get_attendance_records(query=None, limit=None):
    cursor = ATTENDANCE_COLLECTION.find(query or {}).sort("attendance_date", -1)
    if limit:
        cursor = cursor.limit(limit)
    return cursor


def attendance_stats(query=None):
    records = list(get_attendance_records(query))
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
        "records": records,
    }
