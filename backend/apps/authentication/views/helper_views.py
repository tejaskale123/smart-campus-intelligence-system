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

    filters = [{"student_id": str(student["_id"]) }]

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
