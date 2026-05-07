from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from django.conf import settings
from bson import ObjectId
from .decorators import admin_only

from database.mongo import db
from django.contrib.auth.models import User
from django.contrib.auth import (

    authenticate,
    login,
    logout

)

from .services import (

    create_student,

    get_all_students,

    get_student

)

# ==============================
# HOME PAGE
# ==============================

def home(request):

    return render(
        request,
        'base/base.html'
    )


# ==============================
# LOGIN
# ==============================

def login_page(request):

    if request.method == "POST":

        username = request.POST.get(

            "username"

        )

        password = request.POST.get(

            "password"

        )

        user = authenticate(

            request,

            username=username,

            password=password

        )

        if user is not None:

            login(

                request,
                user

            )

            return redirect(

                'dashboard'

            )

        else:

            return render(

                request,

                'authentication/login.html',

                {

                    'error':

                    'Invalid Username or Password'

                }

            )

    return render(

        request,

        'authentication/login.html'

    )
# ==============================
# DASHBOARD
# ==============================

@login_required

@admin_only

def dashboard(request):

    # TOTAL COUNTS

    total_students = db["students"].count_documents({})

    total_attendance = db["attendance_logs"].count_documents({})

    present_count = db["attendance_logs"].count_documents({

        "status": "Present"

    })

    absent_count = db["attendance_logs"].count_documents({

        "status": "Absent"

    })


    # ==========================
    # MONTHLY ATTENDANCE
    # ==========================

    monthly_data = {

        "Jan": 0,
        "Feb": 0,
        "Mar": 0,
        "Apr": 0,
        "May": 0,
        "Jun": 0,
        "Jul": 0,
        "Aug": 0,
        "Sep": 0,
        "Oct": 0,
        "Nov": 0,
        "Dec": 0

    }

    attendance_records = db["attendance_logs"].find()

    for attendance in attendance_records:

        date = attendance.get(

            "attendance_date"

        )

        if date:

            month = date.split("-")[1]

            if month == "01":

                monthly_data["Jan"] += 1

            elif month == "02":

                monthly_data["Feb"] += 1

            elif month == "03":

                monthly_data["Mar"] += 1

            elif month == "04":

                monthly_data["Apr"] += 1

            elif month == "05":

                monthly_data["May"] += 1

            elif month == "06":

                monthly_data["Jun"] += 1

            elif month == "07":

                monthly_data["Jul"] += 1

            elif month == "08":

                monthly_data["Aug"] += 1

            elif month == "09":

                monthly_data["Sep"] += 1

            elif month == "10":

                monthly_data["Oct"] += 1

            elif month == "11":

                monthly_data["Nov"] += 1

            elif month == "12":

                monthly_data["Dec"] += 1

    context = {

        "total_students": total_students,

        "total_attendance": total_attendance,

        "present_count": present_count,

        "absent_count": absent_count,

        "monthly_labels": list(

            monthly_data.keys()

        ),

        "monthly_values": list(

            monthly_data.values()

        )

    }

    return render(

        request,

        'dashboard/admin_dashboard.html',

        context

    )
# ==============================
# ADD STUDENT
# ==============================
@login_required
@admin_only
def add_student(request):

    if request.method == "POST":

        profile_image = request.FILES.get(

            "profile_image"

        )

        student_data = {

            "name": request.POST.get("name"),

            "course": request.POST.get("course"),

            "age": request.POST.get("age"),

            "email": request.POST.get("email"),

            "profile_image": profile_image.name if profile_image else ""

        }

        create_student(student_data)

        # SAVE IMAGE

        if profile_image:

            with open(

                f"media/{profile_image.name}",

                "wb+"

            ) as destination:

                for chunk in profile_image.chunks():

                    destination.write(chunk)

        return redirect('students_list')

    return render(

        request,

        'students/add_student.html'

    )

# ==============================
# STUDENTS LIST + SEARCH
# ==============================
@login_required
@admin_only
def students_list(request):

    search_query = request.GET.get('search')

    if search_query:

        students_cursor = db["students"].find({

            "name": {

                "$regex": search_query,

                "$options": "i"

            }

        })

    else:

        students_cursor = get_all_students()

    students = []

    for student in students_cursor:

        student['id'] = str(student['_id'])

        student_name = student['name']

        total_attendance = db["attendance_logs"].count_documents({

            "student_name": student_name

        })

        present_attendance = db["attendance_logs"].count_documents({

            "student_name": student_name,

            "status": "Present"

        })

        if total_attendance > 0:

            percentage = (

                present_attendance / total_attendance

            ) * 100

        else:

            percentage = 0

    student['attendance_percentage'] = round(

            percentage,
            2

        )

        # LOW ATTENDANCE ALERT

    if percentage < 75:

        student['attendance_alert'] = "Low Attendance"

        # SEND EMAIL ALERT

        send_mail(

            'Low Attendance Warning',

            f'''

            Hello {student_name},

            Your attendance is below 75%.

            Please improve your attendance.

            ''',

            settings.EMAIL_HOST_USER,

            [student['email']],

            fail_silently=True

        )

    else:

        student['attendance_alert'] = "Good"

    students.append(student)

    context = {

        "students": students

    }

    return render(

        request,

        'students/students_list.html',

        context

    )
# ==============================
# UPDATE STUDENT
# ==============================

def update_student(request, student_id):

    student = get_student(student_id)

    if request.method == "POST":

        updated_data = {

            "name": request.POST.get("name"),

            "course": request.POST.get("course"),

            "age": request.POST.get("age")

        }

        db["students"].update_one(

            {

                "_id": ObjectId(student_id)

            },

            {

                "$set": updated_data

            }

        )

        return redirect('students_list')

    context = {

        "student": student

    }

    return render(

        request,
        'students/update_student.html',
        context

    )


# ==============================
# DELETE STUDENT
# ==============================

def delete_student(request, student_id):

    db["students"].delete_one({

        "_id": ObjectId(student_id)

    })

    return redirect('students_list')

# ==============================
# ADD ATTENDANCE
# ==============================
@login_required
@admin_only
def add_attendance(request):

    if request.method == "POST":

        attendance_data = {

            "student_name": request.POST.get("student_name"),

            "attendance_date": request.POST.get("attendance_date"),

            "status": request.POST.get("status")

        }

        db["attendance_logs"].insert_one(attendance_data)

        return redirect('attendance_list')

    return render(

        request,
        'attendance/add_attendance.html'

    )

# ==============================
# ATTENDANCE LIST + SEARCH
# ==============================
@login_required
def attendance_list(request):

    search_query = request.GET.get('search')

    if search_query:

        attendance_cursor = db["attendance_logs"].find({

            "student_name": {

                "$regex": search_query,

                "$options": "i"

            }

        })

    else:

        attendance_cursor = db["attendance_logs"].find()

    attendance_records = []

    present_count = 0

    absent_count = 0

    for attendance in attendance_cursor:

        attendance['id'] = str(attendance['_id'])

        attendance_records.append(attendance)

        if attendance['status'] == "Present":

            present_count += 1

        else:

            absent_count += 1

    context = {

        "attendance_records": attendance_records,

        "present_count": present_count,

        "absent_count": absent_count

    }

    return render(

        request,

        'attendance/attendance_list.html',

        context

    )

    # ==============================
# STUDENT DETAIL
# ==============================
@login_required
def student_detail(request, student_id):

    student = get_student(student_id)

    student['id'] = str(student['_id'])

    student_name = student['name']

    attendance_cursor = db["attendance_logs"].find({

        "student_name": student_name

    })

    attendance_records = []

    total_attendance = 0

    present_attendance = 0

    for attendance in attendance_cursor:

        attendance['id'] = str(attendance['_id'])

        attendance_records.append(attendance)

        total_attendance += 1

        if attendance['status'] == "Present":

            present_attendance += 1

    if total_attendance > 0:

        attendance_percentage = (

            present_attendance / total_attendance

        ) * 100

    else:

        attendance_percentage = 0

    context = {

        "student": student,

        "attendance_records": attendance_records,

        "attendance_percentage": round(

            attendance_percentage,
            2

        )

    }

    return render(

        request,

        'students/student_detail.html',

        context

    )

    # ==============================
# REGISTER
# ==============================

def register_page(request):

    if request.method == "POST":

        username = request.POST.get(

            "username"

        )

        password = request.POST.get(

            "password"

        )

        User.objects.create_user(

            username=username,

            password=password

        )

        return redirect('login')

    return render(

        request,

        'authentication/register.html'

    )

    # ==============================
# LOGOUT
# ==============================

def logout_page(request):

    logout(request)

    return redirect('login')